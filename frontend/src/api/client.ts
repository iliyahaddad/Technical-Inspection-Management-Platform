import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

export const ACCESS_KEY = 'access_token'
export const REFRESH_KEY = 'refresh_token'

declare module 'axios' {
  interface AxiosRequestConfig {
    /** Return the raw DRF page object ({count, next, results}) instead of auto-following all pages. */
    keepPagination?: boolean
  }
}

export const api = axios.create({ baseURL: '/api' })

export const tokenStore = {
  access: () => localStorage.getItem(ACCESS_KEY),
  refresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh?: string) => {
    localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

api.interceptors.request.use((config) => {
  const token = tokenStore.access()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// DRF returns paginated lists ({count, next, results}); every page in this app expects a plain
// array, so follow `next` links transparently for collection GETs.
api.interceptors.response.use(async (response) => {
  const data = response.data
  if (response.config.method === 'get' && !response.config.keepPagination && data && Array.isArray(data.results) && 'count' in data) {
    let items: unknown[] = [...data.results]
    let next: string | null = data.next
    while (next) {
      const url = new URL(next, window.location.origin)
      // raw axios (not `api`) so the page is not re-processed by this interceptor
      const page: { data: { results: unknown[]; next: string | null } } = await axios.get(url.pathname + url.search, {
        headers: { Authorization: `Bearer ${tokenStore.access()}` },
      })
      items = items.concat(page.data.results)
      next = page.data.next
    }
    response.data = items
  }
  return response
})

let refreshing: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.refresh()
  if (!refresh) throw new Error('no refresh token')
  const res = await axios.post('/api/auth/token/refresh/', { refresh })
  tokenStore.set(res.data.access, res.data.refresh)
  return res.data.access
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
    const isAuthCall = original?.url?.includes('/auth/token')
    if (error.response?.status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true
      try {
        refreshing = refreshing ?? refreshAccessToken().finally(() => { refreshing = null })
        const access = await refreshing
        original.headers.Authorization = `Bearer ${access}`
        return api(original)
      } catch {
        tokenStore.clear()
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export async function logout() {
  const refresh = tokenStore.refresh()
  try {
    if (refresh) await api.post('/auth/logout/', { refresh })
  } catch {
    /* token already invalid: nothing to blacklist */
  } finally {
    tokenStore.clear()
    window.location.assign('/login')
  }
}
