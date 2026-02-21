# 🏋️ AI Realistic Peak Physique Predictor

> A Computer Vision + Agentic AI system that analyzes your body structure and builds a **personalized, realistic transformation plan** — powered by pose estimation, predictive modeling, and an intelligent coaching agent that adapts to your consistency.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-FF6F00?style=flat-square)

---

## 🚀 What Is This?

Most fitness apps show you unrealistic body ideals and generic plans. This system does something fundamentally different — it:

1. **Scans your body structure** using computer vision (MediaPipe pose estimation)
2. **Estimates your genetic potential** using biomechanics + FFMI modeling
3. **Deploys an AI Coaching Agent** that reasons over your data and *adapts* your plan based on your real-world consistency
4. **Predicts a realistic timeline** — and shows you exactly how much faster you can get there by being more consistent

This is not a calorie counter. It is a **data-driven transformation intelligence system**.

---

## 🎯 The Problem We're Solving

| What Exists Today | What We Built |
|---|---|
| Generic workout templates | Plans personalized to your skeletal frame |
| Unrealistic body ideals | Predictions bounded by biological constraints |
| Static one-time plans | Agentic AI that adapts to your consistency |
| No timeline transparency | Confidence intervals with optimistic + realistic estimates |
| Black-box recommendations | Explainable reasoning for every decision |

---

## 🤖 Where Agentic AI Comes In

The core innovation is the **Transformation Coach Agent** — an LLM-powered agent that sits on top of the CV pipeline and:

- **Reasons** over your body analysis output
- **Decides** which tools to call (workout engine, diet engine, timeline engine)
- **Adapts** plans based on your stated consistency — the same body with 80% gym consistency gets a completely different plan than 40% consistency
- **Explains** its decisions in plain language, not just numbers
- **Loops** — if you say "I can only train 3 days", the agent re-runs the workout engine and updates everything

### Consistency → Plan Adaptation

```
High Consistency (>80%)  → 5-day PPL, aggressive surplus, 14-month timeline
Moderate (50–70%)        → 4-day Upper/Lower, moderate surplus, 18-month timeline  
Low (<40%)               → 3-day Full Body, recomp strategy, 26-month timeline
```

The agent tells you: *"If you increase from 50% to 80% consistency, you shave 4 months off your timeline."* That's motivating. That's real coaching.

---

## 🏗️ Architecture

```
Frontend (React + Tailwind)
        ↓
FastAPI Backend
        ↓
┌─────────────────────────────────────┐
│         CV Pipeline                 │
│  MediaPipe → Feature Engineering    │
│  → KMeans Frame Clustering          │
│  → FFMI Calculation                 │
│  → Peak Mass Regression             │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│      Transformation Coach Agent     │
│  LLM + Tool Calling                 │
│  ├── generate_workout_plan()        │
│  ├── generate_diet_plan()           │
│  └── predict_timeline()             │
└─────────────────────────────────────┘
        ↓
SQLite Database
        ↓
Dashboard (Current vs Peak | Timeline | Muscle Focus | Plan)
```

---

## 🔬 Technical Pipeline

### 1. Image Processing
- Input: full-body front-facing photo
- MediaPipe extracts 33 body landmarks (x, y coordinates)
- Normalized by height to remove scale bias

### 2. Feature Engineering
Structural measurements extracted: shoulder width, hip width, torso length, arm length, waist proxy.

Derived ratios: shoulder-to-hip ratio, torso-to-leg ratio, symmetry score.

### 3. Frame Classification (KMeans, k=3)
- Narrow frame
- Balanced frame
- Wide frame

### 4. Body Composition Estimation
Uses height, weight, and structural features to estimate body fat % and lean mass, then computes FFMI.

### 5. Peak Physique Prediction
Regression model using literature-based biological constraints to predict maximum natural lean mass, target body fat %, and peak FFMI.

### 6. Transformation Gap Analysis
```
Muscle Gain Required = Peak Lean Mass − Current Lean Mass
Fat Loss Required    = Current BF% − Target BF%
```
Distributed across muscle groups based on frame dominance.

