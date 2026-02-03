@echo off
REM VividCrowd 停止脚本 (Windows)

echo.
echo ==========================================
echo    停止 VividCrowd 服务
echo ==========================================
echo.

REM 停止后端服务
echo [INFO] 停止后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [SUCCESS] 后端服务已停止

REM 停止前端服务
echo [INFO] 停止前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [SUCCESS] 前端服务已停止

REM 停止所有 uvicorn 进程
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" >nul 2>&1

REM 停止所有 node 进程（谨慎使用）
REM taskkill /F /IM node.exe >nul 2>&1

echo.
echo [SUCCESS] 所有服务已停止
echo.

pause
