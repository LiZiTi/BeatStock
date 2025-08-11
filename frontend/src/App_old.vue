<template>
  <!-- 顶部导航栏 -->
  <header class="navbar">
    <StockNews />
  </header>

  <!-- 内容布局区块 -->
  <div class="sections" ref="sections">
    <!-- BuffettIndicator 和 MarketFundFlow -->
    <section class="full-width-section full-height" :style="{ backgroundColor: '#252A34', marginBottom: '10px' }">
      <BuffettIndicator v-if="loadedSections.includes(0)" />
    </section>
    <section class="full-width-section half-height" :style="{ backgroundColor: '#EAEAEA', marginBottom: '10px' }">
      <MarketFundFlow v-if="loadedSections.includes(1)" />
    </section>

    <div class="custom-grid" style="margin-bottom: 10px;">
      <section class="half-width" :style="{ backgroundColor: '#252A34' }">
        <IndustryFundFlow v-if="loadedSections.includes(2)" @sector-selected="updateSelectedSector" />
      </section>
      <section class="half-width" :style="{ backgroundColor: '#252A34' }">
        <ConceptFundFlow v-if="loadedSections.includes(3)" @sector-selected="updateSelectedSector" />
      </section>
    </div>

    <!-- StockList 默认隐藏，在选择了 IndustryFundFlow 或 ConceptFundFlow 后显示 -->
    <section class="full-width-section half-height" v-show="showStockList"
      :style="{ backgroundColor: '#EAEAEA', marginBottom: '10px' }">
      <StockList :fundFlowData="{ type: fundFlowType, name: fundFlowName }" @stock-selected="updateSelectedStock" />
    </section>
    <!-- StockList 默认隐藏，在选择了 IndustryFundFlow 或 ConceptFundFlow 后显示 -->
    <section class="full-width-section p10-height" :style="{ backgroundColor: '#EAEAEA', marginBottom: '10px' }">
      <StockSearch @stock-selected="updateSelectedStock" />
    </section>
    <!-- Stock 相关子页面默认隐藏，选择股票后显示 -->
    <div class="custom-grid" v-show="showStockDetails">
      <section class="quarter-width" :style="{ backgroundColor: '#252A34' }">
        <StockShares :stockCode="fundStock" />
      </section>
      <section class="half-width" :style="{ backgroundColor: '#252A34' }">
        <StockTrends :stockCode="fundStock" />
      </section>
      <section class="quarter-width" :style="{ backgroundColor: '#252A34' }">
        <StockChips :stockCode="fundStock" />
      </section>
    </div>

    <div class="custom-grid" v-show="showStockDetails" style="margin-bottom: 24px;">
      <section class="half-width" :style="{ backgroundColor: '#252A34' }">
        <StockFundFlow :stockCode="fundStock" />
      </section>
      <section class="half-width" :style="{ backgroundColor: '#252A34' }">
        <StockRoes :stockCode="fundStock" />
      </section>
    </div>

    <!-- 底部信息栏 -->
    <section class="bottom-section" :style="{ backgroundColor: '#EAEAEA' }">
      <MyFooter />
    </section>
  </div>
</template>

<script>
import MarketFundFlow from './components/MarketFundFlow.vue';
import IndustryFundFlow from './components/IndustryFundFlow.vue';
import ConceptFundFlow from './components/ConceptFundFlow.vue';
import BuffettIndicator from './dancerPages/BuffettIndicator.vue';
import StockList from './components/StockList.vue';
import StockTrends from './components/StockTrends.vue';
import StockRoes from './components/StockRoes.vue';
import StockChips from './components/StockChips.vue';
import StockFundFlow from './components/StockFundFlow.vue';
import StockShares from './components/StockShares.vue';
import StockSearch from './components/StockSearch.vue'
import StockNews from './components/StockNews.vue'
// import FundFlowHistory from './components/FundFlowHistory.vue'
import MyFooter from "./components/MyFooter.vue";

