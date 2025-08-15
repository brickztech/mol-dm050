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

