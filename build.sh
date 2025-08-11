#!/bin/bash

# MusicStock 一键打包脚本
# 支持 macOS 和 Linux

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}" >&2
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查 Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 未安装，请先安装 Python 3"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 未安装，请先安装 pip3"
        exit 1
    fi
    
    log "依赖检查通过 ✓"
}

# 清理旧的构建文件
clean_build() {
    log "清理旧的构建文件..."
    rm -rf build/ dist/ frontend/dist/
    
    # 清理前端node_modules，保留package-lock.json用于npm ci
    if [ -d "frontend/node_modules" ]; then
        log "清理前端node_modules..."
        rm -rf frontend/node_modules/
    fi
    
    log "清理完成 ✓"
}

# 构建前端
build_frontend() {
    log "开始构建前端..."
    cd frontend
    
    log "安装前端依赖..."
    # 根据package-lock.json是否存在选择安装方式
    if [ -f "package-lock.json" ]; then
        log "使用npm ci进行清洁安装..."
        npm ci --legacy-peer-deps || {
            log "npm ci失败，尝试npm install..."
            npm install --legacy-peer-deps
        }
    else
        log "使用npm install进行安装..."
        npm install --legacy-peer-deps
    fi
    
    log "构建前端..."
    npm run build
    
    cd ..
    log "前端构建完成 ✓"
}

# 构建后端
build_backend() {
    log "开始构建后端..."
    cd backend
    
    log "检查系统Python环境..."
    # 确保使用系统Python，避免虚拟环境
    SYSTEM_PYTHON=$(which python3 || which python)
    if [ -z "$SYSTEM_PYTHON" ]; then
        error "未找到系统Python解释器"
        exit 1
    fi
    
    log "使用Python: $SYSTEM_PYTHON"
    $SYSTEM_PYTHON --version
    
    log "确保pip已安装..."
    $SYSTEM_PYTHON -m ensurepip --upgrade || true
    
    log "安装后端依赖..."
    $SYSTEM_PYTHON -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn || \
    $SYSTEM_PYTHON -m pip install -r requirements.txt
    
    log "构建后端可执行文件..."
    # 在macOS上使用onedir模式避免警告，在Linux/Windows上使用onefile
    if [[ "$OSTYPE" == "darwin"* ]]; then
        $SYSTEM_PYTHON -m PyInstaller run.py --noconsole --onedir --distpath ../build/backend --name run
    else
        $SYSTEM_PYTHON -m PyInstaller run.py --noconsole --onefile --distpath ../build/backend --name run
    fi
    
    cd ..
    log "后端构建完成 ✓"
}

# 构建 Electron 应用
build_electron() {
    log "开始构建 Electron 应用..."
    
    log "配置 Electron 镜像源..."
    export ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/"
    export ELECTRON_CUSTOM_DIR="33.0.2"
    export NPM_CONFIG_REGISTRY="https://registry.npmmirror.com"
    
    log "安装 Electron 依赖..."
    npm install
    
    log "构建应用..."
    npm run build
    
    log "Electron 应用构建完成 ✓"
}

# 显示构建结果
show_results() {
    log "构建结果:"
    
    if [ -d "dist" ]; then
        echo "构建文件位于:"
        for file in dist/*; do
            if [ -f "$file" ]; then
                echo "  - $(basename "$file")"
            fi
        done
    fi
}

# 主函数
main() {
    log "🚀 开始 MusicStock 一键打包..."
    
    # 检查是否在项目根目录
    if [ ! -f "package.json" ] || [ ! -f "main.js" ]; then
        error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行构建步骤
    check_dependencies
    clean_build
    build_frontend
    build_backend
    build_electron
    show_results
    
    log "🎉 打包完成！"
}

# 处理命令行参数
case "${1:-}" in
    "clean")
        clean_build
        ;;
    "frontend")
        build_frontend
        ;;
    "backend")
        build_backend
        ;;
    "electron")
        build_electron
        ;;
    "help"|"-h"|"--help")
        echo "用法: $0 [选项]"
        echo "选项:"
        echo "  clean     - 仅清理构建文件"
        echo "  frontend  - 仅构建前端"
        echo "  backend   - 仅构建后端"
        echo "  electron  - 仅构建 Electron 应用"
        echo "  help      - 显示此帮助信息"
        echo "  无参数   - 完整构建"
        ;;
    "")
        main
        ;;
    *)
        error "未知参数: $1"
        echo "使用 '$0 help' 查看可用选项"
        exit 1
        ;;
esac