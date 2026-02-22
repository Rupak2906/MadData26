"""
train_all.py
One-shot script to generate data and train all three models.
Run this first before starting the API server.

Usage:
    python train_all.py
"""

import time

print("=" * 55)
print("AI Physique Predictor — ML Training Pipeline")
print("=" * 55)

# ── Step 1: Generate synthetic dataset ────────────────────
print("\n[1/4] Generating synthetic training data …")
t0 = time.time()
from synth_data import generate
df = generate(n=4_000, save_path="data/simulated_dataset.csv")
print(f"      Done in {time.time() - t0:.1f}s")

# ── Step 2: Train frame classifier ────────────────────────
print("\n[2/4] Training frame classifier …")
t0 = time.time()
from train_frame import load_data, train_kmeans, train_classifier
df2 = load_data()
km = train_kmeans(df2)
clf, scaler = train_classifier(df2)
print(f"      Done in {time.time() - t0:.1f}s")

# ── Step 3: Train peak mass regressor ─────────────────────
print("\n[3/4] Training peak lean mass model …")
t0 = time.time()
from train_peak import load_data as load_peak, train as train_peak
df3 = load_peak()
train_peak(df3)
print(f"      Done in {time.time() - t0:.1f}s")

# ── Step 4: Train timeline regressor ──────────────────────
print("\n[4/4] Training timeline model …")
t0 = time.time()
from train_timeline import load_data as load_tl, train as train_tl
df4 = load_tl()
train_tl(df4)
print(f"      Done in {time.time() - t0:.1f}s")

print("\n  All models trained and saved to models/")
print("    You can now start the API: uvicorn main:app --reload")