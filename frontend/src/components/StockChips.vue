<template>
  <div class="chip-distribution-chart">
    <VChart ref="chipChart" :option="chartOption" autoresize style="height: 100%;"/>
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
      required: true // 父组件必须传递股票代码
    }
  },
  data() {
    return {
      chartOption: null,
    };
  },
  watch: {
    stockCode(stockCode) {
      if (stockCode) {
        // 调用 FastAPI 的筹码分布数据接口
        api.get('/stock/chips', { params: { symbol: stockCode } })
            .then(response => {
              const chipData = response.data;
              if (chipData && chipData.length) {
                this.createChartOption(chipData);
              }
            })
            .catch(error => {
              console.error('Error fetching chip data:', error);
            });
      }
    }
  },
  methods: {
    createChartOption(chipData) {
      const dates = chipData.map((item) => item['日期']);
      const avgCosts = chipData.map((item) => item['平均成本']);
      const profitRatios = chipData.map((item) => (item['获利比例'] * 100).toFixed(2));
      const low90Costs = chipData.map((item) => item['90成本-低']);
      const high90Costs = chipData.map((item) => item['90成本-高']);

      this.chartOption = {
        color: ['#FF6347', '#32CD32', '#1E90FF'],
        legend: {
          data: ['平均成本', '获利比例', '90% 成本区间'],
          textStyle: {
            color: '#ffffff',
          },
        },
        dataZoom: [
          {
            type: 'slider',
            start: 80,
            end: 100,
            textStyle: {
              color: '#ffffff',
            },
          },
          {
            type: 'inside',
            start: 80,
            end: 100,
          },
        ],
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLabel: {
            color: '#ffffff',
          },
        },
        yAxis: [
          {
            type: 'value',
            name: '价格（元）',
            axisLabel: {
              color: '#ffffff',
            },
          },
          {
            type: 'value',
            name: '获利比例（%）',
            position: 'right',
            axisLabel: {
              formatter: '{value}%',
              color: '#ffffff',
            },
          },
        ],
        series: [
          {
            name: '平均成本',
            type: 'line',
            data: avgCosts,
            smooth: true,
            lineStyle: {
              color: '#FF6347',
              width: 2,
            },
          },
          {
            name: '获利比例',
            type: 'line',
            yAxisIndex: 1,
            data: profitRatios,
            smooth: true,
            lineStyle: {
              color: '#32CD32',
              width: 2,
            },
          },
          {
            name: '90% 成本区间（低）',
            type: 'line',
            stack: '区间',
            smooth: true,
            lineStyle: {
              width: 0
            },
            showSymbol: false,
            areaStyle: {
              opacity: 0.8,
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(30,144,255,0)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(30,144,255,0)'
                  }
                ]
              }
            },
            emphasis: {
              focus: 'series'
            },
            data: low90Costs,
          },
          {
            name: '90% 成本区间（高）',
            type: 'line',
            stack: '区间',
            smooth: true,
            lineStyle: {
              width: 0
            },
            showSymbol: false,
            areaStyle: {
              opacity: 0.8,
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgb(236,1,154)'
                  },
                  {
                    offset: 1,
                    color: 'rgb(181,255,0)'
                  }
                ]
              }
            },
            emphasis: {
              focus: 'series'
            },
            data: high90Costs.map((high, index) => high - low90Costs[index]),
          },
        ],
      };
    }
  }
};
</script>

<style scoped>
.chip-distribution-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26px;
}
</style>