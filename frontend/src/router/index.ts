/**
 * Vue Router 路由配置
 * 定义应用的所有路由规则和导航守卫
 */
import {
  createRouter,
  createWebHashHistory,
  type RouteRecordRaw,
} from "vue-router";

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Dashboard",
    component: () => import("@/views/DashboardView.vue"),
    meta: { title: "股票监控" },
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("@/views/SettingsView.vue"),
    meta: { title: "设置" },
  },
  {
    path: "/stock/:code",
    name: "StockDetail",
    component: () => import("@/views/StockDetailView.vue"),
    meta: { title: "股票详情" },
    props: true,
  },
  {
    path: "/simulation/:sessionId",
    name: "Simulation",
    component: () => import("@/views/SimulationView.vue"),
    meta: { title: "实盘模拟" },
    props: true,
  },
  {
    path: "/journal",
    name: "Journal",
    component: () => import("@/views/JournalView.vue"),
    meta: { title: "交易日志" },
  },
  {
    path: "/notes",
    name: "Notes",
    component: () => import("@/views/NotesView.vue"),
    meta: { title: "笔记" },
  },
  {
    path: "/float",
    name: "Float",
    component: () => import("@/views/FloatView.vue"),
    meta: { title: "悬浮窗" },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 路由守卫 - 设置页面标题
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || "股票监控助手"}`;
  next();
});

export default router;
