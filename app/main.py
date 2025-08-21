from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib, os, pandas as pd
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_model(model_path: str, timeout: int = 60) -> bool:
    """
    Wait for the model file to be available, with timeout.
    Returns True if model is found, False if timeout reached.
    """
    start_time = time.time()
    logger.info(f"Waiting for model at {model_path} (timeout: {timeout}s)")
    
    while time.time() - start_time < timeout:
        if os.path.exists(model_path):
            logger.info(f"Model found at {model_path}")
            return True
        
        elapsed = int(time.time() - start_time)
        logger.info(f"Model not found yet... waiting ({elapsed}/{timeout}s)")
        time.sleep(2)
    
    logger.error(f"Model not found after {timeout}s timeout")
    return False

def load_model_safely(model_path: str, timeout: int = 60):
    """
    Load model with retry logic and timeout.
    """
    if not wait_for_model(model_path, timeout):
        raise RuntimeError(f"Model not found after {timeout}s. Run training first.")
    
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "model.joblib")
MODEL_WAIT_TIMEOUT = int(os.getenv("MODEL_WAIT_TIMEOUT", "60"))

# Load model with wait logic
model = load_model_safely(MODEL_PATH, MODEL_WAIT_TIMEOUT)

app = FastAPI(
    title="Housing Price Predictor API",
    description="API for predicting housing prices using ML model",
    version="1.0.0"
)

class PredictRequest(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.get("/")
def root():
    return {
        "msg": "Housing Price Predictor API", 
        "endpoints": {
            "predict": "POST /predict",
            "health": "GET /health"
        },
        "model_loaded": model is not None
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    }

@app.post("/predict")
def predict(req: PredictRequest):
    """Predict housing price based on features"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        df = pd.DataFrame([req.dict()])
        pred = model.predict(df)[0]
        return {
            "prediction": float(pred),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/reload-model")
def reload_model():
    """Reload the model (useful for development)"""
    global model
    try:
        model = load_model_safely(MODEL_PATH, timeout=10)
        return {"status": "success", "message": "Model reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")
