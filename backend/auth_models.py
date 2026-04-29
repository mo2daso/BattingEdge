import sqlite3
import uuid
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("AuthModels")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shot_analysis.db"


def init_users_table() -> None:
    """
    Create users table if it doesn't exist, then run schema migration
    to add any columns that were added after the initial table creation.
    Never drops or recreates the table.
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT,
                is_active INTEGER DEFAULT 1,
                is_verified INTEGER DEFAULT 0,
                google_id TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()

        # Schema migration: safely add columns that may not exist in older DBs
        existing = {row[1] for row in cursor.execute("PRAGMA table_info(users)")}
        migrations = {
            "is_verified": "ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0",
            "google_id":   "ALTER TABLE users ADD COLUMN google_id TEXT",
        }
        for col, sql in migrations.items():
            if col not in existing:
                cursor.execute(sql)
                conn.commit()
                logger.info(f"✅ Migrated users table: added column '{col}'")

        logger.info("✅ Users table ready")
    except Exception as e:
        logger.error(f"❌ init_users_table failed: {e}")
        raise
    finally:
        conn.close()


def create_user(email: str, name: str, password_hash: str = None, google_id: str = None) -> str:
    """
    Insert a new user. Email is normalised (strip + lowercase) before insert.
    Raises ValueError if email already registered.
    Returns the new user_id.
    """
    email = email.strip().lower()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        user_id = str(uuid.uuid4())
        # Store empty string for Google users if DB has NOT NULL constraint on password_hash
        safe_pw_hash = password_hash if password_hash is not None else ''
        cursor.execute(
            '''INSERT INTO users (user_id, email, name, password_hash, google_id, is_verified, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                user_id,
                email,
                name.strip(),
                safe_pw_hash,
                google_id,
                0,
                datetime.utcnow().isoformat(),
            )
        )
        conn.commit()
        logger.info(f"[auth] User created: {email}")
        return user_id
    except sqlite3.IntegrityError:
        raise ValueError("Email already registered")
    except Exception as e:
        logger.error(f"[auth] create_user failed: {e}")
        raise
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Email normalised before query. Returns dict or None."""
    email = email.strip().lower()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"[auth] get_user_by_email failed: {e}")
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    """Returns dict or None."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE user_id = ? AND is_active = 1', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"[auth] get_user_by_id failed: {e}")
        return None
    finally:
        conn.close()


def get_user_by_google_id(google_id: str) -> dict | None:
    """Returns dict or None."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE google_id = ? AND is_active = 1', (google_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"[auth] get_user_by_google_id failed: {e}")
        return None
    finally:
        conn.close()


def update_password(user_id: str, new_hashed_password: str) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE user_id = ?',
            (new_hashed_password, user_id)
        )
        conn.commit()
        logger.info(f"[auth] Password updated for user {user_id}")
    except Exception as e:
        logger.error(f"[auth] update_password failed: {e}")
        raise
    finally:
        conn.close()


def update_email(user_id: str, new_email: str) -> None:
    """
    Update user email. Email is normalised before update.
    Raises ValueError if the new email is already taken.
    """
    new_email = new_email.strip().lower()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE users SET email = ? WHERE user_id = ?',
            (new_email, user_id)
        )
        conn.commit()
        logger.info(f"[auth] Email updated for user {user_id}")
    except sqlite3.IntegrityError:
        raise ValueError("Email already in use")
    except Exception as e:
        logger.error(f"[auth] update_email failed: {e}")
        raise
    finally:
        conn.close()


def set_verified(user_id: str) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        logger.info(f"[auth] User verified: {user_id}")
    except Exception as e:
        logger.error(f"[auth] set_verified failed: {e}")
    finally:
        conn.close()


def set_unverified(user_id: str) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET is_verified = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"[auth] set_unverified failed: {e}")
    finally:
        conn.close()


def set_google_id(user_id: str, google_id: str) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET google_id = ? WHERE user_id = ?', (google_id, user_id))
        conn.commit()
    except Exception as e:
        logger.error(f"[auth] set_google_id failed: {e}")
    finally:
        conn.close()
