<template>
  <div class="container">
    <div class="background-image"></div>

    <!-- 中央弹出卡片 -->
    <transition :name="currentTransition" @after-leave="resetTransition">
      <div v-if="showModal" class="popup-card"
        :style="{ backgroundColor: popupCard.backgroundColor, fontSize: `${popupCard.fontSize}px` }">
        <div class="card-title"> <i :class="popupCard.icon"></i>{{ popupCard.title }}</div>
        <div class="card-content" v-html="popupCard.content" :style="{ fontSize: `${popupCard.fontSize * 3}px` }"></div>
        <div class="card-footer">{{ popupCard.footer }}</div>
      </div>
    </transition>

    <!-- 卡片容器 -->
    <div class="cards-container" ref="cardsContainer">
      <transition-group name="fade" tag="div" class="cards-wrapper">
        <div v-for="card in showedCards" :key="card.id" class="card"
          :style="{ backgroundColor: card.backgroundColor, fontSize: `${card.fontSize}px` }">
          <div class="card-title"><i :class="card.icon"></i>{{ card.title }}</div>
          <div class="card-content" v-html="card.content" :style="{ fontSize: `${popupCard.fontSize * 1.5}px` }"></div>
          <div class="card-footer">{{ card.footer }}</div>
        </div>
      </transition-group>
    </div>

    <!-- 控制按钮 -->
    <!-- <div class="control-buttons">
      <button class="next-button" @click="next">Next</button>
      <button class="layout-button" @click="layout" :disabled="!showModal" :class="{ disabled: !showModal }">
        Layout
      </button>
    </div> -->
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
  extends: DancerPageBase,
  name: "ReportIndex2",
  pageName: '今日指标集',
  data() {
    return {
      showModal: false,
      indicatorCards: [],
      showedCards: [],
      currentCardIndex: 0,
      cardsContainer: null,
      transitionOptions: ['fade', 'fly-top', 'fly-bottom', 'fly-left', 'fly-right'],
      currentTransition: 'fade',
      professionalColors: [
        { "name": "深红色", "hex": "#8B0000" },
        { "name": "深橙色", "hex": "#FF4500" },
        { "name": "暗金色", "hex": "#B8860B" },
        { "name": "暗橄榄绿色", "hex": "#556B2F" },
        { "name": "深森林绿色", "hex": "#228B22" },
        { "name": "暗青色", "hex": "#008B8B" },
        { "name": "暗天蓝色", "hex": "#1E3A8A" },
        { "name": "深海军蓝", "hex": "#000080" },
        { "name": "深靛蓝", "hex": "#4B0082" },
        { "name": "深紫罗兰色", "hex": "#800080" },
        { "name": "暗洋红色", "hex": "#8B008B" },
        { "name": "深棕色", "hex": "#654321" },
        { "name": "深灰蓝色", "hex": "#2F4F4F" },
        { "name": "炭灰色", "hex": "#36454F" },
        { "name": "暗灰色", "hex": "#2B2B2B" },
        { "name": "黑曜石黑", "hex": "#1C1C1C" }
      ],
      cardId: 0,
      popupCard: {
        title: '',
        content: '',
        footer: '',
        fontSize: 16,
        backgroundColor: ''
      },
      doPopup: true
    };
  },
  mounted() {
    this.cardsContainer = this.$refs.cardsContainer;
    this.loadIndicators();
  },
  methods: {
    isInnerControl() {
      return true;
    },
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {
      this.showModal = []
    },
    fullfillAllData() {

    },
    updateChartDataPoint() {
      if (this.doPopup) {
        this.popup()
      } else {
        this.layout()
      }
      this.doPopup = !this.doPopup
    },
    async loadIndicators() {
      try {
        const response = await api.get("/report-data");
        this.indicators = response.data;
        this.initCards();
        this.showedCards = this.indicatorCards;
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    initCards() {
      this.indicatorCards = [
        {
          title: "上证指数",
          content: this.indicators.上证行情[0].最新价,
          fontSize: 20,
          icon: "fa fa-bar-chart",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "上证涨跌",
          content: this.indicators.上证行情[0].涨跌幅 + "%",
          fontSize: 20,
          icon: "fas fa-chart-line",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "巴菲特指标",
          content: (this.indicators.巴菲特指标[0].总市值 / this.indicators.巴菲特指标[0].GDP).toFixed(2),
          fontSize: 20,
          icon: "fa fa-graduation-cap",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "总成交金额",
          content: (this.indicators.市场总成交金额 / 1e8).toFixed(2) + " 亿",
          fontSize: 20,
          icon: "fa fa-money",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "主力净流入",
          content: this.indicators.实时主力净流入 + " 亿",
          fontSize: 20,
          icon: "fa fa-money",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "上涨家数",
          content: this.indicators.股票上涨家数,
          fontSize: 20,
          icon: "fa fa-contao",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "下跌家数",
          content: this.indicators.股票下跌家数,
          fontSize: 20,
          icon: "fa fa-contao",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "最强版块",
          content: this.indicators.行业资金前三[0].名称,
          fontSize: 20,
          icon: "fa fa-industry",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "强版个股",
          content: this.indicators.行业资金前三[0].今日主力净流入最大股,
          fontSize: 20,
          icon: "fa fa-industry",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "最弱版块",
          content: this.indicators.行业资金后三[0].名称,
          fontSize: 20,
          icon: "fa fa-industry",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "最弱个股",
          content: this.indicators.行业资金后三[0].今日主力净流入最大股,
          fontSize: 20,
          icon: "fa fa-industry",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "最强概念",
          content: this.indicators.概念资金前三[0].名称,
          fontSize: 20,
          icon: "fa fa-trophy",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "最弱概念",
          content: this.indicators.概念资金后三[0].名称,
          fontSize: 20,
          icon: "fa fa-trophy",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "涨幅>=10%",
          content: this.indicators.股票涨跌分布['涨幅超过10%'],
          fontSize: 20,
          icon: "fa fa-tachometer",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
        {
          title: "跌幅<=-10%",
          content: this.indicators.股票涨跌分布['跌幅超过-10%'],
          fontSize: 20,
          icon: "fa fa-tachometer",
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        },
      ];
      this.generateFundTables()
    },
    generateFundTables() {
      const createTable = (items, icon, isTop = true) => {
        const titlePrefix = isTop ? "资金流入第" : "资金流出第";
        return items.map((item, index) => ({
          title: `${titlePrefix} ${index + 1}`,
          content: `
      <table style="
        width: 100%; 
        border-collapse: collapse; 
        border: 1px solid #ddd; 
        border-radius: 16px; 
        overflow: hidden; 
        text-align: left;
        font-size: 14px;">
        <tr>
          <th style=" border-bottom: 1px solid #ddd;">名称</th>
          <td style="border-bottom: 1px solid #ddd;">${item["名称"]}</td>
        </tr>
        <tr>
          <th style=" border-bottom: 1px solid #ddd;">涨跌幅</th>
          <td style="border-bottom: 1px solid #ddd;">${item["今日涨跌幅"].toFixed(2)}%</td>
        </tr>
        <tr>
          <th style=" border-bottom: 1px solid #ddd;">净流入</th>
          <td style="border-bottom: 1px solid #ddd;">${(item["今日主力净流入-净额"] / 1e8).toFixed(2)} 亿</td>
        </tr>
        <tr>
          <th style=" border-bottom: 1px solid #ddd;">净流入最大股</th>
          <td style="border-bottom: 1px solid #ddd;">${item["今日主力净流入最大股"]}</td>
        </tr>
      </table>
    `,
          icon: icon,
          fontSize: 20,
          backgroundColor:this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex,
        }));
      };

      // 将生成的卡片数据添加到 this.cards 中
      this.indicatorCards.push(
        ...createTable(this.indicators["行业资金前三"], "fa fa-hourglass-end", true)
      );

      this.indicatorCards.push(
        ...createTable(this.indicators["行业资金后三"], "fa fa-hourglass-end", false)
      );
    },
    getOppositeTransition(transition) {
      switch (transition) {
        case 'fly-top': return 'fly-bottom';
        case 'fly-bottom': return 'fly-top';
        case 'fly-left': return 'fly-right';
        case 'fly-right': return 'fly-left';
        case 'fade':
        default: return 'fade';
      }
    },
    getRandomTransition() {
      const randomIndex = Math.floor(Math.random() * this.transitionOptions.length);
      return this.transitionOptions[randomIndex];
    },
    popup() {
      if (this.indicatorCards.length === 0) return; // 如果没有卡片，直接返回

      // 获取当前卡片
      const card = this.indicatorCards[this.currentCardIndex];

      // 更新弹出卡片的内容
      this.popupCard.title = card.title;
      this.popupCard.content = card.content;
      this.popupCard.icon = card.icon;
      this.popupCard.fontSize = card.fontSize;
      this.popupCard.footer = card.footer || ''; // 如果 footer 不存在，设置为空字符串
      this.popupCard.backgroundColor = this.professionalColors[Math.floor(Math.random() * this.professionalColors.length)].hex;

      // 随机设置过渡动画
      this.currentTransition = this.getRandomTransition();

      // 显示弹出卡片
      this.showModal = true;

      // 更新索引，循环从头开始
      this.currentCardIndex = (this.currentCardIndex + 1) % this.indicatorCards.length;
    },
    layout() {
      if (!this.showModal) return;

      const oppositeTransition = this.getOppositeTransition(this.currentTransition);
      this.currentTransition = oppositeTransition;

      this.showedCards.push({
        id: this.cardId++,
        title: this.popupCard.title,
        icon: this.popupCard.icon,
        content: this.popupCard.content,
        fontSize: this.popupCard.fontSize,
        footer: this.popupCard.footer,
        backgroundColor: this.popupCard.backgroundColor
      });

      this.showModal = false;

      this.$nextTick(() => {
        if (this.cardsContainer) {
          this.cardsContainer.scrollTop = this.cardsContainer.scrollHeight;
        }
      });
    },
    resetTransition() {
      this.currentTransition = 'fade';
    }
  },
};
</script>

<!-- Scoped 样式：仅用于组件内部样式，不包括过渡动画 -->
<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 水平居中 */
  justify-content: center;
  /* 垂直居中 */
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
  background-color: rgba(0, 0, 0, 0.5);
}

.background-image {
  background-image: url('@/assets/background.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: absolute;
  width: 100%;
  height: 100%;
  filter: blur(8px);
  z-index: -2;
}

.popup-card {
  position: absolute;
  top: calc(50vh - 225px);
  left: calc(50vw - 300px);
  padding: 30px;
  width: 600px;
  height: 450px;
  border: 6px solid rgba(255, 255, 255, 0.5);
  background: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.9),
      rgba(220, 220, 220, 0.7) 40%,
      rgba(200, 200, 200, 1)),
    linear-gradient(to right,
      rgba(255, 255, 255, 0.9),
      rgba(220, 220, 220, 0.7) 40%,
      rgba(200, 200, 200, 1));
  background-blend-mode: multiply;
  border-radius: 16px;
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.2),
    /* 内部向下阴影 */
    inset 0 -2px 4px rgba(0, 0, 0, 0.2),
    /* 内部向上阴影 */
    inset 2px 0 4px rgba(0, 0, 0, 0.2),
    /* 内部向右阴影 */
    inset -2px 0 4px rgba(0, 0, 0, 0.2),
    /* 内部向左阴影 */
    0 4px 8px rgba(0, 0, 0, 0.6),
    /* 外部向下阴影 */
    0 -4px 8px rgba(0, 0, 0, 0.6),
    /* 外部向上阴影 */
    4px 0 8px rgba(0, 0, 0, 0.6),
    /* 外部向右阴影 */
    -4px 0 8px rgba(0, 0, 0, 0.6);
  /* 外部向左阴影 */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  text-align: center;
  transition: transform 0.3s, opacity 0.3s;
  color: rgba(252, 252, 252, 0.9);
  z-index: 999;
}


