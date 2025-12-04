# 股票价格监控项目计划

## 1. 项目概述
构建一个跨平台的桌面应用，用于实时监控股票价格，支持自定义预警和消息推送。
- **后端**: Python (FastAPI) 负责数据获取、逻辑处理和消息推送。
- **前端**: Electron + Vue 3 + TypeScript 负责用户界面展示和交互。

## 2. 架构设计

### 2.1 整体架构
采用 **Client-Server** 架构，即使前后端打包在一起，逻辑上依然分离。
- **Python Backend**: 作为一个独立的子进程由 Electron 启动，或者独立运行。提供 RESTful API 供前端调用。
- **Electron Frontend**: 负责展示 UI，通过 HTTP 请求与 Python 后端通信。

### 2.2 后端 (Python)
- **Web 框架**: FastAPI (高性能，易于编写 API)
- **数据源**: AkShare (开源财经数据接口)
- **任务调度**: APScheduler (用于定时获取股价)
- **推送服务**: 
    - PushPlus (微信)
    - 钉钉机器人 (DingTalk)
    - 系统通知 (通过 API 返回给前端触发，或后端直接调用系统命令)

### 2.3 前端 (Electron + Vue 3)
- **核心栈**: Electron, Vue 3, TypeScript, Vite
- **样式**: CSS (Vanilla / Scoped CSS)
- **通信**: Axios / Fetch 调用本地 localhost API
- **功能模块**:
    - **托盘程序 (Tray)**: 最小化到托盘，右键菜单（退出、显示主窗口）。
    - **主窗口 (Dashboard)**: 
        - 股票列表表格（代码、名称、当前价、涨跌幅、预警阈值）。
        - 实时刷新（轮询或 WebSocket，初期可用轮询）。
    - **设置页面**:
        - 添加/删除股票。
        - 设置预警规则（价格上限、下限、涨跌幅）。
        - 配置推送密钥 (PushPlus Token, DingTalk Webhook)。

## 3. 核心流程

### 3.1 数据获取与监控
1.  用户在前端添加股票代码 (e.g., `sh600519`).
2.  后端接收请求，存入配置 (JSON/SQLite).
3.  后端定时任务 (e.g., 每 5 秒) 遍历监控列表。
4.  调用 AkShare 获取最新行情。
5.  检查是否触发预警条件。
6.  若触发，执行推送逻辑。

### 3.2 消息推送
- **策略**: 避免重复推送（设置冷却时间，如触发后 5 分钟内不再推送同一股票）。
- **渠道**: 支持多渠道同时发送。

## 4. 开发计划 (TODO)

- [x] **初始化**
    - [x] 搭建 Monorepo 结构 (backend/, frontend/)
    - [x] 配置 Electron 启动 Python 脚本的逻辑 (开发环境与生产环境)
- [ ] **后端开发**
    - [x] 实现 FastAPI 基础服务
    - [x] 集成 AkShare 获取实时数据
    - [ ] 实现监控逻辑与 APScheduler
    - [ ] 实现 PushPlus/DingTalk 推送
- [ ] **前端开发**
    - [x] 初始化 Vue3 + Vite 项目
    - [x] 集成 Electron
    - [x] 实现股票列表 UI
    - [ ] 实现设置界面
    - [ ] 对接后端 API
- [ ] **打包与发布**
    - [ ] 使用 electron-builder 打包
    - [ ] 验证 Python 环境打包问题 (PyInstaller)

## 5. 未来扩展 (AI Analysis)
- 集成 LLM (如 OpenAI/Gemini API) 对个股新闻或走势进行简要分析。