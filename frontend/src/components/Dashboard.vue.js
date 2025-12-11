import { ref, computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { getStocks, addStock, removeStock, getSettings, reorderStocks, setAlert, getTriggeredAlerts, setFocusedStock, setStockGroup, addGroupApi, deleteGroupApi, } from "../api";
import AIAnalysisModal from "./AIAnalysisModal.vue";
import ChangelogModal from "./ChangelogModal.vue";
import UserGuideModal from "./UserGuideModal.vue";
const { locale } = useI18n();
const emit = defineEmits(["openSettings", "openDetail"]);
// 响应式状态
const newStockCode = ref("");
const stockData = ref([]);
const stockOrder = ref([]); // 保存原始顺序
const alerts = ref({});
const stockGroups = ref({});
const indexData = ref({});
const loading = ref(false);
const errorMsg = ref("");
const refreshInterval = ref(5);
const alertNotifications = ref([]);
const focusedStock = ref(null);
// 分组和排序
const currentGroup = ref("");
const sortBy = ref("");
const groupList = ref([]);
const newGroupName = ref("");
const showAddGroupModal = ref(false);
const pendingGroupStock = ref(null); // 待分组的股票代码（右键菜单新建分组时使用）
// 拖拽状态
const dragIndex = ref(null);
// 右键菜单
const contextMenu = ref({ show: false, x: 0, y: 0, stock: null });
// 分组右键菜单
const groupContextMenu = ref({ show: false, x: 0, y: 0, group: "" });
// 预警弹窗
const showAlertModal = ref(false);
const currentAlertStock = ref(null);
const alertForm = ref({
    take_profit: "",
    stop_loss: "",
    change_alert: "",
    enabled: true,
});
// AI 分析
const showAiModal = ref(false);
const aiStockCode = ref("");
const aiType = ref("fast");
// 更新日志和使用手册
const showChangelog = ref(false);
const showUserGuide = ref(false);
const openAIModal = (stock, type) => {
    aiStockCode.value = stock.code;
    aiType.value = type;
    showAiModal.value = true;
};
let intervalId = null;
let alertCheckId = null;
// 大盘指数列表
const indexList = computed(() => {
    const codes = ["sh000001", "sz399001", "sz399006", "sh000300"];
    return codes.map((c) => indexData.value[c]).filter(Boolean);
});
// 排序图标
const sortIcon = computed(() => {
    if (sortBy.value === "change_desc")
        return "↓";
    if (sortBy.value === "change_asc")
        return "↑";
    return "";
});
// 过滤和排序后的股票列表
const filteredStocks = computed(() => {
    let list = [...stockData.value];
    // 按分组过滤
    if (currentGroup.value) {
        list = list.filter((s) => stockGroups.value[s.code] === currentGroup.value);
    }
    // 排序
    if (sortBy.value === "change_desc") {
        list.sort((a, b) => parseFloat(b.change_percent) - parseFloat(a.change_percent));
    }
    else if (sortBy.value === "change_asc") {
        list.sort((a, b) => parseFloat(a.change_percent) - parseFloat(b.change_percent));
    }
    return list;
});
const toggleLanguage = () => {
    locale.value = locale.value === "en" ? "zh" : "en";
};
const getPriceClass = (changePercent) => {
    const value = parseFloat(changePercent);
    if (value > 0)
        return "text-red-500";
    if (value < 0)
        return "text-green-500";
    return "text-slate-600";
};
const getIndexClass = (changePercent) => {
    const value = parseFloat(changePercent || "0");
    if (value > 0)
        return "text-red-500";
    if (value < 0)
        return "text-green-500";
    return "text-slate-800";
};
const formatAmount = (amount) => {
    const val = parseFloat(amount || "0");
    if (val >= 100000000)
        return (val / 100000000).toFixed(2) + "亿";
    if (val >= 10000)
        return (val / 10000).toFixed(0) + "万";
    return val.toFixed(0);
};
const toggleSort = () => {
    if (sortBy.value === "")
        sortBy.value = "change_desc";
    else if (sortBy.value === "change_desc")
        sortBy.value = "change_asc";
    else
        sortBy.value = "";
};
// 拖拽排序 - 修复：保存到后端后不立即刷新
const handleDragStart = (index, e) => {
    dragIndex.value = index;
    if (e.dataTransfer)
        e.dataTransfer.effectAllowed = "move";
};
const handleDrop = async (targetIndex) => {
    if (dragIndex.value === null || dragIndex.value === targetIndex) {
        dragIndex.value = null;
        return;
    }
    // 在当前过滤列表中操作
    const list = filteredStocks.value;
    const draggedStock = list[dragIndex.value];
    // 更新原始顺序
    const newOrder = [...stockOrder.value];
    const fromIdx = newOrder.indexOf(draggedStock.code);
    const targetStock = list[targetIndex];
    const toIdx = newOrder.indexOf(targetStock.code);
    if (fromIdx !== -1 && toIdx !== -1) {
        newOrder.splice(fromIdx, 1);
        newOrder.splice(toIdx, 0, draggedStock.code);
        stockOrder.value = newOrder;
        // 重新排列 stockData
        const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
        stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);
        // 保存到后端
        await reorderStocks(newOrder);
    }
    dragIndex.value = null;
};
// 右键菜单
const showContextMenu = (e, stock) => {
    contextMenu.value = { show: true, x: e.clientX, y: e.clientY, stock };
};
const hideContextMenu = () => {
    contextMenu.value.show = false;
    groupContextMenu.value.show = false;
};
// 分组右键菜单
const showGroupContextMenu = (e, group) => {
    e.preventDefault();
    groupContextMenu.value = { show: true, x: e.clientX, y: e.clientY, group };
};
const handleDeleteGroup = async (deleteStocks) => {
    const group = groupContextMenu.value.group;
    if (!group)
        return;
    const res = await deleteGroupApi(group, deleteStocks);
    if (res.status === "success") {
        // 从本地分组列表移除
        groupList.value = groupList.value.filter((g) => g !== group);
        if (deleteStocks && res.deleted_stocks?.length > 0) {
            // 如果删除了股票，更新本地数据
            stockOrder.value = stockOrder.value.filter((c) => !res.deleted_stocks.includes(c));
            stockData.value = stockData.value.filter((s) => !res.deleted_stocks.includes(s.code));
            for (const code of res.deleted_stocks) {
                delete stockGroups.value[code];
            }
        }
        else {
            // 仅删除分组，清除股票的分组标记
            for (const code in stockGroups.value) {
                if (stockGroups.value[code] === group) {
                    delete stockGroups.value[code];
                }
            }
        }
        // 如果当前选中的是被删除的分组，切换到全部
        if (currentGroup.value === group) {
            currentGroup.value = "";
        }
    }
    hideContextMenu();
};
const handleContextAction = async (action, param) => {
    const stock = contextMenu.value.stock;
    if (!stock)
        return;
    if (action === "top") {
        const newOrder = [
            stock.code,
            ...stockOrder.value.filter((c) => c !== stock.code),
        ];
        stockOrder.value = newOrder;
        const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
        stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);
        await reorderStocks(newOrder);
    }
    else if (action === "bottom") {
        const newOrder = [
            ...stockOrder.value.filter((c) => c !== stock.code),
            stock.code,
        ];
        stockOrder.value = newOrder;
        const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
        stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);
        await reorderStocks(newOrder);
    }
    else if (action === "group") {
        await setStockGroup(stock.code, param || "");
        if (param) {
            stockGroups.value[stock.code] = param;
            if (!groupList.value.includes(param))
                groupList.value.push(param);
        }
        else {
            delete stockGroups.value[stock.code];
        }
    }
    else if (action === "newGroup") {
        // 记住当前股票，打开新建分组弹窗
        pendingGroupStock.value = stock.code;
        showAddGroupModal.value = true;
    }
    else if (action === "delete") {
        await handleRemoveStock(stock.code);
    }
    hideContextMenu();
};
// 关闭新建分组弹窗
const closeAddGroupModal = () => {
    showAddGroupModal.value = false;
    newGroupName.value = "";
    pendingGroupStock.value = null;
};
// 新建分组
const addGroup = async () => {
    if (!newGroupName.value)
        return;
    const groupName = newGroupName.value.trim();
    if (!groupName)
        return;
    // 调用后端 API 持久化分组
    await addGroupApi(groupName);
    // 更新本地分组列表
    if (!groupList.value.includes(groupName)) {
        groupList.value.push(groupName);
    }
    // 如果是从右键菜单新建分组，将当前股票移动到新分组
    if (pendingGroupStock.value) {
        await setStockGroup(pendingGroupStock.value, groupName);
        stockGroups.value[pendingGroupStock.value] = groupName;
    }
    closeAddGroupModal();
};
// 预警弹窗
const openAlertModal = (stock) => {
    currentAlertStock.value = stock;
    const existing = alerts.value[stock.code];
    alertForm.value = {
        take_profit: existing?.take_profit || "",
        stop_loss: existing?.stop_loss || "",
        change_alert: existing?.change_alert || "",
        enabled: existing?.enabled ?? true,
    };
    showAlertModal.value = true;
};
const closeAlertModal = () => {
    showAlertModal.value = false;
    currentAlertStock.value = null;
};
const saveAlert = async () => {
    if (!currentAlertStock.value)
        return;
    await setAlert(currentAlertStock.value.code, alertForm.value);
    alerts.value[currentAlertStock.value.code] = { ...alertForm.value };
    closeAlertModal();
};
const dismissAlert = (index) => {
    alertNotifications.value.splice(index, 1);
};
// 更新托盘
const updateTray = () => {
    if (stockData.value.length > 0) {
        const summary = stockData.value
            .slice(0, 3)
            .map((s) => `${s.name}: ${s.price} (${s.change_percent}%)`)
            .join("\n");
        window.ipcRenderer?.send("update-tray", summary);
    }
};
const updateTrayIcon = (focusedData) => {
    if (focusedData) {
        window.ipcRenderer?.send("update-tray-icon", {
            change: focusedData.change_percent,
            price: focusedData.price,
            name: focusedData.name,
        });
    }
};
const handleSetFocus = async (code) => {
    await setFocusedStock(code);
    focusedStock.value = code;
    const stock = stockData.value.find((s) => s.code === code);
    if (stock)
        updateTrayIcon(stock);
};
const handleRowClick = (code, event) => {
    if (event.target.closest("button"))
        return;
    emit("openDetail", code);
};
// 获取数据 - 修复：不覆盖用户的排序
const fetchData = async () => {
    try {
        const res = await getStocks();
        // 首次加载时保存原始顺序
        if (stockOrder.value.length === 0) {
            stockOrder.value = res.stocks;
        }
        // 按照本地保存的顺序排列数据
        const dataMap = res.data;
        stockData.value = stockOrder.value
            .map((code) => dataMap[code])
            .filter(Boolean);
        alerts.value = res.alerts || {};
        stockGroups.value = res.groups || {};
        indexData.value = res.index_data || {};
        focusedStock.value =
            res.focused_stock || (res.stocks.length > 0 ? res.stocks[0] : null);
        // 更新分组列表（从后端获取的 group_list 优先，再合并已使用的分组）
        const usedGroups = new Set(Object.values(stockGroups.value));
        const backendGroups = res.group_list || [];
        const allGroups = new Set([...backendGroups, ...usedGroups]);
        groupList.value = Array.from(allGroups);
        updateTray();
        if (res.focused_data)
            updateTrayIcon(res.focused_data);
    }
    catch (error) {
        console.error("获取数据失败:", error);
    }
};
const checkAlerts = async () => {
    try {
        const res = await getTriggeredAlerts();
        if (res.alerts?.length > 0) {
            alertNotifications.value.push(...res.alerts);
            for (const alert of res.alerts) {
                const title = `📈 ${alert.name} 预警触发`;
                const body = alert.messages.join("\n") + `\n当前价: ${alert.price}`;
                window.ipcRenderer?.showNotification(title, body);
            }
        }
    }
    catch (e) {
        console.error("检查预警失败:", e);
    }
};
const handleAddStock = async () => {
    if (!newStockCode.value)
        return;
    loading.value = true;
    errorMsg.value = "";
    try {
        const res = await addStock(newStockCode.value);
        if (res.status === "error") {
            errorMsg.value = res.message;
        }
        else {
            // 添加到本地顺序
            const normalizedCode = newStockCode.value.startsWith("sh") ||
                newStockCode.value.startsWith("sz")
                ? newStockCode.value
                : newStockCode.value.startsWith("6")
                    ? `sh${newStockCode.value}`
                    : `sz${newStockCode.value}`;
            if (!stockOrder.value.includes(normalizedCode) &&
                !stockOrder.value.includes(newStockCode.value)) {
                stockOrder.value.push(normalizedCode);
            }
            newStockCode.value = "";
            await fetchData();
        }
    }
    catch (e) {
        errorMsg.value = "添加失败，请检查后端连接";
    }
    finally {
        loading.value = false;
    }
};
const handleRemoveStock = async (code) => {
    await removeStock(code);
    stockOrder.value = stockOrder.value.filter((c) => c !== code);
    stockData.value = stockData.value.filter((s) => s.code !== code);
};
const loadSettingsAndStart = async () => {
    try {
        const res = await getSettings();
        if (res.status === "success" && res.settings?.refresh_interval) {
            refreshInterval.value = res.settings.refresh_interval;
        }
    }
    catch (e) {
        console.error("加载设置失败:", e);
    }
    await fetchData();
    intervalId = setInterval(fetchData, refreshInterval.value * 1000);
    alertCheckId = setInterval(checkAlerts, 3000);
};
// 点击其他地方关闭右键菜单
const handleGlobalClick = () => {
    hideContextMenu();
};
onMounted(() => {
    loadSettingsAndStart();
    document.addEventListener("click", handleGlobalClick);
});
onUnmounted(() => {
    if (intervalId)
        clearInterval(intervalId);
    if (alertCheckId)
        clearInterval(alertCheckId);
    document.removeEventListener("click", handleGlobalClick);
});
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
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "max-w-6xl mx-auto" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex justify-between items-center mb-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({
    ...{ class: "text-2xl font-bold text-slate-800" },
});
(__VLS_ctx.$t("dashboard.title"));
// @ts-ignore
[$t,];
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex items-center gap-2" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.toggleLanguage) },
    ...{ class: "px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
});
// @ts-ignore
[toggleLanguage,];
(__VLS_ctx.locale === "en" ? "中文" : "English");
// @ts-ignore
[locale,];
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.showUserGuide = true;
            // @ts-ignore
            [showUserGuide,];
        } },
    ...{ class: "px-3 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
    title: "使用手册",
});
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.showChangelog = true;
            // @ts-ignore
            [showChangelog,];
        } },
    ...{ class: "px-3 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
    title: "更新日志",
});
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.$emit('openSettings');
            // @ts-ignore
            [$emit,];
        } },
    ...{ class: "px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "grid grid-cols-4 gap-3 mb-4" },
});
for (const [idx] of __VLS_getVForSourceType((__VLS_ctx.indexList))) {
    // @ts-ignore
    [indexList,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        key: (idx.code),
        ...{ class: "bg-white rounded-xl p-3 shadow-sm border border-slate-100" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "text-xs text-slate-500" },
    });
    (idx.name);
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex items-baseline gap-2" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "text-lg font-bold" },
        ...{ class: (__VLS_ctx.getIndexClass(idx.change_percent)) },
    });
    // @ts-ignore
    [getIndexClass,];
    (idx.price);
    __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "text-xs" },
        ...{ class: (__VLS_ctx.getIndexClass(idx.change_percent)) },
    });
    // @ts-ignore
    [getIndexClass,];
    (parseFloat(idx.change_percent) >= 0 ? "+" : "");
    (idx.change_percent);
}
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "bg-white rounded-xl shadow-sm border border-slate-100 p-4 mb-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex gap-3" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "relative flex-1" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
    ...{ class: "absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" },
});
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
    d: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
});
__VLS_asFunctionalElement(__VLS_intrinsics.input)({
    ...{ onKeyup: (__VLS_ctx.handleAddStock) },
    placeholder: (__VLS_ctx.$t('dashboard.placeholder')),
    disabled: (__VLS_ctx.loading),
    ...{ class: "w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white" },
});
(__VLS_ctx.newStockCode);
// @ts-ignore
[$t, handleAddStock, loading, newStockCode,];
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.handleAddStock) },
    disabled: (__VLS_ctx.loading),
    ...{ class: "px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-blue-700 disabled:from-blue-300 disabled:to-blue-400" },
});
// @ts-ignore
[handleAddStock, loading,];
(__VLS_ctx.loading ? __VLS_ctx.$t("dashboard.adding") : __VLS_ctx.$t("dashboard.add"));
// @ts-ignore
[$t, $t, loading,];
if (__VLS_ctx.errorMsg) {
    // @ts-ignore
    [errorMsg,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm" },
    });
    (__VLS_ctx.errorMsg);
    // @ts-ignore
    [errorMsg,];
}
if (__VLS_ctx.alertNotifications.length > 0) {
    // @ts-ignore
    [alertNotifications,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "mb-4 space-y-2" },
    });
    for (const [alert, idx] of __VLS_getVForSourceType((__VLS_ctx.alertNotifications))) {
        // @ts-ignore
        [alertNotifications,];
        __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            key: (idx),
            ...{ class: "bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm flex justify-between" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
        __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ class: "font-medium" },
        });
        (alert.name);
        (alert.code);
        for (const [msg] of __VLS_getVForSourceType((alert.messages))) {
            __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
                key: (msg),
                ...{ class: "text-amber-600" },
            });
            (msg);
        }
        __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.alertNotifications.length > 0))
                        return;
                    __VLS_ctx.dismissAlert(idx);
                    // @ts-ignore
                    [dismissAlert,];
                } },
            ...{ class: "text-amber-400 hover:text-amber-600" },
        });
    }
}
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex items-center justify-between mb-3" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex items-center gap-2" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
    ...{ class: "text-sm text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.currentGroup = '';
            // @ts-ignore
            [currentGroup,];
        } },
    ...{ class: (!__VLS_ctx.currentGroup
            ? 'bg-blue-500 text-white'
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200') },
    ...{ class: "px-3 py-1 text-xs rounded-full transition-colors" },
});
// @ts-ignore
[currentGroup,];
for (const [g] of __VLS_getVForSourceType((__VLS_ctx.groupList))) {
    // @ts-ignore
    [groupList,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.currentGroup = g;
                // @ts-ignore
                [currentGroup,];
            } },
        ...{ onContextmenu: (...[$event]) => {
                __VLS_ctx.showGroupContextMenu($event, g);
                // @ts-ignore
                [showGroupContextMenu,];
            } },
        key: (g),
        ...{ class: (__VLS_ctx.currentGroup === g
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200') },
        ...{ class: "px-3 py-1 text-xs rounded-full transition-colors" },
    });
    // @ts-ignore
    [currentGroup,];
    (g);
}
__VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.showAddGroupModal = true;
            // @ts-ignore
            [showAddGroupModal,];
        } },
    ...{ class: "px-2 py-1 text-xs text-blue-500 border border-blue-200 rounded-full hover:bg-blue-50" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "flex items-center gap-2" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
    ...{ class: "text-sm text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.select, __VLS_intrinsics.select)({
    value: (__VLS_ctx.sortBy),
    ...{ class: "text-xs border border-slate-200 rounded px-2 py-1 focus:outline-none" },
});
// @ts-ignore
[sortBy,];
__VLS_asFunctionalElement(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    value: "",
});
__VLS_asFunctionalElement(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    value: "change_desc",
});
__VLS_asFunctionalElement(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    value: "change_asc",
});
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.table, __VLS_intrinsics.table)({
    ...{ class: "w-full table-fixed" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.thead, __VLS_intrinsics.thead)({});
__VLS_asFunctionalElement(__VLS_intrinsics.tr, __VLS_intrinsics.tr)({
    ...{ class: "bg-slate-50 border-b border-slate-100" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-8 px-1 py-3" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-24 px-2 py-3 text-left text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-20 px-2 py-3 text-left text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-20 px-2 py-3 text-right text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ onClick: (__VLS_ctx.toggleSort) },
    ...{ class: "w-20 px-2 py-3 text-right text-xs font-semibold text-slate-500 cursor-pointer hover:text-blue-500" },
});
// @ts-ignore
[toggleSort,];
(__VLS_ctx.sortIcon);
// @ts-ignore
[sortIcon,];
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-16 px-2 py-3 text-right text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-16 px-2 py-3 text-right text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-20 px-2 py-3 text-right text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-16 px-2 py-3 text-left text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.th, __VLS_intrinsics.th)({
    ...{ class: "w-28 px-2 py-3 text-center text-xs font-semibold text-slate-500" },
});
__VLS_asFunctionalElement(__VLS_intrinsics.tbody, __VLS_intrinsics.tbody)({
    ...{ class: "divide-y divide-slate-100" },
});
for (const [stock, index] of __VLS_getVForSourceType((__VLS_ctx.filteredStocks))) {
    // @ts-ignore
    [filteredStocks,];
    __VLS_asFunctionalElement(__VLS_intrinsics.tr, __VLS_intrinsics.tr)({
        ...{ onDragstart: (...[$event]) => {
                __VLS_ctx.handleDragStart(index, $event);
                // @ts-ignore
                [handleDragStart,];
            } },
        ...{ onDragover: () => { } },
        ...{ onDrop: (...[$event]) => {
                __VLS_ctx.handleDrop(index);
                // @ts-ignore
                [handleDrop,];
            } },
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.handleRowClick(stock.code, $event);
                // @ts-ignore
                [handleRowClick,];
            } },
        ...{ onContextmenu: (...[$event]) => {
                __VLS_ctx.showContextMenu($event, stock);
                // @ts-ignore
                [showContextMenu,];
            } },
        key: (stock.code),
        ...{ class: "hover:bg-slate-50 transition-colors cursor-pointer" },
        draggable: "true",
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ onClick: () => { } },
        ...{ class: "px-1 py-3 cursor-move" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "text-slate-400 hover:text-slate-600 text-sm font-bold" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-xs font-mono text-slate-600" },
    });
    (stock.code);
    if (__VLS_ctx.alerts[stock.code]?.enabled) {
        // @ts-ignore
        [alerts,];
        __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "ml-0.5 text-amber-500" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-sm font-medium text-slate-800 truncate" },
    });
    (stock.name);
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-sm text-right font-semibold tabular-nums" },
        ...{ class: (__VLS_ctx.getPriceClass(stock.change_percent)) },
    });
    // @ts-ignore
    [getPriceClass,];
    (stock.price);
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-sm text-right font-medium tabular-nums" },
        ...{ class: (__VLS_ctx.getPriceClass(stock.change_percent)) },
    });
    // @ts-ignore
    [getPriceClass,];
    __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
        ...{ class: "inline-flex items-center gap-0.5" },
    });
    if (parseFloat(stock.change_percent) > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
    }
    else if (parseFloat(stock.change_percent) < 0) {
        __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
    }
    (stock.change_percent);
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-sm text-right text-slate-600 tabular-nums" },
    });
    (stock.high);
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-sm text-right text-slate-600 tabular-nums" },
    });
    (stock.low);
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-xs text-right text-slate-500" },
    });
    (__VLS_ctx.formatAmount(stock.amount));
    // @ts-ignore
    [formatAmount,];
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ class: "px-2 py-3 text-xs text-slate-500" },
    });
    if (__VLS_ctx.stockGroups[stock.code]) {
        // @ts-ignore
        [stockGroups,];
        __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            ...{ class: "px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded" },
        });
        (__VLS_ctx.stockGroups[stock.code]);
        // @ts-ignore
        [stockGroups,];
    }
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        ...{ onClick: () => { } },
        ...{ class: "px-2 py-3 text-center" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex items-center justify-center gap-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.handleSetFocus(stock.code);
                // @ts-ignore
                [handleSetFocus,];
            } },
        ...{ class: (__VLS_ctx.focusedStock === stock.code
                ? 'bg-amber-100 text-amber-600 border-amber-300'
                : 'text-slate-400 border-slate-200 hover:bg-amber-50') },
        ...{ class: "px-1.5 py-0.5 text-xs border rounded" },
    });
    // @ts-ignore
    [focusedStock,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.openAIModal(stock, 'fast');
                // @ts-ignore
                [openAIModal,];
            } },
        ...{ class: "px-1.5 py-0.5 text-xs text-purple-500 border border-purple-200 rounded hover:bg-purple-50" },
        title: "快速AI分析",
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.openAlertModal(stock);
                // @ts-ignore
                [openAlertModal,];
            } },
        ...{ class: "px-1.5 py-0.5 text-xs text-blue-500 border border-blue-200 rounded hover:bg-blue-50" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.handleRemoveStock(stock.code);
                // @ts-ignore
                [handleRemoveStock,];
            } },
        ...{ class: "px-1.5 py-0.5 text-xs text-slate-500 border border-slate-200 rounded hover:bg-red-50 hover:text-red-500" },
    });
}
if (__VLS_ctx.filteredStocks.length === 0) {
    // @ts-ignore
    [filteredStocks,];
    __VLS_asFunctionalElement(__VLS_intrinsics.tr, __VLS_intrinsics.tr)({});
    __VLS_asFunctionalElement(__VLS_intrinsics.td, __VLS_intrinsics.td)({
        colspan: "10",
        ...{ class: "px-4 py-12 text-center text-slate-400 text-sm" },
    });
    (__VLS_ctx.$t("dashboard.empty"));
    // @ts-ignore
    [$t,];
}
__VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
    ...{ class: "mt-4 text-center text-xs text-slate-400" },
});
(__VLS_ctx.$t("dashboard.auto_refresh", { interval: __VLS_ctx.refreshInterval }));
// @ts-ignore
[$t, refreshInterval,];
if (__VLS_ctx.groupContextMenu.show) {
    // @ts-ignore
    [groupContextMenu,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: () => { } },
        ...{ class: "fixed bg-white rounded-lg shadow-xl border border-slate-200 py-1 z-50 min-w-40" },
        ...{ style: ({
                left: __VLS_ctx.groupContextMenu.x + 'px',
                top: __VLS_ctx.groupContextMenu.y + 'px',
            }) },
    });
    // @ts-ignore
    [groupContextMenu, groupContextMenu,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "px-4 py-2 text-xs text-slate-400 border-b border-slate-100" },
    });
    (__VLS_ctx.groupContextMenu.group);
    // @ts-ignore
    [groupContextMenu,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.groupContextMenu.show))
                    return;
                __VLS_ctx.handleDeleteGroup(false);
                // @ts-ignore
                [handleDeleteGroup,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm hover:bg-slate-50" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.groupContextMenu.show))
                    return;
                __VLS_ctx.handleDeleteGroup(true);
                // @ts-ignore
                [handleDeleteGroup,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50" },
    });
}
if (__VLS_ctx.contextMenu.show) {
    // @ts-ignore
    [contextMenu,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: () => { } },
        ...{ class: "fixed bg-white rounded-lg shadow-xl border border-slate-200 py-1 z-50 min-w-32" },
        ...{ style: ({ left: __VLS_ctx.contextMenu.x + 'px', top: __VLS_ctx.contextMenu.y + 'px' }) },
    });
    // @ts-ignore
    [contextMenu, contextMenu,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.contextMenu.show))
                    return;
                __VLS_ctx.handleContextAction('top');
                // @ts-ignore
                [handleContextAction,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm hover:bg-slate-50" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.contextMenu.show))
                    return;
                __VLS_ctx.handleContextAction('bottom');
                // @ts-ignore
                [handleContextAction,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm hover:bg-slate-50" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "border-t border-slate-100 my-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "px-4 py-2 text-xs text-slate-400" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.contextMenu.show))
                    return;
                __VLS_ctx.handleContextAction('group', '');
                // @ts-ignore
                [handleContextAction,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm hover:bg-slate-50" },
    });
    for (const [g] of __VLS_getVForSourceType((__VLS_ctx.groupList))) {
        // @ts-ignore
        [groupList,];
        __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.contextMenu.show))
                        return;
                    __VLS_ctx.handleContextAction('group', g);
                    // @ts-ignore
                    [handleContextAction,];
                } },
            key: (g),
            ...{ class: "w-full px-4 py-2 text-left text-sm hover:bg-slate-50" },
        });
        (g);
        if (__VLS_ctx.stockGroups[__VLS_ctx.contextMenu.stock?.code] === g) {
            // @ts-ignore
            [stockGroups, contextMenu,];
            __VLS_asFunctionalElement(__VLS_intrinsics.span, __VLS_intrinsics.span)({
                ...{ class: "text-blue-500" },
            });
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.contextMenu.show))
                    return;
                __VLS_ctx.handleContextAction('newGroup');
                // @ts-ignore
                [handleContextAction,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm text-blue-500 hover:bg-blue-50" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "border-t border-slate-100 my-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.contextMenu.show))
                    return;
                __VLS_ctx.handleContextAction('delete');
                // @ts-ignore
                [handleContextAction,];
            } },
        ...{ class: "w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50" },
    });
}
if (__VLS_ctx.showAlertModal) {
    // @ts-ignore
    [showAlertModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: (__VLS_ctx.closeAlertModal) },
        ...{ class: "fixed inset-0 bg-black/50 flex items-center justify-center z-50" },
    });
    // @ts-ignore
    [closeAlertModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "bg-white rounded-xl shadow-xl w-96 p-6" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
        ...{ class: "text-lg font-semibold text-slate-800 mb-4" },
    });
    (__VLS_ctx.currentAlertStock?.name);
    // @ts-ignore
    [currentAlertStock,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "space-y-4" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsics.label, __VLS_intrinsics.label)({
        ...{ class: "block text-sm font-medium text-slate-600 mb-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.input)({
        type: "number",
        step: "0.01",
        placeholder: "价格达到时提醒",
        ...{ class: "w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" },
    });
    (__VLS_ctx.alertForm.take_profit);
    // @ts-ignore
    [alertForm,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsics.label, __VLS_intrinsics.label)({
        ...{ class: "block text-sm font-medium text-slate-600 mb-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.input)({
        type: "number",
        step: "0.01",
        placeholder: "价格跌至时提醒",
        ...{ class: "w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" },
    });
    (__VLS_ctx.alertForm.stop_loss);
    // @ts-ignore
    [alertForm,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsics.label, __VLS_intrinsics.label)({
        ...{ class: "block text-sm font-medium text-slate-600 mb-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.input)({
        type: "number",
        step: "0.1",
        placeholder: "涨跌幅达到时提醒",
        ...{ class: "w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" },
    });
    (__VLS_ctx.alertForm.change_alert);
    // @ts-ignore
    [alertForm,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex items-center gap-2" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.input)({
        type: "checkbox",
        id: "alert-enabled",
        ...{ class: "w-4 h-4" },
    });
    (__VLS_ctx.alertForm.enabled);
    // @ts-ignore
    [alertForm,];
    __VLS_asFunctionalElement(__VLS_intrinsics.label, __VLS_intrinsics.label)({
        for: "alert-enabled",
        ...{ class: "text-sm text-slate-600" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex justify-end gap-3 mt-6" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.closeAlertModal) },
        ...{ class: "px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
    });
    // @ts-ignore
    [closeAlertModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.saveAlert) },
        ...{ class: "px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600" },
    });
    // @ts-ignore
    [saveAlert,];
}
if (__VLS_ctx.showAddGroupModal) {
    // @ts-ignore
    [showAddGroupModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ onClick: (__VLS_ctx.closeAddGroupModal) },
        ...{ class: "fixed inset-0 bg-black/50 flex items-center justify-center z-50" },
    });
    // @ts-ignore
    [closeAddGroupModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "bg-white rounded-xl shadow-xl w-80 p-6" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
        ...{ class: "text-lg font-semibold text-slate-800 mb-4" },
    });
    if (__VLS_ctx.pendingGroupStock) {
        // @ts-ignore
        [pendingGroupStock,];
        __VLS_asFunctionalElement(__VLS_intrinsics.p, __VLS_intrinsics.p)({
            ...{ class: "text-xs text-slate-500 mb-2" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsics.input)({
        ...{ onKeyup: (__VLS_ctx.addGroup) },
        placeholder: "输入分组名称",
        ...{ class: "w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4" },
    });
    (__VLS_ctx.newGroupName);
    // @ts-ignore
    [addGroup, newGroupName,];
    __VLS_asFunctionalElement(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex justify-end gap-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.closeAddGroupModal) },
        ...{ class: "px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50" },
    });
    // @ts-ignore
    [closeAddGroupModal,];
    __VLS_asFunctionalElement(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.addGroup) },
        ...{ class: "px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600" },
    });
    // @ts-ignore
    [addGroup,];
}
/** @type {[typeof AIAnalysisModal, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AIAnalysisModal, new AIAnalysisModal({
    visible: (__VLS_ctx.showAiModal),
    stockCode: (__VLS_ctx.aiStockCode),
    type: (__VLS_ctx.aiType),
}));
const __VLS_1 = __VLS_0({
    visible: (__VLS_ctx.showAiModal),
    stockCode: (__VLS_ctx.aiStockCode),
    type: (__VLS_ctx.aiType),
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
// @ts-ignore
[showAiModal, aiStockCode, aiType,];
/** @type {[typeof ChangelogModal, ]} */ ;
// @ts-ignore
const __VLS_5 = __VLS_asFunctionalComponent(ChangelogModal, new ChangelogModal({
    visible: (__VLS_ctx.showChangelog),
}));
const __VLS_6 = __VLS_5({
    visible: (__VLS_ctx.showChangelog),
}, ...__VLS_functionalComponentArgsRest(__VLS_5));
// @ts-ignore
[showChangelog,];
/** @type {[typeof UserGuideModal, ]} */ ;
// @ts-ignore
const __VLS_10 = __VLS_asFunctionalComponent(UserGuideModal, new UserGuideModal({
    visible: (__VLS_ctx.showUserGuide),
}));
const __VLS_11 = __VLS_10({
    visible: (__VLS_ctx.showUserGuide),
}, ...__VLS_functionalComponentArgsRest(__VLS_10));
// @ts-ignore
[showUserGuide,];
/** @type {__VLS_StyleScopedClasses['min-h-screen']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gradient-to-br']} */ ;
/** @type {__VLS_StyleScopedClasses['from-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['to-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-6xl']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-4']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-baseline']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['relative']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['absolute']} */ ;
/** @type {__VLS_StyleScopedClasses['left-4']} */ ;
/** @type {__VLS_StyleScopedClasses['top-1/2']} */ ;
/** @type {__VLS_StyleScopedClasses['-translate-y-1/2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['pl-11']} */ ;
/** @type {__VLS_StyleScopedClasses['pr-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gradient-to-r']} */ ;
/** @type {__VLS_StyleScopedClasses['from-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['to-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:from-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:to-blue-700']} */ ;
/** @type {__VLS_StyleScopedClasses['disabled:from-blue-300']} */ ;
/** @type {__VLS_StyleScopedClasses['disabled:to-blue-400']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-red-200']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-amber-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-amber-200']} */ ;
/** @type {__VLS_StyleScopedClasses['text-amber-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-amber-600']} */ ;
/** @type {__VLS_StyleScopedClasses['text-amber-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-amber-600']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-blue-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-blue-50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['table-fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['w-8']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['w-24']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-20']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-20']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-20']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['cursor-pointer']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-16']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-16']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-20']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-16']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-28']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['divide-y']} */ ;
/** @type {__VLS_StyleScopedClasses['divide-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['cursor-pointer']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['cursor-move']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-amber-500']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['tabular-nums']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['tabular-nums']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['tabular-nums']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['tabular-nums']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blue-50']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-purple-500']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-purple-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-purple-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-blue-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-blue-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-red-500']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-12']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['z-50']} */ ;
/** @type {__VLS_StyleScopedClasses['min-w-40']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-500']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['z-50']} */ ;
/** @type {__VLS_StyleScopedClasses['min-w-32']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border-t']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['my-1']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-blue-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border-t']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['my-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-500']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['inset-0']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-black/50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['z-50']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['w-96']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-end']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-6']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['inset-0']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-black/50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['z-50']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['w-80']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-end']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blue-500']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-blue-600']} */ ;
const __VLS_export = (await import('vue')).defineComponent({
    emits: {},
});
export default {};
