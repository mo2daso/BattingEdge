# 🏏 BattingEdge: AI-Powered Cricket Analysis System
![Version](https://img.shields.io/badge/version-V9.5_Ensemble-blue)
![Stack](https://img.shields.io/badge/React-FastAPI-green)
![AI](https://img.shields.io/badge/Hybrid_Intelligence-Stacking_Ensemble-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**BattingEdge** is a professional-grade AI coaching platform that democratizes cricket analysis. It utilizes a **Hybrid Intelligence** approach, combining **Computer Vision (MediaPipe, YOLOv8)** with a **Stacking Ensemble Classifier (Bi-LSTM + Random Forest + XGBoost)** to deliver state-of-the-art shot classification and biomechanical grading.

Acting as a **Virtual Coach**, BattingEdge provides objective, actionable feedback (e.g., "Elbow dropped," "Head falling over") with **94.71% classification accuracy**, significantly outperforming traditional single-model systems.

---

## 🚀 Key Features

### 🧠 Hybrid AI Engine (V9.5)
* **Ensemble Classification:** Uses a meta-learner to combine predictions from:
    * **Bi-LSTM:** Captures temporal motion sequences (the "flow" of the shot).
    * **Random Forest:** Analyzes geometric shapes and limb angles (the "structure" of the shot).
    * **XGBoost:** Corrects residual errors and handles edge cases.
* **Smart Tracking:** Utilizes **YOLOv8** to intelligently isolate the batsman, filtering out umpires and wicketkeepers for precise skeletal tracking.
* **Biomechanics Grading:** Calculates a 0-100 "Form Score" based on professional coaching standards (ECB/MCC guidelines) for Elbow Extension, Head Stability, and Footwork.

### 💻 Modern Web Platform
* **Smart Overlay:** Renders a color-coded skeletal overlay (Green = Good, Red = Error) with a "Target Box" tracking the batsman in real-time.
* **Professional Reporting:** Auto-generates detailed PDF Coaching Reports featuring shot summaries, strength/weakness tables, and drill recommendations.
* **Interactive Dashboard:** Dark-mode React UI with drag-and-drop uploads, animated score gauges, and a searchable history database.

---

## 📊 Model Performance (V9.5 Ensemble)

| Shot Class | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Drive** | 92% | 95% | 0.93 | Excellent |
| **Pull** | 94% | 93% | 0.93 | Excellent |
| **Cut** | 96% | 94% | 0.95 | Superior |
| **Sweep** | 91% | 90% | 0.90 | High |
| **Defense** | 98% | 99% | 0.98 | Perfect |
| **OVERALL** | **94.71%** | **94.71%** | **0.94** | **Production Ready** |

---

## 🏗️ System Architecture

```mermaid
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
    API -->|Process| Logic[Inference Engine]
    Logic -->|Detect & Crop| YOLO[YOLOv8 (Person Isolation)]
    Logic -->|Extract Features| MP[MediaPipe (Pose Landmarks)]
    
    subgraph "Stacking Ensemble V9.5"
    MP -->|Temporal Data| LSTM[Bi-LSTM Model]
    MP -->|Geometric Data| RF[Random Forest]
    MP -->|Booster| XGB[XGBoost]
    LSTM -->|Vote| META[Logistic Regression Meta-Model]
    RF -->|Vote| META
    XGB -->|Vote| META
    end
    
    META -->|Final Class| Bio[Biomechanics Engine]
    Bio -->|Grade| Report[PDF Generator]
    API -->|Store| DB[(SQLite Database)]
    API -->|Return| Result[JSON + Overlay Video + PDF]

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
# Server running at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

2. Frontend Setup

cd frontend
# Install Node Packages
npm install

# Start React App
npm run dev
# App running at: http://localhost:5173

📂 Project Structure

BattingEdge/
├── backend/                   # Python FastAPI Server
│   ├── models/                # V9.5 Ensemble (keras, pkl, json)
│   ├── outputs/               # Generated Reports & Videos
│   ├── inference.py           # Ensemble Logic & Smart Overlay
│   ├── shot_rules.py          # Biomechanical Rule Engine
│   ├── report.py              # PDF Generation Engine
│   └── main.py                # API Endpoints
├── frontend/                  # React UI
│   ├── src/
│   │   ├── pages/             # Dashboard, Results
│   │   ├── components/        # VideoPlayer, ScoreGauge
│   │   └── utils/             # API Connectors
└── data/                      # Dataset & Artifacts

📜 License
Developed by Mohammad Soban as a Final Year Project (BS CS). Copyright © 2026. All Rights Reserved.