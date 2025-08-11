# ElonMars (MusicStock) - 音乐可视化与股票分析工具

<div align="center">
  <img src="resources/ElonMars.icns" alt="ElonMars Logo" width="128" height="128">
</div>

## 🎵🎶📊 项目简介

ElonMars (又名 MusicStock) 是一个双功能的桌面应用程序，结合了音乐可视化和股票数据分析功能：

1. **BeatStock 音乐可视化模块** - 将音乐节拍与动态数据图表结合，创造独特的视听体验
2. **股票分析模块** - 基于 AKShare 的金融数据分析工具，提供巴菲特指标、资金流向等专业分析

本项目使用 Electron 将前端 Vue.js 应用和后端 Python 服务打包成跨平台桌面应用。

## 🌟 主要特性

### 音乐可视化功能 (BeatStock)
- 🎵 音频节拍检测与可视化
- 📊 多种动态图表展示模式
- 🎨 实时激光背景效果
- 🎛️ 可调节节拍与数据点对应关系
- 📁 支持多种音频格式 (MP3 等)

### 股票分析功能
- 📈 巴菲特指标分析
- 💰 板块与行业资金流向监控
- 📊 股票筹码分布分析
- 📉 ROE 历史数据分析
- 📋 十大股东信息查询
- 🕐 实时行情与分钟级交易数据

## 🏗️ 技术架构

```
ElonMars (MusicStock)
├── 前端应用 (Vue.js 3 + Electron)
│   ├── 音乐可视化界面 (BeatStock)
│   ├── 股票分析界面 (ElonIndex)
│   └── 动态图表组件系统
├── 后端服务 (Python 3 + FastAPI)
│   ├── 音频处理模块
│   ├── 金融数据接口 (AKShare)
│   └── 数据缓存与处理
└── 打包系统 (Electron Builder)
    ├── Windows 支持
    ├── macOS 支持
    └── Linux 支持 (计划中)
```

### 核心技术栈
- **前端**: Vue 3, Electron, ECharts, Vxe-Table
- **后端**: Python 3, FastAPI, AKShare
- **音频处理**: Librosa (节拍检测)
- **打包工具**: Electron Builder, PyInstaller
- **数据源**: AKShare (金融数据), 本地音频文件

## 🚀 快速开始

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Node.js**: 14.x 或更高版本
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM (推荐 8GB+)
- **存储**: 500MB 可用空间

### 安装与运行

#### 方法一：使用预编译版本 (推荐)
从 [Releases](https://github.com/your-username/ElonMars/releases) 下载对应平台的安装包：
- **Windows**: 下载 `.exe` 文件
- **macOS**: 下载 `.dmg` 文件
- **Linux**: 下载 `.AppImage` 文件

#### 方法二：从源码运行

1. **克隆项目**
```bash
git clone https://github.com/your-username/ElonMars.git
cd ElonMars
```

2. **安装前端依赖**
```bash
cd frontend
npm install
cd ..
```

3. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

4. **运行开发模式**
```bash
# 启动前端开发服务器
cd frontend
npm run serve

# 在新终端中启动后端服务
cd backend
python run.py
```

5. **运行桌面应用**
```bash
# 安装 Electron 依赖
npm install

# 启动 Electron 应用
npm start
```

### 构建与打包

#### 一键打包 (推荐)
```bash
# macOS/Linux
chmod +x build.sh
./build.sh

# Windows
build.bat
```

#### 使用 npm 脚本
```bash
# 完整打包
npm run package

# 仅打包 Windows 版本
npm run package:win

# 仅打包 macOS 版本
npm run package:mac

# 打包所有平台
npm run package:all
```

#### 清理后重新打包
```bash
npm run build:clean
```

## 🎛️ 使用指南

### 音乐可视化模式
1. 启动应用后，默认进入 BeatStock 音乐可视化界面
2. 从下拉菜单选择音频文件
3. 选择可视化图表类型
4. 点击播放按钮开始体验音乐可视化

### 股票分析模式
1. 在应用中切换到股票分析界面
2. 使用搜索功能查找股票
3. 查看各类金融指标和分析图表

## 📁 项目结构

```
ElonMars/
├── backend/                    # 后端服务
│   ├── app/                    # 主应用逻辑
│   ├── audio_files/            # 音频文件目录
│   ├── config/                 # 配置文件
│   ├── indicators/             # 金融指标计算模块
│   ├── requirements.txt        # Python 依赖
│   └── run.py                  # 后端入口文件
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/         # 共享组件
│   │   ├── dancerPages/        # 动态图表组件
│   │   ├── assets/             # 静态资源
│   │   └── App.vue             # 主应用组件
│   └── package.json            # 前端依赖配置
├── resources/                  # 应用资源文件
├── main.js                     # Electron 主进程
├── loading.html                # 加载页面
└── package.json                # 项目配置与脚本
```

## 🔧 配置说明

### 环境变量
```bash
# 后端配置
API_PORT=8088                  # 后端服务端口
AUDIO_FILES_DIR=./audio_files  # 音频文件目录
```

### 自定义音频文件
将 MP3 文件放入 `backend/audio_files/` 目录，应用会自动扫描并显示在音乐选择列表中。

## 📊 数据源说明

### 金融数据
本项目使用 [AKShare](https://github.com/akfamily/akshare) 作为主要数据源，提供：
- A股实时行情
- 财务数据
- 资金流向
- 宏观经济指标

### 音频数据
支持本地 MP3 文件，应用内置节拍检测算法。

## 🤝 贡献指南

欢迎任何形式的贡献！

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 前端遵循 Vue.js 官方风格指南
- 后端遵循 PEP 8 Python 编码规范
- 提交前运行相应测试

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **邮箱**: ok_ai@outlook.com
- **项目地址**: [https://github.com/your-username/ElonMars](https://github.com/your-username/ElonMars)

## 🙏 致谢

- [AKShare](https://github.com/akfamily/akshare) - 提供金融数据支持
- [Vue.js](https://vuejs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Electron](https://www.electronjs.org/) - 桌面应用框架
- [Librosa](https://librosa.org/) - 音频分析库

## ⚠️ 免责声明

本软件仅供学习和研究使用，不构成任何投资建议。金融数据仅供参考，投资有风险，入市需谨慎。