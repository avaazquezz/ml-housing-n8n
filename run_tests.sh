#!/bin/bash

# Local test runner script for ML Housing Prediction Project
# This script sets up the environment and runs tests locally

set -e

echo "🏠 ML Housing Prediction - Test Runner"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_status "Python version: $(python3 --version)"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Running in virtual environment: $VIRTUAL_ENV"
else
    print_warning "Not running in a virtual environment. Consider using one."
fi

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-test.txt

# Create model directory if it doesn't exist
mkdir -p model

# Check if model exists, if not train it
if [ ! -f "model/model.joblib" ]; then
    print_status "Model not found. Training new model..."
    python scripts/train.py
else
    print_status "Model found. Skipping training."
fi

# Run tests based on argument
case "${1:-all}" in
    "unit")
        print_status "Running unit tests..."
        pytest tests/test_model.py tests/test_api.py -v
        ;;
    "integration")
        print_status "Running integration tests..."
        pytest tests/test_integration.py -v -m "not integration"
        ;;
    "api")
        print_status "Running API tests..."
        pytest tests/test_api.py -v
        ;;
    "model")
        print_status "Running model tests..."
        pytest tests/test_model.py -v
        ;;
    "coverage")
        print_status "Running tests with coverage..."
        pytest --cov=app --cov=scripts --cov-report=html --cov-report=term-missing
        print_status "Coverage report generated in htmlcov/index.html"
        ;;
    "fast")
        print_status "Running fast tests only..."
        pytest -x -v --tb=short
        ;;
    "docker")
        print_status "Running tests with Docker..."
        
        # Create model directory with proper permissions
        mkdir -p model
        chmod -R 755 model/ tests/ app/ scripts/ 2>/dev/null || true
        
        if command -v "docker compose" &> /dev/null; then
            docker compose -f docker-compose.test.yml down --remove-orphans --volumes 2>/dev/null || true
            docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
            docker compose -f docker-compose.test.yml down
        elif command -v docker-compose &> /dev/null; then
            docker-compose -f docker-compose.test.yml down --remove-orphans --volumes 2>/dev/null || true
            docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
            docker-compose -f docker-compose.test.yml down
        else
            print_error "Neither 'docker compose' nor 'docker-compose' found"
            exit 1
        fi
        ;;
    "lint")
        print_status "Running code quality checks..."
        if command -v flake8 &> /dev/null; then
            flake8 app/ scripts/ tests/ --max-line-length=88
        else
            print_warning "flake8 not installed, skipping..."
        fi
        
        if command -v black &> /dev/null; then
            black --check app/ scripts/ tests/
        else
            print_warning "black not installed, skipping..."
        fi
        
        if command -v isort &> /dev/null; then
            isort --check-only app/ scripts/ tests/
        else
            print_warning "isort not installed, skipping..."
        fi
        ;;
    "all"|*)
        print_status "Running all tests..."
        
        # Lint first
        print_status "Step 1/4: Code quality checks..."
        if command -v flake8 &> /dev/null && command -v black &> /dev/null && command -v isort &> /dev/null; then
            flake8 app/ scripts/ tests/ --max-line-length=88 || print_warning "Linting issues found"
            black --check app/ scripts/ tests/ || print_warning "Code formatting issues found"
            isort --check-only app/ scripts/ tests/ || print_warning "Import sorting issues found"
        else
            print_warning "Some linting tools not installed, skipping quality checks"
        fi
        
        # Model tests
        print_status "Step 2/4: Model tests..."
        pytest tests/test_model.py -v
        
        # API tests
        print_status "Step 3/4: API tests..."
        pytest tests/test_api.py -v
        
        # Integration tests
        print_status "Step 4/4: Integration tests..."
        pytest tests/test_integration.py -v -m "not integration"
        
        print_status "All tests completed!"
        ;;
esac

print_status "Test run completed successfully! ✅"

# Usage information
if [[ "${1}" == "help" ]] || [[ "${1}" == "--help" ]] || [[ "${1}" == "-h" ]]; then
    echo ""
    echo "Usage: $0 [test-type]"
    echo ""
    echo "Available test types:"
    echo "  all         - Run all tests (default)"
    echo "  unit        - Run unit tests only"
    echo "  integration - Run integration tests only"
    echo "  api         - Run API tests only"
    echo "  model       - Run ML model tests only"
    echo "  coverage    - Run tests with coverage report"
    echo "  fast        - Run tests with fail-fast mode"
    echo "  docker      - Run tests using Docker"
    echo "  lint        - Run code quality checks only"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 unit"
    echo "  $0 coverage"
    echo "  $0 docker"
fi
