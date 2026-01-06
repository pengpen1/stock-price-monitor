/**
 * Vite 配置文件
 * 配置 Vue、Electron、Tailwind 等插件，以及路径别名
 */
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import electron from "vite-plugin-electron"
import renderer from "vite-plugin-electron-renderer"
import tailwindcss from "@tailwindcss/vite"
import { copyFileSync, mkdirSync, existsSync } from "fs"
import { resolve } from "path"

// 自定义插件：复制 preload.cjs 到 dist-electron
function copyPreloadPlugin() {
  return {
    name: "copy-preload",
    buildStart() {
      const src = resolve(__dirname, "electron/preload.cjs")
      const destDir = resolve(__dirname, "dist-electron")
      const dest = resolve(destDir, "preload.cjs")

      if (!existsSync(destDir)) {
        mkdirSync(destDir, { recursive: true })
      }

      if (existsSync(src)) {
        copyFileSync(src, dest)
        console.log("已复制 preload.cjs 到 dist-electron")
      }
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    copyPreloadPlugin(),
    electron([
      {
        // 主进程入口
        entry: "electron/main.ts",
      },
      {
        vite: {
          build: {
            outDir: "dist-electron",
            rollupOptions: {
              input: "electron/preload.ts",
              output: { entryFileNames: "preload.mjs" },
            },
          },
        },
      },
    ]),
    renderer(),
  ],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
})
