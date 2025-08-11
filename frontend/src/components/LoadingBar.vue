<template>
  <div v-if="isLoading" class="loading-bar">
    <h3 class="loading-text">加载中...</h3>
    <div class="loading-spinner"></div>
  </div>
</template>

<script>
export default {
  props: {
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  watch: {
    isLoading(newVal) {
      console.log("LoadingBar isLoading:", newVal); // 检查 isLoading 是否更新
    }
  }
};
</script>

<style scoped>
.loading-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.8); /* 黑色半透明背景 */
  z-index: 9999; /* 确保加载动画在最上层 */
}

.loading-text {
  color: #ffffff;
  font-size: 24px;
  margin-bottom: 20px;
  animation: pulse 1.5s ease-in-out infinite; /* 呼吸效果 */
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 8px solid rgba(255, 255, 255, 0.3); /* 调整背景边框颜色，使其半透明 */
  border-top: 8px solid #3498db; /* 使前景色更明显 */
  border-radius: 50%;
  animation: spin 0.6s linear infinite; /* 加快旋转速度 */
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
  100% { opacity: 0.7; transform: scale(1); }
}
</style>