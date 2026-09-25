import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { showToast, showFailToast } from 'vant'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：FastAPI 直接返回 Pydantic model，无需 code/message 信封
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error.response?.data?.detail
    if (error.response?.status === 401) {
      useUserStore().logout()
    }
    showToast(detail || '请求失败')
    return Promise.reject(error)
  }
)

export default request
