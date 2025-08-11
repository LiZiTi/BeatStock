<template>
    <div class="page-container">
        <div class="top-area">
            <!-- Banner 区域保持不变 -->
            <div class="banner">
                <div class="banner-overlay">
                    <div class="banner-content">
                        <h1 class="banner-title">一寸光阴一寸金 寸金难买寸光阴</h1>
                        <p class="banner-description">The today we waste is the tomorrow that those who passed away
                            yesterday longed for.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 左侧空白区域 -->
        <div class="empty-area left-empty"></div>

        <!-- 中间核心区域 -->
        <div class="content-area">
            <!-- 上层卡片区域 -->
            <div class="top-layer">
                <div
                    class="card"
                    v-for="(card, index) in cards"
                    :key="index"
                    :class="{ active: card.name === activeCard, disabled: card.disabled }"
                    :style="{ backgroundColor: card.color }"
                    @click="!card.disabled && setActiveCard(card.name)"
                >
                    {{ card.label }}
                </div>
            </div>

            <!-- 下层内容区域 -->
            <transition name="fade">
                <div class="bottom-layer" key="activeCard">
                    <IndexCombination v-if="activeCard === 'index'" class="chart-section" />
                    <IndicatorsHistory v-if="activeCard === 'indicators'" class="chart-section" />
                    <BuffettIndicator v-if="activeCard === 'buffett'" class="chart-section" />
                </div>
            </transition>
        </div>

        <!-- 右侧空白区域 -->
        <div class="empty-area right-empty"></div>

        <div class="bottom-area">
            <!-- 保持不变的底部区域 -->
            <p>版权所有 © 2024 ElonMar - 数据源自AKShare，仅供参考，不构成任何建议！</p>
            <div class="wechat-info">
                <img src="@/assets/email.png" alt="邮箱" class="wechat-icon" />
                <span>ok_ai@outlook.com</span>
            </div>
        </div>
    </div>
</template>

<script>
import IndexCombination from './IndexCombination.vue';
import IndicatorsHistory from './MacroEconomyIndicators.vue';
import BuffettIndicator from '../dancerPages/BuffettIndicator.vue';

export default {
  components: {
    IndexCombination,
    IndicatorsHistory,
    BuffettIndicator
  },
  data() {
    return {
      activeCard: 'index', // 默认显示“指数表现”
      cards: [],
      colors: [
        '#1f1f7a', '#333399', '#3366cc', '#0099cc', '#00cccc', '#33cccc', '#00cc99', '#66ffcc',
        '#339966', '#66cc66', '#99cc33', '#ffcc00', '#ff9966', '#cc6600', '#cc3333', '#ff6699'
      ],
    };
  },
  created() {
    this.assignRandomColors();
  },
  methods: {
    assignRandomColors() {
      // 随机选择8个颜色
      const selectedColors = this.colors.sort(() => 0.5 - Math.random()).slice(0, 8);

      // 初始化卡片
      this.cards = [
        { name: 'index', label: '指数表现', disabled: false, color: selectedColors[0] },
        { name: 'indicators', label: '经济指标', disabled: false, color: selectedColors[1] },
        { name: 'buffett', label: '巴菲特指标', disabled: false, color: selectedColors[3] },
        { name: '', label: '敬请期待', disabled: true, color: selectedColors[4] },
        { name: '', label: '敬请期待', disabled: true, color: selectedColors[5] },
        { name: '', label: '敬请期待', disabled: true, color: selectedColors[6] },
        { name: '', label: '敬请期待', disabled: true, color: selectedColors[7] },
      ];
    },
    setActiveCard(card) {
      if (['index', 'indicators', 'buffett'].includes(card)) {
        this.activeCard = card;
      }
    },
  },
};
</script>

<style scoped>
.page-container {
    display: grid;
    grid-template-areas:
        "top top top top"
        "empty-left content right empty-right"
        "bottom bottom bottom bottom";
    grid-template-columns: 5% 90% 5%;
    grid-template-rows: auto 1fr auto;
    background: linear-gradient(135deg, #000000, #1d0131);
    color: #ffffff;
}

.top-area {
    grid-area: top;
}

.left-area,
.right-area {
    background-color: #22222200;
    padding: 10px;
    overflow-y: auto;
}

.content-area {
    grid-area: content;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    width: 100%;
    margin: 0 auto;
}

.banner-title {
    font-size: 2.5rem;
    color: #ffcc00;
    text-shadow: 0 0 10px #ff9900, 0 0 20px #ff3300, 0 0 30px #ff6600;
}

.banner-description {
    color: #ffaa00;
    text-shadow: 0 0 5px #ff6600, 0 0 10px #ff3300;
}

.top-layer {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-evenly;
    width: 100%;
    height: 168px;
    align-items: center;
    gap: 20px;
}

.card {
    width: 120px;
    height: 36px;
    color: #fff;
    padding: 20px;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    transition: transform 0.3s, background-color 0.3s;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 20%, transparent 20%);
    transform: translate(-50%, -50%) scale(0);
    transition: transform 0.5s;
    border-radius: 50%;
    pointer-events: none;
}

.card:hover::before {
    transform: translate(-50%, -50%) scale(1);
}

.card:hover {
    transform: scale(1.3);
}

.card.active {
    transform: scale(1.2);
}

.card.disabled {
    cursor: default;
    opacity: 0.7;
}

.bottom-layer {
    width: 100%;
    margin-top: 20px;
}

.bottom-area {
    grid-area: bottom;
    text-align: center;
    padding: 10px;
    font-size: 0.9rem;
    color: #ffffff7f;
    margin-top: 168px;
}

.wechat-info {
    margin-top: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.wechat-icon {
    width: 24px;
    height: 24px;
    margin-right: 8px;
}

.fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
    opacity: 0;
}
</style>
