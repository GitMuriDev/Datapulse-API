import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Injeta o token Bearer em todas as requisições autenticadas
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('datapulse_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Trata expiração de token (401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
      localStorage.removeItem('datapulse_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;