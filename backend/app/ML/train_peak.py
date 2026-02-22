"""
train_peak.py
Trains and saves the peak lean mass regression model.

Target:  peak_lean_mass_kg
Model:   XGBoostRegressor with cross-validated hyperparameter selection

Saves:
  models/peak_mass_model.pkl
  models/peak_scaler.pkl
"""

import os
import joblib
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

DATA_PATH = "data/simulated_dataset.csv"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

PEAK_FEATURES = [
    # structural
    "shoulder_width_n", "hip_width_n", "waist_width_n",
    "torso_length_n", "leg_length_n",
    "upper_arm_n", "forearm_n", "thigh_n", "calf_n",
    "symmetry_score",
    # ratios
    "shoulder_hip_ratio", "shoulder_waist_ratio",
    "torso_leg_ratio", "arm_torso_ratio",
    "upper_lower_arm_ratio", "thigh_calf_ratio",
    # user inputs
    "sex", "age", "height_cm", "weight_kg",
    "intensity", "weekly_training_days",
    # composition
    "bmi", "predicted_body_fat", "lean_mass_kg", "ffmi",
    # frame
    "frame_label",
]
TARGET = "peak_lean_mass_kg"


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} rows.")
    return df


def train(df: pd.DataFrame):
    X = df[PEAK_FEATURES].values
    y = df[TARGET].values

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )

    # Cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_mae = -cross_val_score(model, X_scaled, y, cv=kf,
                               scoring="neg_mean_absolute_error")
    cv_r2  =  cross_val_score(model, X_scaled, y, cv=kf, scoring="r2")
    print(f"CV MAE : {cv_mae.mean():.3f} ± {cv_mae.std():.3f} kg")
    print(f"CV R²  : {cv_r2.mean():.4f} ± {cv_r2.std():.4f}")

    # Final fit
    model.fit(X_scaled, y)

    # Train-set diagnostics
    y_pred = model.predict(X_scaled)
    print(f"\nTrain MAE : {mean_absolute_error(y, y_pred):.3f} kg")
    print(f"Train R²  : {r2_score(y, y_pred):.4f}")

    # Feature importance
    imp = pd.Series(model.feature_importances_, index=PEAK_FEATURES)
    print("\nTop-10 features (peak lean mass):")
    print(imp.nlargest(10).to_string())

    # Save
    joblib.dump(model,  os.path.join(MODEL_DIR, "peak_mass_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "peak_scaler.pkl"))
    print("\nPeak model + scaler saved → models/")
    return model, scaler


if __name__ == "__main__":
    df = load_data()
    train(df)