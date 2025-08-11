import axios from 'axios';
import { loadingManager } from './loadingManager';

const api = axios.create({
  baseURL: process.env.VUE_APP_BASE_URL,
  timeout: 180000, // 超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

const xlApi = axios.create({
  baseURL: process.env.VUE_APP_XINLANG_URL,
  timeout: 180000, // 超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 为 `api` 添加请求和响应拦截器
api.interceptors.request.use(config => {
  if (config.moduleId) {
    loadingManager.startLoading(config.moduleId);
  }
  return config;
}, error => {
  return Promise.reject(error);
});

api.interceptors.response.use(response => {
  if (response.config.moduleId) {
    loadingManager.stopLoading(response.config.moduleId);
  }
  return response;
}, error => {
  return Promise.reject(error);
});

// 为 `xlApi` 添加请求和响应拦截器
xlApi.interceptors.request.use(config => {
  if (config.moduleId) {
    loadingManager.startLoading(config.moduleId);
  }
  return config;
}, error => {
  return Promise.reject(error);
});

xlApi.interceptors.response.use(response => {
  if (response.config.moduleId) {
    loadingManager.stopLoading(response.config.moduleId);
  }
  return response;
}, error => {
  return Promise.reject(error);
});

export { api, xlApi };
