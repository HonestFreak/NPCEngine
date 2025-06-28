// Frontend configuration for different environments
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const config = {
  apiBase: API_BASE,
  isDevelopment: import.meta.env.MODE === 'development',
  isProduction: import.meta.env.MODE === 'production'
}

export default config 