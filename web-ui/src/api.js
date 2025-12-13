import axios from 'axios';

// In production, the API is served from the same origin
// In development, Vite proxy will handle /api requests
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const syncAPI = {
  // Start a sync task
  startSync: (config) => api.post('/api/sync/start', config),
  
  // Get sync task status
  getStatus: (taskId) => api.get(`/api/sync/status/${taskId}`),
  
  // List all tasks
  listTasks: () => api.get('/api/sync/tasks'),
  
  // Test connection
  testConnection: (params) => api.get('/api/test-connection', { params }),
};

export const configAPI = {
  // Save configuration
  save: (name, config) => api.post(`/api/config/save?name=${encodeURIComponent(name)}`, config),
  
  // Load configuration
  load: (name) => api.get(`/api/config/load/${encodeURIComponent(name)}`),
  
  // List configurations
  list: () => api.get('/api/config/list'),
  
  // Delete configuration
  delete: (name) => api.delete(`/api/config/delete/${encodeURIComponent(name)}`),
};

export default api;
