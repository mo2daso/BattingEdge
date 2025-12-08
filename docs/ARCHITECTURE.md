# 🏗️ BattingEdge System Architecture

**Version:** 1.0 (V8p Production)
**Date:** December 2025

## 1. High-Level Design
BattingEdge employs a **Monolithic Client-Server Architecture** decoupled via REST APIs. The system is designed to process high-frame-rate sports video asynchronously to ensure a responsive user experience.

### System Context Diagram
```mermaid
graph TD
    User[User / Player] <-->|HTTPS| Frontend[React Single Page App]
    Frontend <-->|JSON/Multipart| Backend[FastAPI Backend Server]
    
    subgraph "Backend Core"
        Backend -->|Async Task| Pipeline[Inference Pipeline]
        Pipeline -->|Read/Write| DB[(SQLite Database)]
        Pipeline -->|Read/Write| FS[File System (Uploads/Outputs)]
        
        subgraph "AI Engine"
            Pipeline --> YOLO[YOLOv8 (Person Detection)]
            Pipeline --> MP[MediaPipe (Pose Extraction)]
            Pipeline --> LSTM[Bi-LSTM V8p (Classification)]
            Pipeline --> Bio[Biomechanics Analyzer (Rule-Based)]
        end
    end
2. Core Components
A. Frontend (Presentation Layer)
Framework: React 18 + Vite

Styling: Tailwind CSS (Dark Mode/Light Mode capable)

Responsibility:

Handles video file selection and validation.

Polls the backend for analysis status.

Renders the processed video stream (H.264).

Visualizes complex data (Confidence Bars, Form Score Gauge) using Framer Motion.

B. Backend (Application Layer)
Framework: FastAPI (Python 3.11)

Server: Uvicorn (ASGI)

Concurrency: Uses BackgroundTasks to offload heavy AI inference from the main request thread, preventing timeouts during large video uploads.

Responsibility:

Validates API requests.

Orchestrates the AI pipeline.

Manages database transactions.

Generates PDF reports via ReportLab.

C. The AI Engine (The Logic Core)
This is the unique intellectual property of the project. It utilizes a Dual-Stream Processing Strategy to maximize both accuracy and visual clarity.

1. Stream A: The Logic Stream (For Model)
Input: Raw Full-Frame Video.

Process: * MediaPipe Pose runs on the full uncropped frame.

This preserves Absolute Coordinate Integrity.

Data is normalized using a StandardScaler fitted on the V8p training set.

Model: shot_model_V8p_best.keras (Bidirectional LSTM).

Input Shape: (50, 103) -> 50 frames, 103 features (99 skeletal + 4 kinematic).

Output: Softmax probability across 4 classes (Drive, Pull, Cut, Sweep).

2. Stream B: The Visual Stream (For User)
Input: Frame + YOLOv8 Detection.

Process:

YOLO scans for the "Tallest Person" (Heuristic to ignore crouching wicketkeepers).

A dynamic bounding box locks onto the batsman.

Output: The visual overlay (Skeleton + HUD) is drawn relative to this focused view, providing a zoomed-in, "Broadcast-Style" replay.

D. Data Persistence (Data Layer)
Database: SQLite (shot_analysis.db)

Schema: analyses table.

Storage Strategy:

Metadata: Stored in DB (Shot type, Confidence %, Form Score, JSON Logs).

Blob Data: Video files are stored in the filesystem (backend/uploads/, backend/outputs/) to keep the DB lightweight.

3. Data Flow Scenario: "Analyze Video"
Upload: User POSTs a video to /api/upload. Server saves raw file to disk and creates a DB entry with status uploaded.

Trigger: User POSTs to /api/analyze/{id}. Server initiates BackgroundTasks and immediately returns 200 OK.

Inference (Background):

Frame extraction & normalization.

Biomechanical Check: Logic engine measures angles (e.g., Elbow > 120°) against the "Textbook Criteria."

Scoring: Deductive algorithm calculates Form Score (100 - penalties).

Overlay Generation: OpenCV renders the skeleton and HUD frame-by-frame using the avc1 codec.

Completion: DB record is updated to completed.

Retrieval: Frontend polls /api/result/{id}, detects completion, and fetches the JSON results and Video stream.

4. Key Design Decisions
Why SQLite over PostgreSQL?
Zero Configuration: No external server process required.

Portability: The entire database is a single file, making the project easy to submit or move between demo machines.

Why Bi-LSTM over CNN?
Temporal Dynamics: Cricket shots are defined by motion over time, not static poses. LSTM captures the sequence (Backlift -> Impact -> Follow-through) better than frame-by-frame CNNs.

Lightweight: The feature-based approach (103 floats per frame) is computationally cheaper than processing raw pixel grids.

Why Dual-Stream?
Discovery: Early testing showed that cropping the video before pose estimation destroyed the coordinate reliability (Relative vs Absolute position issue), dropping accuracy to <25%.

Solution: Separating the "Mathematical View" (Full Frame) from the "Visual View" (Cropped) restored accuracy to 78% while maintaining a high-quality user experience.