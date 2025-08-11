<template>
  <div class="music-visualizer">
    <!-- 激光射线背景 -->
    <div class="laser-background" ref="laserBackground"></div>

    <!-- 控制区域 -->
    <div class="outer-border">
      <div class="controls">
        <!-- 音乐选择 -->
        <div class="control-item">
          <label id="beatdataLogo" ref="beatdataLogo">
            <i class="fas fa-music"></i>&nbsp;&nbsp;BeatData
          </label>
        </div>
        <!-- 音乐选择 -->
        <div class="control-item">
          <label><i class="fas fa-volume-up"></i> </label>
          <select v-model="selectedMusic" @change="onMusicChange">
            <option v-for="music in musicList" :value="music.file" :key="music.file">
              {{ music.name }}
            </option>
          </select>
        </div>
        <div class="control-item">
          <label><i class="fas fa-volume-up"></i> </label>
          <select v-model="beatsPerData" @change="onBeatsChange">
            <option value="1" selected>1</option>
            <option value="2" selected>2</option>
            <option value="4" selected>4</option>
            <option value="8" selected>8</option>
          </select>
        </div>

        <!-- 图表选择 -->
        <div class="control-item">
          <label><i class="fas fa-chart-bar"></i></label>
          <select v-model="selectedChart" @change="onChartChange">
            <option v-for="chart in chartList" :value="chart.value" :key="chart.value">
              {{ chart.name }}
            </option>
          </select>
        </div>
        <!-- 图表选择 -->
        <div class="control-item">
          <label><i class="fas fa-chart-bar"></i></label>
          <select v-model="beatsKeepInChart" @change="onChartKeepChange">
            <option value="36" selected>36</option>
            <option value="66" selected>66</option>
            <option value="96" selected>96</option>
            <option value="-1" selected>All</option>
          </select>
        </div>
        <!-- 音频播放器 -->
        <audio v-if="audioSrc" ref="audio" :src="audioSrc" controls class="audio-preview" @play="onPlay"
          @pause="onPause" @ended="onEnded"></audio>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div class="chart-container" v-if="selectedChartComponent">
      <component :is="selectedChartComponent" ref="chartComponent" :total-beats="beatTimes.length"
        :beats-per-data="beatsPerData" />
    </div>
  </div>
</template>

<script>
import { api } from "@/axiosConfig";

// 使用 require.context 动态扫描 ./components/ 下的所有 .vue 文件
const requireComponent = require.context('./dancerPages', false, /\.vue$/);

