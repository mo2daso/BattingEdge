import axios from 'axios';

// Connects to your Python backend running on port 8000
const API_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Check if backend is alive
export const checkHealth = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error("Backend offline:", error);
        return { status: "offline" };
    }
};

// Upload video to backend
export const uploadVideo = async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            if (onProgress) onProgress(percentCompleted);
        }
    });
    return response.data; // Returns { video_id, status }
};

// Start the AI analysis
export const triggerAnalysis = async (videoId) => {
    const response = await api.post(`/analyze/${videoId}`);
    return response.data; // Returns { status: "processing_started" }
};

export default api;