export default {
  components: {
    MarketFundFlow,
    ConceptFundFlow,
    IndustryFundFlow,
    StockList,
    StockTrends,
    // FundFlowHistory,
    StockNews,
    StockSearch,
    StockFundFlow,
    StockShares,
    StockChips,
    StockRoes,
    BuffettIndicator,
    MyFooter,
  },
  data() {
    return {
      activeSection: -1,
      fundFlowType: null,
      fundFlowName: null,
      fundStock: null,
      showStockList: false,
      showStockDetails: false,
      loadedSections: [0], // 初始化加载第一个 section
      ticking: false,
    };
  },
  methods: {
    onScroll() {
      if (!this.ticking) {
        window.requestAnimationFrame(() => {
          const sections = this.$refs.sections.children;
          for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            const rect = section.getBoundingClientRect();
            if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
              if (!this.loadedSections.includes(i)) {
                this.loadedSections.push(i);
                this.loadChartData(i);
              }
            }
          }
          this.ticking = false;
        });
        this.ticking = true;
      }
    },
    loadChartData(index) {
      console.log(`加载第 ${index} 个 section 的数据`);
    },
    updateSelectedSector(type, name) {
      this.fundFlowType = type;
      this.fundFlowName = name;
      this.showStockList = true;
    },
    updateSelectedStock(code) {
      this.fundStock = code;
      this.$nextTick(() => {
        this.showStockDetails = true; // 确保页面完全更新后显示所有股票详情页面
      });
    },
  },
  mounted() {
    window.addEventListener('scroll', this.onScroll);
    this.onScroll(); // 初始化检查，加载第一页内容
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll);
  },
};
</script>

<style scoped>
/* 您的样式保持不变 */
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body,
html {
  margin: 0 !important;
  padding: 0;
  box-sizing: border-box;
  font-family: Arial, sans-serif;
  height: 100%;
  width: 100%;
  background-color: #ffffff;
  display: block;
}

/* 自定义滚动条样式 */
body::-webkit-scrollbar {
  width: 6px;
  /* 使滚动条更细 */
}

body::-webkit-scrollbar-thumb {
  background: #1e1e1e;
  /* 深色滚动条与页面颜色匹配 */
  border-radius: 6px;
}

body::-webkit-scrollbar-track {
  background: #252A34;
  /* 滚动条轨道颜色与页面主色一致 */
}
</style>

<style scoped>
#app {
  height: 100%;
  width: 100%;
  padding: 0;
}

.full-width-section {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-size: cover;
  background-position: center;
}

/* 新增的高度样式 */
.full-height {
  height: calc(100vh - 10px);
  /* 100% 高度 */
  border-radius: 12px;
}

.half-height {
  height: calc(50vh - 5px);
  /* 50% 高度 */
  border-radius: 12px;
}

.p10-height {
  height: calc(10vh - 5px);
  /* 50% 高度 */
  border-radius: 12px;
}

.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  height: 50px;
  background-color: rgba(0, 0, 0, 0.68);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  z-index: 10;
}

.logo {
  margin-right: 20px;
}

.nav-links {
  display: flex;
  gap: 30px;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.custom-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 10px;
}

.custom-section {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.half-width {
  width: calc(50% - 10px);
  /* 中间块占用50%的宽度 */
  height: calc(100vh / 2 - 10px);
  /* 高度为半屏 */
  margin: 0 5px;
  border-radius: 12px;
}

.quarter-width {
  width: calc(25% - 10px);
  /* 两边块占用25%的宽度 */
  height: calc(100vh / 2 - 10px);
  /* 高度为半屏 */
  margin: 0 5px;
  border-radius: 12px;
}


.bottom-section {
  height: calc(100vh / 4 - 10px);
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #252A34;
}

/* 自定义滚动条样式 */
body::-webkit-scrollbar {
  width: 8px;
}

body::-webkit-scrollbar-thumb {
  background: #252A34;
  border-radius: 4px;
}

body::-webkit-scrollbar-track {
  background: #1e1e1e;
}

/* 响应式设计 */
/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    height: 50px;
    padding: 0 10px;
  }

  .nav-links {
    gap: 15px;
  }

  .nav-links a {
    font-size: 14px;
  }

  .custom-section,

  .bottom-section {
    height: auto;
    margin-bottom: 10px;
    padding: 10px;
    /* 在移动设备上增加一点间距 */
  }

  /* 底部固定新闻栏样式 */
  .news-ticker-bar {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 50px;
    background-color: rgba(0, 0, 0, 0.68);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0 20px;
    z-index: 10;
  }
}
</style>