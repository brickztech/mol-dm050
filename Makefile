# Import and expose environment variables
ifneq (,$(wildcard ./.env))
	cnf ?= .env
	include $(cnf)
	export $(shell sed 's/=.*//' $(cnf))
endif

base_dir = $(shell pwd)

.PHONY: help


help:
	@echo
	@echo "Usage: make TARGET"
	@echo
	@echo "$(PROJECT_NAME) project automation helper"
	@echo
	@echo "Targets:"
	@echo "    init                  create .env file from template"
	@echo "    dev-build             build development images"
	@echo "    dev-up                start up development environment"
	@echo "    dev-down              bring down development environment"
	@echo "    az-create-file-share  create Azure Storage Account with file share for container log"
	@echo "    az-create-registry    create Azure Container Registry"
	@echo


init:
	cp env.template .env


# Build development images
dev-build:
	cp docker/dev/.dockerignore .
	docker-compose -f docker/dev/docker-compose.yml build
	rm .dockerignore
	docker image prune -f


# Start up development environment
dev-up:
	docker-compose -f docker/dev/docker-compose.yml up -d


# Bring down development environment
dev-down:
	docker-compose -f docker/dev/docker-compose.yml down


# Create Azure Storage Account and file share for conatiner log
az-create-file-share:
	az storage account create --name dm050storage --resource-group dm050 --location westeurope --sku Standard_LRS --min-tls-version TLS1_2
	az storage share create --name containerlogs --account-name dm050storage


# Create Azure Container Registry
az-create-registry:
	@echo "Not yet implemented"
