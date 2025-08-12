import axios from 'axios'

const API_BASE = (import.meta as any).env?.VITE_API_URL ?? ''

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  const csrf = getCookie('csrf_token')
  if (csrf) {
    config.headers = config.headers || {}
    config.headers['X-CSRF-Token'] = csrf
  }
  return config
})

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}