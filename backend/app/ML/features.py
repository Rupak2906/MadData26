"""
features.py
-----------
Defines the full feature vector schema and computes derived features
from raw MediaPipe keypoints + user form inputs.
"""

import numpy as np
from dataclasses import dataclass, asdict
<<<<<<< HEAD
=======
from typing import Optional

>>>>>>> ML

# 1. Raw keypoint measurements (from CV pipeline)


@dataclass
class RawMeasurements:
    """
    Normalized body measurements (divided by height in pixels).
    """
    shoulder_width_n: float
    hip_width_n: float
    waist_width_n: float
    torso_length_n: float
    leg_length_n: float
    arm_length_n: float
    upper_arm_n: float
    forearm_n: float
    thigh_n: float
    calf_n: float
    symmetry_score: float       # 0–1, higher = more symmetric


# 2. User form inputs


@dataclass
class UserInputs:
    sex: int                    # 0 = female, 1 = male
    age: float
    height_cm: float
    weight_kg: float
    intensity: int              # 0 = beginner, 1 = intermediate, 2 = advanced
    weekly_training_days: int   # 1–7



# 3. Derived features (computed here)

@dataclass
class DerivedFeatures:
    shoulder_hip_ratio: float
    shoulder_waist_ratio: float
    torso_leg_ratio: float
    arm_torso_ratio: float
    upper_lower_arm_ratio: float
    thigh_calf_ratio: float
    bmi: float
    predicted_body_fat: float   # %
    lean_mass_kg: float
    ffmi: float                 # Fat-Free Mass Index


# 4. Full feature vector (X matrix row)

@dataclass
class FeatureVector:
    # Raw structural
    shoulder_width_n: float
    hip_width_n: float
    waist_width_n: float
    torso_length_n: float
    leg_length_n: float
    arm_length_n: float
    upper_arm_n: float
    forearm_n: float
    thigh_n: float
    calf_n: float
    symmetry_score: float
    # Structural ratios
    shoulder_hip_ratio: float
    shoulder_waist_ratio: float
    torso_leg_ratio: float
    arm_torso_ratio: float
    upper_lower_arm_ratio: float
    thigh_calf_ratio: float
    # User inputs
    sex: float
    age: float
    height_cm: float
    weight_kg: float
    intensity: float
    weekly_training_days: float
    # Composition
    bmi: float
    predicted_body_fat: float
    lean_mass_kg: float
    ffmi: float

    def to_array(self) -> np.ndarray:
        return np.array(list(asdict(self).values()), dtype=float)

    @staticmethod
    def feature_names() -> list:
        return list(FeatureVector.__dataclass_fields__.keys())


# 5. Body fat estimation (Deurenberg formula proxy)

def estimate_body_fat(bmi: float, age: float, sex: int) -> float:
    """
    BF% = (1.20 × BMI) + (0.23 × age) − (10.8 × sex) − 5.4
    sex: 1 = male, 0 = female
    """
    bf_pct = (1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4
    return float(np.clip(bf_pct / 100.0, 0.05, 0.50))


# 6. Main assembly function

def build_feature_vector(
    raw: RawMeasurements,
    user: UserInputs,
) -> FeatureVector:
    """
    Combine raw measurements + user inputs into the full feature vector.
    """
    # — structural ratios —
    shr_hip   = raw.shoulder_width_n / (raw.hip_width_n   + 1e-6)
    shr_waist = raw.shoulder_width_n / (raw.waist_width_n + 1e-6)
    torso_leg = raw.torso_length_n   / (raw.leg_length_n  + 1e-6)
    arm_torso = raw.arm_length_n     / (raw.torso_length_n + 1e-6)
    ul_arm    = raw.upper_arm_n      / (raw.forearm_n     + 1e-6)
    th_calf   = raw.thigh_n          / (raw.calf_n        + 1e-6)

    # — composition —
    height_m  = user.height_cm / 100.0
    bmi       = user.weight_kg / (height_m ** 2)
    bf_frac   = estimate_body_fat(bmi, user.age, user.sex)
    lean_mass = user.weight_kg * (1.0 - bf_frac)
    ffmi      = lean_mass / (height_m ** 2)

    return FeatureVector(
        # raw structural
        shoulder_width_n   = raw.shoulder_width_n,
        hip_width_n        = raw.hip_width_n,
        waist_width_n      = raw.waist_width_n,
        torso_length_n     = raw.torso_length_n,
        leg_length_n       = raw.leg_length_n,
        arm_length_n       = raw.arm_length_n,
        upper_arm_n        = raw.upper_arm_n,
        forearm_n          = raw.forearm_n,
        thigh_n            = raw.thigh_n,
        calf_n             = raw.calf_n,
        symmetry_score     = raw.symmetry_score,
        # ratios
        shoulder_hip_ratio       = shr_hip,
        shoulder_waist_ratio     = shr_waist,
        torso_leg_ratio          = torso_leg,
        arm_torso_ratio          = arm_torso,
        upper_lower_arm_ratio    = ul_arm,
        thigh_calf_ratio         = th_calf,
        # user inputs
        sex                  = float(user.sex),
        age                  = user.age,
        height_cm            = user.height_cm,
        weight_kg            = user.weight_kg,
        intensity            = float(user.intensity),
        weekly_training_days = float(user.weekly_training_days),
        # composition
        bmi                  = bmi,
        predicted_body_fat   = bf_frac,
        lean_mass_kg         = lean_mass,
        ffmi                 = ffmi,
    )
