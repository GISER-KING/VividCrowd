#!/bin/bash

# VividCrowd 一键启动脚本 (Linux/Mac)
# 用途：自动检查环境、安装依赖、启动服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印欢迎信息
echo ""
echo "=========================================="
echo "   VividCrowd 一键启动脚本"
echo "=========================================="
echo ""

# 1. 检查 Python 环境
print_info "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python 3，请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python 版本: $PYTHON_VERSION"

# 2. 检查 Node.js 环境
print_info "检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    print_error "未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js 版本: $NODE_VERSION"

# 3. 检查 .env 文件
print_info "检查环境变量配置..."
if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，正在创建..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "已创建 .env 文件"
    else
        print_error ".env.example 文件不存在"
        exit 1
    fi

    # 提示用户配置 API Key
    echo ""
    print_warning "请配置 DASHSCOPE_API_KEY："
    echo "1. 访问 https://dashscope.console.aliyun.com/ 获取 API Key"
    echo "2. 编辑 .env 文件，填入 API Key"
    echo "3. 重新运行此脚本"
    echo ""

    # 打开编辑器
    if command -v nano &> /dev/null; then
        read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env
        else
            exit 0
        fi
    else
        print_info "请手动编辑 .env 文件"
        exit 0
    fi
fi

# 检查 API Key 是否配置
source .env
if [ -z "$DASHSCOPE_API_KEY" ] || [ "$DASHSCOPE_API_KEY" = "your-dashscope-api-key-here" ]; then
    print_error "DASHSCOPE_API_KEY 未配置，请编辑 .env 文件"
    exit 1
fi

print_success "环境变量配置正确"

# 4. 安装后端依赖
print_info "安装后端依赖..."
cd backend

if [ ! -d "venv" ]; then
    print_info "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q
print_success "后端依赖安装完成"

cd ..

# 5. 安装前端依赖
print_info "安装前端依赖..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    print_success "前端依赖安装完成"
else
    print_success "前端依赖已存在，跳过安装"
fi

cd ..

# 6. 启动服务
print_info "启动后端服务..."
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
print_success "后端服务已启动 (PID: $BACKEND_PID)"
cd ..

# 等待后端启动
print_info "等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/docs > /dev/null; then
    print_success "后端服务启动成功"
else
    print_error "后端服务启动失败，请查看日志: logs/backend.log"
    exit 1
fi

print_info "启动前端服务..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
print_success "前端服务已启动 (PID: $FRONTEND_PID)"
cd ..

# 7. 打印访问信息
echo ""
echo "=========================================="
print_success "VividCrowd 启动成功！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端: http://localhost:5173"
echo "  后端 API 文档: http://localhost:8000/docs"
echo ""
echo "日志文件："
echo "  后端: logs/backend.log"
echo "  前端: logs/frontend.log"
echo ""
echo "停止服务："
echo "  ./stop.sh"
echo ""
echo "=========================================="
echo ""

# 自动打开浏览器（可选）
if command -v xdg-open &> /dev/null; then
    sleep 3
    xdg-open http://localhost:5173 &
elif command -v open &> /dev/null; then
    sleep 3
    open http://localhost:5173 &
fi
