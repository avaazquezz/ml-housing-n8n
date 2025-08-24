# 🏠 ML Housing Price Prediction Bot

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](https://github.com/avaazquezz/ml-housing-n8n/actions)
[![Coverage](https://img.shields.io/badge/Coverage-80%25%2B-green)](https://github.com/avaazquezz/ml-housing-n8n)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **A complete end-to-end machine learning pipeline that predicts California housing prices through a Telegram bot interface powered by n8n workflows.**

## 🚀 Overview

This project demonstrates a production-ready ML pipeline featuring:

- **ML Model**: RandomForestRegressor trained on California Housing dataset
- **API**: FastAPI service with multiple prediction endpoints  
- **Bot Integration**: Telegram bot with n8n workflow automation
- **Containerization**: Docker support for easy deployment
- **Multi-format Input**: Support for JSON and CSV string inputs
- **🧪 Comprehensive Testing**: 60+ tests covering API, ML model, and integration

## 🏗️ Architecture

```mermaid
graph TD
    A[User] -->|Telegram Message| B[n8n Workflow]
    B -->|Parse & Validate| C[Code Node]
    C -->|Route Message| D[Switch Node]
    D -->|Prediction Request| E[HTTP Request]
    E -->|POST /predict-from-string| F[FastAPI Service]
    F -->|ML Prediction| G[Trained Model]
    G -->|Result| F
    F -->|Formatted Response| E
    E -->|Prepare Message| H[Format Node]
    H -->|Send Response| I[Telegram Bot]
    I -->|Response| A
```

## ✨ Features

### 🎯 Core Functionality
- **Multi-Input Support**: Accept structured JSON or comma-separated strings
- **Currency Conversion**: EUR/USD conversion with configurable rates
- **Rich Responses**: Plain text and HTML-formatted messages for Telegram
- **Model Validation**: Health checks and model status endpoints
- **Error Handling**: Comprehensive error responses with user-friendly messages

### 🔧 Technical Features
- **Containerized Deployment**: Docker & Docker Compose ready
- **Environment Configuration**: Flexible configuration via environment variables
- **Async API**: Built with FastAPI for high performance
- **Model Persistence**: Joblib-based model serialization
- **Pipeline Architecture**: Scikit-learn pipeline with preprocessing

## 📋 Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose** (recommended)
- **n8n Instance** (cloud or self-hosted)
- **Telegram Bot Token** (from BotFather)

## 🚦 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/avaazquezz/ml-housing-n8n.git
cd ml-housing-n8n
```

### 2. Run Tests (Recommended First Step)
```bash
# Test everything works with Docker (new Docker CLI)
docker compose -f docker-compose.test.yml up --build

# Or with legacy Docker Compose
docker-compose -f docker-compose.test.yml up --build

# Clean up
docker compose -f docker-compose.test.yml down
# OR: docker-compose -f docker-compose.test.yml down
```

### 3. Environment Setup
Create a `.env` file in the project root:

```env
# Model Configuration
MODEL_WAIT_TIMEOUT=60
PRICE_MULTIPLIER=100000.0
EUR_TO_USD=1.10
TARGET_TRANSFORM=none
MODEL_PATH=/app/model/model.joblib

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Deploy with Docker (Recommended)

```bash
# Build and start services (new Docker CLI)
docker compose up -d

# Or with legacy Docker Compose
docker-compose up -d

# Check service status
docker compose ps
# OR: docker-compose ps

# View logs
docker compose logs -f api
# OR: docker-compose logs -f api
```

### 5. Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Train the model (optional)
python scripts/train.py

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Test prediction
curl -X POST "http://localhost:8000/predict-from-string" \
  -H "Content-Type: application/json" \
  -d '{"input":"4.2,15,5.3,1.2,1800,3.1,34.05,-118.25"}'

# Run tests to verify everything works
docker compose -f docker-compose.test.yml up --build
# OR: docker-compose -f docker-compose.test.yml up --build
```
  -d '{"input":"4.2,15,5.3,1.2,1800,3.1,34.05,-118.25"}'
```

## 📚 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and status |
| `GET` | `/health` | Health check and model status |
| `POST` | `/predict` | Structured JSON prediction |
| `POST` | `/predict-from-string` | CSV string prediction |

### 📝 Request/Response Examples

#### Structured Prediction

**Request:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 4.2,
    "HouseAge": 15,
    "AveRooms": 5.3,
    "AveBedrms": 1.2,
    "Population": 1800,
    "AveOccup": 3.1,
    "Latitude": 34.05,
    "Longitude": -118.25
  }'
```

#### String-based Prediction

**Request:**
```bash
curl -X POST "http://localhost:8000/predict-from-string" \
  -H "Content-Type: application/json" \
  -d '{"input":"4.2,15,5.3,1.2,1800,3.1,34.05,-118.25"}'
```

**Response:**
```json
{
  "prediction": 193101.0,
  "prediction_eur": 193101.0,
  "prediction_usd": 212411.1,
  "prediction_eur_formatted": "193,101.00 EUR",
  "prediction_usd_formatted": "212,411.10 USD",
  "status": "success",
  "message_text": "🏠 Estimated price: 193,101.00 EUR / 212,411.10 USD\n\nStatus: success",
  "message_html": "🏠 <b>Estimated price</b>\n193,101.00 EUR / 212,411.10 USD\n\n✅ <b>Status</b>: success"
}
```

## 🤖 Telegram Bot Setup

### 🚀 Try the Live Demo Bot

**Bot URL**: https://t.me/HouseValuePredictorBot

### 1. Create Your Own Bot with BotFather

```bash
# Start conversation with BotFather
/newbot

# Set bot commands
/setcommands
start - Show welcome message and usage instructions
```

### 2. Bot Commands Configuration

Use this JSON payload to set commands programmatically:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command":"start","description":"Show welcome & usage instructions"},
      {"command":"predict","description":"Predict house price"},
      {"command":"help","description":"Show help & example"}
    ]
  }'
```

### 3. Example Input Format

Send this message to the bot:
```
4.2,15,5.3,1.2,1800,3.1,34.05,-118.25
```

**Parameter Order:**
1. `MedInc` - Median income
2. `HouseAge` - House age
3. `AveRooms` - Average rooms
4. `AveBedrms` - Average bedrooms  
5. `Population` - Population
6. `AveOccup` - Average occupancy
7. `Latitude` - Latitude
8. `Longitude` - Longitude

## 🔧 n8n Workflow Configuration

### 📊 Workflow Visual Overview

The n8n workflow follows this structure:

**Telegram Trigger** → **Code Node** → **Switch Node** → **API/Response Nodes**

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│ Telegram        │    │ Code Node    │    │ Switch      │
│ Trigger         │───▶│ (Parse &     │───▶│ (Route by   │
│ (Receive msg)   │    │ Validate)    │    │ mode)       │
└─────────────────┘    └──────────────┘    └─────────────┘
                                                  │
                        ┌─────────────────────────┼─────────────────────────┐
                        │                         │                         │
                        ▼                         ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
              │ HTTP Request    │       │ Send Welcome    │       │ Send Error      │
              │ (API Call)      │       │ (Instructions)  │       │ (Invalid input) │
              └─────────────────┘       └─────────────────┘       └─────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Send Prediction │
              │ (Formatted)     │
              └─────────────────┘
```

*For detailed workflow configuration, see [`docs/n8n-workflow.md`](docs/n8n-workflow.md)*

### Workflow Nodes Structure

1. **Telegram Trigger** - Receives incoming messages
2. **Code Node** - Parses and validates input
3. **Switch Node** - Routes based on message type
4. **HTTP Request** - Calls prediction API
5. **Set Node** - Formats response message
6. **Telegram Send** - Sends formatted response

### Key n8n Expressions

```javascript
// Extract chat ID
{{$json["message"]["chat"]["id"]}}

// Extract message text
{{$json["message"]["text"]}}

// Normalize input text
const raw = $json["message"]?.text || "";
const normalized = raw.trim().replace(/\u00A0/g, " ").replace(/;/g, ",");

// API response mapping
{{$node["HTTP Request"].json["message_html"]}}
```

### Import Workflow

1. Copy the workflow from `n8n/Workflow_HPP-ML.json`
2. Import into your n8n instance
3. Configure Telegram credentials
4. Update API endpoint URL
5. Activate the workflow

### 🎯 Detailed Node Configuration

#### 1. Telegram Trigger Node
- **Updates**: `message`
- **Webhook URL**: Configure your webhook endpoint
- **Credentials**: Add your Telegram Bot API credentials

#### 2. Code Node (Message Processing)
```javascript
// Detect mode (welcome / predict / error)
const message = ($json?.message?.text ?? $json?.message ?? $json?.text ?? "").toString().trim();

let mode = "";
const m = message.toLowerCase();

// /start -> welcome
if (m === "/start") {
  mode = "welcome";
} 
// Predict -> exactly 8 numbers separated by commas
else if (/^\s*-?\d+([.,]\d+)?\s*(,\s*-?\d+([.,]\d+)?\s*){7}$/.test(message)) {
  mode = "predict";
} 
// Any other case -> error
else {
  mode = "error";
}

return [{
  json: {
    chat_id: $json?.message?.chat?.id ?? $json?.chat_id ?? null,
    message,
    mode
  }
}];
```

#### 3. Switch Node
- **Mode**: Routes based on `{{$json.mode}}`
- **Routes**: 
  - `welcome` → Send Welcome message
  - `predict` → HTTP Request to API
  - `error` → Send Error message

#### 4. HTTP Request Node (API Call)
- **Method**: POST
- **URL**: `https://your-api-endpoint.com/predict-from-string`
- **Body**: 
  ```json
  {
    "input": "{{$json.message}}"
  }
  ```

#### 5. Send Nodes (Telegram Response)
- **Chat ID**: `{{$json.chat_id}}`
- **Message**: `{{$node["HTTP Request"].json["message_html"]}}`
- **Parse Mode**: HTML (for formatted responses)

## 🐳 Docker Configuration

### Services Overview

- **trainer**: Trains the ML model and saves it
- **api**: Serves the FastAPI prediction service

### Commands

```bash
# Build and start
docker compose up -d
# OR: docker-compose up -d

# Rebuild services
docker compose up -d --build
# OR: docker-compose up -d --build

# View logs
docker compose logs -f
# OR: docker-compose logs -f

# Stop services
docker compose down
# OR: docker-compose down

# Clean up
docker compose down -v --remove-orphans
# OR: docker-compose down -v --remove-orphans
```

## 🔍 Model Details

### Dataset
- **Source**: California Housing Dataset (scikit-learn)
- **Features**: 8 numerical features
- **Target**: Median house value (in hundreds of thousands of dollars)

### Pipeline Components
1. **StandardScaler**: Feature normalization
2. **RandomForestRegressor**: Main prediction model
   - n_estimators: 100
   - random_state: 42
   - n_jobs: -1 (parallel processing)

### Performance Considerations
- The model is trained on 1990 California data
- Predictions are estimates and should not be used for real financial decisions
- Consider retraining with more recent data for production use

## 🛠️ Development

### Project Structure
```
ml-housing-n8n/
├── app/
│   └── main.py              # FastAPI application
├── model/
│   └── model.joblib         # Trained ML model
├── n8n/
│   ├── Workflow_HPP-ML.json # n8n workflow configuration
│   └── README-n8n.md        # n8n setup instructions
├── scripts/
│   └── train.py             # Model training script
├── tests/                   # Test suite
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_api.py          # API endpoint tests
│   ├── test_model.py        # ML model tests
│   └── test_integration.py  # Integration tests
├── .github/
│   └── workflows/
│       └── test.yml         # CI/CD pipeline
├── docs/
│   └── n8n-workflow.md     # n8n workflow documentation
├── docker-compose.yml       # Docker services configuration
├── docker-compose.test.yml  # Docker testing configuration
├── Dockerfile               # Container build instructions
├── requirements.txt         # Python dependencies
├── requirements-test.txt    # Testing dependencies
├── pytest.ini              # Pytest configuration
├── .coveragerc             # Coverage configuration
├── Makefile                # Development commands
├── run_tests.sh            # Local test runner script
└── README.md               # This file
```

## 🧪 Testing

This project includes comprehensive testing for both the API and ML model components.

### Test Categories

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: Tests for component interactions
- **API Tests**: FastAPI endpoint testing
- **Model Tests**: ML model validation and performance
- **Performance Tests**: Load and response time testing

### Quick Start Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
./run_tests.sh

# Or use pytest directly
pytest -v
```

### Running Specific Test Types

```bash
# Unit tests only
./run_tests.sh unit
pytest tests/test_model.py tests/test_api.py

# API tests only
./run_tests.sh api
pytest tests/test_api.py

# Model tests only
./run_tests.sh model
pytest tests/test_model.py

# Integration tests
./run_tests.sh integration
pytest tests/test_integration.py -m "not integration"

# With coverage report
./run_tests.sh coverage
pytest --cov=app --cov=scripts --cov-report=html
```

### Docker Testing

```bash
# Run tests in Docker environment (RECOMMENDED)
docker compose -f docker-compose.test.yml up --build
# OR: docker-compose -f docker-compose.test.yml up --build

# Alternative with script (auto-detects Docker version)
./run_tests.sh docker

# Clean up after testing
docker compose -f docker-compose.test.yml down
# OR: docker-compose -f docker-compose.test.yml down
```

### Test Results Example

When you run the tests, you'll see output like this:

```
test-api-1         | tests/test_api.py::TestAPIEndpoints::test_root_endpoint PASSED     [ 15%]
test-api-1         | tests/test_api.py::TestAPIEndpoints::test_health_endpoint PASSED   [ 18%]
test-api-1         | tests/test_api.py::TestPredictEndpoint::test_predict_valid_input PASSED [ 25%]
test-api-1         | tests/test_model.py::TestModelTraining::test_model_creation_and_fitting PASSED [ 35%]
test-api-1         | tests/test_integration.py::TestAPIIntegration::test_api_throughput PASSED [ 66%]
```

**Test Categories Covered:**
- ✅ **API Endpoints** - All FastAPI routes tested
- ✅ **ML Model** - Training, prediction, and validation
- ✅ **Integration** - End-to-end pipeline testing
- ✅ **Performance** - Response time and concurrency
- ✅ **Error Handling** - Edge cases and failure scenarios

### Using Makefile

```bash
# Install dependencies
make install-dev

# Run all tests
make test

# Run tests with coverage
make coverage

# Run code quality checks
make lint

# Format code
make format
```

### Test Coverage

The project maintains >80% test coverage across all components:

```bash
# Generate HTML coverage report
pytest --cov=app --cov=scripts --cov-report=html
open htmlcov/index.html  # View in browser

# Quick coverage check with Docker
docker compose -f docker-compose.test.yml run test-api pytest --cov=app --cov=scripts
# OR: docker-compose -f docker-compose.test.yml run test-api pytest --cov=app --cov=scripts
```

**Coverage Breakdown:**
- 🎯 **API Endpoints**: ~95% coverage
- 🤖 **ML Model**: ~90% coverage  
- 🔗 **Integration**: ~85% coverage
- 📊 **Overall Project**: >80% coverage

### Test Metrics & Benchmarks

| Test Category | Count | Coverage | Performance Target |
|---------------|-------|----------|-------------------|
| **API Tests** | 25+ tests | 95% | < 1s response time |
| **Model Tests** | 20+ tests | 90% | < 100ms prediction |
| **Integration** | 15+ tests | 85% | End-to-end < 5s |
| **Performance** | 10+ tests | 80% | 10+ concurrent users |

### Continuous Integration

Tests run automatically on:
- ✅ Push to main/develop branches
- ✅ Pull requests
- ✅ Multiple Python versions (3.8-3.11)
- ✅ Docker environment testing
- ✅ Code quality checks
- ✅ Security scanning

**CI/CD Pipeline includes:**
- 🔍 **Linting**: flake8, black, isort
- 🧪 **Testing**: pytest with coverage
- 🐳 **Docker**: Multi-stage testing
- 🔒 **Security**: bandit, safety checks
- 📊 **Performance**: Load testing
- 📈 **Reports**: Coverage, security, performance

### Test Structure

```python
# Example test
def test_api_prediction(client, sample_housing_data):
    """Test API prediction endpoint"""
    response = client.post("/predict", json=sample_housing_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prediction"] > 0
```

### Performance Benchmarks

- API Response Time: < 1 second average
- Model Prediction: < 100ms per request
- Memory Usage: Stable during operation
- Concurrent Requests: Supports 10+ simultaneous requests

### 🔧 Testing Troubleshooting

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements-test.txt` |
| `Model not found` | Execute `python scripts/train.py` first |
| `Docker build fails` | Check Docker daemon and disk space |
| `Tests timeout` | Increase `MODEL_WAIT_TIMEOUT` in docker-compose |
| `Permission denied` | Run `chmod +x run_tests.sh` |
| `docker-compose: command not found` | Use `docker compose` (newer Docker) instead of `docker-compose` |
| `Docker Compose compatibility` | Our scripts auto-detect and support both versions |

**Debug Commands:**
```bash
# Check test environment
./run_tests.sh help

# Verbose test output
pytest -v -s tests/

# Run single test file
pytest tests/test_api.py -v

# Skip slow tests
pytest -m "not slow" tests/

# Test with debug output
docker compose -f docker-compose.test.yml up --build --no-deps test-api
# OR: docker-compose -f docker-compose.test.yml up --build --no-deps test-api
```

**Performance Optimization:**
```bash
# Fast test run (fail on first error)
pytest -x tests/

# Parallel testing (if pytest-xdist installed)
pytest -n auto tests/

# Profile slow tests
pytest --durations=10 tests/
```

### Code Style

```bash
# Install formatting tools
pip install black isort flake8 mypy

# Format code
black app/ scripts/ tests/
isort app/ scripts/ tests/

# Lint code
flake8 app/ scripts/ tests/
mypy app/ scripts/ --ignore-missing-imports
```

## 📊 Test Architecture

```mermaid
graph TD
    A[Docker Compose Test] --> B[Test Trainer]
    A --> C[Test API]
    B --> D[Model Training]
    C --> E[API Tests]
    C --> F[Model Tests]
    C --> G[Integration Tests]
    E --> H[Endpoint Testing]
    E --> I[Performance Testing]
    F --> J[ML Validation]
    F --> K[Model Persistence]
    G --> L[End-to-End Testing]
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/avaazquezz/ml-housing-n8n/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avaazquezz/ml-housing-n8n/discussions)
- **Documentation**: Check the `n8n/README-n8n.md` for n8n specific setup

## 🙏 Acknowledgments

- California Housing Dataset from scikit-learn
- FastAPI framework for the excellent async API capabilities
- n8n community for workflow automation inspiration
- Telegram Bot API for seamless integration

---

<div align="center">

**⭐ If this project helped you, please consider giving it a star! ⭐**

Made with ❤️ by [avaazquezz](https://github.com/avaazquezz)

</div>
