import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), svgr()],
  resolve: {
    alias: {
      src: '/src',
      components: '/src/components',
      assets: '/src/assets',
      api: '/src/api',
      layouts: '/src/layouts',
      pages: '/src/pages',
      '~': '/src',
      config: '/src/config',
    },
  },
  server: {
    proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,      
          ws: true,
        }
      }
  },
  build: {
    outDir: '../backend/dist',
    sourcemap: true,
  }
});