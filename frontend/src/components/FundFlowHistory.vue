<template>
  <div class="fund-flow">
    <!-- 图表容器 -->
    <v-chart
      ref="fundFlowChart"
      :option="chartOption"
      autoresize
      style="height: 100%;"
    />
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
      chartOption: {},
    };
  },
  methods: {
    async fetchData() {
      try {
        const response = await api.get("/sector-fund-flow-his", {
          params: {
            sector_type: "行业资金流", // 替换为实际的板块类型
            symbol: "能源金属",     // 替换为实际的符号
          },
        });
        const data = response.data;
        console.log(data)
        this.initChart(data);
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    initChart(data) {
      const dates = [];
      const mainNetAmounts = [];
      const mediumNetAmounts = [];
      const smallNetAmounts = [];

      data.forEach(item => {
        dates.push(item['日期']);
        // 金额换算成以万为单位
        mainNetAmounts.push((item['主力净流入-净额'] / 10000).toFixed(2));
        mediumNetAmounts.push((item['中单净流入-净额'] / 10000).toFixed(2));
        smallNetAmounts.push((item['小单净流入-净额'] / 10000).toFixed(2));
      });

      this.chartOption = {
        color: ['#FF5733', '#33FF57', '#3357FF'], // 鲜艳的颜色：橙红、亮绿、亮蓝
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function (params) {
            let result = params[0].name + '<br/>';
            params.forEach(item => {
              result += item.marker + item.seriesName + ': ' + item.value + ' 万<br/>';
            });
            return result;
          }
        },
        legend: {
          data: ['主力净流入-净额', '中单净流入-净额', '小单净流入-净额'],
          textStyle: {
            color: '#fff'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        dataZoom: [
          {
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            start: 60, // 默认展示后40%
            end: 100,
            bottom: '5%',
            textStyle: {
              color: '#fff'
            },
            handleIcon: 'M8.2,13.9v-3.4H5v3.4H2.5l3.7,3.7l3.7-3.7H8.2z',
            handleSize: '80%',
            handleStyle: {
              color: '#fff',
              shadowBlur: 3,
              shadowColor: 'rgba(0, 0, 0, 0.6)',
              shadowOffsetX: 2,
              shadowOffsetY: 2
            },
            backgroundColor: 'rgba(47,69,84,0.3)',
            fillerColor: 'rgba(167,183,204,0.4)',
            dataBackground: {
              lineStyle: {
                color: '#fff'
              },
              areaStyle: {
                color: '#fff'
              }
            }
          },
          {
            type: 'inside',
            xAxisIndex: [0],
            start: 60,
            end: 100
          }
        ],
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            interval: 0,
            rotate: 45,
            textStyle: {
              color: '#fff'
            }
          },
          axisLine: {
            lineStyle: {
              color: '#fff'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '净额 (万)',
          axisLabel: {
            textStyle: {
              color: '#fff'
            }
          },
          axisLine: {
            lineStyle: {
              color: '#fff'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#555'
            }
          }
        },
        series: [
          {
            name: '主力净流入-净额',
            type: 'bar',
            stack: '总量',
            data: mainNetAmounts
          },
          {
            name: '中单净流入-净额',
            type: 'bar',
            stack: '总量',
            data: mediumNetAmounts
          },
          {
            name: '小单净流入-净额',
            type: 'bar',
            stack: '总量',
            data: smallNetAmounts
          }
        ]
      };
    }
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style scoped>
.fund-flow {
  background-color: #2c343c;
  padding: 20px;
  width: 100%;
  height: 100%;
}
</style>