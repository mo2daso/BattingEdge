"""
SQLite Database Module for BattingEdge
Simple, lightweight, no ORM needed
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("Database")

# Database path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shot_analysis.db"

def init_db():
    """Initialize SQLite database with analyses table"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                video_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                shot_type TEXT,
                confidence REAL,
                form_score INTEGER,
                all_probabilities TEXT,
                form_checks TEXT,
                original_path TEXT,
                overlay_path TEXT,
                status TEXT DEFAULT 'uploaded',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {DB_PATH}")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        raise

def save_initial_upload(video_id: str, filename: str, filepath: Path):
    """Save initial upload record"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analyses (video_id, filename, original_path, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (video_id, filename, str(filepath), "uploaded", datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def update_analysis_result(video_id: str, result_data: dict, overlay_path: Path):
    """Update analysis with inference results"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Extract data
    shot_type = result_data.get('prediction', 'unknown')
    confidence = float(result_data.get('confidence', 0.0))
    
    form_analysis = result_data.get('form_analysis', {})
    form_score = int(form_analysis.get('overall_score', 0))
    
    all_probs = result_data.get('all_probabilities', {})
    
    # --- CRITICAL FIX START ---
    # Previously: form_checks = form_analysis.get('checks', []) 
    # Now: We save the WHOLE form_analysis dict (checks + summary + improvements)
    # This allows the frontend to extract 'summary' and 'key_improvements'
    checks_json = json.dumps(form_analysis) 
    # --- CRITICAL FIX END ---

    probs_json = json.dumps(all_probs)
    
    cursor.execute('''
        UPDATE analyses 
        SET shot_type = ?,
            confidence = ?,
            form_score = ?,
            all_probabilities = ?,
            form_checks = ?,
            overlay_path = ?,
            status = ?
        WHERE video_id = ?
    ''', (
        shot_type,
        confidence,
        form_score,
        probs_json,
        checks_json,
        str(overlay_path),
        'completed',
        video_id
    ))
    
    conn.commit()
    conn.close()

def update_status(video_id: str, status: str, error_msg: str = None):
    """Update status of analysis"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE analyses 
        SET status = ?, error_message = ?
        WHERE video_id = ?
    ''', (status, error_msg, video_id))
    
    conn.commit()
    conn.close()

def get_analysis(video_id: str) -> dict:
    """Get analysis record by video_id"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM analyses WHERE video_id = ?', (video_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Convert to dict
    data = dict(row)
    
    # Parse JSON fields
    if data.get('all_probabilities'):
        try:
            data['all_probabilities'] = json.loads(data['all_probabilities'])
        except:
            data['all_probabilities'] = {}
    
    if data.get('form_checks'):
        try:
            data['form_checks'] = json.loads(data['form_checks'])
        except:
            # Fallback if empty
            data['form_checks'] = {"checks": [], "summary": "Error loading data"}
    
    return data

def delete_analysis(video_id: str):
    """Delete analysis record"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM analyses WHERE video_id = ?', (video_id,))
    
    conn.commit()
    conn.close()

def get_db():
    """Dependency for FastAPI"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()