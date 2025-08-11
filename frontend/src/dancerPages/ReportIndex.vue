<template>
  <div class="page-container">
    <!-- <div class="background" :style="{ backgroundImage: `url(${backgroundImage})` }"></div> -->
    <!-- Isotope 容器 -->
    <div class="isotope-grid">
      <div v-for="(item, index) in sortedIndicators" :key="index" class="isotope-item"
        :style="{ backgroundColor: generateRandomColor(index) }">
        <div class="item-content">
          <!-- 图标和标题 -->
          <div class="card-content">
            <i :class="item.icon" class="card-icon"></i>
            <h3>{{ item.title }}</h3>
          </div>
          <!-- 其他内容 -->
          <p v-if="!item.table">{{ item.value }}</p>
          <table v-if="item.table" class="content-table">
            <thead>
              <tr>
                <th v-for="header in item.table.headers" :key="header">{{ header }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in item.table.rows" :key="rowIndex">
                <td v-for="cell in row" :key="cell">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Isotope from "isotope-layout";
import { api } from "@/axiosConfig";
import backgroundImage from '@/assets/background.png'; // 导入背景图片
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
  extends: DancerPageBase,
  name: "ReportIndex",
  pageName: '全局指标卡片',
  data() {
    return {
      indicators: [],
      cards: [],
      isotope: null,
      backgroundImage, // 将背景图片添加到数据属性中
    };
  },
  computed: {
    sortedIndicators() {
      return [...this.cards].sort((a, b) => b.weight - a.weight);
    },
  },
  methods: {
    isInnerControl() {
      return true;
    },
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

    },
    fullfillAllData() {

    },
    updateChartDataPoint() {
      this.triggerRandomCardEffect()
    },
    async loadIndicators() {
      try {
        const response = await api.get("/report-data");
        this.indicators = response.data;
        this.copyToClipboard(this.indicators)
        this.fetchCardIndicators();
        this.$nextTick(() => {
          this.initIsotope();
        });
        // this.copyToClipboard(JSON.stringify(this.indicators))
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    // 初始化 Isotope
    initIsotope() {
      if (this.isotope) {
        this.isotope.destroy(); // 如果已有实例，先销毁
      }
      this.isotope = new Isotope(".isotope-grid", {
        itemSelector: ".isotope-item",
        layoutMode: "masonry",
        percentPosition: true,
        masonry: {
          columnWidth: ".isotope-item",
          gutter: 10,
        },
      });
    },
    fetchCardIndicators() {
      this.cards = [
        { weight: 5, title: "上证指数", value: this.indicators.上证行情[0].最新价, icon: "fa fa-bar-chart" },
        { weight: 5, title: "上证涨跌", value: this.indicators.上证行情[0].涨跌幅 + "%", icon: "fas fa-chart-line" },
        { weight: 5, title: "巴菲特指标", value: (this.indicators.巴菲特指标[0].总市值 / this.indicators.巴菲特指标[0].GDP).toFixed(2), icon: "fa fa-graduation-cap" },
        { weight: 5, title: "总成交金额", value: (this.indicators.市场总成交金额 / 1e8).toFixed(2) + " 亿", icon: "fa fa-money" },
        { weight: 5, title: "主力净流入", value: (this.indicators.市场资金流[0]['主力净流入-净额'] / 1e8).toFixed(2) + " 亿", icon: "fa fa-money" },
        { weight: 5, title: "上涨家数", value: this.indicators.股票上涨家数, icon: "fa fa-contao" },
        { weight: 5, title: "下跌家数", value: this.indicators.股票下跌家数, icon: "fa fa-contao" },
        { weight: 5, title: "最强版块", value: this.indicators.行业资金前三[0].名称, icon: "fa fa-industry" },
        { weight: 5, title: "最弱版块", value: this.indicators.行业资金后三[0].名称, icon: "fa fa-industry" },
        { weight: 5, title: "最强概念", value: this.indicators.概念资金前三[0].名称, icon: "fa fa-trophy" },
        { weight: 5, title: "最弱概念", value: this.indicators.概念资金后三[0].名称, icon: "fa fa-trophy" },
        { weight: 5, title: "涨停数", value: this.indicators.股票涨跌分布['涨幅超过10%'], icon: "fa fa-tachometer" },
        { weight: 5, title: "跌停数", value: this.indicators.股票涨跌分布['跌幅超过-10%'], icon: "fa fa-tachometer" },
      ];

      this.generateFundTables(this.indicators);
      this.generateStockDistributionTable(this.indicators);
      this.generateStockChangeDistributionTable(this.indicators);
    },
    copyToClipboard(text) {
      let prompt = "基于以下JSON格式的指标集，写一份 1200 字左右的A股复盘报告，" +
        "重点关注当日股票的数据表现并依次分析，历史数据可作为后市预测的参考，要做到面面俱到的陈述与分析，包括对投资者情绪的影响" +
        "宏观经济相关的指标如果跟当日的盘面没有关联就不需要提及，切记不要出现‘中国’,'政府'及国家领导人相关的字眼！" +
        "文风要风趣幽默，内容要严谨，可以模仿知名经济学家的口吻，让人看不出来是AI生成的" +
        "生成的内容既可以作为单独的文章来使用，也可以作为视频的文案来使用！" +
        "开头以‘我是BetaData，一个喜欢捣鼓股市数据的程序员，接下来就看看最强AI模型对当日股市的复盘吧’，" +
        "报告中不要有空虚的文字，特别是开头与结尾，我力求直来直去，有一说一。" +
        "接下来直接进入正题，但要明确说明是对哪天股市数据的复盘。\r\n"

      prompt += JSON.stringify(text);
      navigator.clipboard.writeText(prompt).then(() => {
        console.log("内容已复制到剪切板");
      }).catch(err => {
        console.error("复制失败:", err);
      });
    },
    generateFundTables(data) {
      const parseRows = (items) =>
        items.map((item) => [
          item["名称"],
          `${item["今日涨跌幅"].toFixed(2)}%`,
          `${(item["今日主力净流入-净额"] / 1e8).toFixed(2)} 亿`,
          item["今日主力净流入最大股"],
        ]);

      let tab = {
        title: "行业资金流入前三",
        table: {
          headers: ["名称", "今日涨跌幅", "今日主力净流入-净额", "今日主力净流入最大股"],
          rows: parseRows(data["行业资金前三"]),
        },
        weight: 3,
        icon: "fa fa-hourglass-end",
      };
      this.cards.push(tab);

      tab = {
        title: "行业资金流入后三",
        table: {
          headers: ["名称", "今日涨跌幅", "今日主力净流入-净额", "今日主力净流入最大股"],
          rows: parseRows(data["行业资金后三"]),
        },
        weight: 3,
        icon: "fa fa-hourglass-end",
      };
      this.cards.push(tab);
    },
    generateStockDistributionTable(data) {
      this.cards.push({
        title: "股票涨跌家数分布",
        table: {
          headers: ["类型", "家数"],
          rows: [
            ["上涨家数", data["股票上涨家数"]],
            ["平盘家数", data["股票平盘家数"]],
            ["下跌家数", data["股票下跌家数"]],
          ],
        },
        weight: 3,
        icon: "fa fa-podcast",
      });
    },
    generateStockChangeDistributionTable(data) {
      const distribution = data["股票涨跌分布"];
      this.cards.push({
        title: "股票涨跌分布",
        table: {
          headers: ["涨跌分布", "数量"],
          rows: Object.entries(distribution).map(([key, value]) => [key, value]),
        },
        weight: 3,
        icon: "fa fa-pie-chart",
      });
    },
    // 随机生成背景颜色
    generateRandomColor(index) {
      const colors = [
        "#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1", "#955251", "#B565A7",
        "#DD4124", "#D65076", "#45B8AC", "#EFC050", "#5B5EA6", "#9B2335", "#BC243C",
        "#00A170", "#4B5335", "#55B4B0", "#B565A7", "#E15D44", "#7FCDCD", "#6CACE4",
        "#E94B3C", "#F6A4C9", "#FFAA1D", "#B83A4B", "#6C5B7B", "#355C7D", "#99B898",
        "#FECEA8", "#FF847C", "#E84A5F", "#2A363B",
      ];

      // 返回按索引选择的颜色
      return colors[index % colors.length];
    },
    // 新增的函数：随机触发卡片效果
    triggerRandomCardEffect() {
      // 获取所有卡片元素
      const cardElements = this.$el.querySelectorAll('.isotope-item');
      if (cardElements.length === 0) return;

      // 随机选择一个索引
      const randomIndex = Math.floor(Math.random() * cardElements.length);
      const randomCard = cardElements[randomIndex];

      // 添加效果类
      randomCard.classList.add('glow-shake-effect');

      // 在动画结束后移除效果类
      const removeEffect = () => {
        randomCard.classList.remove('glow-shake-effect');
        randomCard.removeEventListener('animationend', removeEffect);
      };
      randomCard.addEventListener('animationend', removeEffect);
    },
  },
  mounted() {
    this.loadIndicators();

    // 可选：定期触发随机卡片效果（例如每5秒）
    // setInterval(this.triggerRandomCardEffect, 5000);
  },
};
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.822);
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  filter: blur(1px);
  opacity: 0.9;
  z-index: -1;
}