export default {
  name: 'MusicVisualizer',
  components: {},
  data() {
    return {
      clickSound: null,
      typingSound: null,
      musicList: [], // 音频列表，将从后端获取
      chartList: [], // 图表组件列表，将动态生成
      selectedMusic: null, // 选中的音频文件
      beatsPerData: 1,
      beatsKeepInChart: 36,
      selectedChart: 'ReportIndex2', // 选中的图表组件
      selectedChartComponent: null, // 当前展示的图表组件
      audioSrc: '', // 音频源路径
      beatTimes: [], // 节拍时间列表
      beatTimeouts: [], // 定时器列表，用于清理
      currentColorIndex: 0
    };
  },
  async created() {
    await this.fetchMusicList(); // 获取音频列表
    this.loadChartComponents(); // 动态加载图表组件
    this.onChartChange();
  },
  methods: {
    // 获取音频列表
    async fetchMusicList() {
      try {
        const response = await api.get('/get_audio_files/');
        this.musicList = response.data;
      } catch (error) {
        console.error('Error fetching music list:', error);
      }
    },

    // 动态加载图表组件并生成列表
    loadChartComponents() {
      requireComponent.keys().forEach((fileName) => {
        const componentConfig = requireComponent(fileName);
        const componentName = fileName.replace(/^\.\/(.*)\.vue$/, '$1');
        const component = componentConfig.default || componentConfig;

        // 读取 pageName，如果不存在则默认使用组件名
        const pageName = component.pageName || componentName;

        // 注册组件
        this.$options.components[componentName] = component;

        // 添加到 chartList
        this.chartList.push({ name: pageName, value: componentName });
      });
    },

    onBeatsChange() {

    },
    // 当音频发生变化时
    async onMusicChange() {
      if (!this.selectedMusic) {
        this.stopAudio();
        this.audioSrc = '';
        return;
      }

      this.stopAudio();
      this.clearBeatTimeouts();

      // 设置新音频源
      this.audioSrc = `http://localhost:8088/audio_files/${this.selectedMusic}`;

      // 获取新节拍数据
      await this.fetchBeatTimes();
      // 通知子组件重新计算数据并重置状态
      const chartComponent = this.$refs.chartComponent;
      if (chartComponent && chartComponent.resetData) {
        chartComponent.resetData(this.beatTimes.length);
      }
      // 自动播放新音频
      // this.playAudio();
    },
    // 获取音频的节拍时间
    async fetchBeatTimes() {
      if (!this.selectedMusic) return;
      try {
        const response = await api.get('/getBeatTimes', {
          params: { audio_file_name: this.selectedMusic },
        });
        const data = response.data;
        if (data.error) {
          console.error('Error from server:', data.error);
          return;
        }
        this.beatTimes = data.beatTimes;

      } catch (error) {
        console.error('Error fetching beat times:', error);
      }
    },

    // 播放音频
    playAudio() {
      const audioElement = this.$refs.audio;
      if (audioElement) {
        
        // 更新图表以反映新的节拍数量
        this.updateChartForBeats();
        audioElement.play();
      }
    },

    // 停止音频
    stopAudio() {
      const audioElement = this.$refs.audio;
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0; // 重置播放进度
      }
    },

    // 当音频开始播放时
    onPlay() {
      const audioElement = this.$refs.audio;
      if (!Array.isArray(this.beatTimes) || this.beatTimes.length === 0) {
        console.warn('Beat times are not ready yet.');
        return;
      }

      this.clearBeatTimeouts();
      this.scheduleChartBeats(audioElement.currentTime);
    },
    onPause() {
      console.log("Audio paused. Stopping all actions.");
      // 清理所有节拍定时器
      this.clearBeatTimeouts();
      // 通知子组件停止更新
      const chartComponent = this.$refs.chartComponent;
      if (chartComponent && chartComponent.stopUpdates) {
        chartComponent.stopUpdates();
      }
    },
    // 更新图表联动逻辑
    updateChartForBeats() {
      const audioElement = this.$refs.audio;
      if (audioElement && !audioElement.paused) {
        this.scheduleChartBeats(audioElement.currentTime);
      }
    },
    beatLogo() {
      const element = this.$refs.beatdataLogo;

      if (!element) {
        console.error("BeatData logo element not found.");
        return;
      }

      // 七色光数组（七色顺序：红、橙、黄、绿、青、蓝、紫）
      const rainbowColors = [
        'rgba(255, 0, 0, 0.8)',    // 红色
        'rgba(255, 165, 0, 0.8)',  // 橙色
        'rgba(255, 255, 0, 0.8)',  // 黄色
        'rgba(0, 255, 0, 0.8)',    // 绿色
        'rgba(0, 255, 255, 0.8)',  // 青色
        'rgba(0, 0, 255, 0.8)',    // 蓝色
        'rgba(128, 0, 128, 0.8)'   // 紫色
      ];

      // 获取当前颜色
      const currentGlowColor = rainbowColors[this.currentColorIndex];

      // 设置文字光晕（text-shadow）
      element.style.textShadow = `0 0 10px ${currentGlowColor}, 0 0 20px ${currentGlowColor}`;

      // 更新颜色索引，循环回到开头
      this.currentColorIndex = (this.currentColorIndex + 1) % rainbowColors.length;

      // 移除动画类以确保重新触发
      element.classList.remove('beat-animation');

      // 强制 DOM 重绘
      void element.offsetWidth;

      // 添加动画类
      element.classList.add('beat-animation');

      // 动画结束后清理动画类（保留文字光晕效果）
      element.addEventListener(
        'animationend',
        () => {
          element.classList.remove('beat-animation');
        },
        { once: true }
      );
    },
    // 根据节拍时间安排图表更新
    scheduleChartBeats(startTime) {
      if (!this.beatTimes.length || !this.selectedChartComponent) return;
      const audioElement = this.$refs.audio;
      const playbackRate = audioElement ? audioElement.playbackRate : 1;

      const currentTime = startTime || 0;

      this.beatTimes.forEach((beatTime) => {
        const adjustedBeatTime = (beatTime - currentTime) / playbackRate;

        const delay = adjustedBeatTime * 1000;
        if (delay >= 0) {
          const timeout = setTimeout(() => {
            this.beatLogo();
            this.triggerChartBeat(); // 触发图表更新
          }, delay);
          this.beatTimeouts.push(timeout);
        }
      });
    },

    // 清理节拍定时器
    clearBeatTimeouts() {
      this.beatTimeouts.forEach((timeout) => clearTimeout(timeout));
      this.beatTimeouts = [];
    },

    // 当图表组件发生变化时
    onChartChange() {
      this.selectedChartComponent = this.selectedChart;
      this.clearBeatTimeouts();
    },
    onChartKeepChange() {
      const chartComponent = this.$refs.chartComponent;
      if (chartComponent && chartComponent.updateChartOnBeat) {
        chartComponent.setMaxDisplayPoints(this.beatsKeepInChart);
      }
    },
    // 触发图表跳动和激光效果
    triggerChartBeat() {
      this.triggerChartAnimation(); // 图表跳动逻辑
      this.triggerLaserAnimation(); // 激光动画联动
    },

    // 独立图表跳动逻辑
    triggerChartAnimation() {
      const chartComponent = this.$refs.chartComponent;
      if (chartComponent && chartComponent.updateChartOnBeat) {
        chartComponent.updateChartOnBeat();
      }
    },

    // 激光动画联动
    triggerLaserAnimation(beatInterval) {
      const laserElement = this.$refs.laserBackground;
      if (laserElement) {
        const generateRandomColor = () =>
          `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.8)`;

        const randomColors = Array.from({ length: 10 }, generateRandomColor);
        const randomDeg = Math.floor(Math.random() * 360);

        laserElement.style.background = `repeating-linear-gradient(
      ${randomDeg}deg,
      ${randomColors.join(', ')},
      transparent
    )`;
        laserElement.style.backgroundSize = '200% 200%';
        laserElement.style.backgroundPosition = `${Math.random() * 100}% ${Math.random() * 100}%`;

        const animationDuration = beatInterval / 1000; // 转换为秒
        laserElement.style.animation = `rotateLaser ${animationDuration}s linear`;

        laserElement.classList.add('active');
        setTimeout(() => {
          laserElement.classList.remove('active');
        }, animationDuration * 1000);
      }
    },
    playMouseClickSound() {
      if (this.clickSound) {
        const audio = this.clickSound.cloneNode(); // 克隆 Audio 对象
        audio.play();
      }
    },
    playTypingSound() {
      if (this.typingSound) {
        const audio = this.typingSound.cloneNode(); // 克隆 Audio 对象
        audio.play();
      }
    }
  },
  mounted() {

    // 在组件挂载时初始化音频对象
    this.clickSound = new Audio(require('@/assets/click.mp3'));
    this.typingSound = new Audio(require('@/assets/typing.mp3'));
    this.clickSound.load();
    this.typingSound.load();


    document.addEventListener("keydown", this.playTypingSound, true);
    document.addEventListener("change", this.playMouseClickSound, true);
    document.addEventListener("click", this.playMouseClickSound, true);
    const audioElement = this.$refs.audio;
    if (audioElement) {
      audioElement.addEventListener('ratechange', this.onRateChange);
    }
  },
  beforeUnmount() {
    document.removeEventListener("keydown", this.playTypingSound, true);
    document.removeEventListener("change", this.playMouseClickSound, true);
    document.removeEventListener("click", this.playMouseClickSound, true);
    const audioElement = this.$refs.audio;
    if (audioElement) {
      audioElement.removeEventListener('ratechange', this.onRateChange);
    }
    this.clearBeatTimeouts();
    this.stopAudio();
  },
};
</script>

