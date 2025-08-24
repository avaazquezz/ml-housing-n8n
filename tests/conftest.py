# Test configuration and fixtures
import pytest
import os
import sys
import tempfile
import shutil
from fastapi.testclient import TestClient
import joblib
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

@pytest.fixture(scope="session")
def test_model():
    """Create a test model for testing purposes"""
    # Create a simple test model with California housing data
    data = fetch_california_housing(as_frame=True)
    X = data.data.head(100)  # Use small subset for faster testing
    y = data.target.head(100)
    
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(n_estimators=10, random_state=42, n_jobs=1)),
    ])
    
    pipeline.fit(X, y)
    return pipeline

@pytest.fixture(scope="session")
def test_model_file(test_model):
    """Create a temporary model file"""
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
        joblib.dump(test_model, f.name)
        yield f.name
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def client(test_model_file, monkeypatch):
    """Create FastAPI test client with test model"""
    # Set environment variables for testing
    monkeypatch.setenv("MODEL_PATH", test_model_file)
    monkeypatch.setenv("MODEL_WAIT_TIMEOUT", "5")
    monkeypatch.setenv("PRICE_MULTIPLIER", "100000.0")
    monkeypatch.setenv("EUR_TO_USD", "1.10")
    
    # Import app after setting environment variables
    from main import app
    
    return TestClient(app)

@pytest.fixture
def sample_housing_data():
    """Sample housing data for testing"""
    return {
        "MedInc": 4.2,
        "HouseAge": 15.0,
        "AveRooms": 5.3,
        "AveBedrms": 1.2,
        "Population": 1800.0,
        "AveOccup": 3.1,
        "Latitude": 34.05,
        "Longitude": -118.25
    }

@pytest.fixture
def sample_csv_input():
    """Sample CSV string input for testing"""
    return "4.2,15,5.3,1.2,1800,3.1,34.05,-118.25"

@pytest.fixture
def california_housing_data():
    """Real California housing dataset for model testing"""
    return fetch_california_housing(as_frame=True)
