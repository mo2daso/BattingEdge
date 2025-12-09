
# 🏏 BattingEdge: AI-Powered Cricket Analysis System
![Version](https://img.shields.io/badge/version-V8p_Production-blue)
![Stack](https://img.shields.io/badge/React-FastAPI-green)
![AI](https://img.shields.io/badge/TensorFlow_|_MediaPipe-Computer_Vision-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

BattingEdge is an end-to-end AI coaching platform that brings professional-grade cricket analytics to everyday players. It fuses Computer Vision and Deep Learning to classify shots and deliver real-time biomechanical feedback—acting as your own virtual batting coach.

With its V8p model achieving 78% classification accuracy, BattingEdge provides actionable insights such as "Elbow dropped" or "Head leaning off line" to help players systematically improve their batting technique.

🚀 Key Features
🧠 AI Analysis Engine

Shot Classification
Predicts 4 core cricket shots using a custom Bi-LSTM sequence model:

Drive

Pull

Cut

Sweep

Biomechanics Grading
Generates a 0–100 Form Score using 5 biomechanical checks:

Elbow Angle

Head Stability

Footwork Balance

Hip Rotation

Follow Through

Smart Player Tracking
Utilizes YOLOv8 to isolate the batter for accurate pose extraction.

💻 Modern Web Platform

33-point MediaPipe Skeleton Overlay directly rendered on video frames.

Interactive dashboard with confidence bars and expandable coaching insights.

PDF coaching reports with technique grades, summaries, and drill recommendations.

Smooth H.264 video streaming and dark-mode optimized UI.

📊 Model Performance (V8p)
Shot Class	Precision	Recall	F1-Score	Status
Drive	70%	74%	0.72	Good
Pull	77%	77%	0.77	Excellent
Cut	88%	83%	0.86	Superior
Sweep	80%	80%	0.80	Stable
OVERALL	78%	78%	0.78	Production Ready
🏗️ System Architecture
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
    API -->|Process| Inference[Inference Engine]
    Inference -->|Detect| YOLO[YOLOv8 Person Detection]
    Inference -->|Extract| MP[MediaPipe Pose Landmarks]
    Inference -->|Classify| LSTM[Bi-LSTM Shot Classifier]
    Inference -->|Grade| Bio[Biomechanics Engine]
    API -->|Store| DB[(SQLite Database)]
    API -->|Return| Result[JSON + Overlay Video + PDF Report]

⚡ Quick Start Guide
Prerequisites

Python 3.10+

Node.js 18+

1. Backend Setup
cd BattingEdge_FYP

# Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt

# Start API Server
uvicorn backend.main:app --reload


Server available at: http://127.0.0.1:8000

2. Frontend Setup
cd frontend

# Install Node Packages
npm install

# Start React App
npm run dev


App available at: http://localhost:5173

📂 Project Structure
BattingEdge/
├── backend/                    # FastAPI Backend
│   ├── models/                 # Trained Models (.keras, .pkl)
│   ├── inference.py            # Core AI Logic
│   ├── database.py             # SQLite Handler
│   ├── report.py               # PDF Generation Engine
│   └── main.py                 # API Endpoints
├── frontend/                   # React Application
│   ├── src/
│   │   ├── pages/              # UI Pages
│   │   ├── components/         # Reusable Components
│   │   └── utils/              # API Wrappers & Helpers
├── data/
│   ├── dataset_v8p/            # Training Data
│   └── defense_demos/          # Sample Videos
└── docs/                       # Documentation Resources

🔬 Biomechanical Checks

Technique evaluation follows standard cricket coaching orthodoxy:

Metric	Ideal Benchmark
Front Elbow	120°–140° at ball impact
Head Stability	<10 cm vertical drift
Back Foot Lift	<5 cm (for stable base)
Hip Rotation	>30° (front-foot) / >60° (cross-bat)
Follow Through	Hands must finish above shoulder height
📜 License

Developed by Mohammad Soban as a Final Year Project (BS Computer Science), 2025.
Licensed under the MIT License.
