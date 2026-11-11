import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

// Built into the Python package (src/profsagent/app/static/ui) and served by the FastAPI app at /ui.
// In development, `npm run dev` proxies /api to the app on port 8000 (scripts/run_app.py or scripts/run_app_demo.py).
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/ui/' : '/',
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  build: {
    outDir: fileURLToPath(new URL('../src/profsagent/app/static/ui', import.meta.url)),
    emptyOutDir: true,
    chunkSizeWarningLimit: 900,
  },
  server: {
    port: 5173,
    proxy: { '/api': { target: process.env.PROFSAGENT_API ?? 'http://127.0.0.1:8000', changeOrigin: false } },
  },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
}))
