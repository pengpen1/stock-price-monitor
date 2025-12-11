@echo off
chcp 65001 >nul
echo ========================================
echo   股票监控助手 - 启动脚本
echo ========================================
echo.

:: 启动后端
echo [1/2] 启动后端服务...
cd backend
if not exist venv (
    echo 创建 Python 虚拟环境...
    python -m venv venv
    call venv\Scripts\pip install -r requirements.txt
)
start "后端服务" cmd /k "venv\Scripts\python main.py"
cd ..

:: 等待后端启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端应用...
cd frontend
start "前端应用" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   服务已启动！
echo   后端: http://127.0.0.1:8000
echo   前端: http://localhost:5173
echo ========================================
echo.
echo 按任意键关闭此窗口（服务会继续运行）
pause >nul
