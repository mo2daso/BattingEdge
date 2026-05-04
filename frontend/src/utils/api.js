import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({ baseURL: BASE });

// Attach JWT to every request
api.interceptors.request.use((cfg) => {
  const tok = localStorage.getItem('be_token');
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`;
  return cfg;
});

// Auto-logout on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('be_token');
      window.dispatchEvent(new Event('be:logout'));
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authRegister     = (d)       => api.post('/auth/register', d).then(r => r.data);
export const authLogin        = (d)       => api.post('/auth/login', d).then(r => r.data);
export const authGoogle       = (token)   => api.post('/auth/google', { google_token: token }).then(r => r.data);
export const getMe            = ()        => api.get('/auth/me').then(r => r.data);
export const authForgotPw     = (email)   => api.post('/auth/forgot-password', { email }).then(r => r.data);
export const authResetPw      = (tok, pw) => api.post('/auth/reset-password', { token: tok, new_password: pw }).then(r => r.data);
export const authUpdatePw     = (cur, nw)        => api.put('/auth/update-password', { current_password: cur, new_password: nw }).then(r => r.data);
export const authUpdateEmail  = (newEmail, pw)   => api.put('/auth/update-email',    { new_email: newEmail, password: pw }).then(r => r.data);
export const authResendVerify = (email)   => api.post('/auth/resend-verification', { email }).then(r => r.data);

// ── Video ─────────────────────────────────────────────────────────────────────
export const checkHealth = () => api.get('/api/health').then(r => r.data).catch(() => ({ status: 'offline' }));

export const uploadVideo = (file, onProgress, startTime = null, endTime = null) => {
  const fd = new FormData();
  fd.append('file', file);
  if (startTime !== null && startTime > 0) fd.append('start_time', String(startTime));
  if (endTime   !== null)                  fd.append('end_time',   String(endTime));
  return api.post('/api/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / e.total)),
  }).then(r => r.data);
};

export const triggerAnalysis = (videoId) => api.post(`/api/analyze/${videoId}`).then(r => r.data);
export const getResult       = (videoId) => api.get(`/api/result/${videoId}`).then(r => r.data);
export const getPdfUrl     = (videoId) => `${BASE}/api/report/${videoId}/pdf`;
export const getOverlayUrl = (videoId) => `${BASE}/api/video/${videoId}/overlay`;

// ── History — backend (logged-in users) + localStorage (guests) ──────────────

const historyKey = (userId) => userId ? `be_history_${userId}` : 'be_history';

/**
 * Save a history entry.
 * When user is logged in: saves to backend DB (persistent across devices).
 * When guest: saves to localStorage only.
 */
export const saveToHistory = async (videoId, shotType, score, grade, userId) => {
  // Always write to localStorage as instant/offline cache
  const key = historyKey(userId);
  const existing = JSON.parse(localStorage.getItem(key) || '[]');
  const updated = [
    { videoId, shotType, score, grade, date: new Date().toISOString() },
    ...existing.filter(h => h.videoId !== videoId),
  ].slice(0, 50);
  localStorage.setItem(key, JSON.stringify(updated));

  // Also persist to backend when logged in
  if (userId) {
    try {
      await api.post('/api/user/history', { video_id: videoId, shot_type: shotType, score: score || 0, grade: grade || '' });
    } catch {
      // non-fatal — localStorage already saved it
    }
  }
};

/**
 * Fetch history:
 * When logged in: fetches from backend (source of truth) then updates localStorage cache.
 * When guest: reads from localStorage.
 * Returns array immediately from localStorage, then refetches from backend async.
 */
export const getHistory = (userId) => JSON.parse(localStorage.getItem(historyKey(userId)) || '[]');

export const fetchHistoryFromBackend = async (userId) => {
  if (!userId) return getHistory(null);
  try {
    const { data } = await api.get('/api/user/history');
    const entries = (data.history || []).map(h => ({
      videoId:  h.video_id,
      shotType: h.shot_type,
      score:    h.score,
      grade:    h.grade,
      date:     h.created_at,
    }));
    // Update local cache
    localStorage.setItem(historyKey(userId), JSON.stringify(entries));
    return entries;
  } catch {
    // Backend unavailable — fall back to local cache
    return getHistory(userId);
  }
};

/**
 * When a user logs in, merge any guest-session analyses into their backend history,
 * then clear the guest localStorage key.
 */
export const mergeGuestHistory = async (userId) => {
  if (!userId) return;
  const guestKey  = 'be_history';
  const guestData = JSON.parse(localStorage.getItem(guestKey) || '[]');
  if (!guestData.length) return;

  // Push guest entries to backend
  for (const h of guestData) {
    try {
      await api.post('/api/user/history', {
        video_id:  h.videoId,
        shot_type: h.shotType,
        score:     h.score || 0,
        grade:     h.grade || '',
      });
    } catch { /* non-fatal */ }
  }

  // Merge into user's local cache
  const userKey  = historyKey(userId);
  const userData = JSON.parse(localStorage.getItem(userKey) || '[]');
  const existingIds = new Set(userData.map(h => h.videoId));
  const merged   = [...guestData.filter(h => !existingIds.has(h.videoId)), ...userData].slice(0, 50);
  localStorage.setItem(userKey, JSON.stringify(merged));
  localStorage.removeItem(guestKey);
};

export default api;
