"""
synth_data.py
Generates a scientifically plausible synthetic dataset (4 000 samples)
for training the frame, peak-mass, and timeline models.

"""

import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

RNG = np.random.default_rng(42)
N   = 4_000

# Helpers
def clamp(arr, lo, hi):
    return np.clip(arr, lo, hi)

# 1. User demographics

def gen_demographics(n: int) -> dict:
    sex            = RNG.integers(0, 2, n)                      # 0 = F, 1 = M
    age            = RNG.uniform(18, 50, n)
    # height differs by sex
    height_cm      = np.where(sex, RNG.uniform(155, 205, n),
                                    RNG.uniform(145, 190, n))
    # weight: rough normal around BMI ~24
    bmi_target     = RNG.normal(24, 4, n)
    weight_kg      = clamp(bmi_target * (height_cm / 100) ** 2, 45, 130)
    intensity      = RNG.integers(0, 3, n)          # 0 = beginner, 1 = intermediate, 2 = advanced
    weekly_days    = RNG.integers(1, 7, n)

    return dict(
        sex=sex, age=age, height_cm=height_cm, weight_kg=weight_kg,
        intensity=intensity, weekly_training_days=weekly_days,
    )


# 2. Structural measurements (normalized by height)

def gen_structural(n: int, sex: np.ndarray) -> dict:
    """
    All measurements normalized by standing height (0–1 scale).
    Males tend slightly wider shoulders; females slightly wider hips.
    """
    shoulder_width_n = np.where(sex,
        clamp(RNG.normal(0.26, 0.025, n), 0.20, 0.34),
        clamp(RNG.normal(0.24, 0.025, n), 0.18, 0.32),
    )
    hip_width_n = np.where(sex,
        clamp(RNG.normal(0.21, 0.020, n), 0.16, 0.28),
        clamp(RNG.normal(0.23, 0.022, n), 0.17, 0.30),
    )
    waist_width_n    = clamp(RNG.normal(0.175, 0.018, n), 0.13, 0.24)
    torso_length_n   = clamp(RNG.normal(0.32,  0.025, n), 0.25, 0.42)
    leg_length_n     = clamp(RNG.normal(0.48,  0.030, n), 0.38, 0.58)
    arm_length_n     = clamp(RNG.normal(0.45,  0.025, n), 0.36, 0.54)
    upper_arm_n      = clamp(RNG.normal(0.19,  0.015, n), 0.13, 0.25)
    forearm_n        = clamp(RNG.normal(0.155, 0.012, n), 0.11, 0.20)
    thigh_n          = clamp(RNG.normal(0.245, 0.020, n), 0.18, 0.31)
    calf_n           = clamp(RNG.normal(0.200, 0.018, n), 0.14, 0.26)
    symmetry_score   = clamp(RNG.beta(8, 2, n), 0.60, 1.00)  # most people fairly symmetric

    return dict(
        shoulder_width_n=shoulder_width_n, hip_width_n=hip_width_n,
        waist_width_n=waist_width_n, torso_length_n=torso_length_n,
        leg_length_n=leg_length_n, arm_length_n=arm_length_n,
        upper_arm_n=upper_arm_n, forearm_n=forearm_n,
        thigh_n=thigh_n, calf_n=calf_n, symmetry_score=symmetry_score,
    )


# 3. Derived ratios + composition

