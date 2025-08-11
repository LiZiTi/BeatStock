<template>
  <div id="main" class="stock-detail-view">
    <VChart :option="trendOption" ref="trendChart" autoresize class="trend-container"/>
  </div>
</template>

<script>
import VChart from 'vue-echarts';
import 'echarts';
import {api} from "@/axiosConfig";

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
  name: 'StockTrendReplay',
  data() {
    return {
      stockData: [],
      sampledStockData: [],
      highestPrice: 0,
      lowestPrice: 0,
      initialInvestment: 1000000,
      initialShares: 0,
      trendOption: {}
    };
  },
  watch: {
    stockCode(stockCode) {
      if (stockCode) {
        // 调用 FastAPI 的股票历史数据接口
        api.get(`/stock/history`, {params: {symbol: stockCode}})
            .then(response => {
              const stockHistoryData = response.data;

              // 处理返回的数据
              this.stockData = stockHistoryData;
              this.sampledStockData = this.sampleStockData(stockHistoryData);

              // 计算最高价和最低价
              const prices = this.sampledStockData.map(item => item['收盘']);
              this.highestPrice = Math.max(...prices);
              this.lowestPrice = Math.min(...prices);

              // 计算初始持股数量
              this.initialShares = this.initialInvestment / this.sampledStockData[0]['收盘'];

              // 创建股票趋势回放图
              this.createStockTrendReplay(this.sampledStockData);
            })
            .catch(error => {
              console.error("Error fetching stock history:", error);
            });
      }
    }
  },
  methods: {
    sampleStockData(stockData) {
      const oneYearAgo = new Date(new Date().setFullYear(new Date().getFullYear() - 1));
      const oneYearAgoIndex = stockData.findIndex(item => new Date(item['日期']) >= oneYearAgo);
      const recentData = stockData.slice(oneYearAgoIndex);
      const sampledData = [];

      for (let i = 0; i < oneYearAgoIndex; i += 10) {
        sampledData.push(stockData[i]);
      }

      return [...sampledData, ...recentData];
    },
    calculateMovingAverage(stockData, days) {
      const maData = [];
      for (let i = 0; i < stockData.length; i++) {
        if (i < days - 1) {
          maData.push(null);
        } else {
          const sum = stockData.slice(i - days + 1, i + 1).reduce((acc, item) => acc + item['收盘'], 0);
          maData.push((sum / days).toFixed(2));
        }
      }
      return maData;
    },
    createStockTrendReplay(stockData) {
      // 创建股票趋势回放的图表配置
      const ma5 = this.calculateMovingAverage(stockData, 5);
      const ma21 = this.calculateMovingAverage(stockData, 21);

      this.trendOption = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
        },
        legend: {
          data: ['K线图', '5日均线', '21日均线', '成交额'],
          top: 30,
          textStyle: {
            color: '#ffffff'
          }
        },
        xAxis: {
          type: 'category',
          data: stockData.map(item => item['日期']),
          boundaryGap: true,
          axisLabel: {
            color: '#ffffff',
            show: true
          }
        },
        yAxis: {
          type: 'value',
          name: '价格',
          axisLabel: {
            color: '#ffffff'
          }
        },
        dataZoom: [
          {
            type: 'slider',
            start: 90,
            end: 100,
            textStyle: {
              color: '#ffffff'
            }
          }
        ],
        series: [
          {
            name: 'K线图',
            type: 'candlestick',
            data: stockData.map(item => [
              item['开盘'],
              item['收盘'],
              item['最高'],
              item['最低']
            ]),
            itemStyle: {
              color: '#ff4d4f',
              color0: '#4caf50',
              borderColor: '#ff4d4f',
              borderColor0: '#4caf50'
            }
          },
          {
            name: '成交额',
            type: 'bar',
            data: stockData.map(item => (item['成交额'] / Math.max(...stockData.map(d => d['成交额']))) * (this.highestPrice * 0.3)),
            barWidth: 10,
            yAxisIndex: 0
          },
          {
            name: '5日均线',
            type: 'line',
            data: ma5,
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#ffa500'
            }
          },
          {
            name: '21日均线',
            type: 'line',
            data: ma21,
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#00bfff'
            }
          }
        ]
      };
    }
  }
});
</script>

<style scoped>
.stock-detail-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.trend-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>