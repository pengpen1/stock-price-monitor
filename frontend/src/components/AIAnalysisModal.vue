<template>
    <div v-if="visible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
        <div
            class="bg-gray-900 rounded-xl w-3/4 max-w-4xl max-h-[90vh] flex flex-col shadow-2xl border border-gray-700 overflow-hidden transform transition-all">
            <!-- Header -->
            <div class="flex justify-between items-center p-4 border-b border-gray-700 bg-gray-800">
                <h3 class="text-lg font-semibold text-white">
                    {{ stockCode }} · {{ type === 'fast' ? '快速分析' : '精准分析' }}
                </h3>
                <button @click="close"
                    class="text-gray-400 hover:text-white transition-colors p-1 rounded hover:bg-gray-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-auto p-6 text-gray-200">
                <!-- Error: No Config -->
                <div v-if="!hasConfig" class="text-center py-16">
                    <div class="bg-red-900/20 text-red-200 rounded-lg p-6 inline-block max-w-md">
                        <h4 class="text-lg font-semibold mb-2">未配置 AI API Key</h4>
                        <p class="text-sm text-red-200/70 mb-4">请前往设置页面配置大模型 API Key (Gemini, GPT, Claude等) 后再使用此功能。</p>
                        <button @click="close"
                            class="px-5 py-2 bg-red-800 hover:bg-red-700 rounded text-white transition-colors">关闭</button>
                    </div>
                </div>

                <!-- Input Form (Precise Mode) -->
                <div v-else-if="step === 'input'" class="space-y-6 max-w-2xl mx-auto py-4">
                    <div class="bg-gray-800/50 p-6 rounded-lg border border-gray-700/50">
                        <h4 class="text-base font-medium text-gray-200 mb-4">基础数据</h4>
                        <div class="grid grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-400 mb-2">持仓成本</label>
                                <div class="relative">
                                    <span class="absolute left-3 top-2.5 text-gray-500">¥</span>
                                    <input v-model="inputs.costPrice" type="number"
                                        class="w-full bg-gray-900 border border-gray-600 rounded-lg pl-8 pr-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                        placeholder="0.00">
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-400 mb-2">持仓数量</label>
                                <input v-model="inputs.position" type="number"
                                    class="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                    placeholder="0">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-400 mb-2">止盈位 (默认20%)</label>
                                <input v-model="inputs.takeProfit" type="text"
                                    class="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                    placeholder="自动计算">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-400 mb-2">止损位 (默认20%)</label>
                                <input v-model="inputs.stopLoss" type="text"
                                    class="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                    placeholder="自动计算">
                            </div>
                        </div>
                    </div>

                    <div class="bg-gray-800/50 p-6 rounded-lg border border-gray-700/50">
                        <h4 class="text-base font-medium text-gray-200 mb-4">补充信息</h4>
                        <label class="block text-sm font-medium text-gray-400 mb-2">附加材料 (新闻/政策/个人想法)</label>
                        <textarea v-model="inputs.extraText" rows="4"
                            class="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                            placeholder="请输入任何可能影响走势的额外信息..."></textarea>
                    </div>

                    <div class="flex justify-end pt-2">
                        <button @click="startAnalysis"
                            class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium transition-colors">开始分析</button>
                    </div>
                </div>

                <!-- Loading -->
                <div v-else-if="step === 'loading'" class="flex flex-col items-center justify-center py-32">
                    <div class="relative w-16 h-16 mb-6">
                        <div class="absolute inset-0 border-3 border-gray-600 rounded-full"></div>
                        <div class="absolute inset-0 border-3 border-t-blue-500 rounded-full animate-spin"></div>
                    </div>
                    <h4 class="text-lg font-medium text-white mb-2">正在分析中</h4>
                    <p class="text-gray-400 text-sm">通过 {{ config?.provider }} 获取分析结果...</p>
                </div>

                <!-- Result -->
                <div v-else-if="step === 'result'" class="space-y-4">
                    <!-- Prompt 消息流展示 -->
                    <div v-if="promptText" class="bg-gray-800/50 rounded-lg border border-gray-700/50 overflow-hidden">
                        <div 
                            @click="showPrompt = !showPrompt"
                            class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-700/30 transition-colors"
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-gray-400 text-sm">📝 prompt</span>
                                <span class="text-xs text-gray-500">({{ promptText.length }} 字符)</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <button 
                                    @click.stop="copyPrompt"
                                    class="px-2 py-1 text-xs text-blue-400 border border-blue-500/50 rounded hover:bg-blue-500/20 transition-colors"
                                >
                                    复制
                                </button>
                                <span class="text-gray-500 text-sm">{{ showPrompt ? '▼' : '▶' }}</span>
                            </div>
                        </div>
                        <div v-if="showPrompt" class="border-t border-gray-700/50">
                            <pre class="p-4 text-xs text-gray-300 overflow-auto max-h-64 whitespace-pre-wrap font-mono">{{ promptText }}</pre>
                        </div>
                    </div>

                    <!-- 分析结果 -->
                    <div class="rendered-markdown bg-gray-800/30 p-8 rounded-xl border border-gray-700/50"
                        v-html="renderedResult"></div>
                    <div class="flex justify-end pt-4">
                        <button @click="step = 'input'" v-if="type === 'precise'"
                            class="px-4 py-2 border border-blue-500 text-blue-400 rounded hover:bg-blue-500/10 mr-3 transition-colors">重新调整参数</button>
                        <button @click="showPrompt = false; step = 'loading'; startAnalysis()"
                            class="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white transition-colors">重新生成</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { marked } from 'marked';
