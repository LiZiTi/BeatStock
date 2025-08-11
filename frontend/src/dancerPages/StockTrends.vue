<template>
  <div id="main" class="stock-detail-view">
    <StockSearchPage @stockSelected="onStockSelected" />
    <div id="indicator-values" class="indicator-values" v-if="currentDate">
      <div class="value-item">
        <span class="label">日期:</span>
        <strong class="value animated-span">{{ currentDate }}</strong>
      </div>
      <div class="value-item">
        <span class="label">开盘:</span>
        <strong class="value animated-span">{{ currentOpen }}</strong>
      </div>
      <div class="value-item">
        <span class="label">收盘:</span>
        <strong class="value animated-span">{{ currentClose }}</strong>
      </div>
      <div class="value-item">
        <span class="label">最高:</span>
        <strong class="value animated-span">{{ currentHigh }}</strong>
      </div>
      <div class="value-item">
        <span class="label">最低:</span>
        <strong class="value animated-span">{{ currentLow }}</strong>
      </div>
    </div>

    <VChart :option="chartOption" ref="chartInstance" autoresize class="trend-container" />
  </div>
</template>

<script>
import VChart from 'vue-echarts';
import 'echarts';
import { api } from "@/axiosConfig";
import StockSearchPage from "../components/StockSearchPage.vue";
import DancerPageBase from '../components/DancerPageBase.vue';

