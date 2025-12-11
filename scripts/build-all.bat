@echo off
chcp 65001 >nul
echo ========================================
echo   股票监控助手 - 完整打包脚本
echo   (后端 exe + 前端 Electron)
echo ========================================
echo.

:: 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

:: 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo ========================================
echo   第零步：清理敏感配置
echo ========================================
echo.

:: 创建干净的配置文件用于打包（避免泄露 API Key 等敏感信息）
echo {"refresh_interval":5,"pushplus_token":"","dingtalk_webhook":"","alert_cooldown":300,"ai_provider":"gemini","ai_api_key":"","ai_model":"","ai_proxy":""} > backend\data\settings.json
echo {"stocks":[],"focused_stock":null,"groups":{},"group_list":[]} > backend\data\stocks.json
echo {} > backend\data\alerts.json
echo 敏感配置已清理

echo.
echo ========================================
echo   第一步：打包后端为 exe
echo ========================================
echo.

cd backend

:: 检查虚拟环境
if not exist venv (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境并安装依赖
echo 安装后端依赖...
call venv\Scripts\pip install -r requirements.txt -q

:: 使用 PyInstaller 打包
echo 使用 PyInstaller 打包后端...
call venv\Scripts\pyinstaller --clean --noconfirm build_backend.spec

if %errorlevel% neq 0 (
    echo [错误] 后端打包失败
    cd ..
    pause
    exit /b 1
)

:: 复制打包结果到前端目录
echo 复制后端 exe 到前端资源目录...
if not exist ..\frontend\resources mkdir ..\frontend\resources
copy /Y dist\stock-monitor-backend.exe ..\frontend\resources\
xcopy /E /I /Y data ..\frontend\resources\data

cd ..

echo.
echo ========================================
echo   第二步：打包前端 Electron
echo ========================================
echo.

cd frontend

:: 安装依赖
echo 安装前端依赖...
call npm install

:: 构建前端
echo 构建前端...
call npm run build

if %errorlevel% neq 0 (
    echo [错误] 前端构建失败
    cd ..
    pause
    exit /b 1
)

:: 打包 Electron
echo 打包 Electron 应用...
call npx electron-builder --win

if %errorlevel% neq 0 (
    echo [错误] Electron 打包失败
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo   打包完成！
echo   输出目录: frontend/release
echo ========================================
echo.
pause
