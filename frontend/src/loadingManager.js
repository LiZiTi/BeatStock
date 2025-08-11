// loadingManager.js
import { reactive } from 'vue';

export const loadingManager = reactive({
  loadingStatus: {},

  startLoading(moduleId) {
    console.log('startLoading:', moduleId);
    this.loadingStatus[moduleId] = true;
  },

  stopLoading(moduleId) {
    console.log('stopLoading:', moduleId);
    this.loadingStatus[moduleId] = false;
  },

  isLoading(moduleId) {
    return this.loadingStatus[moduleId] || false;
  }
});