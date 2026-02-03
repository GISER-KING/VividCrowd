@echo off
REM VividCrowd 一键启动脚本 (Windows)
REM 用途：自动检查环境、安装依赖、启动服务

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo    VividCrowd 一键启动脚本
echo ==========================================
echo.

REM 1. 检查 Python 环境
echo [INFO] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 版本: %PYTHON_VERSION%

REM 2. 检查 Node.js 环境
echo [INFO] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js 版本: %NODE_VERSION%

REM 3. 检查 .env 文件
echo [INFO] 检查环境变量配置...
if not exist ".env" (
    echo [WARNING] .env 文件不存在，正在创建...

    if exist ".env.example" (
        copy .env.example .env >nul
        echo [SUCCESS] 已创建 .env 文件
    ) else (
        echo [ERROR] .env.example 文件不存在
        pause
        exit /b 1
    )

    echo.
    echo [WARNING] 请配置 DASHSCOPE_API_KEY：
    echo 1. 访问 https://dashscope.console.aliyun.com/ 获取 API Key
    echo 2. 编辑 .env 文件，填入 API Key
    echo 3. 重新运行此脚本
    echo.

    set /p EDIT_NOW="是否现在编辑 .env 文件？(y/n) "
    if /i "!EDIT_NOW!"=="y" (
        notepad .env
    )
    pause
    exit /b 0
)

REM 检查 API Key 是否配置
findstr /C:"DASHSCOPE_API_KEY=your-dashscope-api-key-here" .env >nul
if not errorlevel 1 (
    echo [ERROR] DASHSCOPE_API_KEY 未配置，请编辑 .env 文件
    pause
    exit /b 1
)

findstr /C:"DASHSCOPE_API_KEY=" .env | findstr /V /C:"#" >nul
if errorlevel 1 (
    echo [ERROR] DASHSCOPE_API_KEY 未配置，请编辑 .env 文件
    pause
    exit /b 1
)

echo [SUCCESS] 环境变量配置正确

REM 4. 创建日志目录
if not exist "logs" mkdir logs

REM 5. 安装后端依赖
echo [INFO] 安装后端依赖...
cd backend

if not exist "venv" (
    echo [INFO] 创建 Python 虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo [SUCCESS] 后端依赖安装完成

cd ..

REM 6. 安装前端依赖
echo [INFO] 安装前端依赖...
cd frontend

if not exist "node_modules" (
    call npm install
    echo [SUCCESS] 前端依赖安装完成
) else (
    echo [SUCCESS] 前端依赖已存在，跳过安装
)

cd ..

REM 7. 启动后端服务
echo [INFO] 启动后端服务...
cd backend
call venv\Scripts\activate.bat

REM 加载环境变量
for /f "usebackq tokens=1,* delims==" %%a in ("..\.env") do (
    set "%%a=%%b"
)

start /B cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"
echo [SUCCESS] 后端服务已启动

cd ..

REM 等待后端启动
echo [INFO] 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 检查后端是否启动成功
curl -s http://localhost:8000/docs >nul 2>&1
if errorlevel 1 (
    echo [WARNING] 后端服务可能未完全启动，请稍后访问
) else (
    echo [SUCCESS] 后端服务启动成功
)

REM 8. 启动前端服务
echo [INFO] 启动前端服务...
cd frontend
start /B cmd /c "npm run dev > ..\logs\frontend.log 2>&1"
echo [SUCCESS] 前端服务已启动

cd ..

REM 9. 打印访问信息
echo.
echo ==========================================
echo [SUCCESS] VividCrowd 启动成功！
echo ==========================================
echo.
echo 访问地址：
echo   前端: http://localhost:5173
echo   后端 API 文档: http://localhost:8000/docs
echo.
echo 日志文件：
echo   后端: logs\backend.log
echo   前端: logs\frontend.log
echo.
echo 停止服务：
echo   stop.bat
echo.
echo ==========================================
echo.

REM 自动打开浏览器
timeout /t 3 /nobreak >nul
start http://localhost:5173

pause
