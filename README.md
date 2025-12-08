Markdown

# 🏏 BattingEdge: AI-Powered Cricket Analysis System
![Version](https://img.shields.io/badge/version-V8p_Production-blue)
![Stack](https://img.shields.io/badge/React-FastAPI-green)
![AI](https://img.shields.io/badge/TensorFlow_|_MediaPipe-Computer_Vision-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**BattingEdge** is a comprehensive AI coaching platform designed to democratize professional-grade cricket analysis. It combines **Computer Vision (MediaPipe, YOLOv8)** with **Deep Learning (Bi-LSTM)** to classify shots and perform real-time biomechanical grading.

Unlike simple video players, BattingEdge acts as a **Virtual Coach**, offering actionable feedback on technique (e.g., "Elbow dropped," "Head falling over") with 78% classification accuracy.

---

## 🚀 Key Features

### 🧠 AI Analysis Engine
* **Shot Classification:** Identifies 4 key shots (Drive, Pull, Cut, Sweep) using a Bi-LSTM network.
* **Biomechanics Grading:** Calculates a 0-100 "Form Score" based on 5 technical checks (Elbow Angle, Head Stability, Footwork, Hip Rotation, Follow Through).
* **Smart Tracking:** Uses YOLOv8 to isolate the batsman from the wicketkeeper/umpire for accurate analysis.

### 💻 Modern Web Platform
* **Visual Overlay:** Renders a 33-point skeleton and HUD directly onto the video in the browser (H.264 streaming).
* **Professional Reporting:** Auto-generates PDF Coaching Reports with grades (A/B/C) and specific corrective drills.
* **Dashboard:** Dark-mode React UI with animated confidence bars and expandable feedback cards.

---

## 📊 Model Performance (V8p)

| Shot Class | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Drive** | 70% | 74% | 0.72 | Good |
| **Pull** | 77% | 77% | 0.77 | Excellent |
| **Cut** | 88% | 83% | 0.86 | Superior |
| **Sweep** | 80% | 80% | 0.80 | Stable |
| **OVERALL** | **78%** | **78%** | **0.78** | **Production Ready** |

---

## 🏗️ System Architecture

```mermaid
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
    API -->|Process| Logic[Inference Engine]
    Logic -->|Detect| YOLO[YOLOv8 (Person Detection)]
    Logic -->|Extract| MP[MediaPipe (Pose Landmarks)]
    Logic -->|Classify| LSTM[Bi-LSTM Model V8p]
    Logic -->|Analyze| Bio[Biomechanics Engine]
    API -->|Store| DB[(SQLite Database)]
    API -->|Return| Result[JSON + Overlay Video + PDF]
⚡ Quick Start Guide
Prerequisites
Python 3.10+

Node.js 18+

1. Backend Setup
Bash

cd BattingEdge_FYP
# Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt

# Start API Server
uvicorn backend.main:app --reload
Server running at: http://127.0.0.1:8000

2. Frontend Setup
Bash

cd frontend
# Install Node Packages
npm install

# Start React App
npm run dev
App running at: http://localhost:5173

📂 Project Structure
Plaintext

BattingEdge/
├── backend/                   # Python FastAPI Server
│   ├── models/                # AI Models (V8p .keras, .pkl)
│   ├── inference.py           # Core AI Logic (Classification + Biomechanics)
│   ├── database.py            # SQLite Handler
│   ├── report.py              # PDF Generation Engine
│   └── main.py                # API Endpoints
├── frontend/                  # React UI
│   ├── src/
│   │   ├── pages/             # UploadPage, ResultPage
│   │   ├── components/        # Navbar, VideoPlayer, HUD
│   │   └── utils/             # API Connectors
├── data/                      # Dataset & Artifacts
│   ├── dataset_v8p/           # Active Training Data
│   └── defense_demos/         # Generated Demo Videos
└── docs/                      # Documentation
🔬 Biomechanical Checks
The system evaluates technique against "Textbook Cricket Orthodoxy":

Front Elbow: Must be 120°-140° at impact for maximum leverage.

Head Stability: Vertical drift must be <10cm to ensure balance.

Back Foot: Must stay grounded (<5cm lift) to anchor power.

Hip Rotation: Must exceed 30° (Front foot) or 60° (Cross bat) for torque.

Follow Through: Hands must finish higher than shoulders.

📜 License
Developed by Mohammad Soban as a Final Year Project (BS CS). Copyright © 2025. All Rights Reserved.


