import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("Database")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shot_analysis.db"

def init_db():
    """Initialize database with proper schema (UNCHANGED)"""
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
    """Save initial upload record (UNCHANGED)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO analyses (video_id, filename, original_path, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            video_id,
            filename,
            str(filepath),
            "uploaded",
            datetime.now().isoformat()
        ))
        
        conn.commit()
        logger.info(f"✅ Saved upload: {video_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save upload: {e}")
        raise
    finally:
        conn.close()

def update_analysis_result(video_id: str, result_data: dict, overlay_path: Path):
    """
    Update analysis results in database
    UPDATED: Handles new form_analysis structure with performance_level
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Extract data (YOUR LOGIC - MOSTLY UNCHANGED)
        shot_type = result_data.get('prediction', 'unknown')
        confidence = float(result_data.get('confidence', 0.0))
        all_probs = result_data.get('all_probabilities', {})
        
        # Get form analysis (FLAT structure from inference.py)
        form_data = result_data.get('form_analysis', {})
        
        # Safety check for nested structure (YOUR LOGIC - UNCHANGED)
        if 'form_analysis' in form_data:
            logger.warning("⚠️ Nested form_analysis detected - fixing...")
            form_data = form_data['form_analysis']
        
        form_score = int(form_data.get('overall_score', 0))
        
        # Serialize for storage (UNCHANGED)
        checks_json = json.dumps(form_data, ensure_ascii=False)
        probs_json = json.dumps(all_probs, ensure_ascii=False)
        
        # Update database (UNCHANGED)
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
        logger.info(f"✅ Updated analysis: {video_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update analysis: {e}")
        raise
    finally:
        conn.close()

def update_status(video_id: str, status: str, error_msg: str = None):
    """Update processing status (UNCHANGED)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE analyses 
            SET status = ?, error_message = ?
            WHERE video_id = ?
        ''', (status, error_msg, video_id))
        
        conn.commit()
        logger.info(f"✅ Status updated: {video_id} → {status}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update status: {e}")
    finally:
        conn.close()

def get_analysis(video_id: str) -> dict:
    """
    Retrieve analysis from database
    UPDATED: Returns new structure with performance_level
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM analyses WHERE video_id = ?', (video_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        data = dict(row)
        
        # Deserialize JSON fields (YOUR LOGIC - UNCHANGED)
        if data.get('all_probabilities'):
            try:
                data['all_probabilities'] = json.loads(data['all_probabilities'])
            except Exception as e:
                logger.warning(f"Failed to parse probabilities: {e}")
                data['all_probabilities'] = {}
        
        if data.get('form_checks'):
            try:
                # Parse and return as 'form_analysis' (frontend expects this key)
                form_data = json.loads(data['form_checks'])
                
                # Ensure no double nesting (YOUR LOGIC - UNCHANGED)
                if 'form_analysis' in form_data:
                    form_data = form_data['form_analysis']
                
                data['form_analysis'] = form_data
                
            except Exception as e:
                logger.warning(f"Failed to parse form_checks: {e}")
                data['form_analysis'] = {
                    'overall_score': 0,
                    'performance_level': 'N/A',
                    'grade': 'F',
                    'checks': [],
                    'summary': 'Failed to load analysis',
                    'key_improvements': [],
                    'strengths': [],
                    'recommended_drills': []
                }
        
        # ===== UPDATED: Add backward compatibility =====
        # Frontend might look for 'prediction' instead of 'shot_type'
        if 'shot_type' in data:
            data['prediction'] = data['shot_type']
        
        # Ensure confidence is present
        if 'confidence' not in data:
            data['confidence'] = 0.0
        
        return data
        
    except Exception as e:
        logger.error(f"❌ Failed to get analysis: {e}")
        return None
    finally:
        conn.close()

def delete_analysis(video_id: str):
    """Delete analysis from database (UNCHANGED)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM analyses WHERE video_id = ?', (video_id,))
        conn.commit()
        logger.info(f"✅ Deleted analysis: {video_id}")
    except Exception as e:
        logger.error(f"❌ Failed to delete analysis: {e}")
    finally:
        conn.close()

def get_db():
    """Dependency for FastAPI (if needed) - UNCHANGED"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()