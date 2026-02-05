.PHONY: help build up down logs restart clean test

help:
	@echo "Reddit Summarizer - Available Commands"
	@echo ""
	@echo "  make build      - Build Docker image"
	@echo "  make up         - Start services"
	@echo "  make down       - Stop services"
	@echo "  make logs       - View logs"
	@echo "  make restart    - Restart services"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make shell      - Access container shell"
	@echo "  make test       - Run tests"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Dashboard available at http://localhost:8000"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

shell:
	docker-compose exec app sh

test:
	docker-compose exec app pytest -v

dev:
	docker-compose up --build
