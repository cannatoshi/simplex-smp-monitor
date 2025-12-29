import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Nur spezifische HTMX Endpoints - NICHT alle /clients/*
      '/clients/messages/send/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/clients/connections/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Connect URLs mit slug pattern
      '^/clients/[a-z0-9-]+/connect/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/start/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/stop/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/restart/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
  },
})