<style>
body {
  margin: 0;
  /* 去掉浏览器默认的边距 */
  padding: 0;
  overflow-x: hidden;
  /* 禁止水平滚动条 */
}

html {
  overflow-x: hidden;
  /* 彻底禁止水平滚动条 */
}
</style>

<style scoped>
.music-visualizer {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100vw;
  height: 100vh; /* 让容器占满整个屏幕 */
  box-sizing: border-box;
  padding: 24px; /* 控制整体的左右上下内边距 */
  overflow: hidden;
}

.outer-border {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  width: calc(100% - 48px); /* 减去左右的 padding */
  margin: 0 auto; /* 居中对齐 */
  border: 2px solid #ffffff;
  padding: 10px;
  background-color: #ffffffa8;
  color: white;
  margin-bottom: 24px; /* 控制区域与图表区域间距 */
}

.controls {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: left;
  align-items: center;
  border-radius: 12px;
  padding: 10px;
  background-color: #252a34dd;
  color: white;
}

.chart-container {
  flex: 1; /* 自动填充剩余高度 */
  border: 2px solid #ffffff;
  padding: 10px;
  background-color: #ffffffa8;
  overflow: auto; /* 如果内容过多可以滚动 */
  width: calc(100% - 48px); /* 保持与左右边距一致 */
  margin: 0 auto; /* 居中对齐 */
}

@media (max-width: 768px) {
  .music-visualizer {
    padding: 16px; /* 小屏幕减小内边距 */
  }

  .outer-border,
  .chart-container {
    width: calc(100% - 32px); /* 动态调整宽度 */
  }

  .controls {
    flex-direction: column; /* 控制区域换行显示 */
    align-items: stretch;
  }
}

@keyframes rotateLaser {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
    /* 一次完整旋转 */
  }
}

.laser-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;

  /* 默认射线效果 */
  background: repeating-linear-gradient(45deg,
      rgba(255, 0, 0, 0.5),
      rgba(0, 255, 0, 0.5),
      rgba(0, 0, 255, 0.5),
      rgba(255, 255, 0, 0.5),
      transparent);
  background-size: 200% 200%;
  background-position: 50% 50%;
  transition: background-position 0.2s linear;

  /* 初始化旋转 */
  transform-origin: center;
}

/* 控制项样式 */
.control-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 20px;
  margin-right: 20px;
}

/* 选择框样式 */
select {
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
}

/* 音频预览样式 */
.audio-preview {
  margin-left: auto;
  width: 300px;
  height: 30px;
}


@keyframes beat {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.2);
  }

  100% {
    transform: scale(1);
  }
}

.beat-animation {
  animation: beat 0.3s ease-in-out;
}
</style>