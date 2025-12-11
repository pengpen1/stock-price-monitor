import { ref, computed } from "vue";
import { marked } from "marked";
const __VLS_props = defineProps();
const emit = defineEmits(["update:visible"]);
const activeSection = ref("quickstart");
const sections = [
    { id: "quickstart", title: "快速开始" },
    { id: "stocks", title: "股票管理" },
    { id: "alerts", title: "预警设置" },
    { id: "ai", title: "AI 分析" },
    { id: "settings", title: "系统设置" },
];
const guideContent = {
    quickstart: `
## 快速开始

欢迎使用**股票监控助手**！这是一款功能强大的股票实时监控工具。

### 启动应用

1. 启动后端服务：\`cd backend && python main.py\`
2. 启动前端应用：\`cd frontend && npm run dev\`
3. 应用会自动打开，显示主界面

### 界面概览

- **顶部**：大盘指数（上证、深证、创业板、沪深300）
- **中部**：股票列表，显示实时行情
- **底部**：自动刷新状态

### 基本操作

| 操作 | 说明 |
|------|------|
| 添加股票 | 输入股票代码（如 000001 或 sh600000）后回车 |
| 查看详情 | 点击股票行可打开详情页 |
| 右键菜单 | 右键点击股票可进行更多操作 |
| 拖拽排序 | 拖动股票行可调整顺序 |
`,
    stocks: `
## 股票管理

### 添加股票

支持多种代码格式：
- 纯数字：\`000001\`、\`600000\`
- 带前缀：\`sh600000\`、\`sz000001\`

### 分组管理

1. 点击 **+ 新建** 创建分组
2. 右键股票 → 选择 **移动到分组**
3. 点击分组标签可筛选显示

### 排序功能

- **拖拽排序**：按住股票行左侧 ⋮⋮ 图标拖动
- **涨跌幅排序**：点击表头"涨跌幅"列
- **右键菜单**：置顶 / 置底

### 重点关注

点击 ⭐ 按钮设置重点关注股票，该股票数据会显示在：
- 系统托盘图标
- 悬浮窗
`,
    alerts: `
## 预警设置

### 设置预警

1. 点击股票行的 **预警** 按钮
2. 设置以下参数：
   - **止盈价格**：股价达到时提醒
   - **止损价格**：股价跌至时提醒
   - **涨跌幅预警**：涨跌幅达到百分比时提醒

### 预警通知

触发预警后会通过以下方式通知：
- 🖥️ 系统桌面通知
- 📱 PushPlus 微信推送（需配置）
- 💬 钉钉机器人推送（需配置）

### 冷却时间

为避免频繁提醒，同一股票预警触发后会进入冷却期（默认 5 分钟），可在设置中调整。
`,
    ai: `
## AI 智能分析

### 配置 AI

1. 进入 **设置** 页面
2. 选择 AI 提供商（推荐 Gemini）
3. 填写 API Key
4. 配置代理地址（国内用户必填）
5. 点击 **获取模型** 选择模型
6. 推荐使用 \`gemini-1.5-flash\`（配额高、速度快）

### 获取 API Key

- **Gemini**：访问 [Google AI Studio](https://aistudio.google.com/)
- **OpenAI**：访问 [OpenAI Platform](https://platform.openai.com/)
- **Claude**：访问 [Anthropic Console](https://console.anthropic.com/)

### 使用分析

1. **快速分析**：点击股票行的 **AI** 按钮
2. **精准分析**：在详情页点击 **精准分析**，可输入持仓成本等信息

### 分析内容

AI 会分析以下数据并给出建议：
- 📈 近期 K 线走势
- 📊 成交量变化（价量配合）
- 💰 资金流向
- 🎯 操作建议
`,
    settings: `
## 系统设置

### 基础设置

| 设置项 | 说明 |
|--------|------|
| 刷新间隔 | 行情数据刷新频率（1-60秒） |
| 预警冷却 | 同一预警再次触发的间隔时间 |

### AI 配置

| 设置项 | 说明 |
|--------|------|
| AI 提供商 | Gemini / OpenAI / Claude |
| API Key | 对应平台的密钥 |
| 代理地址 | 如 \`http://127.0.0.1:10808\` |
| 模型 | 推荐 gemini-1.5-flash |

### 推送配置

| 设置项 | 说明 |
|--------|------|
| PushPlus Token | 微信推送，[获取地址](https://www.pushplus.plus/) |
| 钉钉 Webhook | 钉钉机器人推送地址 |

### 系统托盘

- 点击托盘图标：显示/隐藏主窗口
- 右键托盘图标：显示菜单
- 托盘图标会根据重点关注股票涨跌变色
`,
};
const renderedContent = computed(() => {
    return marked.parse(guideContent[activeSection.value] || "");
});
const close = () => {
    emit("update:visible", false);
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {
    ...{},
    ...{},
    ...{},
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
if (__VLS_ctx.visible) {
    // @ts-ignore
    [visible,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: (__VLS_ctx.close) },
        ...{ class: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" },
    });
    // @ts-ignore
    [close,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "bg-white rounded-xl shadow-2xl w-[600px] max-h-[85vh] flex flex-col overflow-hidden" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex justify-between items-center p-4 border-b border-slate-100 bg-gradient-to-r from-emerald-500 to-teal-500" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex items-center gap-2" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "text-2xl" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
        ...{ class: "text-lg font-semibold text-white" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.close) },
        ...{ class: "text-white/80 hover:text-white transition-colors p-1 rounded hover:bg-white/10" },
    });
    // @ts-ignore
    [close,];
    __VLS_asFunctionalElement(__VLS_intrinsics.svg, __VLS_intrinsics.svg)({
        xmlns: "http://www.w3.org/2000/svg",
        ...{ class: "h-5 w-5" },
        fill: "none",
        viewBox: "0 0 24 24",
        stroke: "currentColor",
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.path)({
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
        'stroke-width': "2",
        d: "M6 18L18 6M6 6l12 12",
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex bg-slate-50 px-4 gap-1 border-b border-slate-200" },
        ...{ style: "height: 80px; overflow: hidden" },
    });
    for (const [section] of __VLS_getVForSourceType((__VLS_ctx.sections))) {
        // @ts-ignore
        [sections,];
        __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.visible))
                        return;
                    __VLS_ctx.activeSection = section.id;
                    // @ts-ignore
                    [activeSection,];
                } },
            key: (section.id),
            ...{ class: (__VLS_ctx.activeSection === section.id
                    ? 'text-emerald-600 border-emerald-500'
                    : 'text-slate-500 hover:text-slate-700 border-transparent') },
            ...{ class: "px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px" },
        });
        // @ts-ignore
        [activeSection,];
        (section.title);
    }
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex-1 overflow-auto p-6" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "prose prose-sm max-w-none" },
    });
    __VLS_asFunctionalDirective(__VLS_directives.vHtml)(null, { ...__VLS_directiveBindingRestFields, value: (__VLS_ctx.renderedContent) }, null, null);
    // @ts-ignore
    [renderedContent,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "p-4 border-t border-slate-100 bg-slate-50 flex justify-between items-center" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "text-xs text-slate-400" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.close) },
        ...{ class: "px-4 py-1.5 bg-emerald-500 text-white text-sm rounded-lg hover:bg-emerald-600 transition-colors" },
    });
    // @ts-ignore
    [close,];
}
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['inset-0']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-black/50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['z-50']} */ ;
/** @type {__VLS_StyleScopedClasses['backdrop-blur-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['w-[600px]']} */ ;
/** @type {__VLS_StyleScopedClasses['max-h-[85vh]']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gradient-to-r']} */ ;
/** @type {__VLS_StyleScopedClasses['from-emerald-500']} */ ;
/** @type {__VLS_StyleScopedClasses['to-teal-500']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white/80']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['p-1']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-white/10']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['whitespace-nowrap']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b-2']} */ ;
/** @type {__VLS_StyleScopedClasses['-mb-px']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['prose']} */ ;
/** @type {__VLS_StyleScopedClasses['prose-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-none']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['border-t']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-emerald-500']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-emerald-600']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
const __VLS_export = (await import('vue')).defineComponent({
    emits: {},
    __typeProps: {},
});
export default {};
