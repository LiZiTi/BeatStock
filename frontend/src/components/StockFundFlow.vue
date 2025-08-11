<template>
  <div class="chip-distribution-chart">
    <VChart ref="chipChart" :option="chartOption" autoresize class="flow-container" />
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';

export default {
  components: {
    VChart,
  },
  props: {
    stockCode: {
      type: String,
      required: true, // 父组件必须传递股票代码
    },
  },
  data() {
    return {
      chartOption: {},
      fundFlowData: [], // 保存从接口获取的数据
    };
  },
  watch: {
    stockCode: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchFundFlowData(newVal);
        }
      },
    },
  },
  methods: {
    // 调用接口获取资金流向数据
    async fetchFundFlowData(stockCode) {
      try {
        const response = await api.get(`/stock/flow`, { params: { symbol: stockCode } });
        this.fundFlowData = response.data;
        this.generateChartOption();
      } catch (error) {
        console.error("Error fetching fund flow data:", error);
      }
    },
    // 生成 ECharts 的配置项
    generateChartOption() {
      const dates = this.fundFlowData.map(item => item["日期"]);
      const mainInflow = this.fundFlowData.map(item => item["主力净流入-净额"] / 1e8);
      const largeOrder = this.fundFlowData.map(item => item["超大单净流入-净额"] / 1e8);
      const bigOrder = this.fundFlowData.map(item => item["大单净流入-净额"] / 1e8);
      const mediumOrder = this.fundFlowData.map(item => item["中单净流入-净额"] / 1e8);
      const smallOrder = this.fundFlowData.map(item => item["小单净流入-净额"] / 1e8);

      this.chartOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          formatter: function (params) {
            let content = `${params[0].name}<br/>`;
            params.forEach(param => {
              content += `${param.seriesName}: ${param.value}<br/>`;
            });
            return content;
          },
        },
        legend: {
          data: ['超大单', '大单', '中单', '小单', '主力净流入'],
          textStyle: {
            color: '#ffffff',
          },
        },
        dataZoom: [
          {
            type: 'inside',
            start: 80, // 默认展示近10个交易日的数据
            end: 100,
          },
          {
            start: 80,
            end: 100,
          },
        ],
        xAxis: {
          type: 'category',
          data: dates,
          boundaryGap: true,
        },
        yAxis: [
          {
            type: 'value',
            name: '流入流出',
            position: 'left',
          },
          {
            type: 'value',
            name: '主力净流入',
            position: 'right',
            axisLabel: {
              formatter: '{value}',
            },
          },
        ],
        series: [
          {
            name: '超大单',
            type: 'bar',
            stack: '流入流出',
            data: largeOrder,
          },
          {
            name: '大单',
            type: 'bar',
            stack: '流入流出',
            data: bigOrder,
          },
          {
            name: '中单',
            type: 'bar',
            stack: '流入流出',
            data: mediumOrder,
          },
          {
            name: '小单',
            type: 'bar',
            stack: '流入流出',
            data: smallOrder,
          },
          {
            name: '主力净流入',
            type: 'line',
            yAxisIndex: 1,
            data: mainInflow,
          },
        ],
      };
    },
  },
};
</script>

<style scoped>
.chip-distribution-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 26px;
}

.flow-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
