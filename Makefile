# Import and expose environment variables
ifneq (,$(wildcard ./.env))
	cnf ?= .env
	include $(cnf)
	export $(shell sed 's/=.*//' $(cnf))
endif

base_dir = $(shell pwd)

AZ_RESOURCE_GROUP = dm050
AZ_LOCATION = westeurope
AZ_REGISTRY = dm050registry

.PHONY: help


help:
	@echo
	@echo "Usage: make TARGET"
	@echo
	@echo "$(PROJECT_NAME) project automation helper"
	@echo
	@echo "Targets:"
	@echo "    init                  create .env file from template"
	@echo "    dev-build             build Web App image"
	@echo "    dev-up                start up development environment"
	@echo "    dev-down              bring down development environment"
	@echo "    az-up                 bring up Azure environment"
	@echo "    az-app-push           push container image to Azure Container Registry"
	@echo "    az-app-deploy         deploy container as Web App Service"
	@echo "    az-app-configure      configure Web App Service"
	@echo "    az-down               bring down Azure environment"
	@echo


init:
	cp env.template .env


# Build Web App image
dev-build:
	cp docker/.dockerignore .
	docker-compose -f docker/docker-compose.yml build
	rm .dockerignore
	docker image prune -f


# Start up development environment
dev-up:
	docker-compose -f docker/docker-compose.yml up -d


# Bring down development environment
dev-down:
	docker-compose -f docker/docker-compose.yml down


# Bring up Azure environment
az-up:
	@echo "Creating resource group..."
	@az group create -n ${AZ_RESOURCE_GROUP} -l ${AZ_LOCATION}
	@echo
	@echo "Creating storge account and file share..."
	@az storage account create -n dm050storage -g ${AZ_RESOURCE_GROUP} -l ${AZ_LOCATION} --sku Standard_LRS --min-tls-version TLS1_2
	@az storage share create -n containerlogs --account-name dm050storage
	@echo
	@echo "Creating service plan..."
	@az appservice plan create -g ${AZ_RESOURCE_GROUP} -n dm050asp --is-linux --sku B1
	@echo
	@echo "Creating managed identity..."
	@az identity create -g ${AZ_RESOURCE_GROUP} -n dm050identity
	@echo
	@echo "Creating container registry..."
	@az acr create -n ${AZ_REGISTRY} -g ${AZ_RESOURCE_GROUP} --sku Basic
	@az acr update -n ${AZ_REGISTRY} --admin-enabled true
	@echo
	@echo "Assigning role to managed identity..."
	@PRINCIPAL_ID=$$(az identity show -n dm050identity -g ${AZ_RESOURCE_GROUP} --query principalId --output tsv); \
	ACR_ID=$$(az acr show -n ${AZ_REGISTRY} -g ${AZ_RESOURCE_GROUP} --query id --output tsv); \
	az role assignment create --assignee $$PRINCIPAL_ID --role AcrPull --scope $$ACR_ID


# Push container image to Azure Container Registry
az-app-push:
	az acr login -n ${AZ_REGISTRY}
	docker image tag ${WEBAPP_IMAGE_NAME} ${AZ_REGISTRY}.azurecr.io/${WEBAPP_IMAGE_NAME}
	docker image push ${AZ_REGISTRY}.azurecr.io/${WEBAPP_IMAGE_NAME}


# Deploy container image as Web App Service
az-app-deploy:
	@IDENTITY_ID=$$(az identity show -n dm050identity -g ${AZ_RESOURCE_GROUP} --query id --output tsv); \
	az webapp create -g ${AZ_RESOURCE_GROUP} -n dm050webapp -p dm050asp \
	  --container-image-name ${AZ_REGISTRY}.azurecr.io/${WEBAPP_IMAGE_NAME} \
	  --assign-identity $$IDENTITY_ID \
	  --acr-identity $$IDENTITY_ID \
	  --acr-use-identity


# Configure Web App Service
az-app-configure:
	@if az webapp config storage-account list -n dm050webapp -g ${AZ_RESOURCE_GROUP} | grep -q '"name": "LogMapping"'; then \
		echo "LogMapping storage configuration already exists."; \
	else \
		echo "Creating LogMapping storage configuration..."; \
		ACCESS_KEY=$$(az storage account keys list -g ${AZ_RESOURCE_GROUP} -n dm050storage --query [0].value -o tsv); \
		az webapp config storage-account add -g ${AZ_RESOURCE_GROUP} -n dm050webapp --custom-id LogMapping --storage-type AzureFiles --account-name dm050storage --share-name containerlogs --access-key $$ACCESS_KEY --mount-path /app/log; \
	fi
	@echo
	@echo "Creating environment variables..."
	@az webapp config appsettings set --n dm050webapp -g ${AZ_RESOURCE_GROUP} --settings LOG_DIR=/app/log LOGURU_DIAGNOSE=NO LOGURU_FORMAT='${LOGURU_FORMAT}'
	@az webapp config appsettings set --n dm050webapp -g ${AZ_RESOURCE_GROUP} --settings OPENAI_API_KEY=${OPENAI_API_KEY}
	@echo
	@echo "Restarting web app..."
	@az webapp restart -n dm050webapp -g ${AZ_RESOURCE_GROUP}


az-app-delete:
	az webapp delete -n dm050webapp -g ${AZ_RESOURCE_GROUP}
	az appservice plan create -g ${AZ_RESOURCE_GROUP} -n dm050asp --is-linux --sku B1


# Bring down Azure environment
az-down:
	@echo "Deleting ${AZ_RESOURCE_GROUP} resource group..."
	@az group delete -n ${AZ_RESOURCE_GROUP} -y
