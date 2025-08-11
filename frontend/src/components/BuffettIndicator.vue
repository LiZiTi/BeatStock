<template>
  <div id="buffett-chart" v-if="isChartReady">
    <div id="indicator-values" class="indicator-values">
      <div class="value-item">
        经典巴菲特指标:
        <span class="value">
          <span class="highlight">{{ classicBuffettLatest.toFixed(3) }}</span>
        </span>
      </div>
      <div class="value-item">
        个人巴菲特指标:
        <span class="value">
          <span class="highlight">{{ optimizedBuffettLatest.toFixed(3) }}</span>
        </span>
      </div>
    </div>
    <v-chart ref="chartInstance" :option="chartOption" autoresize/>
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import { defineComponent } from "vue";
import VChart from "vue-echarts";
import "echarts";

export default defineComponent({
  name: "BuffettShanghaiCompositeChart",
  components: {
    VChart,
  },
  data() {
    return {
      chartOption: {},
      isChartReady: false,
      classicBuffettLatest: null,
      optimizedBuffettLatest: null,
    };
  },
  async created() {
    try {
      const response = await api.get("/buffett-indicator",{ moduleId: 'buffett-indicator' });
      const data = response.data;

      const dates = data.map((item) => item.日期);
      const shanghaiIndexData = data.map((item) => [
        item.open,
        item.close,
        item.low,
        item.high,
      ]);
      const classicBuffettIndex = data.map((item) => item.经典巴菲特指标);
      const optimizedBuffettIndex = data.map((item) => item.优化巴菲特指标);

      // 获取最新的指标值
      this.classicBuffettLatest =
          classicBuffettIndex[classicBuffettIndex.length - 1];
      this.optimizedBuffettLatest =
          optimizedBuffettIndex[optimizedBuffettIndex.length - 1];

      // 单一图表配置
      this.chartOption = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
          },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
        },
        legend: {
          data: ["上证指数", "经典巴菲特指标", "优化巴菲特指标"],
          textStyle: {
            color: "#EAEAEA", // 调整为浅色文字颜色
          },
        },
        xAxis: {
          type: "category",
          data: dates,
          axisPointer: {
            type: "shadow",
          },
          splitLine: {
            show: false,
          },
          axisLine: {
            lineStyle: {
              color: "#EAEAEA", // 浅色轴线
            },
          },
        },
        yAxis: [
          {
            type: "value",
            scale: true,
            name: "上证指数",
            splitLine: {
              show: false,
            },
            axisLine: {
              lineStyle: {
                color: "#EAEAEA", // 浅色轴线
              },
            },
          },
          {
            type: "value",
            scale: true,
            name: "巴菲特指标",
            splitLine: {
              show: false,
            },
            axisLine: {
              lineStyle: {
                color: "#EAEAEA", // 浅色轴线
              },
            },
          },
        ],
        series: [
          {
            name: "上证指数",
            type: "candlestick",
            data: shanghaiIndexData,
          },
          {
            name: "经典巴菲特指标",
            type: "line",
            yAxisIndex: 1,
            data: classicBuffettIndex,
            smooth: true,
            lineStyle: {
              color: "#FBBC05", // 使用红色系线条
            },
          },
          {
            name: "优化巴菲特指标",
            type: "line",
            yAxisIndex: 1,
            data: optimizedBuffettIndex,
            smooth: true,
            lineStyle: {
              color: "#4285F4 ", // 使用绿色系线条
            },
          },
        ],
        dataZoom: [
          {
            type: "inside",
            start: 70,
            end: 100,
          },
          {
            start: 70,
            end: 100,
          },
        ],
      };
      this.isChartReady = true;
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  },
  mounted() {
    window.addEventListener("resize", this.resizeChart);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.resizeChart);
  },
  methods: {
    resizeChart() {
      const chart = this.$refs.buffettChart;
      if (chart) {
        chart.resize();
      }
    },
  },
});
</script>

<style scoped>
#buffett-chart {
  height: 80%;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.indicator-values {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #EAEAEA; /* 浅色文字 */
  cursor: pointer;
  transition: transform 0.3s ease; /* 添加平滑的放大效果 */
}

.indicator-values:hover {
  transform: scale(1.2); /* 悬停时放大 1.2 倍 */
}

.value-item {
  color: #EAEAEA; /* 浅色文字 */
  margin: 0 25px;
}

.value {
  color: #FBBC05; /* 强调使用红色系 */
}

.highlight {
  font-size: 2em;
  color: #34A853; /* 高亮使用绿色系 */
  font-weight: bold;
}
</style>