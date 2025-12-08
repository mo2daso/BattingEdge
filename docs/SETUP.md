### **2. `docs/SETUP.md` (Detailed Installation)**

```markdown
# 🛠️ BattingEdge Setup Guide

## 1. Environment Requirements
* **OS:** Windows 10/11 (Project configured for Windows paths)
* **Python:** Version 3.10 or 3.11 (TensorFlow compatibility)
* **Node.js:** Version 16 or higher (React Vite)

## 2. Backend Installation

### Step A: Virtual Environment
If you haven't created one yet:
```bash
python -m venv venv
Activate it:

PowerShell

.\venv\Scripts\activate
Step B: Dependencies
Install the AI and Server libraries:

Bash

pip install -r requirements.txt
Note: This includes TensorFlow, MediaPipe, Ultralytics, FastAPI, and ReportLab.

Step C: Verify Models
Ensure the following files exist in backend/models/:

shot_model_V8p_best.keras

shot_encoder_V8p.pkl

shot_scaler_V8p.pkl

yolov8n.pt (Will auto-download if missing)

3. Frontend Installation
Step A: Install Packages
Navigate to the frontend folder:

Bash

cd frontend
npm install
Step B: Environment Config
The frontend is pre-configured to talk to http://localhost:8000. No .env is required for local dev.

4. Running the System
You need two terminal windows.

Terminal 1 (Backend):

PowerShell

uvicorn backend.main:app --reload
Terminal 2 (Frontend):

PowerShell

npm run dev
Open your browser to the link shown in Terminal 2 (usually http://localhost:5173).