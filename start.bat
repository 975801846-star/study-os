@echo off
echo 🎓 StudyOS 启动中...
echo.

:: 启动后端
start "StudyOS Backend" cmd /k "cd /d D:\Projects\study-os\backend && venv\Scripts\activate && uvicorn src.main:app --reload --port 8000"

:: 等后端先起来
timeout /t 3 /nobreak >nul

:: 启动前端
start "StudyOS Frontend" cmd /k "cd /d D:\Projects\study-os\frontend && npm run dev -- --port 3000"

:: 等前端就绪
echo 等待前端启动...
timeout /t 8 /nobreak >nul

:: 打开浏览器
start http://localhost:3000

echo.
echo ✅ StudyOS 已启动！浏览器已打开 http://localhost:3000
echo 关闭两个终端窗口即可停止。
