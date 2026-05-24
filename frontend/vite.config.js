import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, proxy /api to the FastAPI server on :7860.
// In production the same FastAPI server serves the built files, so relative
// /api paths resolve against the same origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:7860',
    },
  },
  build: {
    outDir: 'dist',
  },
})
