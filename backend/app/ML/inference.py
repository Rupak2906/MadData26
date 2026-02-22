"""
inference.py
------------
Loads the trained models and exposes three clean functions:

  extract_features(raw, user) -> FeatureVector
  predict(fv)                 -> PredictionResult
  explain(fv)                 -> ExplainResult

These are the functions wired into the FastAPI endpoints.
"""

import os
import joblib
import numpy as np

from features import (
    RawMeasurements, UserInputs, FeatureVector, build_feature_vector
)

MODEL_DIR = "models"

_models = {}

def _load():
    if _models:
        return
    _models["frame_clf"]    = joblib.load(os.path.join(MODEL_DIR, "frame_classifier.pkl"))
    _models["frame_scaler"] = joblib.load(os.path.join(MODEL_DIR, "frame_scaler.pkl"))
    _models["peak_model"]   = joblib.load(os.path.join(MODEL_DIR, "peak_mass_model.pkl"))
    _models["peak_scaler"]  = joblib.load(os.path.join(MODEL_DIR, "peak_scaler.pkl"))
    _models["tl_model"]     = joblib.load(os.path.join(MODEL_DIR, "timeline_model.pkl"))
    _models["tl_scaler"]    = joblib.load(os.path.join(MODEL_DIR, "timeline_scaler.pkl"))
    _models["tl_features"]  = joblib.load(os.path.join(MODEL_DIR, "timeline_features.pkl"))


# ─────────────────────────────────────────────
# Output schema
# ─────────────────────────────────────────────

class PredictionResult:
    def __init__(self, frame_type, frame_label, frame_confidence,
                 current_lean_mass_kg, current_ffmi, predicted_body_fat_pct,
                 peak_lean_mass_kg, peak_ffmi, lean_mass_gap_kg,
                 months_realistic, months_optimistic, months_conservative):
        self.frame_type             = frame_type
        self.frame_label            = frame_label
        self.frame_confidence       = frame_confidence
        self.current_lean_mass_kg   = current_lean_mass_kg
        self.current_ffmi           = current_ffmi
        self.predicted_body_fat_pct = predicted_body_fat_pct
        self.peak_lean_mass_kg      = peak_lean_mass_kg
        self.peak_ffmi              = peak_ffmi
        self.lean_mass_gap_kg       = lean_mass_gap_kg
        self.months_realistic       = months_realistic
        self.months_optimistic      = months_optimistic
        self.months_conservative    = months_conservative

    def to_dict(self) -> dict:
        return {
            "frame_type":             self.frame_type,
            "frame_label":            self.frame_label,
            "frame_confidence":       round(self.frame_confidence, 3),
            "current_lean_mass_kg":   round(self.current_lean_mass_kg, 2),
            "current_ffmi":           round(self.current_ffmi, 2),
            "predicted_body_fat_pct": round(self.predicted_body_fat_pct * 100, 1),
            "peak_lean_mass_kg":      round(self.peak_lean_mass_kg, 2),
            "peak_ffmi":              round(self.peak_ffmi, 2),
            "lean_mass_gap_kg":       round(self.lean_mass_gap_kg, 2),
            "months_realistic":       round(self.months_realistic, 1),
            "months_optimistic":      round(self.months_optimistic, 1),
            "months_conservative":    round(self.months_conservative, 1),
        }


class ExplainResult:
    def __init__(self, peak_shap: dict, timeline_shap: dict):
        self.peak_shap     = peak_shap
        self.timeline_shap = timeline_shap


# ─────────────────────────────────────────────
# Feature helpers
# ─────────────────────────────────────────────

FRAME_FEATURES = [
    "shoulder_width_n", "hip_width_n", "waist_width_n",
    "torso_length_n", "leg_length_n", "upper_arm_n",
    "forearm_n", "thigh_n", "calf_n", "symmetry_score",
    "shoulder_hip_ratio", "shoulder_waist_ratio",
    "torso_leg_ratio", "arm_torso_ratio",
    "upper_lower_arm_ratio", "thigh_calf_ratio",
    "sex", "age", "height_cm", "weight_kg",
    "intensity", "weekly_training_days",
    "bmi", "predicted_body_fat", "lean_mass_kg", "ffmi",
]

PEAK_FEATURES = FRAME_FEATURES + ["frame_label"]

FRAME_NAME_MAP = {0: "narrow", 1: "balanced", 2: "wide"}

# Structural-only features used by the frame classifier
_FRAME_STRUCT_FEATURES = [
    "shoulder_width_n", "hip_width_n", "waist_width_n",
    "torso_length_n", "leg_length_n", "upper_arm_n",
    "forearm_n", "thigh_n", "calf_n", "symmetry_score",
    "shoulder_hip_ratio", "shoulder_waist_ratio",
    "torso_leg_ratio", "arm_torso_ratio",
    "upper_lower_arm_ratio", "thigh_calf_ratio",
]

def _fv_to_frame_array(fv: FeatureVector) -> np.ndarray:
    vals = [getattr(fv, f) for f in _FRAME_STRUCT_FEATURES]
    return np.array(vals).reshape(1, -1)


def _fv_to_peak_array(fv: FeatureVector, frame_label: int) -> np.ndarray:
    vals = [getattr(fv, f) for f in FRAME_FEATURES] + [float(frame_label)]
    return np.array(vals).reshape(1, -1)


