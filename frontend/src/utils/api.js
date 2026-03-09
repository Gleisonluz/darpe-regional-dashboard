import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const api = axios.create({
  baseURL: API_URL,
});

// Adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Public API
export const publicApi = {
  getCidades: () => api.get('/public/cidades'),
  getUnidades: (params) => api.get('/public/unidades', { params }),
  getUnidade: (id) => api.get(`/public/unidades/${id}`),
};

// Auth API
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

// Users API
export const usersApi = {
  getAll: (params) => api.get('/users/', { params }),
  getOne: (id) => api.get(`/users/${id}/`),
  update: (id, data) => api.put(`/users/${id}/`, data),
  approve: (id) => api.post(`/users/${id}/approve/`),
  reactivate: (id) => api.post(`/users/${id}/reactivate/`),
};

// Units API
export const unitsApi = {
  getAll: () => api.get('/units/'),
  create: (data) => api.post('/units/', data),
  update: (id, data) => api.put(`/units/${id}/`, data),
  delete: (id) => api.delete(`/units/${id}/`),
  addResponsavel: (unitId, userId) => api.post(`/units/${unitId}/responsaveis/${userId}/`),
  removeResponsavel: (unitId, userId) => api.delete(`/units/${unitId}/responsaveis/${userId}/`),
};

// Attendance API
export const attendanceApi = {
  register: (data) => api.post('/attendance/', data),
  getMyRecords: () => api.get('/attendance/my-records/'),
  getUnitRecords: (unitId) => api.get(`/attendance/unit/${unitId}/`),
};

// Service API
export const serviceApi = {
  register: (data) => api.post('/services/', data),
  getAll: (params) => api.get('/services/', { params }),
  getOne: (id) => api.get(`/services/${id}/`),
};

// Credential API
export const credentialApi = {
  get: () => api.get('/credential/'),
};

// Notifications API
export const notificationsApi = {
  getAll: () => api.get('/notifications/'),
  getUnreadCount: () => api.get('/notifications/unread-count/'),
  markAsRead: (id) => api.put(`/notifications/${id}/read/`),
  markAllAsRead: () => api.put('/notifications/read-all/'),
};

// Reports API
export const reportsApi = {
  attendanceByCity: () => api.get('/reports/attendance-by-city/'),
  attendanceByUnit: () => api.get('/reports/attendance-by-unit/'),
  activeAttendees: () => api.get('/reports/active-attendees/'),
  inactiveAttendees: () => api.get('/reports/inactive-attendees/'),
  agenda: () => api.get('/reports/agenda/'),
};

// Upload API
export const uploadApi = {
  uploadPhoto: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/photo/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default api;
