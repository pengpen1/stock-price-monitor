/**
 * 应用入口文件
 * 初始化 Vue 应用，注册插件（Router、Pinia、i18n）
 */
import { createApp } from "vue"
import { createPinia } from "pinia"
import "./style.css"
import App from "./App.vue"
import router from "./router"
import i18n from "./i18n"

const app = createApp(App)

// 注册插件
app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount("#app")
