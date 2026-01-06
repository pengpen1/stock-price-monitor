<picture>
  <img alt="股票监控助手" src="docs/assets/screenshot.png">
</picture>

<div align="center">

# 股票监控助手

一个跨平台的桌面股票监控应用，支持实时行情、AI 智能分析、预警推送和桌面悬浮窗。

[English](./README.md) | 简体中文

<p>
  <img src="https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=for-the-badge&logo=electron&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p>
  <img src="https://img.shields.io/badge/AI-GPT%20%7C%20Claude%20%7C%20Gemini%20%7C%20DeepSeek-FF6F00?style=for-the-badge&logo=openai&logoColor=white" alt="AI Models" />
  <img src="https://img.shields.io/badge/市场-A股-red?style=for-the-badge" alt="A-Share" />
</p>

</div>

> **免责声明**：本软件仅供学习交流使用，不构成任何投资建议。AI 分析结果和趋势预测仅供参考，不保证准确性。股市有风险，投资需谨慎，使用本软件产生的任何盈亏均由用户自行承担，与开发者无关。

## 目录

- [更新日志](#更新日志)
- [功能特性](#功能特性)
- [截图展示](#截图展示)
- [快速开始](#快速开始)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [使用说明](#使用说明)
- [许可证](#许可证)

## 更新日志

- **[2025-12-24]** 🎉 V1.2.0 发布！新增笔记功能，支持 Markdown 编辑、自动保存、AI 智能提取交易记录。
- **[2025-12-22]** 🚀 V1.1.0 发布！实盘模拟功能，基于历史 K 线数据练习交易；交易日志页面；交易风格分析。
- **[2025-12-15]** ✨ V1.0.3 发布！交易记录功能，K 线图标记，AI 结构化输出自动提取信号。
- **[2025-12-12]** 📊 V1.0.2 发布！大盘指数分时图，AI Prompt 展示，配置导入导出。
- **[2025-12-10]** 🎊 V1.0.0 首次发布！实时行情、预警推送、悬浮窗、股票详情。

## 功能特性

### 📈 行情监控

- 实时获取 A 股行情数据（价格、涨跌幅、成交量等）
- 大盘指数展示（上证、深证、创业板、沪深300）
- 股票分组管理和拖拽排序
- 桌面悬浮窗，始终置顶显示重点关注股票

### 🤖 AI 智能分析

- 多模型支持：GPT / Claude / Gemini / DeepSeek / Kimi / 通义千问 / 豆包 / GLM
- 快速分析：基于当日数据快速判断
- 精准分析：综合技术面、基本面、资金流向、北向资金、融资融券等多维度数据
- 趋势预测：AI 预测未来 5 个交易日价格走势
- 结构化输出：自动提取看涨/谨慎/看跌信号

### 📝 交易记录与笔记

- 记录买入/卖出/做T 操作及原因
- K 线图标记：直观展示历史操作点位
- AI 分析历史：查看历史分析记录和信号
- 自动计算持仓成本和数量
- Markdown 笔记，支持自动保存
- AI 智能转换，从笔记中自动提取交易记录

### 🎮 实盘模拟

- 基于历史数据进行模拟交易练习
- 自定义模拟天数（7-50天）和初始资金
- 时间回溯：K线图只显示到当前模拟日期
- 分时图查看：可查看当日分时图辅助决策
- AI 智能评分：模拟结束后 AI 综合评价交易表现

### 🔔 预警推送

- 止盈/止损价格预警
- 涨跌幅异动提醒
- 支持 PushPlus（微信）和钉钉机器人推送

## 截图展示

<table>
  <tr>
    <td align="center"><b>股票详情</b></td>
    <td align="center"><b>AI 预测</b></td>
  </tr>
  <tr>
    <td><img src="docs/assets/detail.png" alt="股票详情" /></td>
    <td><img src="docs/assets/prediction.png" alt="AI 预测" /></td>
  </tr>
  <tr>
    <td align="center"><b>实盘模拟</b></td>
    <td align="center"><b>交易记录</b></td>
  </tr>
  <tr>
    <td><img src="docs/assets/simulation.png" alt="实盘模拟" /></td>
    <td><img src="docs/assets/history.png" alt="交易记录" /></td>
  </tr>
  <tr>
    <td align="center"><b>交易日志</b></td>
    <td align="center"><b>笔记</b></td>
  </tr>
  <tr></tr>g src="docs/assets/trade-log.png" alt="交易日志" /></td>
    <td><img src="docs/assets/note.png" alt="笔记" /></td>
  </tr>
</table>

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.9

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/stock-monitor.git
cd stock-monitor

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 运行

```bash
# 终端 1：启动后端
cd backend
python main.py

# 终端 2：启动前端
cd frontend
npm run dev
```

### 打包

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## 技术栈

| 层级   | 技术                                                  |
| ------ | ----------------------------------------------------- |
| 前端   | Electron + Vue 3 + TypeScript + TailwindCSS + ECharts |
| 后端   | Python + FastAPI                                      |
| 数据源 | 新浪财经、东方财富                                    |

## 项目结构

```
stock-monitor/
├── backend/                # Python 后端
│   ├── api/               # API 路由层
│   ├── domain/            # 业务领域层
│   ├── services/          # 服务层
│   ├── providers/         # AI 提供商
│   ├── repositories/      # 数据存储层
│   ├── schemas/           # 数据模型
│   ├── core/              # 核心配置
│   └── main.py            # 入口文件
├── frontend/              # Electron + Vue 前端
│   ├── electron/          # Electron 主进程
│   └── src/               # Vue 源码
├── docs/                  # 文档
└── scripts/               # 构建脚本
```

## 使用说明

### 添加股票

输入股票代码，支持以下格式：

- 纯数字：`600519`（自动识别沪深）
- 带前缀：`sh600519`、`sz000001`

### AI 配置

在设置页面配置 AI 服务：

- 选择模型提供商
- 填入 API Key
- 可选配置代理地址

### 消息推送

- **PushPlus**：在 [pushplus.plus](https://www.pushplus.plus/) 获取 Token
- **钉钉**：创建钉钉群机器人获取 Webhook URL

## 许可证

[MIT License](LICENSE)

---

<div align="center">
  <sub>为 A 股投资者用 ❤️ 打造</sub>
</div>
