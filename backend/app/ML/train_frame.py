"""
train_frame.py
--------------
Trains and saves the frame-type classifier.
  1. KMeans unsupervised
  2. RandomForestClassifier — trained on those labels so we can
     classify unseen users at inference time without re-running KMeans.

Saves:
  models/clustering_model.pkl   – KMeans (for reference / re-labelling)
  models/frame_classifier.pkl   – RandomForest (used at inference)
  models/frame_scaler.pkl        – StandardScaler
"""

import os
import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

DATA_PATH   = "data/simulated_dataset.csv"
MODEL_DIR   = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Features used for frame clustering / classification
FRAME_FEATURES = [
    "shoulder_width_n",
    "hip_width_n",
    "torso_length_n",
    "shoulder_hip_ratio",
    "shoulder_waist_ratio",
    "waist_width_n",
    "symmetry_score",
]

def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} rows.")
    return df


def train_kmeans(df: pd.DataFrame) -> KMeans:
    """Re-fit KMeans and save."""
    X = df[FRAME_FEATURES].values
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    km.fit(X)
    joblib.dump(km, os.path.join(MODEL_DIR, "clustering_model.pkl"))
    print("KMeans saved → models/clustering_model.pkl")
    return km


def train_classifier(df: pd.DataFrame):
    """Train Random Forest on the KMeans-derived frame_label column."""
    X = df[FRAME_FEATURES].values
    y = df["frame_label"].values          # 0 / 1 / 2

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="accuracy")
    print(f"CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

    # Final fit on full data
    clf.fit(X_scaled, y)

    # Report
    y_pred = clf.predict(X_scaled)
    le_map = {0: "narrow", 1: "balanced", 2: "wide"}
    y_named      = [le_map[i] for i in y]
    y_pred_named = [le_map[i] for i in y_pred]
    print(classification_report(y_named, y_pred_named))

    # Save
    joblib.dump(clf,    os.path.join(MODEL_DIR, "frame_classifier.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "frame_scaler.pkl"))
    print("Frame classifier + scaler saved → models/")

    return clf, scaler


def feature_importances(clf: RandomForestClassifier):
    imp = pd.Series(clf.feature_importances_, index=FRAME_FEATURES)
    print("\nFeature importances (frame classifier):")
    print(imp.sort_values(ascending=False).to_string())


if __name__ == "__main__":
    df  = load_data()
    km  = train_kmeans(df)
    clf, scaler = train_classifier(df)
    feature_importances(clf)