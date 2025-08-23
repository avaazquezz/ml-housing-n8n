# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib, os, pandas as pd
import time
import logging
import math
import html as _html

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helpers para cargar modelo
def wait_for_model(model_path: str, timeout: int = 60) -> bool:
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
    if not wait_for_model(model_path, timeout):
        raise RuntimeError(f"Model not found after {timeout}s. Run training first.")
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")

# --- Config (env override recommended) ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "model.joblib")
MODEL_WAIT_TIMEOUT = int(os.getenv("MODEL_WAIT_TIMEOUT", "60"))

# Por cómo entrenaste (California housing): target en unidades de 100000 por defecto
PRICE_MULTIPLIER = float(os.getenv("PRICE_MULTIPLIER", "100000.0"))
EUR_TO_USD = float(os.getenv("EUR_TO_USD", "1.10"))
TARGET_TRANSFORM = os.getenv("TARGET_TRANSFORM", "none").lower()  # none | log | log1p

# Load model
model = load_model_safely(MODEL_PATH, MODEL_WAIT_TIMEOUT)

app = FastAPI(title="Housing Price Predictor API", version="1.0.0")

# Schemas
class PredictRequest(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

class PredictResponse(BaseModel):
    prediction: float
    prediction_eur: float
    prediction_usd: float
    prediction_eur_formatted: str
    prediction_usd_formatted: str
    status: str
    message_text: str
    message_html: str

class PredictStringInput(BaseModel):
    input: str

# Formateadores:
def format_usd_en(v: float) -> str:
    """Formato americano: 1,234,567.89"""
    return f"{v:,.2f}"

def format_eur_eu(v: float) -> str:
    """
    Formato europeo común: 1.234.567,89
    Implementación sin dependencias de locale.
    """
    # Usamos primero la representación con coma como separador de miles y punto decimal
    s = f"{v:,.2f}"            # '1,234,567.89'
    # intercambiamos comas/puntos -> '1.234.567,89'
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

# convertir la salida cruda del modelo a valor en EUR reales (según TARGET_TRANSFORM)
def inverse_transform(raw_pred: float) -> float:
    rp = float(raw_pred)
    if TARGET_TRANSFORM == "log":
        val = math.exp(rp)
    elif TARGET_TRANSFORM == "log1p":
        val = math.expm1(rp)
    else:
        val = rp * PRICE_MULTIPLIER
    return float(val)

@app.get("/")
def root():
    return {"msg": "Housing Price Predictor API", "model_loaded": model is not None}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None, "model_path": MODEL_PATH}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        df = pd.DataFrame([req.dict()])
        raw_pred = model.predict(df)[0]

        pred_eur_value = inverse_transform(raw_pred)
        pred_usd_value = pred_eur_value * EUR_TO_USD

        # redondeamos a 2 decimales para presentacion y formatamos apropiadamente
        pred_eur_rounded = round(float(pred_eur_value), 2)
        pred_usd_rounded = round(float(pred_usd_value), 2)

        eur_fmt = format_eur_eu(pred_eur_rounded) + " EUR"
        usd_fmt = format_usd_en(pred_usd_rounded) + " USD"

        # plain text
        message_text = (
            f"Estimated price: {eur_fmt} / {usd_fmt}\n\n"
            f"Details:\n"
            f"- Status: success\n"
        )

        # HTML for Telegram (parse_mode=HTML) — escapamos valores por seguridad aunque sean números
        message_html = (
            f"🏠 <b>Estimated price</b>\n"
            f"{_html.escape(eur_fmt)} / {_html.escape(usd_fmt)}\n\n"
            f"🔎 <b>Details</b>:\n"
            f"• Status: {_html.escape('success')}"
        )

        return PredictResponse(
            prediction=pred_eur_rounded,
            prediction_eur=pred_eur_rounded,
            prediction_usd=pred_usd_rounded,
            prediction_eur_formatted=eur_fmt,
            prediction_usd_formatted=usd_fmt,
            status="success",
            message_text=message_text,
            message_html=message_html
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict-from-string", response_model=PredictResponse)
def predict_from_string(data: PredictStringInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        s = data.input.strip().replace(";", ",")
        parts = [p.strip() for p in s.split(",") if p.strip() != ""]
        if len(parts) != 8:
            raise ValueError(f"Input must contain exactly 8 numerical values (got {len(parts)})")
        nums = list(map(float, parts))
        columns = ["MedInc","HouseAge","AveRooms","AveBedrms","Population","AveOccup","Latitude","Longitude"]
        df = pd.DataFrame([nums], columns=columns)

        raw_pred = model.predict(df)[0]
        pred_eur_value = inverse_transform(raw_pred)
        pred_usd_value = pred_eur_value * EUR_TO_USD

        pred_eur_rounded = round(float(pred_eur_value), 2)
        pred_usd_rounded = round(float(pred_usd_value), 2)

        eur_fmt = format_eur_eu(pred_eur_rounded) + " EUR"
        usd_fmt = format_usd_en(pred_usd_rounded) + " USD"

        message_text = (
            f"Estimated price: {eur_fmt} / {usd_fmt}\n\n"
            f"Details:\n"
            f"- Status: success\n"
        )

        message_html = (
            f"🏠 <b>Estimated price</b>\n"
            f"{_html.escape(eur_fmt)} / {_html.escape(usd_fmt)}\n\n"
            f"🔎 <b>Details</b>:\n"
            f"• Status: {_html.escape('success')}"
        )

        return PredictResponse(
            prediction=pred_eur_rounded,
            prediction_eur=pred_eur_rounded,
            prediction_usd=pred_usd_rounded,
            prediction_eur_formatted=eur_fmt,
            prediction_usd_formatted=usd_fmt,
            status="success",
            message_text=message_text,
            message_html=message_html
        )

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
