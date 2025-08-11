<template>
  <div class="fund-flow">
    <div class="upper-section"
      :class="{ 'positive-flow': lastBullBearScore >= 50, 'negative-flow': lastBullBearScore < 50 }">
      <p>今日多空评分：{{ lastBullBearScore }}</p>
    </div>
    <div class="middle-section">
      <v-chart ref="buffettChart" :option="chartOption" autoresize style="height: 100%;" />
    </div>
  </div>
</template>

<style scoped>
.fund-flow {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 80%;
  background-color: #EAEAEA;
}

.upper-section {
  height: 15%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  font-size: 36px;
  font-weight: bold;
  color: #a808d9;
  transition: transform 0.3s ease;
}

.upper-section:hover {
  transform: scale(1.1);
}

.middle-section {
  height: 85%;
  width: 100%;
  margin-top: 40px;
}
</style>

<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';

export default {
  components: {
    VChart
  },
  data() {
    return {
      lastBullBearScore: 0,
      recent100Market: [],
      chartOption: null,
    };
  },
  async mounted() {
    try {
      const response = await api.get("/market-fund-flow");
      this.recent100Market = response.data;
      if (this.recent100Market.length > 0) {
        this.lastBullBearScore = this.recent100Market[this.recent100Market.length - 1]["多空评分"].toFixed(2);
      }
      this.createBarChart();
    } catch (error) {
      console.error("Failed to fetch fund flow data", error);
    }
  },
  methods: {
    createBarChart() {
      const categories = this.recent100Market.map((item) => item.日期);
      const mainInflow = this.recent100Market.map((item) => (item["主力净流入-净额"] / 10000 / 10000).toFixed(2));
      const midInflow = this.recent100Market.map((item) => (item["中单净流入-净额"] / 10000 / 10000).toFixed(2));
      const minInflow = this.recent100Market.map((item) => (item["小单净流入-净额"] / 10000 / 10000).toFixed(2));
      const bullbearScore = this.recent100Market.map((item) => (item["多空评分"]).toFixed(2));

      this.chartOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: { color: '#ffffff', fontSize: 12 },
        },
        legend: {
          data: ['主力净流入','中单净流入','小单净流入', '资金多空评分'],
          textStyle: { color: '#000000' },
        },
        xAxis: {
          type: 'category',
          data: categories,
        },
        yAxis: [
          {
            type: 'value',
            name: '金额（亿元）',
            min: (value) => Math.min(0, value.min),
            max: (value) => Math.max(0, value.max),
          },
          {
            type: 'value',
            name: '多空评分',
            position: 'right',
            min: 0,
            max: 100,
          }
        ],
        dataZoom: [
          { type: 'inside', start: 80, end: 100 },
          { start: 80, end: 100 },
        ],
        series: [
          {
            name: '主力净流入',
            type: 'bar',
            stack: '总量',
            data: mainInflow,
            itemStyle: {
              color: '#EA4335',  // Red for positive, green for negative
            },
          },
          {
            name: '中单净流入',
            type: 'bar',
            stack: '总量',
            data: midInflow,
            itemStyle: {
              color: '#4285F4',  // Red for positive, green for negative
            },
          },
          {
            name: '小单净流入',
            type: 'bar',
            stack: '总量',
            data: minInflow,
            itemStyle: {
              color:'#34A853',  // Red for positive, green for negative
            },
          },
          {
            name: '资金多空评分',
            type: 'line',
            yAxisIndex: 1,
            data: bullbearScore,
            lineStyle: { color: '#9400D3 ', width: 2 },
            smooth: true,
          },
        ],
      };
    },
  },
};
</script>
