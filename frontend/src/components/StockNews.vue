<template>
  <div id="main" class="news-ticker-view">
    <!-- 滚动的新闻标题容器 -->
    <div class="news-ticker" ref="ticker" @animationiteration="fetchStockNews">
      <div
        v-for="(news, index) in newsData"
        :key="index"
        class="news-item"
        :style="{ color: getColor(news.情感得分) }"
        @mouseover="pauseScroll(news.内容, $event)"
        @mouseleave="resumeScroll"
      >
        <span class="news-title">{{ news.标题 }}</span>
        <span class="news-time">{{ news.时间 }}</span>
      </div>
    </div>

    <!-- 弹出窗口 -->
    <div v-if="tooltipVisible" class="tooltip" :style="{ top: tooltipPosition.top + 'px', left: tooltipPosition.left + 'px' }">
      <p>{{ tooltipContent }}</p>
    </div>
  </div>
</template>

<script>
import { api } from "@/axiosConfig";

export default {
  data() {
    return {
      newsData: [], // 保存获取到的新闻数据
      tooltipVisible: false, // 控制弹出窗口的显示
      tooltipContent: "", // 弹出窗口显示的内容
      tooltipPosition: { top: 0, left: 0 }, // 弹出窗口的位置
    };
  },
  methods: {
    async fetchStockNews() {
      try {
        const response = await api.get(`/news`);
        this.newsData = response.data
          .sort((a, b) => new Date(b.时间) - new Date(a.时间)) // 按时间倒序排序
          .slice(0, 20); // 每次获取20条新闻
      } catch (error) {
        console.error("Error fetching stock news:", error);
      }
    },
    showTooltip(content, event) {
      this.tooltipContent = content;
      this.tooltipVisible = true;

      // 更新弹出窗口的位置，使其在标题下方
      this.tooltipPosition = {
        top: event.clientY + 20, // 显示在标题下方
        left: event.clientX - 10 // 水平微调
      };
    },
    hideTooltip() {
      this.tooltipVisible = false;
    },
    pauseScroll(content, event) {
      this.showTooltip(content, event);
      // 暂停滚动
      this.$refs.ticker.style.animationPlayState = "paused";
    },
    resumeScroll() {
      this.hideTooltip();
      // 恢复滚动
      this.$refs.ticker.style.animationPlayState = "running";
    },
    getColor(score) {
      if (score > 0) return "orange"; // 积极
      if (score < 0) return "deepskyblue"; // 消极
      return "white"; // 中性
    }
  },
  mounted() {
    this.fetchStockNews();
  }
};
</script>

<style scoped>
.news-ticker-view {
  width: 100%;
  overflow: hidden;
  position: relative;
  height: 24px;
}

.news-ticker {
  display: flex;
  animation: scroll 180s linear infinite; /* 调整动画时间以滚动所有20条新闻 */
  animation-play-state: running;
  white-space: nowrap;
}

.news-item {
  display: flex;
  align-items: center;
  padding-right: 20px;
  font-size: 20px;
}

.news-title {
  margin-right: 10px;
}

.news-time {
  font-size: 12px;
  margin-left: 5px;
}

/* 滚动动画 */
@keyframes scroll {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(-100%);
  }
}

/* 悬停显示的完整新闻内容框 */
.tooltip {
  position: fixed;
  max-width: 500px;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.85);
  color: #ffffff;
  border-radius: 12px;
  font-size: 16px;
  z-index: 1000;
  pointer-events: none;
  box-shadow: 0 4px 8px rgba(183, 0, 137, 0.462);
}
</style>
