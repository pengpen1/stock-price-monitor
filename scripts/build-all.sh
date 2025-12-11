#!/bin/bash
echo "========================================"
echo "  股票监控助手 - 完整打包脚本"
echo "  (后端 + 前端 Electron)"
echo "========================================"
echo

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python"
    exit 1
fi

echo "========================================"
echo "  第零步：清理敏感配置"
echo "========================================"
echo

# 创建干净的配置文件用于打包（避免泄露 API Key 等敏感信息）
echo '{"refresh_interval":5,"pushplus_token":"","dingtalk_webhook":"","alert_cooldown":300,"ai_provider":"gemini","ai_api_key":"","ai_model":"","ai_proxy":""}' > backend/data/settings.json
echo '{"stocks":[],"focused_stock":null,"groups":{},"group_list":[]}' > backend/data/stocks.json
echo '{}' > backend/data/alerts.json
echo "敏感配置已清理"

echo
echo "========================================"
echo "  第一步：打包后端"
echo "========================================"
echo

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "安装后端依赖..."
source venv/bin/activate
pip install -r requirements.txt -q

# 使用 PyInstaller 打包
echo "使用 PyInstaller 打包后端..."
pyinstaller --clean --noconfirm build_backend.spec

if [ $? -ne 0 ]; then
    echo "[错误] 后端打包失败"
    cd ..
    exit 1
fi

# 复制打包结果到前端目录
echo "复制后端到前端资源目录..."
mkdir -p ../frontend/resources
cp -f dist/stock-monitor-backend ../frontend/resources/
cp -rf data ../frontend/resources/

deactivate
cd ..

echo
echo "========================================"
echo "  第二步：打包前端 Electron"
echo "========================================"
echo

cd frontend

# 安装依赖
echo "安装前端依赖..."
npm install

# 构建前端
echo "构建前端..."
npm run build

if [ $? -ne 0 ]; then
    echo "[错误] 前端构建失败"
    cd ..
    exit 1
fi

# 根据系统打包
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "打包 Mac 应用..."
    npx electron-builder --mac
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "打包 Linux 应用..."
    npx electron-builder --linux
fi

if [ $? -ne 0 ]; then
    echo "[错误] Electron 打包失败"
    cd ..
    exit 1
fi

cd ..

echo
echo "========================================"
echo "  打包完成！"
echo "  输出目录: frontend/release"
echo "========================================"
