import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === 'production' ? '/static/' : '/',
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/clients/messages/send/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/clients/connections/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
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
}))
