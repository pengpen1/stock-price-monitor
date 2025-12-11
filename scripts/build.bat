@echo off
chcp 65001 >nul
echo ========================================
echo   股票监控助手 - 打包脚本 (Windows)
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

echo [1/4] 安装前端依赖...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/4] 安装 electron-builder...
call npm install electron-builder --save-dev
if %errorlevel% neq 0 (
    echo [错误] electron-builder 安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 构建前端...
call npm run build
if %errorlevel% neq 0 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)

echo.
echo [4/4] 打包 Electron 应用...
call npx electron-builder --win
if %errorlevel% neq 0 (
    echo [错误] Electron 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成！
echo   输出目录: frontend/release
echo ========================================
echo.

cd ..
pause