def _fv_to_timeline_dict(fv: FeatureVector, frame_label: int,
                          peak_lean_mass: float, lean_mass_gap: float) -> dict:
    return {
        "shoulder_width_n":     fv.shoulder_width_n,
        "hip_width_n":          fv.hip_width_n,
        "torso_length_n":       fv.torso_length_n,
        "leg_length_n":         fv.leg_length_n,
        "symmetry_score":       fv.symmetry_score,
        "shoulder_hip_ratio":   fv.shoulder_hip_ratio,
        "torso_leg_ratio":      fv.torso_leg_ratio,
        "sex":                  fv.sex,
        "age":                  fv.age,
        "height_cm":            fv.height_cm,
        "weight_kg":            fv.weight_kg,
        "intensity":            fv.intensity,
        "weekly_training_days": fv.weekly_training_days,
        "bmi":                  fv.bmi,
        "predicted_body_fat":   fv.predicted_body_fat,
        "lean_mass_kg":         fv.lean_mass_kg,
        "ffmi":                 fv.ffmi,
        "peak_lean_mass_kg":    peak_lean_mass,
        "frame_label":          float(frame_label),
        "lean_mass_gap":        lean_mass_gap,
    }


# Public API

def extract_features(raw: RawMeasurements, user: UserInputs) -> FeatureVector:
    """Step 1: build feature vector from raw measurements + user inputs."""
    return build_feature_vector(raw, user)


def predict(fv: FeatureVector) -> PredictionResult:
    """Step 2: run all three models and return structured results."""
    _load()

    height_m = fv.height_cm / 100.0

    # ── Frame classification ──────────────────
    frame_arr        = _fv_to_frame_array(fv)
    frame_arr_scaled = _models["frame_scaler"].transform(frame_arr)
    frame_label      = int(_models["frame_clf"].predict(frame_arr_scaled)[0])
    frame_proba      = _models["frame_clf"].predict_proba(frame_arr_scaled)[0]
    frame_conf       = float(frame_proba[frame_label])
    frame_type       = FRAME_NAME_MAP[frame_label]

    # ── Peak lean mass ────────────────────────
    peak_arr       = _fv_to_peak_array(fv, frame_label)
    peak_scaled    = _models["peak_scaler"].transform(peak_arr)
    peak_lean_mass = float(_models["peak_model"].predict(peak_scaled)[0])
    peak_ffmi      = peak_lean_mass / (height_m ** 2)
    lean_mass_gap  = max(peak_lean_mass - fv.lean_mass_kg, 0.0)

    # ── Timeline ──────────────────────────────
    tl_features = _models["tl_features"]
    fv_dict     = _fv_to_timeline_dict(fv, frame_label, peak_lean_mass, lean_mass_gap)
    tl_row      = np.array([fv_dict[f] for f in tl_features]).reshape(1, -1)
    tl_scaled   = _models["tl_scaler"].transform(tl_row)
    months_realistic = float(np.clip(_models["tl_model"].predict(tl_scaled)[0], 3, 120))

    return PredictionResult(
        frame_type             = frame_type,
        frame_label            = frame_label,
        frame_confidence       = frame_conf,
        current_lean_mass_kg   = fv.lean_mass_kg,
        current_ffmi           = fv.ffmi,
        predicted_body_fat_pct = fv.predicted_body_fat,
        peak_lean_mass_kg      = peak_lean_mass,
        peak_ffmi              = peak_ffmi,
        lean_mass_gap_kg       = lean_mass_gap,
        months_realistic       = months_realistic,
        months_optimistic      = months_realistic * 0.80,
        months_conservative    = months_realistic * 1.20,
    )


def explain(fv: FeatureVector, frame_label: int, peak_lean_mass: float) -> ExplainResult:
    """
    Step 3: generate SHAP values for both regressors.
    Returns top-feature attribution dicts sorted by absolute impact.

    Requires: pip install shap
    """
    try:
        import shap
    except ImportError:
        raise RuntimeError("shap not installed. Run: pip install shap")

    _load()

    lean_mass_gap = max(peak_lean_mass - fv.lean_mass_kg, 0.0)

    # ── Peak SHAP ────────────────────────────
    peak_arr       = _fv_to_peak_array(fv, frame_label)
    peak_scaled    = _models["peak_scaler"].transform(peak_arr)
    peak_explainer = shap.TreeExplainer(_models["peak_model"])
    peak_shap_vals = peak_explainer.shap_values(peak_scaled)[0]
    peak_shap_dict = dict(sorted(
        zip(PEAK_FEATURES, [round(float(v), 4) for v in peak_shap_vals]),
        key=lambda x: abs(x[1]), reverse=True
    ))

    # ── Timeline SHAP ────────────────────────
    tl_features = _models["tl_features"]
    fv_dict     = _fv_to_timeline_dict(fv, frame_label, peak_lean_mass, lean_mass_gap)
    tl_row      = np.array([fv_dict[f] for f in tl_features]).reshape(1, -1)
    tl_scaled   = _models["tl_scaler"].transform(tl_row)
    tl_explainer  = shap.TreeExplainer(_models["tl_model"])
    tl_shap_vals  = tl_explainer.shap_values(tl_scaled)[0]
    tl_shap_dict  = dict(sorted(
        zip(tl_features, [round(float(v), 4) for v in tl_shap_vals]),
        key=lambda x: abs(x[1]), reverse=True
    ))

    return ExplainResult(peak_shap=peak_shap_dict, timeline_shap=tl_shap_dict)