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

---

## 📊 Model Performance (V8p)

| Shot Class | Precision | Recall | F1-Score | Notes              |
|------------|-----------|--------|----------|--------------------|
| Drive      | 70%       | 74%    | 0.72     | Good stability     |
| Pull       | 77%       | 77%    | 0.77     | Excellent, balanced|
| Cut        | 88%       | 83%    | 0.86     | Extremely strong   |
| Sweep      | 80%       | 80%    | 0.80     | Reliable           |
| **Overall**| **78%**   | **78%**| **0.78** | ✅ Production Ready |

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
Python 3.10+

Node.js 18+

Git

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
Backend runs at 👉 http://127.0.0.1:8000

🟩 Frontend Setup (React + Vite)
bash
cd frontend
npm install
npm run dev
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
