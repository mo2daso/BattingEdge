# BattingEdge FYP - Developer Log

**Status:** Production Ready (V8p + React Frontend)
**Current Version:** 1.0.0

### 📅 December 8, 2025 - Full Frontend Integration
- **UI/UX:** Built a modern, dark-themed React Dashboard (`src/pages/ResultPage.jsx`) with animated score gauges and expandable feedback cards.
- **Visuals:** Implemented a new video player overlay with H.264 codec support for browser compatibility.
- **Reporting:** Upgraded PDF generation (`backend/report.py`) to include grading (A/B/C) and specific "Coach's Notes."

### 📅 December 4, 2025 - Backend API Finalization
- **FastAPI:** Completed the transition from scripts to a persistent server (`backend/main.py`).
- **Database:** Integrated SQLite to store analysis history.
- **Pipeline:** Validated the Dual-Stream Inference architecture (Raw Frame for Model, Cropped for Visuals) which restored accuracy to 78%.

### 📅 November 30, 2025 - The "Grand Cleanup"
- **Architecture Audit:** Performed deep file hash analysis on 5.9GB of project data.
- **Optimization:** Archived deprecated V7 and V8 (Early) models to external backup.
- **Standardization:** - Renamed `unprofvids` to `data/raw_test_clips` for professional consistency.
    - Consolidated `yolov8n.pt` model weights to a single source of truth in `backend/models/`.
- **Validation:** Confirmed `V8p` model series as the production candidate.

### 📅 November 25, 2025 - The "V8p" Breakthrough
- **Model Training:** Successfully trained `shot_model_V8p_best.keras`.
- **Metrics:** Achieved highest validation accuracy to date.
- **Inference Pipeline:** Finalized `backend/inference.py` using the new V8p feature extractor.

### 📅 November 22, 2025 - Feature Engineering V8
- **Data Balance:** Addressed class imbalance in the dataset.
- **Refactoring:** Rewrote feature extraction logic to be more modular.

### 📅 November 18, 2025 - Data Sourcing
- **Data:** Extracted 1,750 videos from Hugging Face cache.
- **Pipeline:** Built "Feature Factory" pipeline to batch process 1,750 videos.

### 📅 November 11, 2025 - Project Inception
- Initial environment setup.
- Integration of MediaPipe Pose Estimation.
- First successful skeleton overlay test.
