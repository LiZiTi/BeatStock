# MusicStock 一键打包指南

## 🚀 快速开始

### 一键打包（推荐）

#### macOS/Linux
```bash
chmod +x build.sh
./build.sh
```

#### Windows
双击运行 `build.bat` 文件，或在命令行中执行：
```cmd
build.bat
```

### 使用 npm 脚本
```bash
# 完整打包
npm run package

# 仅打包 Windows 版本
npm run package:win

# 仅打包 macOS 版本
npm run package:mac

# 打包所有平台
npm run package:all

# 清理后重新打包
npm run build:clean
```

## 📋 系统要求

### 必需依赖
- **Node.js** (>= 14.x) - [下载地址](https://nodejs.org/)
- **Python** (>= 3.8) - [下载地址](https://www.python.org/)
- **pip** (通常随 Python 安装)

### 可选依赖（自动安装）
- electron-builder
- PyInstaller

## 🎯 使用场景

### 完整构建
```bash
# 执行完整构建流程
./build.sh
# 或
build.bat
```

### 部分构建
```bash
# 仅构建前端
./build.sh frontend
# 或
build.bat frontend

# 仅构建后端
./build.sh backend
# 或
build.bat backend

# 仅构建 Electron 应用
./build.sh electron
# 或
build.bat electron
```

### 清理构建文件
```bash
./build.sh clean
# 或
build.bat clean
```

## 📦 构建输出

构建完成后，可在以下目录找到打包文件：

- **macOS**: `dist/ElonMars-1.0.0.dmg`
- **Windows**: `dist/ElonMars Setup 1.0.0.exe`
- **Linux**: `dist/elonmars-stock-1.0.0.AppImage`

## 🔧 故障排除

### 常见问题

1. **权限问题** (macOS/Linux)
   ```bash
   chmod +x build.sh
   ```

2. **Python 版本问题**
   确保 Python 3 已安装并添加到 PATH

3. **Node.js 版本问题**
   确保 Node.js 版本 >= 14.x

4. **构建失败**
   先运行清理命令再重新构建：
   ```bash
   ./build.sh clean
   ./build.sh
   ```

### 调试模式

如需查看详细构建日志，可以：

1. **macOS/Linux**: 添加 `-x` 参数
   ```bash
   bash -x build.sh
   ```

2. **Windows**: 使用 PowerShell
   ```powershell
   powershell -ExecutionPolicy Bypass -File build.ps1
   ```

## 📝 自定义配置

### 修改打包配置
编辑 `package.json` 中的 `build` 部分：

```json
{
  "build": {
    "appId": "com.yourcompany.app",
    "productName": "YourAppName",
    "directories": {
      "output": "release"
    }
  }
}
```

### 添加新平台支持
在 `package.json` 中添加新的平台配置：

```json
{
  "linux": {
    "target": "AppImage",
    "icon": "resources/icon.png"
  }
}
```

## 🔄 持续集成

### GitHub Actions 示例
```yaml
name: Build and Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Build
        run: npm run package
```

## 📞 支持

如遇到问题，请检查：
1. 所有依赖是否已正确安装
2. 是否在项目根目录运行脚本
3. 查看构建日志获取详细错误信息