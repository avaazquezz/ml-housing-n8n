import os
import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure model directory exists
model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
model_dir = os.path.abspath(model_dir)
os.makedirs(model_dir, exist_ok=True)
logger.info(f"Model directory: {model_dir}")

logger.info("Loading California housing dataset...")
data = fetch_california_housing(as_frame=True)
X = data.data
y = data.target
logger.info(f"Dataset shape: {X.shape}, Target shape: {y.shape}")

logger.info("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

logger.info("Creating ML pipeline...")
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)),
])

logger.info("Training model...")
pipeline.fit(X_train, y_train)

logger.info("Evaluating model...")
y_pred = pipeline.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

logger.info(f"Model Performance:")
logger.info(f"  MSE: {mse:.4f}")
logger.info(f"  R²: {r2:.4f}")

# Save model
model_path = os.path.join(model_dir, "model.joblib")
joblib.dump(pipeline, model_path)
logger.info(f"Model saved to: {model_path}")

# Verify model was saved
if os.path.exists(model_path):
    logger.info("✅ Model training completed successfully!")
else:
    logger.error("❌ Model file not found after saving!")
    exit(1)
