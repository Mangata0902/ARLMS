import axios from 'axios'

// =====================
// 创建 axios 实例
// =====================
const http = axios.create({ baseURL: '/api/v1' })

// 请求拦截器：自动携带 token
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：401 自动跳转登录
http.interceptors.response.use(
  res => res.data,          // ✅ 直接返回 res.data，调用方无需再 .data
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// =====================
// 认证相关
// =====================
export const authAPI = {
  login:    (data) => http.post('/auth/login',    data),
  register: (data) => http.post('/auth/register', data),
  me:       ()     => http.get('/auth/me'),
}

// =====================
// 对话相关
// =====================
export const chatAPI = {
  send:          (data) => http.post('/chat',              data),
  history:       ()     => http.get('/chat/history'),
  deleteSession: (id)   => http.delete(`/chat/sessions/${id}`),  // ✅ 新增删除会话
}

// =====================
// 科研报告相关
// =====================
export const researchAPI = {
  generate: (data) => http.post('/research/generate', data),
}

// =====================
// 文件上传相关
// =====================
export const ingestionAPI = {
  upload: (formData) => http.post('/ingest', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// =====================
// 学习资料相关
// =====================
export const materialsAPI = {
  list:   ()   => http.get('/materials'),
  delete: (id) => http.delete(`/materials/${id}`),
}

// =====================
// AI 检测相关
// =====================
export const detectionAPI = {
  detect:    (formData) => http.post('/ai/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  history:   ()         => http.get('/ai/history'),
  getReport: (id)       => http.get(`/ai/report/${id}`, { responseType: 'blob' }),
}

// =====================
// 默认导出 http 实例（供 App.vue 等直接使用）
// =====================
export default http
