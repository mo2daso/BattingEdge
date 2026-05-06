import sqlite3
import json
import uuid
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
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Schema migration: add progress column if it doesn't exist yet
        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN progress INTEGER DEFAULT 0')
            conn.commit()
            logger.info("✅ Migrated analyses table: added progress column")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Schema migration: add start_time / end_time for video trimmer
        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN start_time REAL')
            conn.commit()
            logger.info("✅ Migrated analyses table: added start_time column")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN end_time REAL')
            conn.commit()
            logger.info("✅ Migrated analyses table: added end_time column")
        except sqlite3.OperationalError:
            pass

        # Schema migration: add delivery context for coaching commentary
        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN bowling_type TEXT')
            conn.commit()
            logger.info("✅ Migrated analyses table: added bowling_type column")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN ball_pitch TEXT')
            conn.commit()
            logger.info("✅ Migrated analyses table: added ball_pitch column")
        except sqlite3.OperationalError:
            pass

        # Schema migration: bowling_context, camera_context, feature_completeness, groq_commentary
        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN bowling_context TEXT DEFAULT 'unknown'")
            conn.commit()
            logger.info("✅ Migrated analyses table: added bowling_context column")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN camera_context TEXT DEFAULT 'unknown'")
            conn.commit()
            logger.info("✅ Migrated analyses table: added camera_context column")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN feature_completeness REAL DEFAULT 1.0')
            conn.commit()
            logger.info("✅ Migrated analyses table: added feature_completeness column")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN groq_commentary TEXT DEFAULT NULL')
            conn.commit()
            logger.info("✅ Migrated analyses table: added groq_commentary column")
        except sqlite3.OperationalError:
            pass

        # NOTE: users table is managed exclusively by auth_models.init_users_table()
        # which runs on startup after init_db(). Do NOT create users table here —
        # the correct schema (nullable password_hash for Google OAuth) lives in auth_models.

        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {DB_PATH}")

    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        raise

def save_initial_upload(video_id: str, filename: str, filepath: Path,
                        start_time: float = None, end_time: float = None,
                        bowling_type: str = None, ball_pitch: str = None,
                        bowling_context: str = None, camera_context: str = None):
    """Save initial upload record with optional trim window and delivery context."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO analyses (video_id, filename, original_path, status, created_at,
                                  start_time, end_time, bowling_type, ball_pitch,
                                  bowling_context, camera_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            filename,
            str(filepath),
            "uploaded",
            datetime.now().isoformat(),
            start_time,
            end_time,
            bowling_type,
            ball_pitch,
            bowling_context,
            camera_context,
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
        confidence = float(result_data.get('confidence') or 0.0)
        all_probs = result_data.get('all_probabilities', {})
        
        # Get form analysis (FLAT structure from inference.py)
        form_data = result_data.get('form_analysis', {})
        
        # Safety check for nested structure (YOUR LOGIC - UNCHANGED)
        if 'form_analysis' in form_data:
            logger.warning("⚠️ Nested form_analysis detected - fixing...")
            form_data = form_data['form_analysis']
        
        form_score = int(form_data.get('overall_score') or 0)

        # New context/quality fields from Task C predict_video() result
        bowling_context      = result_data.get('bowling_context')
        camera_context       = result_data.get('camera_context')
        feature_completeness = result_data.get('feature_completeness')

        # groq_commentary lives inside form_analysis (set by Task C)
        groq_raw = form_data.get('groq_commentary')
        groq_json = json.dumps(groq_raw, ensure_ascii=False) if groq_raw is not None else None

        # Serialize for storage (UNCHANGED)
        checks_json = json.dumps(form_data, ensure_ascii=False)
        probs_json  = json.dumps(all_probs, ensure_ascii=False)

        # Update database
        cursor.execute('''
            UPDATE analyses
            SET shot_type            = ?,
                confidence           = ?,
                form_score           = ?,
                all_probabilities    = ?,
                form_checks          = ?,
                overlay_path         = ?,
                status               = ?,
                bowling_context      = COALESCE(?, bowling_context),
                camera_context       = COALESCE(?, camera_context),
                feature_completeness = COALESCE(?, feature_completeness),
                groq_commentary      = ?
            WHERE video_id = ?
        ''', (
            shot_type,
            confidence,
            form_score,
            probs_json,
            checks_json,
            str(overlay_path) if overlay_path else None,
            'completed',
            bowling_context,
            camera_context,
            feature_completeness,
            groq_json,
            video_id,
        ))
        
        conn.commit()
        logger.info(f"✅ Updated analysis: {video_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update analysis: {e}")
        raise
    finally:
        conn.close()

def update_progress(video_id: str, progress: int, status: str = None) -> None:
    """Update processing progress (0-100). Optionally update status at the same time."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        if status:
            cursor.execute(
                'UPDATE analyses SET progress = ?, status = ? WHERE video_id = ?',
                (progress, status, video_id)
            )
        else:
            cursor.execute(
                'UPDATE analyses SET progress = ? WHERE video_id = ?',
                (progress, video_id)
            )
        conn.commit()
        logger.debug(f"Progress updated: {video_id} → {progress}%")
    except Exception as e:
        logger.error(f"❌ Failed to update progress: {e}")
    finally:
        conn.close()


