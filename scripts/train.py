import os
import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

os.makedirs("model", exist_ok=True)

print("Loading dataset...")
data = fetch_california_housing(as_frame=True)
X = data.data
y = data.target


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)),
])

print("Training...")
pipeline.fit(X_train, y_train)

print("Evaluating...")
y_pred = pipeline.predict(X_test)
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))

joblib.dump(pipeline, "model/model.joblib")
print("Saved model to model/model.joblib")
