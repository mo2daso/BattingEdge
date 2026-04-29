# BattingEdge — AI Cricket Batting Analysis System

[![Version](https://img.shields.io/badge/Model-V9.5_Stacking_Ensemble-blue?style=for-the-badge)](.)
[![Accuracy](https://img.shields.io/badge/Accuracy-94.71%25-brightgreen?style=for-the-badge)](.)
[![Stack](https://img.shields.io/badge/FastAPI_%2B_React-Full_Stack-orange?style=for-the-badge)](.)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)](.)

**BattingEdge** is a full-stack AI coaching platform that analyses cricket batting technique from a video upload. It classifies the shot type and evaluates biomechanical form, giving every player access to the kind of feedback previously reserved for professional coaching setups.

Built as a Final Year Project — Bahria University Karachi, BS Computer Science, 2025.

---

## What It Does

Upload a video of a batting shot and BattingEdge will:

- Detect and classify the shot (Cover Drive, Cut Shot, Defense, Pull Shot, Sweep Shot)
- Extract 33-point MediaPipe pose landmarks for every frame
- Score the technique 0–100 against ECB/MCC biomechanical standards
- Generate a letter grade (A+ to F) with per-check pass/fail breakdown
- Overlay the skeleton on the video with color-coded joints (green = correct, red = error)
- Recommend targeted practice drills
- Generate a full PDF coaching report
- Provide an AI assistant (BESSA) for follow-up coaching questions

---

## Model Performance (V9.5 Stacking Ensemble)

The final model is a **stacking ensemble** that combines three base classifiers through a logistic regression meta-learner:

| Model | Accuracy |
|---|---|
| Bi-LSTM | 91.80% |
| BiGRU | 91.80% |
| Random Forest | 89.42% |
| XGBoost | 87.30% |
| **Stacking Ensemble (V9.5)** | **94.71%** |

**Shots classified:** Cover Drive · Cut Shot · Defense · Pull Shot · Sweep Shot  
**Feature shape:** 50 frames × 107 features  
**Standards:** ECB Level 2 + MCC Laws of Cricket

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI, Python 3.10+ |
| Pose Estimation | MediaPipe Pose (33 landmarks) |
| Player Detection | YOLOv8n |
| Deep Learning | TensorFlow / Keras (Bi-LSTM) |
| Classical ML | XGBoost, Random Forest, Scikit-learn |
| Database | SQLite (raw sqlite3 — no ORM) |
| Auth | JWT (python-jose) + Google OAuth 2.0 |
| AI Assistant | Groq API (LLaMA 3) |
| PDF Reports | ReportLab |
| Deployment | Render (backend) + Vercel (frontend) |

---

## Project Structure

```
BattingEdge_FYP/
├── backend/
│   ├── main.py                  # FastAPI app — all API endpoints
│   ├── inference_v9_5.py        # Stacking ensemble inference pipeline
│   ├── shot_rules.py            # Biomechanical rule engine (ECB/MCC)
│   ├── database.py              # SQLite helpers (raw sqlite3)
│   ├── report.py                # PDF report generator
│   ├── auth_router.py           # Auth endpoints (register, login, Google)
│   ├── auth_models.py           # User DB operations
│   ├── auth_utils.py            # JWT, bcrypt, email utilities
│   ├── groq_router.py           # AI assistant + weekly tips scheduler
│   ├── models/                  # V9.5 model files (.keras, .pkl, .json)
│   ├── uploads/                 # Uploaded videos (gitignored)
│   └── outputs/                 # Overlay videos + PDFs (gitignored)
├── frontend/
│   ├── src/
│   │   ├── pages/               # LandingPage, AnalyzePage, ResultPage,
│   │   │                        # DashboardPage, SettingsPage, FAQPage,
│   │   │                        # MobilePage, VerifyEmailPage
│   │   ├── components/          # Navbar, AuthModal, ChatBot (BESSA)
│   │   ├── context/             # AuthContext, ThemeContext
│   │   └── utils/               # api.js — all backend calls
│   └── public/
├── notebooks/                   # Training notebooks (V9.5)
├── requirements.txt
└── README.md
```

---

## API Endpoints

```
GET  /                           Health check
GET  /api/health                 Health check (JSON)
POST /api/upload                 Upload video — returns video_id
POST /api/analyze/{video_id}     Start analysis (background task)
GET  /api/result/{video_id}      Poll for result
GET  /api/video/{video_id}/overlay   Stream overlay video
GET  /api/report/{video_id}/pdf      Download PDF report

POST /auth/register              Create account (auto-verified)
POST /auth/login                 Login — returns JWT
POST /auth/google                Google OAuth login
GET  /auth/me                    Get current user (requires JWT)
PUT  /auth/update-password       Change password
PUT  /auth/update-email          Change email
POST /auth/forgot-password       Send reset email
POST /auth/reset-password        Reset with token

POST /groq/chat                  AI assistant message
POST /groq/send-weekly-tips      Trigger weekly tip email
```

---

## Local Setup

**Prerequisites:** Python 3.10+, Node.js 18+

**Backend**
```bash
cd BattingEdge_FYP
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Create backend/.env with:
# SECRET_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD,
# GOOGLE_CLIENT_ID, GROQ_API_KEY, FRONTEND_URL

cd backend
uvicorn main:app --reload
# Runs at http://127.0.0.1:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

---

## Key Features

- **Free analysis for guests** — one analysis without an account, then prompted to sign up
- **Video trimming** — client-side trim before upload so users send only the relevant clip
- **Mobile recording page** (`/mobile`) — QR-code accessible, recording-only, no chatbot
- **Dark/light theme** — persisted across sessions
- **Dashboard** — full analysis history for logged-in users
- **PDF reports** — downloadable coaching report with ECB/MCC standards table

---

## Authors

Mohammad Soban — [github.com/MohammadSoban](https://github.com/MohammadSoban)

Bahria University Karachi · BS Computer Science · FYP 2025
