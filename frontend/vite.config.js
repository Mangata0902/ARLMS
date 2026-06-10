import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // 确保你已经安装了 node 类型定义，或者直接使用 path

export default defineConfig({
  plugins: [vue()],
  // --- 新增 resolve 配置 ---
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // -----------------------
  server: {
    port: 3000,
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})

