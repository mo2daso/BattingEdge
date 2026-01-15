import os
import sys
import uuid
import logging
from pathlib import Path
import aiofiles
import uvicorn

# Fix Imports (YOUR LOGIC - UNCHANGED)
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from inference import StackingEnsembleClassifier 
    import database as db
    import report as rpt
except ImportError:
    from backend.inference import StackingEnsembleClassifier
    import backend.database as db
    import backend.report as rpt

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse  # ===== ADDED: JSONResponse =====
from fastapi.middleware.cors import CORSMiddleware

# ================= CONFIGURATION (UNCHANGED) =================
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

ALLOWED_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.webm',
    '.wmv', '.mpeg', '.mpg', '.3gp', '.flv', '.m4v'
}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Logging (UNCHANGED)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "backend" / "api.log")
    ]
)
logger = logging.getLogger("BattingEdgeAPI")

# FastAPI App (UNCHANGED)
app = FastAPI(
    title="BattingEdge API",
    version="9.5",
    description="Professional Cricket Shot Analysis - Stacking Ensemble (95% accuracy)"
)

# CORS (UNCHANGED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

classifier = None

@app.on_event("startup")
async def startup_event():
    """YOUR STARTUP LOGIC - UNCHANGED"""
    global classifier
    logger.info("=" * 60)
    logger.info("🚀 BattingEdge V9.5 Server Starting...")
    logger.info("=" * 60)
    
    db.init_db()
    logger.info("✅ Database initialized")
    
    try:
        classifier = StackingEnsembleClassifier()
        mode = "Stacking Ensemble (BiLSTM+XGBoost+RF)" if classifier.is_ensemble else "BiLSTM Fallback"
        logger.info(f"✅ Model loaded: {mode}")
        logger.info(f"   Accuracy: {'95%' if classifier.is_ensemble else '~85%'}")
    except Exception as e:
        logger.critical(f"❌ Model load FAILED: {e}")
        raise
    
    logger.info(f"📁 Upload directory: {UPLOAD_DIR}")
    logger.info(f"📁 Output directory: {OUTPUT_DIR}")
    logger.info(f"🎬 Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    logger.info("=" * 60)
    logger.info("✅ Server Ready - Listening on http://0.0.0.0:8000")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """UNCHANGED"""
    logger.info("🛑 Server shutting down...")

# ================= BACKGROUND TASK (UNCHANGED) =================
def process_video_task(video_id: str, input_path: Path):
    """YOUR PROCESSING LOGIC - UNCHANGED"""
    logger.info(f"{'=' * 60}")
    logger.info(f"⏳ PROCESSING START: {video_id}")
    logger.info(f"   File: {input_path.name}")
    logger.info(f"{'=' * 60}")
    
    try:
        db.update_status(video_id, "processing")
        
        # Step 1: Inference
        logger.info(f"[{video_id}] Step 1/4: Running inference...")
        result = classifier.predict_video(str(input_path))
        result['filename'] = input_path.name
        
        if 'error' in result:
            error_msg = result.get('error', 'Unknown inference error')
            logger.error(f"[{video_id}] ❌ Inference FAILED: {error_msg}")
            db.update_status(video_id, "failed", error_msg)
            return
        
        logger.info(f"[{video_id}]    ✅ Prediction: {result['prediction']}")
        logger.info(f"[{video_id}]    ✅ Confidence: {result['confidence']:.1f}%")
        logger.info(f"[{video_id}]    ✅ Score: {result['form_analysis']['overall_score']}/100")
        
        # Step 2: Overlay
        logger.info(f"[{video_id}] Step 2/4: Creating overlay video...")
        output_filename = f"{video_id}_overlay.webm"
        output_path = OUTPUT_DIR / output_filename
        
        try:
            success = classifier.create_overlay(str(input_path), str(output_path), result)
            if success:
                logger.info(f"[{video_id}]    ✅ Overlay created: {output_filename}")
            else:
                logger.warning(f"[{video_id}]    ⚠️ Overlay generation returned False")
        except Exception as e:
            logger.warning(f"[{video_id}]    ⚠️ Overlay error (non-critical): {e}")
            output_path = None
        
        # Step 3: PDF
        logger.info(f"[{video_id}] Step 3/4: Generating PDF report...")
        pdf_filename = f"{video_id}_report.pdf"
        pdf_path = OUTPUT_DIR / pdf_filename
        
        try:
            rpt.generate_pdf(result, pdf_path)
            logger.info(f"[{video_id}]    ✅ PDF created: {pdf_filename}")
        except Exception as e:
            logger.warning(f"[{video_id}]    ⚠️ PDF error (non-critical): {e}")
        
        # Step 4: Save
        logger.info(f"[{video_id}] Step 4/4: Saving results to database...")
        db.update_analysis_result(video_id, result, output_path)
        
        logger.info(f"{'=' * 60}")
        logger.info(f"✅ PROCESSING COMPLETE: {video_id}")
        logger.info(f"{'=' * 60}")
        
    except Exception as e:
        logger.error(f"[{video_id}] ❌ CRITICAL ERROR in processing task:")
        logger.error(f"[{video_id}]    {str(e)}", exc_info=True)
        db.update_status(video_id, "failed", str(e))
        logger.info(f"{'=' * 60}")

# ================= ENDPOINTS (UNCHANGED) =================

@app.get("/")
async def root():
    """YOUR ROOT ENDPOINT - UNCHANGED"""
    return {
        "name": "BattingEdge API",
        "version": "9.5",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload",
            "analyze": "/api/analyze/{video_id}",
            "result": "/api/result/{video_id}",
            "overlay": "/api/video/{video_id}/overlay",
            "pdf": "/api/report/{video_id}/pdf"
        }
    }