/* 卡片容器样式 */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, 200px);
  /* 每列200px，自动填充 */
  grid-auto-rows: 150px;
  /* 每行150px */
  gap: 20px;
  /* 卡片之间的间距 */
  padding: 20px;
  max-width: 90%;
  /* 限制最大宽度 */
  margin-top: 20px;
  overflow-y: auto;
  /* 为了居中 */
  justify-content: center;
  /* 水平居中 */
  align-content: start;
  /* 从上开始对齐 */
}

/* 卡片包装器样式 */
.cards-wrapper {
  display: contents;
  /* 让 transition-group 的子元素直接参与 grid 布局 */
}

.card {
  padding: 6px;
  border: 6px solid rgba(255, 255, 255, 0.5);
  background: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.9),
      rgba(220, 220, 220, 0.7) 40%,
      rgba(200, 200, 200, 1)),
    linear-gradient(to right,
      rgba(255, 255, 255, 0.9),
      rgba(220, 220, 220, 0.7) 40%,
      rgba(200, 200, 200, 1));
  background-blend-mode: multiply;
  border-radius: 16px;
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.2), 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  text-align: center;
  width: 200px;
  height: 150px;
  position: relative;
  transition: transform 0.3s, opacity 0.3s;
  color: rgba(255, 255, 255, 0.9);
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.2),
    /* 内部向下阴影 */
    inset 0 -2px 4px rgba(0, 0, 0, 0.2),
    /* 内部向上阴影 */
    inset 2px 0 4px rgba(0, 0, 0, 0.2),
    /* 内部向右阴影 */
    inset -2px 0 4px rgba(0, 0, 0, 0.2),
    /* 内部向左阴影 */
    0 4px 8px rgba(0, 0, 0, 0.6),
    /* 外部向下阴影 */
    0 -4px 8px rgba(0, 0, 0, 0.6),
    /* 外部向上阴影 */
    4px 0 8px rgba(0, 0, 0, 0.6),
    /* 外部向右阴影 */
    -4px 0 8px rgba(0, 0, 0, 0.6);
  /* 外部向左阴影 */
}

