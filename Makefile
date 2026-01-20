.PHONY: help build up down clean test-pipeline test-api install-pipeline install-api install-frontend

help:
	@echo "Swedish Labor Market Analytics - Development Commands"
	@echo ""
	@echo "Local Development:"
	@echo "  make build          - Build all Docker containers"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make clean          - Clean up containers and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make test-pipeline  - Run pipeline tests"
	@echo "  make test-api       - Run API tests"
	@echo ""
	@echo "Installation:"
	@echo "  make install-pipeline  - Install pipeline dependencies"
	@echo "  make install-api       - Install API dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f

test-pipeline:
	cd data-pipeline && pytest tests/

test-api:
	cd api && pytest tests/

install-pipeline:
	cd data-pipeline && pip install -r requirements.txt

install-api:
	cd api && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

deploy-gcp:
	@echo "Deploying to GCP..."
	@echo "See DEPLOYMENT.md for detailed instructions"
