"""
train_timeline.py
Trains and saves the transformation timeline regression model.

Target:  months_to_peak
Model:   XGBoostRegressor

Saves:
  models/timeline_model.pkl
  models/timeline_scaler.pkl
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

TIMELINE_FEATURES = [
    # structural
    "shoulder_width_n", "hip_width_n",
    "torso_length_n", "leg_length_n",
    "symmetry_score",
    # ratios
    "shoulder_hip_ratio", "torso_leg_ratio",
    # user inputs
    "sex", "age", "height_cm", "weight_kg",
    "intensity", "weekly_training_days",
    # composition
    "bmi", "predicted_body_fat", "lean_mass_kg", "ffmi",
    # derived gap info
    "peak_lean_mass_kg",
    "frame_label",
]
TARGET = "months_to_peak"


def load_data():
    df = pd.read_csv(DATA_PATH)
    # Add explicit lean mass gap column (very informative feature)
    df["lean_mass_gap"] = df["peak_lean_mass_kg"] - df["lean_mass_kg"]
    df["lean_mass_gap"] = df["lean_mass_gap"].clip(lower=0)
    print(f"Loaded {len(df):,} rows.")
    return df


def train(df: pd.DataFrame):
    features = TIMELINE_FEATURES + ["lean_mass_gap"]
    X = df[features].values
    y = df[TARGET].values

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBRegressor(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.75,
        min_child_weight=3,
        reg_alpha=0.05,
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

    print(f"CV MAE : {cv_mae.mean():.2f} ± {cv_mae.std():.2f} months")
    print(f"CV R²  : {cv_r2.mean():.4f} ± {cv_r2.std():.4f}")

    # Final fit
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    print(f"\nTrain MAE : {mean_absolute_error(y, y_pred):.2f} months")
    print(f"Train R²  : {r2_score(y, y_pred):.4f}")

    # Feature importance
    imp = pd.Series(model.feature_importances_, index=features)
    print("\nTop-10 features (timeline):")
    print(imp.nlargest(10).to_string())

    # Save
    joblib.dump(model,    os.path.join(MODEL_DIR, "timeline_model.pkl"))
    joblib.dump(scaler,   os.path.join(MODEL_DIR, "timeline_scaler.pkl"))
    # Also save the feature list so inference.py can reconstruct it
    joblib.dump(features, os.path.join(MODEL_DIR, "timeline_features.pkl"))
    print("\nTimeline model + scaler saved → models/")
    return model, scaler


if __name__ == "__main__":
    df = load_data()
    train(df)