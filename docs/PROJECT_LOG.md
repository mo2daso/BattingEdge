# BattingEdge FYP - Developer Log

**Status:** Production Ready (V9.5 Ensemble + Smart Overlay)
**Current Version:** 1.5.0

### 📅 January 15, 2026 - Smart Tracking & Validation
- **Smart Overlay:** Integrated `YOLOv8n` into the inference pipeline (`backend/inference.py`) to automatically detect and draw a "Target Box" around the batsman, fixing issues with umpire tracking.
- **Data Quality:** Developed `validate_and_move.py` script to automate the quality assurance of 550+ processed videos, ensuring 100% overlay alignment before the final defense.
- **Reporting:** Refined PDF generation (`backend/report.py`) with professional styling, "KeepTogether" logic for tables, and improved visual hierarchy.

### 📅 January 11, 2026 - The V9.5 Ensemble Architecture
- **Model Upgrade:** Replaced the single Bi-LSTM model with a **Stacking Ensemble (V9.5)**.
- **Hybrid Intelligence:** Combined:
    - **Bi-LSTM** (91.80% acc) for temporal sequences.
    - **Random Forest** (89.42% acc) for geometric shape analysis.
    - **XGBoost** for error correction.
- **Meta-Learner:** Implemented a Logistic Regression meta-model to arbitrate predictions, boosting final test accuracy to **94.71%**.
- **Defense:** Eliminated false positives in "Defensive Shot" classification.

### 📅 January 5, 2026 - Biomechanical Rule Engine
- **Logic:** Created `backend/shot_rules.py` to decouple grading logic from the main inference loop.
- **Calibration:** Tuned angle thresholds (e.g., Elbow Extension 120°-140°) based on feedback to ensure "Strict but Fair" grading.
- **Feedback:** Implemented dynamic advice generation (e.g., "Good shot, but watch your head position").

### 📅 December 8, 2025 - Full Frontend Integration
- **UI/UX:** Built a modern, dark-themed React Dashboard (`src/pages/ResultPage.jsx`) with animated score gauges and expandable feedback cards.
- **Visuals:** Implemented a new video player overlay with H.264 codec support for browser compatibility.
- **Reporting:** Upgraded PDF generation to include grading (A/B/C) and specific "Coach's Notes."

### 📅 December 4, 2025 - Backend API Finalization
- **FastAPI:** Completed the transition from scripts to a persistent server (`backend/main.py`).
- **Database:** Integrated SQLite to store analysis history.
- **Pipeline:** Validated the Dual-Stream Inference architecture.

### 📅 November 30, 2025 - The "Grand Cleanup"
- **Architecture Audit:** Performed deep file hash analysis on 5.9GB of project data.
- **Standardization:** Consolidated model weights to a single source of truth in `backend/models/`.
- **Validation:** Confirmed `V8p` as the base candidate before Ensemble development.

### 📅 November 25, 2025 - The "V8p" Breakthrough
- **Model Training:** Successfully trained `shot_model_V8p_best.keras`.
- **Metrics:** Achieved highest validation accuracy to date.

### 📅 November 11, 2025 - Project Inception
- Initial environment setup.
- Integration of MediaPipe Pose Estimation.
- First successful skeleton overlay test.