### 7. Agentic Plan Generation
The coaching agent receives the full analysis, user's consistency score, and available tools. It reasons over the data and calls tools to generate a fully personalized workout split, nutrition plan, and timeline — then explains its reasoning in natural language.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Computer Vision | MediaPipe + OpenCV |
| Backend | FastAPI |
| Machine Learning | scikit-learn, XGBoost |
| Agentic AI | Claude API (tool calling) |
| Database | SQLite |
| Frontend | React + Tailwind CSS |
| Charts | Recharts |
| Deployment | Uvicorn (local) / Render (cloud) |

---

## 📁 Project Structure

```
ai-physique-predictor/
│
├── backend/
│   ├── main.py                  # FastAPI app + endpoints
│   ├── pose_extractor.py        # MediaPipe pose estimation
│   ├── feature_engineering.py   # Keypoint → feature vector
│   ├── clustering_model.pkl     # KMeans frame classifier
│   ├── peak_mass_model.pkl      # Peak mass regression model
│   ├── workout_engine.py        # Rule-based workout generator
│   ├── nutrition_engine.py      # TDEE + macro calculator
│   ├── agent.py                 # Transformation Coach Agent
│   ├── database.py              # SQLite helpers
│   └── schema.sql               # DB schema
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── IntakeForm.jsx   # Photo upload + user inputs
│       │   ├── Analyzing.jsx    # Loading screen
│       │   └── Dashboard.jsx    # Results dashboard
│       ├── components/
│       │   ├── StatsCard.jsx
│       │   ├── CoachMessage.jsx
│       │   ├── MuscleGapChart.jsx
│       │   ├── TimelineBar.jsx
│       │   ├── WorkoutPlan.jsx
│       │   └── DietPlan.jsx
│       └── api/
│           └── client.js
│
├── data/
│   └── simulated_dataset.csv    # Training data for regression models
│
├── notebooks/
│   └── model_training.ipynb
│
└── README.md
```

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Anthropic API key (for the coaching agent)

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/your-username/ai-physique-predictor.git
cd ai-physique-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn mediapipe opencv-python scikit-learn \
            xgboost pandas numpy anthropic python-multipart

# Initialize database
sqlite3 physique.db < backend/schema.sql

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Run the backend
cd backend
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🗄️ Database Schema

```sql
-- User profile and intake form data
users (id, name, age, height_cm, weight_kg, gender,
       experience_level, days_available, consistency_score,
       diet_strictness, dietary_preference, goal)

-- CV pipeline output
body_analysis (id, user_id, shoulder_width, hip_width,
               frame_type, body_fat_pct, lean_mass_kg, ffmi, ...)

-- Agent-generated transformation plan
transformation_plan (id, user_id, peak_lean_mass_kg, target_bf_pct,
                     timeline_months_realistic, timeline_months_optimistic,
                     workout_plan JSON, diet_plan JSON, agent_reasoning)

-- Per-muscle gap data for visualization
muscle_gaps (id, plan_id, muscle_group, current_kg, target_kg, gap_kg)
```

---

## 🖥️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Upload photo + user data, runs full pipeline |
| `GET` | `/plan/{user_id}` | Retrieve a user's transformation plan |
| `POST` | `/refine` | Send follow-up to agent (adjust plan) |

---

## ⚖️ Ethics & Disclaimers

- This tool is **not medical advice**
- All predictions are **probabilistic estimates** with confidence intervals
- Designed to promote **realistic and healthy** body standards — not unrealistic ideals
- No body comparison to other users — predictions are based solely on the individual's own biological constraints
- Transparent about estimation limitations at every step

---

## 🛣️ Roadmap

- [ ] SHAP explainability layer for prediction transparency
- [ ] Longitudinal progress tracking (re-upload photos over time)
- [ ] Reinforcement learning for adaptive plan updates
- [ ] 3D body mesh reconstruction
- [ ] Wearable device integration
- [ ] Injury risk modeling
- [ ] Posture and muscle imbalance detection

---

## 👥 Team

Built with 💪 at [Hackathon Name] by a team of 3.

| Role | Focus |
|---|---|
| ML / CV Engineer | Pose extraction, feature engineering, regression models |
| Backend Engineer | FastAPI, agent implementation, database |
| Frontend Engineer | React dashboard, UI/UX, data visualization |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

> *"Stop comparing yourself to others. Start understanding your own potential."*
