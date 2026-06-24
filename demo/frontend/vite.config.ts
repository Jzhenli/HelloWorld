import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/static/',  // Static files are mounted at /static in FastAPI
  server: {
    // Proxy /api to backend during development
    // Set VITE_API_PORT environment variable to match pyproject.toml port
    proxy: {
      '/api': {
        target: `http://localhost:${process.env.VITE_API_PORT || 18080}`,
        changeOrigin: true,
      }
    }
  }
})
