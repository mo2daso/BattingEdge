import os
import sys
import uuid
import logging
from pathlib import Path
import aiofiles
import uvicorn

# Fix Imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from inference import CricketShotClassifier
    import database as db
    import report as rpt  # <--- IMPORTING PDF MODULE
except ImportError:
    from backend.inference import CricketShotClassifier
    import backend.database as db
    import backend.report as rpt

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Config
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
MAX_FILE_SIZE = 100 * 1024 * 1024 
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(title="BattingEdge API", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    logger.info("🚀 Starting BattingEdge Server...")
    db.init_db()
    try:
        classifier = CricketShotClassifier()
        logger.info("✅ Model loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")

# ================= BACKGROUND TASKS =================
def process_video_task(video_id: str, input_path: Path):
    try:
        logger.info(f"⏳ Processing started for {video_id}")
        db.update_status(video_id, "processing")
        
        # 1. Run Inference
        result = classifier.predict_video(str(input_path))
        
        if not result or "error" in result:
            err_msg = result.get('error', 'Unknown Inference Error')
            logger.error(f"❌ Inference failed: {err_msg}")
            db.update_status(video_id, "failed", err_msg)
            return

        # 2. Generate Overlay Video
        output_filename = f"{video_id}_overlay.mp4"
        output_path = OUTPUT_DIR / output_filename
        classifier.create_overlay(str(input_path), str(output_path), result)
        
        # 3. Generate PDF Report (THIS WAS MISSING BEFORE)
        pdf_filename = f"{video_id}_report.pdf"
        pdf_path = OUTPUT_DIR / pdf_filename
        
        # Ensure result has filename
        result['filename'] = input_path.name
        rpt.generate_pdf(result, pdf_path)  # <--- CALLING REPORT.PY
        
        # 4. Save Results to DB
        db.update_analysis_result(video_id, result, output_path)
        logger.info(f"✅ Processing complete for {video_id} (Video + PDF)") # <--- NEW LOG MESSAGE
        
    except Exception as e:
        logger.error(f"❌ Critical Task Error: {e}")
        db.update_status(video_id, "failed", str(e))

# ================= ENDPOINTS =================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model_loaded": classifier is not None}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    video_id = str(uuid.uuid4())
    filename = f"{video_id}{ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File too large")
            await out_file.write(content)
            
        db.save_initial_upload(video_id, file.filename, file_path)
        return {"video_id": video_id, "status": "uploaded"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/{video_id}")
async def analyze_video(video_id: str, background_tasks: BackgroundTasks):
    record = db.get_analysis(video_id)
    if not record: raise HTTPException(status_code=404, detail="Video ID not found")
    input_path = Path(record['original_path'])
    background_tasks.add_task(process_video_task, video_id, input_path)
    return {"video_id": video_id, "status": "processing_started"}

@app.get("/api/result/{video_id}")
async def get_result(video_id: str):
    record = db.get_analysis(video_id)
    if not record: raise HTTPException(status_code=404, detail="Analysis not found")
    return record

@app.get("/api/video/{video_id}/overlay")
async def get_overlay_video(video_id: str):
    record = db.get_analysis(video_id)
    if not record or not record['overlay_path']:
        raise HTTPException(status_code=404, detail="Overlay not ready")
    video_path = Path(record['overlay_path'])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="File deleted")
    return FileResponse(video_path, media_type="video/mp4")

# --- PDF DOWNLOAD ENDPOINT ---
@app.get("/api/report/{video_id}/pdf")
async def get_pdf_report(video_id: str):
    pdf_path = OUTPUT_DIR / f"{video_id}_report.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found. Processing might be incomplete.")
        
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"BattingEdge_Report_{video_id}.pdf")

@app.delete("/api/video/{video_id}")
async def delete_entry(video_id: str):
    record = db.get_analysis(video_id)
    if record:
        try:
            if record['original_path']: os.remove(record['original_path'])
            if record['overlay_path']: os.remove(record['overlay_path'])
            pdf_path = OUTPUT_DIR / f"{video_id}_report.pdf"
            if pdf_path.exists(): os.remove(pdf_path)
        except: pass
        db.delete_analysis(video_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)