def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    df["shoulder_hip_ratio"]     = df["shoulder_width_n"] / (df["hip_width_n"]    + 1e-6)
    df["shoulder_waist_ratio"]   = df["shoulder_width_n"] / (df["waist_width_n"]  + 1e-6)
    df["torso_leg_ratio"]        = df["torso_length_n"]   / (df["leg_length_n"]   + 1e-6)
    df["arm_torso_ratio"]        = df["arm_length_n"]     / (df["torso_length_n"] + 1e-6)
    df["upper_lower_arm_ratio"]  = df["upper_arm_n"]      / (df["forearm_n"]      + 1e-6)
    df["thigh_calf_ratio"]       = df["thigh_n"]          / (df["calf_n"]         + 1e-6)

    height_m       = df["height_cm"] / 100
    df["bmi"]      = df["weight_kg"] / height_m ** 2

    df["predicted_body_fat"] = clamp(
        (1.20 * df["bmi"]) + (0.23 * df["age"]) - (10.8 * df["sex"]) - 5.4,
        5, 50
    ) / 100.0

    df["lean_mass_kg"] = df["weight_kg"] * (1 - df["predicted_body_fat"])
    df["ffmi"]         = df["lean_mass_kg"] / height_m ** 2
    return df


def add_frame_labels(df: pd.DataFrame) -> tuple[pd.DataFrame, KMeans]:
    cluster_features = ["shoulder_width_n", "hip_width_n",
                        "torso_length_n", "shoulder_hip_ratio"]
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["_cluster"] = km.fit_predict(df[cluster_features])

    cluster_shoulder = (
        df.groupby("_cluster")["shoulder_width_n"].mean()
          .sort_values()
    )
    mapping = {
        cluster_shoulder.index[0]: "narrow",
        cluster_shoulder.index[1]: "balanced",
        cluster_shoulder.index[2]: "wide",
    }
    df["frame_type"]  = df["_cluster"].map(mapping)
    df["frame_label"] = df["_cluster"].map({
        cluster_shoulder.index[0]: 0,
        cluster_shoulder.index[1]: 1,
        cluster_shoulder.index[2]: 2,
    })
    df.drop(columns=["_cluster"], inplace=True)
    return df, km

# 5. Peak lean mass target

def add_peak_lean_mass(df: pd.DataFrame) -> pd.DataFrame:
    """
    Based on Martin Berkhan / Casey Butt natural potential models.
    max_ffmi ~ 25 (male) / 22 (female) ± frame bonus.
    """
    frame_bonus = df["frame_label"].map({0: -1.0, 1: 0.0, 2: 1.0})
    base_ffmi   = np.where(df["sex"] == 1, 24.5, 21.0)
    max_ffmi    = base_ffmi + frame_bonus + RNG.normal(0, 0.5, len(df))
    max_ffmi    = clamp(max_ffmi, 18, 27)

    height_m              = df["height_cm"] / 100
    df["max_ffmi"]        = max_ffmi
    df["peak_lean_mass_kg"] = max_ffmi * height_m ** 2
    return df

# 6. Timeline target

def add_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    months_to_peak = lean_mass_gap / monthly_gain_rate
    Monthly gain rate depends on training experience.
    """
    lean_gap = np.maximum(df["peak_lean_mass_kg"] - df["lean_mass_kg"], 0.5)

    # monthly rate (kg/month) based on intensity level
    rate = np.where(
        df["intensity"] == 0,  0.90,   # beginner
        np.where(df["intensity"] == 1, 0.45,   # intermediate
                                        0.20)   # advanced
    )

    months = lean_gap / rate
    noise  = RNG.normal(0, months * 0.10)   # ±10% noise
    df["months_to_peak"] = clamp(months + noise, 3, 120)

    # convenience bands
    df["months_optimistic"]   = df["months_to_peak"] * 0.80
    df["months_conservative"] = df["months_to_peak"] * 1.20
    return df

# 7. Main

def generate(n: int = N, save_path: str = "data/simulated_dataset.csv"):
    demo     = gen_demographics(n)
    struct   = gen_structural(n, demo["sex"])
    df       = pd.DataFrame({**demo, **struct})
    df       = add_derived(df)
    df, _km  = add_frame_labels(df)
    df       = add_peak_lean_mass(df)
    df       = add_timeline(df)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f" Saved {len(df):,} rows → {save_path}")
    print(df[["sex", "frame_type", "peak_lean_mass_kg",
              "months_to_peak", "ffmi", "max_ffmi", "intensity"]].describe().round(2))
    return df


if __name__ == "__main__":
    generate()
