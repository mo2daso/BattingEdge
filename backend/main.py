import os
import sys
import uuid
import copy
import logging
import ipaddress
import time
from collections import defaultdict
from pathlib import Path
import aiofiles
import uvicorn
from dotenv import load_dotenv
from jose import JWTError, jwt as _jwt
from pydantic import BaseModel as _BaseModel

load_dotenv(Path(__file__).resolve().parent / '.env')

# Fix Imports (YOUR LOGIC - UNCHANGED)
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from inference_v9_5 import StackingEnsembleClassifier
    import database as db
    import report as rpt
    import auth_models
    from auth_router  import router as auth_router
    from groq_router  import router as groq_router
    from groq_vision  import analyze_with_groq_vision, merge_results as groq_merge
    from video_checks import check_motion, check_pose_completeness, auto_detect_trim
    import auth_utils as _auth_utils
except ImportError:
    from backend.inference_v9_5 import StackingEnsembleClassifier
    import backend.database as db
    import backend.report as rpt
    import backend.auth_models as auth_models
    from backend.auth_router  import router as auth_router
    from backend.groq_router  import router as groq_router
    from backend.groq_vision  import analyze_with_groq_vision, merge_results as groq_merge
    from backend.video_checks import check_motion, check_pose_completeness, auto_detect_trim
    import backend.auth_utils as _auth_utils

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
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
    version="V9.5 Stable",
    description="Professional Cricket Shot Analysis - Stacking Ensemble V9.5 (94.71% accuracy)"
)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(groq_router, tags=["AI / Groq"])

_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]

def _is_allowed_origin(origin: str | None) -> bool:
    """Allow localhost and private LAN origins only."""
    if not origin:
        return True
    for prefix in ("http://localhost", "https://localhost",
                   "http://127.0.0.1", "https://127.0.0.1"):
        if origin.startswith(prefix):
            return True
    try:
        host = origin.split("://", 1)[1].split(":")[0]
        ip = ipaddress.ip_address(host)
        return any(ip in net for net in _PRIVATE_NETS)
    except Exception:
        return False

# Upload rate limiter: 10 uploads per minute per IP
_upload_log: dict[str, list] = defaultdict(list)
_RATE_LIMIT, _RATE_WINDOW = 10, 60

def _check_rate(ip: str) -> bool:
    now = time.time()
    _upload_log[ip] = [t for t in _upload_log[ip] if now - t < _RATE_WINDOW]
    if len(_upload_log[ip]) >= _RATE_LIMIT:
        return False
    _upload_log[ip].append(now)
    return True

# Video magic-byte signatures
_VIDEO_MAGIC: list[tuple[int, bytes]] = [
    (0,  b'RIFF'),              # AVI
    (0,  b'\x1a\x45\xdf\xa3'), # WebM / MKV
    (4,  b'ftyp'),              # MP4 / MOV / M4V
    (0,  b'\x00\x00\x00'),     # Some MP4 variants
]

def _looks_like_video(header: bytes) -> bool:
    if len(header) < 12:
        return True  # too short to validate — allow and let inference handle it
    for offset, sig in _VIDEO_MAGIC:
        if header[offset:offset + len(sig)] == sig:
            return True
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # actual check done in _is_allowed_origin per-request
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    logger.info("=" * 60)
    logger.info("BattingEdge V9.5 Server Starting...")
    logger.info("=" * 60)

    db.init_db()
    logger.info("Database initialized")
    auth_models.init_users_table()
    logger.info("Users table initialized")
    db.init_history_table()
    logger.info("User history table initialized")

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
    logger.info("✅ Server Ready — V9.5 Stable | Listening on http://0.0.0.0:8000")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """UNCHANGED"""
    logger.info("🛑 Server shutting down...")