.isotope-grid {
  width: 100%;
  max-width: 1680px;
  position: relative;
}

.isotope-item {
  margin-bottom: 10px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
    box-shadow 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.isotope-item:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.item-content {
  padding: 16px;
  background-color: rgba(7, 7, 7, 0.707);
  height: 100%;
  border: 1px solid gold;
  box-shadow:
    0 4px 8px rgba(0, 0, 0, 0.3),
    /* 下方外部阴影 */
    0 -4px 8px rgba(0, 0, 0, 0.3),
    /* 上方外部阴影 */
    4px 0 8px rgba(0, 0, 0, 0.3),
    /* 右侧外部阴影 */
    -4px 0 8px rgba(0, 0, 0, 0.3),
    /* 左侧外部阴影 */
    inset 0 0 10px rgba(255, 215, 0, 0.5);
  /* 内部光晕 */
}


.item-content p {
  color: antiquewhite;
  font-size: 1.6rem;
  text-align: center;
}

.card-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  width: 100%;
  color: white;
}

.card-icon {
  font-size: 1.5rem;
  color: white;
}

.card-content h3 {
  margin: 0;
  font-size: 1rem;
}

.card-content p {
  color: white;
}

.content-table {
  margin-top: 12px;
  width: 100%;
  border-collapse: collapse;
}

.content-table th,
.content-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  font-size: 0.8rem;
}

.content-table th {
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.content-table tr:nth-child(even) {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 定义震动效果的关键帧 */
@keyframes shake {
  0% {
    transform: translate(0, 0);
  }

  10%,
  30%,
  50%,
  70%,
  90% {
    transform: translate(-5px, 0);
  }

  20%,
  40%,
  60%,
  80% {
    transform: translate(5px, 0);
  }

  100% {
    transform: translate(0, 0);
  }
}

/* 定义光晕效果的关键帧 */
@keyframes glow {

  0%,
  100% {
    box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
  }

  50% {
    box-shadow: 0 0 20px rgba(255, 255, 255, 1);
  }
}

/* 定义触发效果的类 */
.glow-shake-effect {
  animation: glow 2s ease-in-out, shake 0.5s;
}
</style>