export default ({
  extends: DancerPageBase,
  pageName: '个股历史趋势',
  components: {
    VChart,
    StockSearchPage,
  },
  name: 'StockTrendReplay',
  props: {
    totalBeats: {
      type: Number,
      required: true,
    },
  },
  watch: {
    totalBeats(newVal) {
      if (newVal && this.fullData.length > 0) {
        this.internalTotalBeats = newVal; // 同步更新内部数据
        this.computeDataPointsPerBeat(); // 重新计算数据
      }
    },
  },
  data() {
    return {
      selectedStockCode: null, // 当前选中的股票
      selectedStockName:null,
      selectedPeriod: 'weekly',
      currentOpen: 0,
      currentClose: 0,
      currentHigh: 0,
      currentLow: 0,
      currentDate: null,
      displayStockData: [],
      displayAvg5: [],
      displayAvg21: [],
      rainbowColors: [
        'rgba(255, 0, 0, 0.8)',    // 红色
        'rgba(255, 165, 0, 0.8)',  // 橙色
        'rgba(255, 255, 0, 0.8)',  // 黄色
        'rgba(0, 255, 0, 0.8)',    // 绿色
        'rgba(0, 255, 255, 0.8)',  // 青色
        'rgba(0, 0, 255, 0.8)',    // 蓝色
        'rgba(128, 0, 128, 0.8)'   // 紫色
      ]
    };
  },
  computed: {
    indexValueStyle() {
      if (this.beatIndex <= 0 || this.beatIndex >= this.dataPointsToDisplayAtBeat.length) {
        return { color: "#FBBC05" }; // 默认颜色
      }

      const currentData = this.dataPointsToDisplayAtBeat[this.beatIndex];
      const previousData = this.dataPointsToDisplayAtBeat[this.beatIndex - 1];

      // 使用通用方法计算样式
      return this.calculateStyle(currentData["close"], previousData["close"]);
    }
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {
      this.displayDates = [];
      this.displayStockData = [];
      this.displayAvg5 = [];
      this.displayAvg21 = [];

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: [] },
          series: [
            { data: [] },
            { data: [] },
            { data: [] },
          ],
        });
      }
    },
    fullfillAllData() {
      this.displayDates = this.fullData.map(item => item.分钟时间);

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: this.displayDates },
          series: [
            { data: this.fullData },
            { data: this.displayAvg5 },
            { data: this.displayAvg21 },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {
      this.displayDates.push(dataPoint["日期"]);
      this.displayStockData.push([
        dataPoint['开盘'],
        dataPoint['收盘'],
        dataPoint['最低'],
        dataPoint['最高']
      ]);
      this.currentClose = dataPoint['收盘'];
      this.currentOpen = dataPoint['开盘'];
      this.currentHigh = dataPoint['最高'];
      this.currentLow = dataPoint['最低'];
      this.currentDate = dataPoint['日期'];

      this.whenValueUpdated()

      this.displayAvg5.push(dataPoint['avg5'])
      this.displayAvg21.push(dataPoint['avg21'])

      while (this.maxDisplayPoints > 0 && this.displayDates.length > this.maxDisplayPoints) {
        this.displayDates.shift();
        this.displayStockData.shift();
        this.displayAvg5.shift();
        this.displayAvg21.shift();
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.displayStockData;
      this.chartOption.series[1].data = this.displayAvg5;
      this.chartOption.series[2].data = this.displayAvg21;
    },
    loadStockHistory() {
      let stockCode = this.selectedStockCode;
      if (stockCode) {
        // 调用 FastAPI 的股票历史数据接口
        api.get(`/stock/history`, { params: { symbol: stockCode, period: this.selectedPeriod } })
          .then(response => {
            const stockHistoryData = response.data;
            this.displayAvg5 = this.calculateMovingAverage(stockHistoryData, 5);
            this.displayAvg21 = this.calculateMovingAverage(stockHistoryData, 21);

            stockHistoryData.forEach((item, index) => {
              item.avg5 = this.displayAvg5[index];  // 添加 avg5
              item.avg21 = this.displayAvg21[index]; // 添加 avg21
            });

            this.setFullData(stockHistoryData)
            this.initChart(stockHistoryData);
          })
          .catch(error => {
            console.error("Error fetching stock history:", error);
          });
      }
    },
    onStockSelected(stockCode, stockName, dataPeriod) {
      this.selectedStockCode = stockCode;
      this.selectedStockName = stockName;
      this.selectedPeriod = dataPeriod;
      this.loadStockHistory();
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
    calculateStyle(currentValue, previousValue) {
      if (currentValue > previousValue) {
        return { color: "#ff00aa" }; // 增长
      } else if (currentValue < previousValue) {
        return { color: "#34A853" }; // 下降
      } else {
        return { color: "#FBBC05" }; // 不变
      }
    },
    initChart(stockData) {

      this.chartOption = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 16
          },
          axisPointer: {
            type: 'cross', // 显示十字准线
            crossStyle: {
              color: '#999',
              type: 'dashed',
              width: 1
            },
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: ['K线图', '5日均线', '21日均线'],
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
            start: 0,
            end: 100
          },
          {
            type: 'inside',
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线图',
            type: 'candlestick',
            data: stockData.map(item => [
              item['开盘'],
              item['收盘'],
              item['最低'],
              item['最高']
            ]),
            itemStyle: {
              color: '#ff4d4f',
              color0: '#4caf50',
              borderColor: '#ff4d4f',
              borderColor0: '#4caf50'
            }
          },
          {
            name: '5日均线',
            type: 'line',
            data: stockData.map(item => item['avg5']),
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#ffa500'
            }
          },
          {
            name: '21日均线',
            type: 'line',
            data: stockData.map(item => item['avg21']),
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#00bfff'
            }
          }
        ]
      };
    },
    whenValueUpdated() {
      // 选择所有带有指定 class 的元素
      const elements = this.$el.querySelectorAll('.animated-span');

      if (!elements || elements.length === 0) {
        return;
      }

      elements.forEach((element) => {
        // 设置光晕颜色
        const currentGlowColor = this.rainbowColors[this.currentColorIndex];
        element.style.textShadow = `0 0 10px ${currentGlowColor}, 0 0 20px ${currentGlowColor}`;
        this.currentColorIndex = (this.currentColorIndex + 1) % this.rainbowColors.length;

        // 强制触发动画
        element.classList.remove('enlarged');
        void element.offsetWidth; // 强制 DOM 重绘
        element.classList.add('enlarged');

        // 动画结束后清除类名
        element.addEventListener(
          'animationend',
          () => {
            element.classList.remove('enlarged');
          },
          { once: true }
        );
      });
    },
  }
});
</script>

<style scoped>
.stock-detail-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #000000c7;
  border-radius: 12px;
}

.trend-container {
  width: 100%;
  height: 100%;
  position: relative;
}


.indicator-values {
  height: 15%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  margin-bottom: 40px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #EAEAEA;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.value-item {
  color: #EAEAEA;
  margin: 0 25px;
  display: flex;
  /* 使用 flex 布局 */
  /* 垂直排列子元素 */
  align-items: center;
  /* 水平居中 */
  justify-content: center;
  /* 垂直居中 */
  font-size: 1.2rem;
  /* 默认字体大小 */
}

.label {
  font-size: 1rem;
  /* 标签名称字体大小 */
  color: #EAEAEA;
  /* 标签名称颜色 */
}


.value {
  font-size: 1.6rem;
  transition: font-size 0.1s ease, text-shadow 0.1s ease;
  color: #FBBC05;
}

.value.enlarged {
  font-size: 3rem;
  animation: pulse 0.1s ease;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }

  100% {
    transform: scale(1);
  }
}
</style>