# ================= BACKGROUND TASK (UNCHANGED) =================
def process_video_task(video_id: str, input_path: Path):
    """Processing pipeline with 4-step progress tracking"""
    logger.info(f"{'=' * 60}")
    logger.info(f"[api/analyze] ⏳ PROCESSING START: {video_id}")
    logger.info(f"[api/analyze]    File: {input_path.name}")
    logger.info(f"{'=' * 60}")

    try:
        # Retrieve trim window set at upload time
        _meta = db.get_analysis(video_id) or {}
        _start_time = _meta.get('start_time')
        _end_time   = _meta.get('end_time')

        # ── Pre-inference checks ──────────────────────────────────────────────

        # Feature 5: Auto-trim — detect active shot window when user didn't trim
        if _start_time is None and _end_time is None:
            _auto_s, _auto_e = auto_detect_trim(str(input_path))
            if _auto_s is not None:
                _start_time, _end_time = _auto_s, _auto_e
                logger.info(f"[api/analyze]    ✂️ Auto-trim: {_start_time:.1f}s → {_end_time:.1f}s")

        # Feature 3: Motion check — reject standing-still / non-action videos
        _has_motion, _motion_warning = check_motion(str(input_path), _start_time, _end_time)
        if not _has_motion:
            logger.warning(f"[api/analyze]    ⚠️ Motion check failed: {_motion_warning}")
            db.update_progress(video_id, 0, status="failed")
            db.update_status(video_id, "failed", _motion_warning)
            return

        # Step 1: Pose extraction / inference (progress 10 → 60)
        db.update_progress(video_id, 10, status="processing")
        logger.info(f"[api/analyze] Step 1/4: Running inference...")
        result = classifier.predict_video(str(input_path), start_time=_start_time, end_time=_end_time)
        result['filename'] = input_path.name

        if 'error' in result:
            error_msg = result.get('error', 'Unknown inference error')
            logger.error(f"[api/analyze] ❌ Inference FAILED: {error_msg}")
            db.update_progress(video_id, 0, status="failed")
            db.update_status(video_id, "failed", error_msg)
            return

        db.update_progress(video_id, 60)
        logger.info(f"[api/analyze]    ✅ Prediction: {result['prediction']}")
        logger.info(f"[api/analyze]    ✅ Confidence: {float(result.get('confidence', 0)):.1f}%")
        logger.info(f"[api/analyze]    ✅ Score: {result['form_analysis']['overall_score']}/100")

        # Feature 2: Pose completeness — warn if body landmarks < 50 % visible
        _, _pose_warning = check_pose_completeness(str(input_path), _start_time, _end_time)
        if _pose_warning:
            _fa = result.get('form_analysis', {})
            if not _fa.get('body_warning'):   # don't overwrite Groq's check later
                _fa['body_warning'] = _pose_warning
            result['form_analysis'] = _fa
            logger.info(f"[api/analyze]    ⚠️ Pose completeness: {_pose_warning}")

        # Step 1b: Groq Vision enhancement (sync, 14 s timeout via SDK client)
        try:
            _groq_result = analyze_with_groq_vision(
                str(input_path),
                result.get('prediction'),
                result.get('confidence'),
                start_time=_start_time,
                end_time=_end_time,
            )
            result = groq_merge(result, _groq_result)

            if result.get('error') and result.get('cricket_shot_detected') is False:
                logger.warning(f"[api/analyze]    ⚠️ Groq: {result['error']}")
                db.update_progress(video_id, 0, status="failed")
                db.update_status(video_id, "failed", result['error'])
                return

            logger.info(
                f"[api/analyze]    ✅ Groq Vision: "
                f"ai_verified={result.get('form_analysis', {}).get('ai_verified')}, "
                f"enhanced_score={result.get('form_analysis', {}).get('overall_score')}"
            )
        except Exception as _groq_exc:
            logger.warning(f"[api/analyze]    ⚠️ Groq Vision failed (using ML result): {_groq_exc}")

        # Step 2: Overlay generation (progress 60 → 85)
        db.update_progress(video_id, 60)
        logger.info(f"[api/analyze] Step 2/4: Creating overlay video...")
        output_filename = f"{video_id}_overlay.mp4"
        output_path = OUTPUT_DIR / output_filename

        try:
            overlay_result = copy.deepcopy(result)
            for chk in overlay_result.get('form_analysis', {}).get('checks', []):
                for field in ('value', 'ideal_range'):
                    if isinstance(chk.get(field), str):
                        chk[field] = chk[field].replace('°', 'deg')
            success = classifier.create_overlay(str(input_path), str(output_path), overlay_result)
            if success:
                logger.info(f"[api/analyze]    ✅ Overlay created: {output_filename}")
            else:
                logger.warning(f"[api/analyze]    ⚠️ Overlay generation returned False")
                output_path = None
        except Exception as e:
            logger.warning(f"[api/analyze]    ⚠️ Overlay error (non-critical): {e}")
            output_path = None

        db.update_progress(video_id, 85)

        # Step 3: PDF report (progress 85 → 95)
        logger.info(f"[api/analyze] Step 3/4: Generating PDF report...")
        pdf_filename = f"{video_id}_report.pdf"
        pdf_path = OUTPUT_DIR / pdf_filename

        try:
            rpt.generate_pdf(result, pdf_path)
            logger.info(f"[api/analyze]    ✅ PDF created: {pdf_filename}")
        except Exception as e:
            logger.warning(f"[api/analyze]    ⚠️ PDF error (non-critical): {e}")

        db.update_progress(video_id, 95)

        # Step 4: Persist to DB (progress 95 → 100)
        logger.info(f"[api/analyze] Step 4/4: Saving results to database...")
        db.update_analysis_result(video_id, result, output_path)
        db.update_progress(video_id, 100, status="completed")

        logger.info(f"{'=' * 60}")
        logger.info(f"[api/analyze] ✅ PROCESSING COMPLETE: {video_id}")
        logger.info(f"{'=' * 60}")

    except Exception as e:
        logger.error(f"[api/analyze] ❌ CRITICAL ERROR: {str(e)}", exc_info=True)
        db.update_status(video_id, "failed", str(e))
        logger.info(f"{'=' * 60}")

