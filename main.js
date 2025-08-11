const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;
let backendStarted = false;
let frontendReady = false;

const logFilePath = path.join(app.getPath('userData'), 'app-log.log');

// Simple logger
function log(message) {
  const logMessage = `${new Date().toISOString()} - ${message}\n`;
  fs.appendFileSync(logFilePath, logMessage);
  console.log(message); // Also log to console
}

function startBackend() {
  const isDev = !app.isPackaged;
  let backendPath;
  let processArgs = [];
  
  // 添加启动超时机制
  let backendStartupTimeout;
  
  if (isDev) {
    log('Running in development mode.');
    backendPath = 'python3'; // Use python3, it's more standard. 'python' can be v2.
    processArgs = [path.join(__dirname, 'backend', 'run.py')];
  } else {
    log('Running in packaged mode.');
    const platform = process.platform;
    const executableName = platform === 'win32' ? 'run.exe' : 'run';
    backendPath = path.join(process.resourcesPath, 'backend', executableName);
    
    // On non-windows, ensure the file is executable
    if (platform !== 'win32') {
      try {
        fs.chmodSync(backendPath, 0o755);
        log(`Made backend executable: ${backendPath}`);
      } catch (err) {
        log(`Error setting backend executable permissions: ${err}`);
      }
    }
  }

  log(`Attempting to start backend with path: ${backendPath}`);
  if (processArgs.length > 0) {
    log(`With arguments: ${processArgs.join(' ')}`);
  }

  backendProcess = spawn(backendPath, processArgs);
  
  // 设置启动超时（30秒）
  backendStartupTimeout = setTimeout(() => {
    if (!backendStarted) {
      log('Backend startup timeout. Proceeding with UI load.');
      // Send timeout message to frontend
      if (mainWindow) {
        mainWindow.webContents.send('backend-loading-status', {
          status: 'timeout',
          message: '后端服务启动超时，部分功能可能无法使用'
        });
      }
      backendStarted = true;
      if (frontendReady) {
        loadMainApp();
      }
    }
  }, 30000);

  const handleData = (source, data) => {
    const message = data.toString().trim();
    log(`Backend ${source}: ${message}`);
    
    // Send loading progress to frontend
    if (mainWindow) {
      if (message.includes('正在加载') || message.includes('加载')) {
        mainWindow.webContents.send('backend-loading-status', {
          status: 'loading',
          message: message
        });
      } else if (message.includes('完成') || message.includes('完成')) {
        mainWindow.webContents.send('backend-loading-status', {
          status: 'loading',
          message: message
        });
      }
    }
    
    if (message.includes('Uvicorn') && message.includes('running')) {
      log('Backend has started successfully.');
      clearTimeout(backendStartupTimeout); // 清除超时
      backendStarted = true;
      // Send success message to frontend
      if (mainWindow) {
        mainWindow.webContents.send('backend-loading-status', {
          status: 'ready',
          message: '后端服务已就绪'
        });
      }
      if (frontendReady) {
        loadMainApp();
      }
    }
  };

  backendProcess.stdout.on('data', (data) => handleData('STDOUT', data));
  backendProcess.stderr.on('data', (data) => handleData('STDERR', data));

  backendProcess.on('close', (code) => {
    log(`Backend process exited with code ${code}`);
    clearTimeout(backendStartupTimeout); // 清除超时
    // Send exit message to frontend
    if (mainWindow) {
      mainWindow.webContents.send('backend-loading-status', {
        status: 'error',
        message: `后端服务已退出 (代码: ${code})`
      });
    }
  });

  backendProcess.on('error', (err) => {
    log(`Failed to start backend process: ${err}`);
    clearTimeout(backendStartupTimeout); // 清除超时
    // Send error message to frontend
    if (mainWindow) {
      mainWindow.webContents.send('backend-loading-status', {
        status: 'error',
        message: `后端服务启动失败: ${err.message}`
      });
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    show: false // Don't show until content is ready
  });

  const loadingPath = path.join(__dirname, 'loading.html');
  mainWindow.loadFile(loadingPath);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // More robust check for when the frontend is actually ready
  mainWindow.webContents.on('did-finish-load', () => {
      // This event fires for every page load, including loading.html
      if(mainWindow.webContents.getURL().includes('loading.html')) {
          log('Loading screen finished loading.');
          frontendReady = true;
          if (backendStarted) {
              loadMainApp();
          }
      }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function loadMainApp() {
    if (!mainWindow || !backendStarted) {
        log('Aborting loadMainApp: main window or backend not ready.');
        return;
    }
    log('Loading main application content.');
    // In production, files are relative to the app's root.
    const mainAppPath = path.join(__dirname, 'frontend', 'dist', 'index.html');
    mainWindow.loadFile(mainAppPath);
}

function setupMenu() {
    const template = [
        {
          label: 'App',
          submenu: [
            { role: 'reload' },
            { role: 'forcereload' },
            { role: 'toggledevtools' },
            { type: 'separator' },
            { role: 'quit' }
          ]
        }
      ];
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

app.on('ready', () => {
  setupMenu();
  createWindow();
  startBackend();
});

app.on('will-quit', () => {
  if (backendProcess) {
    log('Killing backend process.');
    backendProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
