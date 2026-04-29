# BattingEdge Backend — Setup Guide

## 1. Install Python Dependencies

```bash
cd backend
pip install passlib[bcrypt]==1.7.4
pip install "python-jose[cryptography]==3.3.0"
pip install python-dotenv==1.0.0
pip install python-multipart==0.0.6
pip install "google-auth==2.28.0"
```

---

## 2. Generate SECRET_KEY

Run this once and paste the output into `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Gmail App Password (for email verification & password reset)

1. Go to **myaccount.google.com → Security**
2. Enable **2-Step Verification** (required)
3. Search for **"App Passwords"** in the Security search bar
4. Select: **Mail** + **Windows Computer** → Click **Generate**
5. Copy the 16-character password shown (no spaces)
6. Paste into `.env` as `GMAIL_APP_PASSWORD`

> The App Password looks like: `abcd efgh ijkl mnop` — paste without spaces: `abcdefghijklmnop`

---

## 4. Google OAuth Client ID (for "Continue with Google")

1. Go to **console.cloud.google.com**
2. Create a new project: **BattingEdge**
3. Go to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorised JavaScript origins:
   - `http://localhost:5173`
7. Authorised redirect URIs: *(leave empty for implicit flow)*
8. Click **Create**
9. Copy the **Client ID** ending in `.apps.googleusercontent.com`
10. Paste into `.env` as `GOOGLE_CLIENT_ID`
11. Paste the same value into `frontend/.env.local` as `VITE_GOOGLE_CLIENT_ID`

---

## 5. Frontend .env.local

Create `frontend/.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
```

---

## 6. Start the Server

```bash
cd backend
uvicorn main:app --reload
```

Confirm the startup log shows:
```
✅ Database initialized
✅ Users table initialized
✅ Model loaded: Stacking Ensemble (BiLSTM+XGBoost+RF)
✅ Server Ready — V9.5 Stable
```

---

## 7. Run Auth Tests

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@battingedge.com","password":"Test1234!","full_name":"Test Player"}'

# Login (expects 403 until verified)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@battingedge.com","password":"Test1234!"}'

# Manually verify (for testing only)
# Run in Python:
# import sqlite3
# conn = sqlite3.connect('backend/shot_analysis.db')
# conn.execute("UPDATE users SET is_verified=1 WHERE email='test@battingedge.com'")
# conn.commit(); conn.close()

# Login again (expects 200 with access_token)
# Get current user
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
