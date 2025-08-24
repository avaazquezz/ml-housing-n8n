# Makefile for ML Housing Price Prediction Project

.PHONY: help install install-dev test test-unit test-integration test-api test-model coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development and testing dependencies"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-api      Run API tests only"
	@echo "  test-model    Run ML model tests only"
	@echo "  coverage      Run tests with coverage report"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black and isort"
	@echo "  clean         Clean up generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install black isort flake8 mypy

test:
	pytest

test-unit:
	pytest -m "not integration"

test-integration:
	pytest -m integration

test-api:
	pytest -m api tests/test_api.py

test-model:
	pytest -m model tests/test_model.py

coverage:
	pytest --cov=app --cov=scripts --cov-report=html --cov-report=term-missing

coverage-xml:
	pytest --cov=app --cov=scripts --cov-report=xml

lint:
	flake8 app/ scripts/ tests/
	mypy app/ scripts/ --ignore-missing-imports

format:
	black app/ scripts/ tests/
	isort app/ scripts/ tests/

clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

train-model:
	python scripts/train.py

run-api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

validate-model:
	python -c "import joblib; model = joblib.load('model/model.joblib'); print('Model loaded successfully')"
