<template>
  <div class="fund-flow">
    <!-- 容器：用于将两个柱状图放在一行 -->
    <div class="charts-container">
      <!-- 概念版块的图表，包含 top5 和 tail5 -->
      <div class="chart-section">
        <h3 style="text-align: center;color: aliceblue;">概念版块 - Top 5 和 Tail 5</h3>
        <v-chart ref="conceptChart" :option="conceptChartOption" autoresize @click="handleChartClick" style="height: 100%;" />
      </div>
    </div>
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';

export default {
  name: "FundFlowCharts",
  components: {
    VChart,
  },
  data() {
    return {
      conceptChartOption: {},
    };
  },
  mounted() {
    this.fetchFundFlowData();
  },
  methods: {
    async fetchFundFlowData() {
      try {
        const response = await api.get("/sector-fund-flow", { params: { sector_type: "概念资金流" } });
        const data = response.data;
        this.initCharts(data);
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    initCharts(data) {
      const top5Data = data['top5'];
      const tail5Data = data['tail5'];

      // 合并 top5 和 tail5 数据
      const conceptData = [...top5Data, ...tail5Data];
      const conceptNames = [
        ...top5Data.map(item => `Top 5 - ${item['名称']}`),
        ...tail5Data.map(item => `Tail 5 - ${item['名称']}`)
      ];

      // 将数值转化为“亿”单位
      conceptData.forEach(item => {
        item['今日主力净流入-净额'] /= 1e8;
        item['5日主力净流入-净额'] /= 1e8;
        item['10日主力净流入-净额'] /= 1e8;
      });

      this.conceptChartOption = this.createChartOption(conceptData, conceptNames, '概念版块');
    },
    handleChartClick(params) {
      if (params && params.name) {
        const industryName = params.name.split(' - ')[1]; 
        this.$emit('sector-selected', '概念资金流', industryName);
      }
    },
    createChartOption(data, names, title) {
      return {
        legend: {
          data: ['今日主力净流入-净额', '5日主力净流入-净额', '10日主力净流入-净额'],
          top: '5%',
          textStyle: {
            color: "#EAEAEA",
          },
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            const dataIndex = params[0].dataIndex;
            const item = data[dataIndex];
            return `
              <div>
                <strong>${title}</strong><br/>
                名称: <span style="color: #00FF00;">${item['名称']}</span><br/>
                今日涨跌幅: ${item['今日涨跌幅']}%<br/>
                今日主力净流入-净额: ${item['今日主力净流入-净额'].toFixed(2)} 亿<br/>
                5日主力净流入-净额: ${item['5日主力净流入-净额'].toFixed(2)} 亿<br/>
                10日主力净流入-净额: ${item['10日主力净流入-净额'].toFixed(2)} 亿
              </div>`;
          }
        },
        xAxis: {
          type: 'category',
          data: names,
          axisLabel: {
            rotate: 30,
            interval: 0
          },
          axisLine: {
            lineStyle: {
              color: "#EAEAEA",
            },
          },
        },
        yAxis: {
          type: 'value',
          name: '金额（亿）',
          axisLine: {
            lineStyle: {
              color: "#EAEAEA",
            },
          },
          axisLabel: {
            formatter: '{value} 亿'
          }
        },
        series: [
          // 今日主力净流入-净额
          {
            name: '今日主力净流入-净额',
            type: 'bar',
            data: data.map(item => item['今日主力净流入-净额']),
            barWidth: '20%',
            itemStyle: {
              color: (params) => params.value >= 0 ? '#FF0000' : '#008000'
            },
            z: 2
          },
          // 5日主力净流入-净额（堆叠柱子）
          {
            name: '5日主力净流入-净额',
            type: 'bar',
            stack: '5日10日',
            data: data.map(item => item['5日主力净流入-净额']),
            barWidth: '20%',
            itemStyle: {
              color: '#FFA500'
            },
            z: 1
          },
          // 10日主力净流入-净额（堆叠柱子）
          {
            name: '10日主力净流入-净额',
            type: 'bar',
            stack: '5日10日',
            data: data.map(item => item['10日主力净流入-净额']),
            barWidth: '20%',
            itemStyle: {
              color: '#00A4EF'
            },
            z: 1
          }
        ],
        grid: {
          containLabel: true,
        }
      };
    }
  }
};
</script>

<style scoped>
.fund-flow {
  width: 100%;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.charts-container {
  display: flex;
  height: 100%;
}

.chart-section {
  flex: 1;
  height: 100%;
  padding: 28px;
}

.chart-title {
  text-align: center;
}
</style>
