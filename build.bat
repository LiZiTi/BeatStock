@echo off
REM MusicStock 一键打包脚本 - Windows版本
REM 支持 Windows 系统

setlocal enabledelayedexpansion

REM 颜色输出 (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "NC=[0m"

REM 日志函数
:log
echo %GREEN%[%date% %time%] %~1%NC%
goto :eof

:error
echo %RED%[ERROR] %~1%NC% 1>&2
goto :eof

:warn
echo %YELLOW%[WARNING] %~1%NC% 1>&2
goto :eof

REM 检查依赖
:check_dependencies
call :log "检查依赖..."

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    call :error "Node.js 未安装，请先安装 Node.js"
    exit /b 1
)

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    call :error "Python 未安装，请先安装 Python"
    exit /b 1
)

call :log "依赖检查通过 ✓"
goto :eof

REM 清理旧的构建文件
:clean_build
call :log "清理旧的构建文件..."
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "frontend\dist" rmdir /s /q "frontend\dist"

REM 清理前端node_modules，保留package-lock.json用于npm ci
if exist "frontend\node_modules" (
    call :log "清理前端node_modules..."
    rmdir /s /q "frontend\node_modules"
)

call :log "清理完成 ✓"
goto :eof

REM 构建前端
:build_frontend
call :log "开始构建前端..."
cd frontend

call :log "安装前端依赖..."
REM 根据package-lock.json是否存在选择安装方式
if exist "package-lock.json" (
    call :log "使用npm ci进行清洁安装..."
    npm ci --legacy-peer-deps
    if %errorlevel% neq 0 (
        call :log "npm ci失败，尝试npm install..."
        npm install --legacy-peer-deps
        if %errorlevel% neq 0 (
            call :error "前端依赖安装失败"
            exit /b 1
        )
    )
) else (
    call :log "使用npm install进行安装..."
    npm install --legacy-peer-deps
    if %errorlevel% neq 0 (
        call :error "前端依赖安装失败"
        exit /b 1
    )
)

call :log "构建前端..."
npm run build
if %errorlevel% neq 0 (
    call :error "前端构建失败"
    exit /b 1
)

cd ..
call :log "前端构建完成 ✓"
goto :eof

REM 构建后端
:build_backend
call :log "开始构建后端..."
cd backend

call :log "检查系统Python环境..."
for /f "tokens=*" %%i in ('where python 2^>nul') do set PYTHON_PATH=%%i
if "%PYTHON_PATH%"=="" (
    call :error "未找到系统Python解释器"
    exit /b 1
)

call :log "使用Python: %PYTHON_PATH%"
%PYTHON_PATH% --version

call :log "确保pip已安装..."
%PYTHON_PATH% -m ensurepip --upgrade 2>nul || (
    call :warn "pip可能需要手动安装或更新"
)

call :log "安装后端依赖..."
%PYTHON_PATH% -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    call :warn "使用清华镜像失败，尝试默认源..."
    %PYTHON_PATH% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        call :error "后端依赖安装失败"
        exit /b 1
    )
)

call :log "构建后端可执行文件..."
%PYTHON_PATH% -m PyInstaller run.py --noconsole --onefile --distpath ..\build\backend --name run --noconfirm
if %errorlevel% neq 0 (
    call :error "后端构建失败"
    exit /b 1
)

cd ..
call :log "后端构建完成 ✓"
goto :eof

REM 构建 Electron 应用
:build_electron
call :log "开始构建 Electron 应用..."

call :log "配置 Electron 镜像源..."
set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
set ELECTRON_CUSTOM_DIR=33.0.2
set NPM_CONFIG_REGISTRY=https://registry.npmmirror.com

call :log "安装 Electron 依赖..."
npm install
if %errorlevel% neq 0 (
    call :error "Electron 依赖安装失败"
    exit /b 1
)

call :log "构建应用..."
npm run build
if %errorlevel% neq 0 (
    call :error "Electron 构建失败"
    exit /b 1
)

call :log "Electron 应用构建完成 ✓"
goto :eof

REM 显示构建结果
:show_results
call :log "构建结果:"
if exist "dist" (
    echo 构建文件位于:
    for %%f in (dist\*) do (
        echo   - %%~nxf
    )
)
goto :eof

REM 主函数
:main
call :log "🚀 开始 MusicStock 一键打包..."

REM 检查是否在项目根目录
if not exist "package.json" (
    call :error "请在项目根目录运行此脚本"
    exit /b 1
)

REM 执行构建步骤
call :check_dependencies
call :clean_build
call :build_frontend
call :build_backend
call :build_electron
call :show_results

call :log "🎉 打包完成！"
goto :eof

REM 处理命令行参数
if "%1"=="clean" (
    call :clean_build
    goto :eof
)

if "%1"=="frontend" (
    call :build_frontend
    goto :eof
)

if "%1"=="backend" (
    call :build_backend
    goto :eof
)

if "%1"=="electron" (
    call :build_electron
    goto :eof
)

if "%1"=="help" (
    echo 用法: %0 [选项]
    echo 选项:
    echo   clean     - 仅清理构建文件
    echo   frontend  - 仅构建前端
    echo   backend   - 仅构建后端
    echo   electron  - 仅构建 Electron 应用
    echo   help      - 显示此帮助信息
    echo   无参数   - 完整构建
    goto :eof
)

if "%1"=="" (
    call :main
    goto :eof
)

call :error "未知参数: %1"
echo 使用 '%0 help' 查看可用选项
exit /b 1