@app.get("/api/health")
async def health_check():
    """YOUR HEALTH CHECK - UNCHANGED"""
    return {
        "status": "healthy",
        "version": "9.5",
        "model_loaded": classifier is not None,
        "model_type": "Stacking Ensemble (BiLSTM+XGBoost+RF)" if classifier and classifier.is_ensemble else "BiLSTM Only",
        "accuracy": "95%" if classifier and classifier.is_ensemble else "~85%",
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """YOUR UPLOAD LOGIC - UNCHANGED"""
    ext = Path(file.filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Upload rejected: Invalid extension {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    video_id = str(uuid.uuid4())
    filename = f"{video_id}{ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            
            file_size_mb = len(content) / (1024 * 1024)
            if len(content) > MAX_FILE_SIZE:
                logger.warning(f"Upload rejected: File too large ({file_size_mb:.1f}MB)")
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large ({file_size_mb:.1f}MB). Max size: {MAX_FILE_SIZE/(1024*1024):.0f}MB"
                )
            
            await out_file.write(content)
        
        db.save_initial_upload(video_id, file.filename, file_path)
        
        logger.info(f"✅ Upload successful: {video_id} ({file.filename}, {file_size_mb:.1f}MB)")
        
        return {
            "video_id": video_id,
            "status": "uploaded",
            "filename": file.filename,
            "size_mb": round(file_size_mb, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/analyze/{video_id}")
async def analyze_video(video_id: str, background_tasks: BackgroundTasks):
    """YOUR ANALYZE LOGIC - UNCHANGED"""
    record = db.get_analysis(video_id)
    if not record:
        logger.warning(f"Analysis request rejected: Video ID {video_id} not found")
        raise HTTPException(status_code=404, detail="Video ID not found")
    
    input_path = Path(record['original_path'])
    if not input_path.exists():
        logger.error(f"Analysis request rejected: File not found for {video_id}")
        raise HTTPException(status_code=404, detail="Video file not found on server")
    
    if record.get('status') == 'processing':
        logger.info(f"Analysis already in progress for {video_id}")
        return {
            "video_id": video_id,
            "status": "already_processing",
            "message": "Analysis already in progress"
        }
    
    background_tasks.add_task(process_video_task, video_id, input_path)
    logger.info(f"Analysis queued for {video_id}")
    
    return {
        "video_id": video_id,
        "status": "processing_started",
        "message": "Analysis task started in background"
    }

@app.get("/api/result/{video_id}")
async def get_result(video_id: str):
    """YOUR RESULT ENDPOINT - UNCHANGED"""
    record = db.get_analysis(video_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status = record.get('status', 'unknown')
    if status != 'completed':
        logger.debug(f"Status check for {video_id}: {status}")
    
    return record

@app.get("/api/video/{video_id}/overlay")
async def get_overlay_video(video_id: str):
    """YOUR OVERLAY ENDPOINT - UNCHANGED"""
    record = db.get_analysis(video_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Video analysis not found")
    
    if not record.get('overlay_path'):
        raise HTTPException(
            status_code=404, 
            detail="Overlay video not ready yet. Check /api/result/{video_id} for status"
        )
    
    video_path = Path(record['overlay_path'])
    
    if not video_path.exists():
        logger.error(f"Overlay file missing for {video_id}: {video_path}")
        raise HTTPException(status_code=404, detail="Overlay file not found on server")
    
    logger.debug(f"Serving overlay video for {video_id}")
    
    media_type = "video/webm" if video_path.suffix == ".webm" else "video/mp4"
    
    return FileResponse(
        video_path,
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename={video_path.name}",
            "Accept-Ranges": "bytes"
        }
    )

@app.get("/api/report/{video_id}/pdf")
async def get_pdf_report(video_id: str):
    """YOUR PDF ENDPOINT - UNCHANGED"""
    pdf_path = OUTPUT_DIR / f"{video_id}_report.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="PDF report not found. Analysis may still be processing"
        )
    
    logger.debug(f"Serving PDF report for {video_id}")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=BattingEdge_Report_{video_id}.pdf"
        }
    )

# ================= ERROR HANDLERS (FIXED!) =================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    ===== FIXED: Added Request parameter and returns JSONResponse =====
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """
    ===== FIXED: Added Request parameter and returns JSONResponse =====
    """
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again or contact support."
        }
    )

# ================= MAIN (UNCHANGED) =================

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        access_log=True
    )