<<<<<<< HEAD
# 🏏 BattingEdge: AI-Powered Cricket Analysis System
![Version](https://img.shields.io/badge/version-V9.5_Ensemble-blue)
![Stack](https://img.shields.io/badge/React-FastAPI-green)
![AI](https://img.shields.io/badge/Hybrid_Intelligence-Stacking_Ensemble-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**BattingEdge** is a professional-grade AI coaching platform that democratizes cricket analysis. It utilizes a **Hybrid Intelligence** approach, combining **Computer Vision (MediaPipe, YOLOv8)** with a **Stacking Ensemble Classifier (Bi-LSTM + Random Forest + XGBoost)** to deliver state-of-the-art shot classification and biomechanical grading.

Acting as a **Virtual Coach**, BattingEdge provides objective, actionable feedback (e.g., "Elbow dropped," "Head falling over") with **94.71% classification accuracy**, significantly outperforming traditional single-model systems.
=======
## 🏗️ System Architecture

### 🔄 Flow Overview
- 👤 **User** uploads video via React frontend  
- 💻 **Frontend (React)** sends request to FastAPI backend  
- ⚡ **FastAPI API** forwards video to inference engine  
- 🔍 **YOLOv8** detects player and removes interference  
- 🎯 **MediaPipe Pose** extracts skeleton landmarks  
- 📈 **Bi-LSTM Model V8p** predicts shot type  
- 🏃 **Biomechanics Engine** checks technique and calculates form score  
- 📄 **PDF Report Generator** creates coaching report  
- 🗄️ **SQLite Database** stores results  
- ✅ **Output** returned: JSON + overlay video + PDF report  

### 📊 Mermaid Diagram (plain text only)
```mermaid
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
🔑 Why this works
The Mermaid block is now pure text (no emojis, no extra characters).

The bullet list above gives the colorful, emoji-rich explanation that GitHub can render safely.

Readers get both: a diagram and a readable step-by-step list.

👉 Do you want me to also add collapsible sections (like <details> blocks) so the README looks even cleaner and lets users expand/collapse the architecture flow?

NOW GIVE ME FULL EVEN BETTER README WGIC IS EVEN MORE ATTRACTIVE AND ACTUALLY WORKS ON GITHUB
Perfect — let’s craft a fully polished, GitHub‑ready README that is both attractive and functional. I’ll use working badges, emojis, bullet points, collapsible sections, and a clean Mermaid diagram (without errors). This version will render correctly on GitHub and look professional.

markdown
# 🏏 BattingEdge: AI-Powered Cricket Analysis System

[![Version](https://img.shields.io/badge/version-V8p_Production-blue?style=for-the-badge&logo=github)](https://github.com/MohammadSoban/BattingEdge)
[![Stack](https://img.shields.io/badge/React-FastAPI-green?style=for-the-badge&logo=react)](https://react.dev/)
[![AI](https://img.shields.io/badge/TensorFlow_|_MediaPipe-Computer_Vision-orange?style=for-the-badge&logo=tensorflow)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)](./LICENSE)
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3

---

## 🌟 Overview

**BattingEdge** is a full-stack, AI-driven cricket coaching system built to bring **professional-level analytics** to everyday players.  
It combines **Computer Vision**, **Deep Learning**, and **Biomechanical Analysis** to evaluate batting technique, classify shots, and generate coaching feedback — all through a modern web interface.

🎯 BattingEdge functions as a **Virtual Batting Coach**, providing:
- ⚡ Real-time technique feedback  
- 🎥 Skeleton pose tracking overlay  
- 🧠 Shot classification (Drive, Pull, Cut, Sweep)  
- 📄 Automated PDF coaching reports  
- 📊 Performance dashboards  
- 🏃 Biomechanics-based grading  

---

## 🚀 Feature Highlights

<<<<<<< HEAD
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
=======
### 🧠 AI Analysis Engine
- **Shot Classification (Bi-LSTM)**  
  - Predicts: `Drive | Pull | Cut | Sweep`  
  - Uses frame-level pose sequences, YOLOv8 cropping, and Bidirectional LSTM for temporal modeling.  

- **Biomechanics Grading (Form Score 0–100)**  
  Evaluates form using five technical parameters:

| Parameter       | Metric                          |
|-----------------|---------------------------------|
| Elbow Angle     | 120°–140° at impact             |
| Head Stability  | <10 cm vertical drift           |
| Back Foot Contact | <5 cm lift                   |
| Hip Rotation    | >30° (front-foot) / >60° (cross-bat) |
| Follow Through  | Hands finishing above shoulder  |

✅ Output: Letter grade (A/B/C), per-check evaluation, corrective suggestions.

- **Smart Player Detection**  
  - YOLOv8 segmentation removes umpire/wicketkeeper interference.  
  - Improves pose extraction stability.  

---

### 💻 Modern Web Platform (React)
- 🌑 Dark-mode UI  
- 🎥 Video Player with HUD Overlay  
- 🦾 33-point MediaPipe skeleton tracking  
- 📊 Confidence bar charts  
- 🗂️ Expandable feedback cards  
- ⚡ Real-time form score visualization  
- 📄 Instant report download  

---

### 📄 Automated Coaching Reports (PDF)
Generated via **FastAPI backend**:
- 👤 Player summary  
- 🏏 Detected shot type  
- 📊 Form Score (0–100)  
- 🧩 Biomechanical breakdown  
- 📝 Feedback notes & recommended drills  
- ⏱️ Time-coded snapshots  
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3

---

## 📊 Model Performance (V9.5 Ensemble)

<<<<<<< HEAD
| Shot Class | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Drive** | 92% | 95% | 0.93 | Excellent |
| **Pull** | 94% | 93% | 0.93 | Excellent |
| **Cut** | 96% | 94% | 0.95 | Superior |
| **Sweep** | 91% | 90% | 0.90 | High |
| **Defense** | 98% | 99% | 0.98 | Perfect |
| **OVERALL** | **94.71%** | **94.71%** | **0.94** | **Production Ready** |
=======
| Shot Class | Precision | Recall | F1-Score | Notes              |
|------------|-----------|--------|----------|--------------------|
| Drive      | 70%       | 74%    | 0.72     | Good stability     |
| Pull       | 77%       | 77%    | 0.77     | Excellent, balanced|
| Cut        | 88%       | 83%    | 0.86     | Extremely strong   |
| Sweep      | 80%       | 80%    | 0.80     | Reliable           |
| **Overall**| **78%**   | **78%**| **0.78** | ✅ Production Ready |
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3

---

## 🏗️ System Architecture

### 🔄 Flow Overview
- 👤 **User** uploads video via React frontend  
- 💻 **Frontend (React)** sends request to FastAPI backend  
- ⚡ **FastAPI API** forwards video to inference engine  
- 🔍 **YOLOv8** detects player and removes interference  
- 🎯 **MediaPipe Pose** extracts skeleton landmarks  
- 📈 **Bi-LSTM Model V8p** predicts shot type  
- 🏃 **Biomechanics Engine** checks technique and calculates form score  
- 📄 **PDF Report Generator** creates coaching report  
- 🗄️ **SQLite Database** stores results  
- ✅ **Output** returned: JSON + overlay video + PDF report  

### 📊 Mermaid Diagram
```mermaid
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
<<<<<<< HEAD
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
=======
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
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3
Python 3.10+

Node.js 18+

<<<<<<< HEAD
1. Backend Setup
=======
Git
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3

FFmpeg (for local video processing)

🟦 Backend Setup (FastAPI)
bash
cd BattingEdge_FYP

# Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Development Server
uvicorn backend.main:app --reload
<<<<<<< HEAD
# Server running at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

2. Frontend Setup
=======
Backend runs at 👉 http://127.0.0.1:8000
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3

🟩 Frontend Setup (React + Vite)
bash
cd frontend
npm install
npm run dev
<<<<<<< HEAD
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
=======
Frontend runs at 👉 http://localhost:5173

📂 Project Structure
Code
BattingEdge/
├── backend/
│   ├── models/        # AI Models (V8p .keras, scalers, pickles)
│   ├── inference.py   # Core AI pipeline (YOLO + MP + LSTM + Biomech)
│   ├── report.py      # PDF Generation
│   ├── database.py    # SQLite + ORM helpers
│   └── main.py        # FastAPI routes
│
├── frontend/
│   ├── src/
│   │   ├── pages/     # UploadPage, ResultPage
│   │   ├── components/# Navbar, Player, SkeletonOverlay, Cards
│   │   └── utils/     # API Handler & helper functions
│
├── data/
│   ├── dataset_v8p/   # Preprocessed Training Data
│   └── defense_demos/ # Demo videos for testing
│
└── docs/
    └── architecture/  # Diagrams, notes, documentation
🔬 Biomechanics Engine Details
Frame-Level Metrics

Joint angles, distance deltas, shoulder-line stability, Z-axis depth, hip–shoulder torque ratio.

Temporal Smoothing

Median filter + moving average to avoid jitter.

Form Score Calculation

Weighted parameters:

Elbow (25%), Head (20%), Footwork (20%), Hip Rotation (20%), Follow Through (15%).

Output: Score (0–100), Grade (A/B/C), Issue detection list.

🎯 Roadmap
➕ Add 7-shot classifier (Drive, Pull, Hook, Cut, Sweep, Flick, Defense)

📱 Mobile app (React Native)

🎥 Real-time camera-based assessment

☁️ Cloud-hosted central database

📊 Player progress tracking

🏏 Video comparison with pro players

📜 License
This project is licensed under the MIT License. Developed by Mohammad Soban (BSCS, 2025). 📄 View License
>>>>>>> 66b3a810abcb4462c26c4522ff5d43f5490af6a3
