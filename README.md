# 股票监控助手 (Stock Price Monitor)

一个跨平台的桌面股票监控应用，支持实时行情、预警推送和桌面悬浮窗显示。

![screenshot](docs/screenshot.png)

## ✨ 功能特性

- 📈 **实时行情** - 自动获取 A 股实时价格、涨跌幅等数据
- 🔔 **智能预警** - 支持止盈、止损、涨跌幅异动提醒
- 📱 **消息推送** - 支持 PushPlus (微信) 和钉钉机器人推送
- 🖥️ **桌面悬浮窗** - 始终置顶的迷你行情窗口，支持拖拽和吸边
- 📌 **系统托盘** - 最小化到托盘，悬停显示股票信息
- 🔄 **拖拽排序** - 自定义股票列表顺序
- 💾 **本地存储** - 股票列表和设置自动保存

## 🛠️ 技术栈

- **前端**: Electron + Vue 3 + TypeScript + TailwindCSS
- **后端**: Python + FastAPI
- **数据源**: 新浪财经 API

## 📦 安装与运行

### 环境要求

- Node.js >= 18
- Python >= 3.9

### 1. 克隆项目

```bash
git clone https://github.com/your-username/stock-price-monitor.git
cd stock-price-monitor
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动应用

**启动后端服务：**
```bash
cd backend
python main.py
```

**启动前端应用：**
```bash
cd frontend
npm run dev
```

## 📖 使用说明

### 添加股票

在输入框中输入股票代码（如 `600519`），点击添加按钮。支持的格式：
- 纯数字：`600519`（自动识别沪深）
- 带前缀：`sh600519`、`sz000001`

### 设置预警

点击股票行的「预警」按钮，可设置：
- **止盈价格**：当前价 >= 设定值时触发
- **止损价格**：当前价 <= 设定值时触发
- **涨跌幅预警**：涨跌幅绝对值 >= 设定值时触发

### 消息推送配置

点击右上角「设置」按钮：
- **PushPlus Token**：在 [pushplus.plus](https://www.pushplus.plus/) 获取
- **钉钉 Webhook**：创建钉钉群机器人获取

### 悬浮窗

- 启动时自动显示在屏幕右下角
- 拖拽标题栏可移动位置
- 靠近屏幕边缘自动吸附
- 点击 × 关闭，可从托盘菜单重新打开

## 📁 项目结构

```
stock-price-monitor/
├── backend/                # Python 后端
│   ├── main.py            # FastAPI 入口
│   ├── monitor.py         # 股票监控核心逻辑
│   ├── requirements.txt   # Python 依赖
│   └── data/              # 本地数据存储
├── frontend/              # Electron + Vue 前端
│   ├── electron/          # Electron 主进程
│   ├── src/               # Vue 源码
│   │   ├── components/    # 组件
│   │   └── api.ts         # API 封装
│   └── package.json
└── README.md
```

## 🔧 配置说明

### 后端配置

数据存储在 `backend/data/` 目录：
- `stocks.json` - 股票列表
- `settings.json` - 应用设置
- `alerts.json` - 预警配置

### 前端配置

- 后端 API 地址：`frontend/src/api.ts` 中的 `baseURL`

## 📝 开发计划

- [x] 实时行情获取
- [x] 桌面悬浮窗
- [x] 系统托盘
- [x] 预警功能
- [x] 消息推送
- [x] 拖拽排序
- [x] 打包发布 (electron-builder)
- [x] K 线图表
- [x] AI 分析

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