import { analyzeStock, getSettings } from '../api';

const props = defineProps<{
    visible: boolean;
    stockCode: string;
    type: 'fast' | 'precise';
}>();

const emit = defineEmits(['update:visible']);

const step = ref<'input' | 'loading' | 'result'>('input');
const inputs = ref({
    costPrice: '',
    position: '',
    takeProfit: '',
    stopLoss: '',
    extraText: ''
});
const result = ref('');
const promptText = ref(''); // 保存发送给大模型的 prompt
const showPrompt = ref(false); // 是否展开 prompt
const config = ref<{ provider: string, apiKey: string, model: string, proxy?: string } | null>(null);

const hasConfig = computed(() => !!config.value?.apiKey);

const renderedResult = computed(() => {
    return marked.parse(result.value);
});

watch(() => props.visible, async (newVal) => {
    if (newVal) {
        await loadConfig();
        result.value = '';

        // 如果没有配置，就不进行后续判断了
        if (!config.value?.apiKey) {
            return;
        }

        if (props.type === 'fast') {
            step.value = 'loading';
            startAnalysis();
        } else {
            step.value = 'input';
        }
    }
});

// 从后端加载 AI 配置
const loadConfig = async () => {
    try {
        const res = await getSettings();
        if (res.status === 'success' && res.settings?.ai_api_key) {
            config.value = {
                provider: res.settings.ai_provider || 'gemini',
                apiKey: res.settings.ai_api_key || '',
                model: res.settings.ai_model || '',
                proxy: res.settings.ai_proxy || ''
            };
        } else {
            config.value = null;
        }
    } catch (e) {
        console.error('加载 AI 配置失败:', e);
        config.value = null;
    }
};

const close = () => {
    emit('update:visible', false);
};

const startAnalysis = async () => {
    step.value = 'loading';
    try {
        if (!config.value) return;

        const analysisInputs = {
            cost_price: inputs.value.costPrice,
            position: inputs.value.position,
            take_profit: inputs.value.takeProfit || '20%',
            stop_loss: inputs.value.stopLoss || '20%',
            extra_text: inputs.value.extraText
        };

        const res = await analyzeStock(
            props.stockCode,
            props.type,
            config.value.provider,
            config.value.apiKey,
            config.value.model,
            props.type === 'precise' ? analysisInputs : {},
            config.value.proxy
        );

        if (res.status === 'success') {
            result.value = res.result;
            promptText.value = res.prompt || ''; // 保存 prompt
            step.value = 'result';
        } else {
            result.value = `**分析失败**: ${res.message}`;
            promptText.value = '';
            step.value = 'result';
        }
    } catch (e: any) {
        result.value = `**发生错误**: ${e.message || '未知错误'}`;
        promptText.value = '';
        step.value = 'result';
    }
};

// 复制 prompt 到剪贴板
const copyPrompt = async () => {
    try {
        await navigator.clipboard.writeText(promptText.value);
        // 可以添加一个提示
    } catch (e) {
        console.error('复制失败:', e);
    }
};
</script>

<style scoped>
/* Basic styles for markdown content */
.rendered-markdown :deep(h1) {
    font-size: 1.5rem;
    line-height: 2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}

.rendered-markdown :deep(h2) {
    font-size: 1.25rem;
    line-height: 1.75rem;
    font-weight: 700;
    color: #93c5fd;
    margin-bottom: 0.75rem;
    margin-top: 1.25rem;
}

.rendered-markdown :deep(h3) {
    font-size: 1.125rem;
    line-height: 1.75rem;
    font-weight: 700;
    color: #bfdbfe;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}

.rendered-markdown :deep(p) {
    margin-bottom: 0.75rem;
    color: #d1d5db;
    line-height: 1.625;
}

.rendered-markdown :deep(ul) {
    list-style-type: disc;
    list-style-position: inside;
    margin-bottom: 1rem;
    color: #d1d5db;
}

.rendered-markdown :deep(ol) {
    list-style-type: decimal;
    list-style-position: inside;
    margin-bottom: 1rem;
    color: #d1d5db;
}

.rendered-markdown :deep(li) {
    margin-bottom: 0.25rem;
}

.rendered-markdown :deep(strong) {
    color: white;
    font-weight: 700;
}

.rendered-markdown :deep(code) {
    background-color: #374151;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    color: #fde047;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.rendered-markdown :deep(pre) {
    background-color: #111827;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin-bottom: 1rem;
    border: 1px solid #374151;
}

.rendered-markdown :deep(pre code) {
    background-color: transparent;
    padding: 0;
    color: #d1d5db;
}

.rendered-markdown :deep(blockquote) {
    border-left-width: 4px;
    border-left-color: #4b5563;
    padding-left: 1rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    font-style: italic;
    color: #9ca3af;
    background-color: rgba(31, 41, 55, 0.3);
    border-top-right-radius: 0.25rem;
    border-bottom-right-radius: 0.25rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.rendered-markdown :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

.rendered-markdown :deep(th) {
    border: 1px solid #4b5563;
    padding: 0.5rem 0.75rem;
    background-color: #1f2937;
    text-align: left;
    color: #e5e7eb;
}

.rendered-markdown :deep(td) {
    border: 1px solid #4b5563;
    padding: 0.5rem 0.75rem;
    color: #d1d5db;
}

.rendered-markdown :deep(a) {
    color: #60a5fa;
    text-decoration: underline;
}

.rendered-markdown :deep(a:hover) {
    color: #93c5fd;
}

.rendered-markdown :deep(hr) {
    border-color: #374151;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    border-top-width: 1px;
}
</style>
