from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib, os, pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "model.joblib")
if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Model not found. Run training first.")

model = joblib.load(MODEL_PATH)
app = FastAPI(title="Housing Price Predictor API")

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
    return {"msg": "Housing Price Predictor API. POST /predict"}

@app.post("/predict")
def predict(req: PredictRequest):
    df = pd.DataFrame([req.dict()])
    pred = model.predict(df)[0]
    return {"prediction": float(pred)}
