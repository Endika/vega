# Vega Customer Support System Makefile

.PHONY: help install run test lint format clean setup migrate docker-up docker-down

help: ## Show this help message
	@echo "Vega Customer Support System - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install --no-root
	poetry run pre-commit install

setup: ## Setup the project (install dependencies and create directories)
	poetry install --no-root
	mkdir -p knowledge_base
	@echo "Setup complete! Don't forget to:"
	@echo "1. Copy env.example to .env"
	@echo "2. Set your OPENAI_API_KEY in .env"
	@echo "3. Run 'make setup-kb' to setup knowledge base"

migrate: ## Run database migrations
	poetry run alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " message; \
	poetry run alembic revision --autogenerate -m "$$message"

test: ## Run tests
	poetry run pytest --cov=src --cov-report=term-missing -v

setup-kb: ## Setup knowledge base
	poetry run python scripts/setup_knowledge_base.py

lint: ## Run linting
	poetry run ruff check src/ tests/ scripts/
	poetry run mypy src/ tests/

format: ## Format code
	poetry run ruff format src/ tests/ scripts/
	poetry run ruff check --fix src/ tests/ scripts/

pre-commit: ## Run pre-commit checks
	poetry run ruff check src/ tests/
	poetry run ruff format --check src/ tests/
	poetry run mypy src/ tests/

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache

clean-db: ## Clean database files
	rm -f conversations.db
	rm -rf chroma_db/

clean-all: clean clean-db ## Clean everything

docker-build: ## Build Docker image
	docker build -t vega-system .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env vega-system

docker-up: ## Start with docker-compose
	docker-compose up -d

docker-down: ## Stop docker-compose
	docker-compose down

docker-logs: ## Show docker logs
	docker-compose logs -f app

status: ## Show application status
	@echo "Checking application status..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Application not running"

docs: ## Open API documentation
	@echo "Opening API documentation at http://localhost:8000/docs"
	@poetry run python -c "import webbrowser; webbrowser.open('http://localhost:8000/docs')"

check-env: ## Check environment variables
	@echo "Checking environment variables..."
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
		if grep -q "OPENAI_API_KEY" .env; then \
			echo "✅ OPENAI_API_KEY is set"; \
		else \
			echo "❌ OPENAI_API_KEY is not set"; \
		fi; \
	else \
		echo "❌ .env file does not exist"; \
		echo "Please copy env.example to .env and set your variables"; \
	fi

# Default target
.DEFAULT_GOAL := help
