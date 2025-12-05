import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    electron([
      {
        // 主进程入口
        entry: 'electron/main.ts',
      },
      {
        // preload 脚本入口
        entry: 'electron/preload.ts',
        onstart(options) {
          options.reload()
        },
        vite: {
          build: {
            rollupOptions: {
              output: {
                // preload 必须使用 CommonJS 格式
                format: 'cjs',
              },
            },
          },
        },
      },
    ]),
    renderer(),
  ],
})
