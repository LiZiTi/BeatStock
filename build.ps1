# MusicStock 一键打包脚本 - PowerShell版本
# 支持 Windows 系统的高级功能

param(
    [string]$Action = "full",
    [switch]$Clean,
    [switch]$Frontend,
    [switch]$Backend,
    [switch]$Electron,
    [switch]$Verbose,
    [switch]$Help
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出
$Colors = @{
    Green = "Green"
    Red = "Red"
    Yellow = "Yellow"
    Cyan = "Cyan"
}

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { $Colors.Red }
        "WARNING" { $Colors.Yellow }
        "SUCCESS" { $Colors.Green }
        default { $Colors.Cyan }
    }
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# 检查依赖
function Test-Dependencies {
    Write-Log "检查依赖..."
    
    # 检查 Node.js
    try {
        $nodeVersion = node --version
        Write-Log "Node.js 版本: $nodeVersion"
    } catch {
        Write-Log "Node.js 未安装，请先安装 Node.js" -Level "ERROR"
        return $false
    }
    
    # 检查 Python
    try {
        $pythonVersion = python --version
        Write-Log "Python 版本: $pythonVersion"
    } catch {
        Write-Log "Python 未安装，请先安装 Python" -Level "ERROR"
        return $false
    }
    
    # 检查 pip
    try {
        $pipVersion = pip --version
        Write-Log "Pip 可用"
    } catch {
        Write-Log "pip 未安装，请先安装 pip" -Level "ERROR"
        return $false
    }
    
    Write-Log "依赖检查通过 ✓" -Level "SUCCESS"
    return $true
}

# 清理旧的构建文件
function Clear-Build {
    Write-Log "清理旧的构建文件..."
    
    $pathsToClean = @("build", "dist", "frontend\dist")
    foreach ($path in $pathsToClean) {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force
            Write-Log "已清理: $path"
        }
    }
    
    Write-Log "清理完成 ✓" -Level "SUCCESS"
}

# 构建前端
function Build-Frontend {
    Write-Log "开始构建前端..."
    
    Set-Location -Path "frontend"
    
    Write-Log "安装前端依赖..."
    npm install --legacy-peer-deps
    if ($LASTEXITCODE -ne 0) {
        throw "前端依赖安装失败"
    }
    
    Write-Log "构建前端..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "前端构建失败"
    }
    
    Set-Location -Path ".."
    Write-Log "前端构建完成 ✓" -Level "SUCCESS"
}

# 构建后端
function Build-Backend {
    Write-Log "开始构建后端..."
    Set-Location -Path "backend"
    
    Write-Log "安装后端依赖..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "后端依赖安装失败"
    }
    
    Write-Log "安装 PyInstaller..."
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 安装失败"
    }
    
    Write-Log "构建后端可执行文件..."
    python -m PyInstaller run.py --noconsole --onefile --distpath ..\build\backend
    if ($LASTEXITCODE -ne 0) {
        throw "后端构建失败"
    }
    
    Set-Location -Path ".."
    Write-Log "后端构建完成 ✓" -Level "SUCCESS"
}

# 构建 Electron 应用
function Build-Electron {
    Write-Log "开始构建 Electron 应用..."
    
    Write-Log "配置 Electron 镜像源..."
    $env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
    $env:ELECTRON_CUSTOM_DIR = "33.0.2"
    $env:NPM_CONFIG_REGISTRY = "https://registry.npmmirror.com"
    
    Write-Log "安装 Electron 依赖..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "Electron 依赖安装失败"
    }
    
    Write-Log "构建应用..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Electron 构建失败"
    }
    
    Write-Log "Electron 应用构建完成 ✓" -Level "SUCCESS"
}

# 显示构建结果
function Show-Results {
    Write-Log "构建结果:" -Level "SUCCESS"
    
    if (Test-Path "dist") {
        Write-Log "构建文件位于:"
        Get-ChildItem -Path "dist" -File | ForEach-Object {
            Write-Log "  - $($_.Name)"
        }
    }
}

# 显示帮助
function Show-Help {
    Write-Log @"
用法: .\build.ps1 [参数]

参数:
  -Action full|clean|frontend|backend|electron - 指定操作类型
  -Clean - 清理构建文件
  -Frontend - 仅构建前端
  -Backend - 仅构建后端
  -Electron - 仅构建 Electron 应用
  -Verbose - 显示详细输出
  -Help - 显示此帮助信息

示例:
  .\build.ps1                    # 完整构建
  .\build.ps1 -Clean            # 仅清理
  .\build.ps1 -Frontend         # 仅构建前端
  .\build.ps1 -Action backend   # 仅构建后端
"@
}

# 主函数
function Invoke-MainBuild {
    Write-Log "🚀 开始 MusicStock 一键打包..." -Level "SUCCESS"
    
    # 检查是否在项目根目录
    if (-not (Test-Path "package.json") -or -not (Test-Path "main.js")) {
        Write-Log "请在项目根目录运行此脚本" -Level "ERROR"
        exit 1
    }
    
    try {
        # 检查依赖
        if (-not (Test-Dependencies)) {
            exit 1
        }
        
        # 根据参数执行相应操作
        switch ($Action.ToLower()) {
            "clean" { Clear-Build }
            "frontend" { Build-Frontend }
            "backend" { Build-Backend }
            "electron" { Build-Electron }
            "full" {
                Clear-Build
                Build-Frontend
                Build-Backend
                Build-Electron
                Show-Results
            }
            default {
                Write-Log "未知操作: $Action" -Level "ERROR"
                Show-Help
                exit 1
            }
        }
        
        Write-Log "🎉 打包完成！" -Level "SUCCESS"
    } catch {
        Write-Log "构建失败: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

# 处理命令行参数
if ($Help) {
    Show-Help
    exit 0
}

# 处理开关参数
if ($Clean) { $Action = "clean" }
if ($Frontend) { $Action = "frontend" }
if ($Backend) { $Action = "backend" }
if ($Electron) { $Action = "electron" }

# 执行主函数
Invoke-MainBuild