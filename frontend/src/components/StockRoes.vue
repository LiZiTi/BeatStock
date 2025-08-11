<template>
  <div id="main" class="stock-detail-view">
    <VChart :option="roeOption" ref="trendChart" autoresize class="trend-container"/>
  </div>
</template>

<script>
import VChart from 'vue-echarts';
import 'echarts';
import { api } from "@/axiosConfig";

export default ({
  components: {
    VChart
  },
  props: {
    stockCode: {
      type: String,
      required: true // 父组件必须传递股票代码
    }
  },
  watch: {
    stockCode(stockCode) {
      if (stockCode) {
        // 调用 FastAPI 的股票历史数据接口
        api.get(`/stock/roe`, { params: { symbol: stockCode } })
            .then(response => {
              const roeHistory = response.data;
              this.displayHistory(roeHistory); // 更新图表数据
            })
            .catch(error => {
              console.error("Error fetching stock history:", error);
            });
      }
    }
  },
  data() {
    return {
      roeOption: null
    };
  },
  methods: {
    displayHistory(roeData) {
      // 将数据从 API 响应中映射到图表中
      const dates = roeData.map(item => item['日期']);
      const roeValues = roeData.map(item => ({
        value: item['ROE(%)'],
        ...item // 将其他数据也传入 tooltip 中
      }));
      const netProfitMargin = roeData.map(item => ({
        value: item['销售净利率(%)'],
        ...item
      }));
      const assetTurnover = roeData.map(item => ({
        value: item['总资产周转率(次)'],
        ...item
      }));
      const debtRatio = roeData.map(item => ({
        value: item['资产负债率(%)'],
        ...item
      }));

      // 更新图表配置
      this.roeOption = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          formatter: function (params) {
            let result = params[0].name + '<br/>';
            params.forEach(item => {
              const data = item.data;
              const color = item.color; // 获取当前项的颜色
              result += `
                <span style="color:${color};">${item.seriesName}:</span> ${data.value !== undefined ? data.value : 'N/A'}<br/>
              `;
            });
            return result;
          }
        },
        legend: {
          data: ['ROE(%)', '销售净利率(%)', '总资产周转率(次)', '资产负债率(%)'],
          top: '5%',
          textStyle: {
            color: '#ffffff'
          }
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value',
          name: '百分比(%)',
          min: -20, // Y轴下限
          max: 80,  // Y轴上限
        },
        dataZoom: [
          {
            type: 'slider',
            start: 60,
            end: 100,
            textStyle: {
              color: '#ffffff'
            }
          }
        ],
        series: [
          {
            name: 'ROE(%)',
            type: 'line',
            data: roeValues,
            lineStyle: {
              width: 4 // 线条加粗
            },
            z: 3 // 设置为最上层
          },
          {
            name: '销售净利率(%)',
            type: 'line',
            data: netProfitMargin,
            z: 2 // 第二层级
          },
          {
            name: '总资产周转率(次)',
            type: 'line',
            data: assetTurnover,
            z: 1 // 第三层级
          },
          {
            name: '资产负债率(%)',
            type: 'line',
            data: debtRatio,
            z: 1 // 第三层级
          }
        ]
      };

      // 手动更新 ECharts 组件
      this.$refs.trendChart.setOption(this.roeOption);
    }
  }
});
</script>

<style scoped>
.stock-detail-view {
  width: 100%;
  height: 400px;
}

.trend-container {
  width: 100%;
  height: 100%;
}
</style>