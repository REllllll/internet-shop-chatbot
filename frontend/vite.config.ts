import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.ts'],
  },
  server: {
    port: 3000,
    proxy: {
      '/chat': 'http://localhost:8000',
      '/internal': 'http://localhost:8000',
    },
  },
})
