/**
 * EduSight AI — API Service
 * Centralized Axios configuration for all backend calls.
 */

import axios from 'axios'

// ─── Base Configuration ───
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// ─── Request Interceptor ───
api.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response Interceptor ───
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred'

    if (import.meta.env.DEV) {
      console.error(`[API Error] ${message}`, error.response?.data)
    }

    return Promise.reject({ message, details: error.response?.data })
  }
)

// ─── Student APIs ───
export const studentAPI = {
  list:    (params) => api.get('/api/students/', { params }),
  get:     (id)     => api.get(`/api/students/${id}/`),
  create:  (data)   => api.post('/api/students/', data),
  update:  (id, data) => api.patch(`/api/students/${id}/`, data),
  delete:  (id)     => api.delete(`/api/students/${id}/`),
  summary: (id)     => api.get(`/api/students/${id}/summary/`),
}

// ─── Subject APIs ───
export const subjectAPI = {
  list:   (params) => api.get('/api/subjects/', { params }),
  get:    (id)     => api.get(`/api/subjects/${id}/`),
  create: (data)   => api.post('/api/subjects/', data),
}

// ─── Marks APIs ───
export const marksAPI = {
  list:      (params) => api.get('/api/marks/', { params }),
  create:    (data)   => api.post('/api/marks/', data),
  delete:    (id)     => api.delete(`/api/marks/${id}/`),
  uploadCSV: (file)   => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/marks/upload-csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ─── Dashboard API ───
export const dashboardAPI = {
  get: (studentId) => api.get(`/api/dashboard/${studentId}/`),
}

// ─── Analysis API ───
export const analysisAPI = {
  trigger: (studentId) =>
    api.post('/api/analysis/trigger/', { student_id: studentId }),

  getStatus: (taskId) =>
    api.get(`/api/analysis/status/${taskId}/`),

  getSummary: (studentId) =>
    api.get(`/api/analysis/summary/${studentId}/`),

  // ── PDF Download ──
  downloadReport: async (studentId, studentName) => {
    const response = await api.get(
      `/api/analysis/report/${studentId}/`,
      { responseType: 'blob' }
    )

    // Create download link
    const url      = window.URL.createObjectURL(
      new Blob([response.data], { type: 'application/pdf' })
    )
    const link     = document.createElement('a')
    link.href      = url
    link.download  = (
      `EduSight_Report_${studentName.replace(/\s+/g, '_')}.pdf`
    )
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}

// ─── Chat API ───
export const chatAPI = {
  send:       (studentId, message) =>
    api.post('/api/chat/query/', { student_id: studentId, message }),
  getHistory: (studentId) =>
    api.get('/api/chat/query/', { params: { student_id: studentId } }),
}

// ─── Comparison API ───
export const comparisonAPI = {
  compare: (studentIds) => {
    const ids = Array.isArray(studentIds)
      ? studentIds.join(',')
      : studentIds
    return api.get(`/api/compare/?student_ids=${ids}`)
  },
}

export default api
