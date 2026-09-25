import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  // 保留同域相对 /api 为默认（本地/k8s 同域反代零改）；Render 跨域时构建注入 VITE_API_URL 覆盖
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/admin/login'
    } else if (error.response?.status === 403) {
      ElMessage.error('没有操作权限')
    }
    return Promise.reject(error)
  }
)

export default api
