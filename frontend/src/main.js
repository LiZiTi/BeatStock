import { createApp } from 'vue';
import App from './App.vue';
import axios from 'axios';
import { loadingManager } from './loadingManager';
import '@fortawesome/fontawesome-free/css/all.css';
import "@/assets/fonts.css"; 
import "@/assets/global.css"; // 引入全局样式文件

import VxeUI from 'vxe-pc-ui'
import 'vxe-pc-ui/lib/style.css'
import VxeUITable from 'vxe-table'
import 'vxe-table/lib/style.css'

// 创建 Vue 应用实例
const app = createApp(App);

// 将 axios 实例和 loadingManager 挂载到全局属性上
app.config.globalProperties.$axios = axios;
app.config.globalProperties.$loadingManager = loadingManager;

VxeUI.setTheme('dark')
app.use(VxeUI);
app.use(VxeUITable);
// 将应用挂载到 DOM
app.mount('#app');