# ================= ENDPOINTS (UNCHANGED) =================

@app.get("/")
async def root():
    """YOUR ROOT ENDPOINT - UNCHANGED"""
    return {
        "name": "BattingEdge API",
        "version": "V9.5 Stable",
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
        "version": "V9.5 Stable",
        "model_loaded": classifier is not None,
        "model_type": "Stacking Ensemble V9.5 (BiLSTM+XGBoost+RF)" if classifier and classifier.is_ensemble else "BiLSTM Only",
        "accuracy": "94.71%" if classifier and classifier.is_ensemble else "~85%",
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }

@app.get("/api/latest-result")
async def latest_result(after: str = "1970-01-01T00:00:00"):
    """Laptop polls this to auto-detect when a mobile analysis finishes."""
    result = db.get_latest_completed_after(after)
    if result:
        return result
    return {"video_id": None}

@app.get("/api/server-info")
async def server_info(request: Request):
    """Returns LAN IP so mobile QR code can connect to backend."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = str(request.base_url.hostname) or "127.0.0.1"
    return {"lan_ip": lan_ip, "api_port": 8000, "frontend_port": 5173}

@app.post("/api/upload")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    start_time: float = Form(default=None),
    end_time:   float = Form(default=None),
):
    """Upload endpoint with rate limiting and file validation."""
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate(client_ip):
        raise HTTPException(status_code=429, detail="Too many uploads. Please wait a moment.")

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

            if not _looks_like_video(content[:16]):
                logger.warning(f"Upload rejected: File does not appear to be a video ({client_ip})")
                raise HTTPException(status_code=400, detail="File does not appear to be a valid video.")

            await out_file.write(content)
        
        db.save_initial_upload(video_id, file.filename, file_path, start_time=start_time, end_time=end_time)

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
    """
    Returns structured polling response:
      processing → {status, progress}
      completed  → {status, progress, result}
      failed     → {status, error}
    """
    record = db.get_analysis(video_id)

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    status = record.get('status', 'unknown')
    progress = record.get('progress', 0)

    if status == 'completed':
        logger.debug(f"[api/result] Status: completed for {video_id}")
        return {
            "status": "completed",
            "progress": 100,
            "result": record
        }

    if status == 'failed':
        logger.debug(f"[api/result] Status: failed for {video_id}")
        return {
            "status": "failed",
            "progress": 0,
            "error": record.get('error_message', 'Processing failed')
        }

    logger.debug(f"[api/result] Status: {status} (progress={progress}) for {video_id}")
    return {
        "status": status,
        "progress": progress
    }

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

# ================= USER HISTORY ENDPOINTS =================

from fastapi import Header

class HistorySaveRequest(_BaseModel):
    video_id: str
    shot_type: str
    score: int
    grade: str

def _get_user_id_from_token(authorization: str = None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = _jwt.decode(token, _auth_utils.SECRET_KEY, algorithms=[_auth_utils.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

@app.post("/api/user/history")
async def save_history(body: HistorySaveRequest, authorization: str = Header(default=None)):
    user_id = _get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    ok = db.save_user_history(user_id, body.video_id, body.shot_type, body.score, body.grade)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to save history")
    return {"message": "History saved"}

@app.get("/api/user/history")
async def get_history(authorization: str = Header(default=None)):
    user_id = _get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    entries = db.get_user_history(user_id)
    return {"history": entries}

# ================= ERROR HANDLERS =================

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