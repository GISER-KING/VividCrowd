#!/bin/bash

# VividCrowd 停止脚本 (Linux/Mac)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "   停止 VividCrowd 服务"
echo "=========================================="
echo ""

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    print_info "停止后端服务 (PID: $BACKEND_PID)..."

    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        rm backend.pid
        print_success "后端服务已停止"
    else
        print_error "后端进程不存在"
        rm backend.pid
    fi
else
    print_info "未找到后端 PID 文件，尝试查找进程..."
    pkill -f "uvicorn app.main:app" && print_success "后端服务已停止" || print_info "未找到后端进程"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    print_info "停止前端服务 (PID: $FRONTEND_PID)..."

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        rm frontend.pid
        print_success "前端服务已停止"
    else
        print_error "前端进程不存在"
        rm frontend.pid
    fi
else
    print_info "未找到前端 PID 文件，尝试查找进程..."
    pkill -f "vite" && print_success "前端服务已停止" || print_info "未找到前端进程"
fi

echo ""
print_success "所有服务已停止"
echo ""