.card:hover {
  transform: scale(1.2);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.card-footer {
  font-size: 0.9em;
}

/* 删除按钮样式 */
.delete-button {
  position: absolute;
  top: 5px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #888;
  transition: color 0.3s;
}

.delete-button:hover {
  color: #f00;
}

/* 控制按钮容器样式 */
.control-buttons {
  position: absolute;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

/* 控制按钮样式 */
.next-button,
.layout-button {
  padding: 15px 30px;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s, transform 0.3s;
}

.next-button {
  background-color: #28a745;
  color: #fff;
}

.next-button:hover {
  background-color: #218838;
  transform: scale(1.05);
}

.layout-button {
  background-color: #007BFF;
  color: #fff;
}

.layout-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
}

.layout-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>

<!-- 全局样式：用于过渡动画 -->
<style>
/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 自定义飞入动画 */
.fly-top-enter-active,
.fly-bottom-enter-active,
.fly-left-enter-active,
.fly-right-enter-active,
.fly-top-leave-active,
.fly-bottom-leave-active,
.fly-left-leave-active,
.fly-right-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

/* 增加位移距离，例如从 150px 改为更远的位置 */
.fly-top-enter-from {
  opacity: 0;
  transform: translateY(-150px) scale(0.9);
}

.fly-top-leave-to {
  opacity: 0;
  transform: translateY(-150px) scale(0.9);
}

.fly-bottom-enter-from {
  opacity: 0;
  transform: translateY(150px) scale(0.9);
}

.fly-bottom-leave-to {
  opacity: 0;
  transform: translateY(150px) scale(0.9);
}

.fly-left-enter-from {
  opacity: 0;
  transform: translateX(-150px) scale(0.9);
}

.fly-left-leave-to {
  opacity: 0;
  transform: translateX(-150px) scale(0.9);
}

.fly-right-enter-from {
  opacity: 0;
  transform: translateX(150px) scale(0.9);
}

.fly-right-leave-to {
  opacity: 0;
  transform: translateX(150px) scale(0.9);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .cards-container {
    grid-template-columns: repeat(auto-fill, 200px);
  }
}

@media (max-width: 800px) {
  .cards-container {
    grid-template-columns: repeat(auto-fill, 150px);
  }
}

@media (max-width: 500px) {
  .cards-container {
    grid-template-columns: repeat(auto-fill, 100px);
  }
}
</style>