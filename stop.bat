@echo off
echo 🛑 正在停止 StudyOS...
taskkill /f /im node.exe 2>nul
taskkill /f /fi "WINDOWTITLE eq StudyOS*" 2>nul
echo ✅ 已停止
