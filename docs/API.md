---

### **3. `docs/API.md` (Backend Documentation)**

```markdown
# 🔌 BattingEdge API Documentation
**Base URL:** `http://localhost:8000`

## 1. System Health
### `GET /api/health`
Checks if the Model and Database are loaded.
* **Response:** `200 OK`
    ```json
    { "status": "healthy", "model_loaded": true, "database": "connected" }
    ```

## 2. Video Processing Pipeline

### Step 1: Upload
### `POST /api/upload`
Uploads a raw video file for processing.
* **Body:** `multipart/form-data` -> `file: (binary)`
* **Response:**
    ```json
    { "video_id": "c325d3...", "status": "uploaded" }
    ```

### Step 2: Analyze
### `POST /api/analyze/{video_id}`
Triggers the asynchronous AI background task.
* **Response:**
    ```json
    { "video_id": "c325d3...", "status": "processing_started" }
    ```

### Step 3: Get Results
### `GET /api/result/{video_id}`
Polls for the analysis result.
* **Response (Pending):** `{"status": "processing"}`
* **Response (Complete):**
    ```json
    {
      "shot_type": "DRIVE",
      "confidence": 98.5,
      "form_score": 85,
      "form_checks": { ... },
      "status": "completed"
    }
    ```

## 3. Assets

### `GET /api/video/{video_id}/overlay`
Streams the processed video with Skeleton and HUD.
* **Content-Type:** `video/mp4` (H.264 codec)

### `GET /api/report/{video_id}/pdf`
Downloads the professional coaching report.
* **Content-Type:** `application/pdf`