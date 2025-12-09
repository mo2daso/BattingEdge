
# 🏏 BattingEdge: AI-Powered Cricket Analysis System
![Version](https://img.shields.io/badge/version-V8p_Production-blue)
![Stack](https://img.shields.io/badge/React-FastAPI-green)
![AI](https://img.shields.io/badge/TensorFlow_|_MediaPipe-Computer_Vision-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

🌟 Overview

BattingEdge is a full-stack, AI-driven cricket coaching system built to bring professional-level analytics to everyday players.
It combines Computer Vision, Deep Learning, and Biomechanical Analysis to evaluate batting technique, classify shots, and generate coaching feedback — all through a modern web interface.

Whether you're a coach, a player, or a cricket academy, BattingEdge functions as a Virtual Batting Coach, providing:

Real-time technique feedback

Overlayed skeleton pose tracking

Shot classification

Automated PDF coaching reports

Performance dashboards

Biomechanics-based grading

This system is built as a production-ready FYP (Final Year Project) with modular React + FastAPI architecture.

🚀 Feature Highlights
🧠 1. AI Analysis Engine

A tightly integrated inference pipeline combining:

Shot Classification (Bi-LSTM)

Predicts four core shots:

Drive

Pull

Cut

Sweep

Uses:

Frame-level pose sequences

YOLOv8 cropping for cleaner person-focused frames

Bidirectional LSTM for temporal modeling

Biomechanics Grading (0–100 Form Score)

Evaluates form using five technical parameters:

Parameter	Metric
Elbow Angle	120°–140° at impact
Head Stability	<10 cm vertical drift
Back Foot Contact	<5 cm lift
Hip Rotation	>30° (front-foot) / >60° (cross-bat)
Follow Through	Hands finishing above shoulder

Output:

Letter grade (A / B / C)

Per-check evaluation

Corrective suggestions

Smart Player Detection

YOLOv8 segmentation

Removes umpire/wicketkeeper interference

Significantly improves pose extraction stability

💻 2. Modern Web Platform (React)

The frontend delivers a polished, interactive user experience:

Dark-mode UI

Video Player with HUD Overlay

33-point MediaPipe skeleton tracking

Confidence bar charts

Expandable feedback cards

Real-time form score visualization

Instant report download

📄 3. Automated Coaching Reports (PDF)

Generated using a FastAPI backend engine:

Player summary

Detected shot type

Form Score (0–100)

Biomechanical breakdown

Feedback notes

Recommended drills

Time-coded snapshots

Looks clean, professional, and academy-ready.

📊 Model Performance (V8p)
Shot Class	Precision	Recall	F1-Score	Notes
Drive	70%	74%	0.72	Good stability
Pull	77%	77%	0.77	Excellent, balanced
Cut	88%	83%	0.86	Extremely strong
Sweep	80%	80%	0.80	Reliable
OVERALL	78%	78%	0.78	Production Ready
🏗️ System Architecture
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
    API -->|Forward Video| Inference[Inference Engine]
    Inference -->|Detect Player| YOLO[YOLOv8 Detection]
    Inference -->|Extract Landmarks| MP[MediaPipe Pose]
    Inference -->|Predict Shot| LSTM[Bi-LSTM Model V8p]
    Inference -->|Check Technique| Bio[Biomechanics Engine]
    API -->|Generate| PDF[PDF Coaching Report]
    API -->|Save| DB[(SQLite)]
    API -->|Return| Output[JSON + Overlay Video + Report]

⚡ Installation Guide
🔧 Prerequisites

Python 3.10 or higher

Node.js 18+

Git

FFmpeg (if running video processing locally)

🟦 1. Backend Setup (FastAPI)
cd BattingEdge_FYP

# Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Development Server
uvicorn backend.main:app --reload


Backend runs at:
http://127.0.0.1:8000

🟩 2. Frontend Setup (React + Vite)
cd frontend
npm install
npm run dev


Frontend runs at:
http://localhost:5173

📂 Project Structure
BattingEdge/
├── backend/
│   ├── models/                # AI Models (V8p .keras, scalers, pickles)
│   ├── inference.py           # Core AI pipeline (YOLO + MP + LSTM + Biomech)
│   ├── report.py              # PDF Generation
│   ├── database.py            # SQLite + ORM helpers
│   └── main.py                # FastAPI routes
│
├── frontend/
│   ├── src/
│   │   ├── pages/             # UploadPage, ResultPage
│   │   ├── components/        # Navbar, Player, SkeletonOverlay, Cards
│   │   └── utils/             # API Handler & helper functions
│
├── data/
│   ├── dataset_v8p/           # Preprocessed Training Data
│   └── defense_demos/         # Demo videos for testing
│
└── docs/
    └── architecture/          # Diagrams, notes, documentation

🔬 Biomechanics Engine Details
1. Frame-Level Metrics

Calculates:

Joint angles

Distance deltas

Shoulder-line stability

Z-axis depth (if available)

Hip–shoulder torque ratio

2. Temporal Smoothing

Median filter + moving average to avoid jitter.

3. Form Score Calculation

Combined weighting:

Elbow: 25%

Head: 20%

Footwork: 20%

Hip Rotation: 20%

Follow Through: 15%

Output:

Score (0–100)

A/B/C grade

Issue detection list

🎯 Roadmap

Add 7-shot classifier (Drive, Pull, Hook, Cut, Sweep, Flick, Defense)

Introduce mobile app (React Native)

Real-time camera-based assessment

Cloud-hosted central database

Player progress tracking

Video comparison with pro players

📜 License

This project is licensed under the MIT License.
Developed by Mohammad Soban (BSCS, 2025).
Licensed under the MIT License.