def get_latest_completed_after(after_iso: str) -> dict | None:
    """Returns the most recently completed analysis created after a given ISO timestamp."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT video_id, shot_type, form_score, created_at
            FROM analyses
            WHERE status = 'completed' AND created_at > ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (after_iso,))
        row = cursor.fetchone()
        if row:
            return {'video_id': row[0], 'shot_type': row[1], 'form_score': row[2], 'created_at': row[3]}
        return None
    except Exception as e:
        logger.error(f"❌ get_latest_completed_after failed: {e}")
        return None
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


# ==================== USER AUTH ====================

def create_user(email: str, name: str, password_hash: str) -> str | None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        user_id = str(uuid.uuid4())
        cursor.execute(
            'INSERT INTO users (user_id, email, name, password_hash) VALUES (?, ?, ?, ?)',
            (user_id, email.lower().strip(), name.strip(), password_hash),
        )
        conn.commit()
        logger.info(f"✅ User created: {email}")
        return user_id
    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ Email already registered: {email}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to create user: {e}")
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT * FROM users WHERE email = ? AND is_active = 1',
            (email.lower().strip(),),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"❌ Failed to get user by email: {e}")
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT * FROM users WHERE user_id = ? AND is_active = 1',
            (user_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"❌ Failed to get user by id: {e}")
        return None
    finally:
        conn.close()


# ==================== USER HISTORY ====================

def init_history_table():
    """Create user_history table if not exists."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT    NOT NULL,
                video_id   TEXT    NOT NULL,
                shot_type  TEXT,
                score      INTEGER DEFAULT 0,
                grade      TEXT,
                created_at TEXT    DEFAULT (datetime('now')),
                UNIQUE(user_id, video_id)
            )
        """)
        conn.commit()
        conn.close()
        logger.info("✅ user_history table ready")
    except Exception as e:
        logger.error(f"❌ user_history table init failed: {e}")


def save_user_history(user_id: str, video_id: str, shot_type: str, score: int, grade: str) -> bool:
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            """INSERT INTO user_history (user_id, video_id, shot_type, score, grade)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(user_id, video_id) DO UPDATE SET
                 shot_type=excluded.shot_type, score=excluded.score, grade=excluded.grade""",
            (user_id, video_id, shot_type, score, grade),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ save_user_history failed: {e}")
        return False


def get_user_history(user_id: str) -> list:
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT video_id, shot_type, score, grade, created_at
               FROM user_history WHERE user_id=? ORDER BY created_at DESC LIMIT 50""",
            (user_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"❌ get_user_history failed: {e}")
        return []