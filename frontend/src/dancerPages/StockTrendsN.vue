<template>
  <div id="main" class="stock-detail-view">
    <!-- 搜索页面 -->
    <StockSearchPage @stockSelected="onStockSelected" />

    <div id="cards-container" class="cards-container" v-if="stockCardList.length">
      <div class="stock-card" v-for="(card, index) in stockCardList" :key="card.stockCode" :style="{
        backgroundColor: rainbowColors[index],
        color: getReadableTextColor(rainbowColors[index])
      }">
        <h3>{{ card.stockName }}</h3>
        <p>代码: {{ card.stockCode }}</p>
        <p>最新股价: {{ card.currentClose }}</p>
      </div>
    </div>

    <!-- 图表 -->
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
  pageName: '多股趋势比较',
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
      selectedStockName: [], // 存储选中股票的名称
      selectedStockCode: [], // 存储选中股票的代码
      stockHistoryData: new Map(),  // 股票历史数据
      selectedPeriod: 'daily',
      currentClose: [],      // 存储当前选中股票的收盘价
      currentDate: null,     // 当前日期
      stockCardList: [],
      maxStocks: 7,
      rainbowColors: [       // 七种颜色
        '#FF0000', // 红
        '#FF7F00', // 橙
        '#FFFF00', // 黄
        '#00FF00', // 绿
        '#0000FF', // 蓝
        '#4B0082', // 靛
        '#8A2BE2'  // 紫
      ],
    };
  },
  methods: {
    clearChartData() {
      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.clear(); // 清空图表实例
        this.chartOption = {
          tooltip: {
            trigger: 'axis',
          },
          xAxis: {
            type: 'category',
            data: [], // 清空 X 轴数据
            boundaryGap: false,
            axisLabel: {
              color: '#ffffff',
            },
          },
          yAxis: {
            type: 'value',
            name: '归一化股价',
            axisLabel: {
              color: '#ffffff',
            },
            splitLine: {
              lineStyle: {
                type: 'dashed',
                color: '#ddd',
              },
            },
          },
          legend: {
            data: [], // 清空图例
            textStyle: {
              color: '#ffffff',
            },
          },
          series: [], // 清空系列数据
        };

        // 重设图表选项以清空内容
        this.$refs.chartInstance.setOption(this.chartOption);
      }
    },
    afterComputeDataPointsPerBeat(slice) {
      this.normalizeData(slice)
    },
    fullfillAllData() {

    },
    updateChartDataPoint(dataPoint) {
      // 1. 更新 X 轴日期
      const newDate = dataPoint["日期"];
      if (!this.displayDates.includes(newDate)) {
        this.displayDates.push(newDate); // 追加新日期到 X 轴
      }

      // 2. 更新每只股票的价格
      Object.keys(dataPoint).forEach(key => {
        if (key === "日期") return; // 跳过日期字段

        // 查找或创建对应的股票数据
        const seriesIndex = this.chartOption.series.findIndex(series => series.name === key);

        if (seriesIndex !== -1) {
          // 股票已存在，更新数据
          this.chartOption.series[seriesIndex].data.push(dataPoint[key]);
        } else {
          // 新股票，创建新的 series
          this.chartOption.series.push({
            name: key,
            type: 'line',
            data: [dataPoint[key]], // 初始化数据
            smooth: true,
            lineStyle: {
              width: 2,
              color: this.rainbowColors[this.chartOption.series.length % this.rainbowColors.length], // 动态分配颜色
            },
          });

          // 更新图例
          if (!this.chartOption.legend.data.includes(key)) {
            this.chartOption.legend.data.push(key);
          }
        }
      });
      // 3. 更新 X 轴数据
      this.chartOption.xAxis.data = this.displayDates;
      this.whenValueUpdated()
    },

    getReadableTextColor(hexColor) {
      // 去掉 '#' 并将颜色拆分为 R、G、B
      const r = parseInt(hexColor.slice(1, 3), 16);
      const g = parseInt(hexColor.slice(3, 5), 16);
      const b = parseInt(hexColor.slice(5, 7), 16);

      // 计算相对亮度
      const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;

      // 返回黑色或白色，根据亮度选择
      return luminance > 128 ? '#000000' : '#FFFFFF';
    },
    normalizeData(sliceCount) {
      console.log("normalizeData=" + sliceCount);
      if (this.stockHistoryData.size === 0) {
        alert("请先选择股票！");
        return;
      }

      let startDate = "0000-00-00";
      let endDate = "9999-99-99";

      this.stockHistoryData.forEach(history => {
        const stockStartDate = history[0]['日期'];
        const stockEndDate = history[history.length - 1]['日期'];
        if (stockStartDate > startDate) startDate = stockStartDate;
        if (stockEndDate < endDate) endDate = stockEndDate;
      });

      if (startDate > endDate) {
        alert("无有效对齐日期范围！");
        return;
      }

      const slicedData = new Map();
      this.stockHistoryData.forEach((history, stockCode) => {
        const alignedData = history
          .filter(item => item['日期'] >= startDate && item['日期'] <= endDate)
          .slice(-sliceCount);

        if (alignedData.length > 0) {
          slicedData.set(stockCode, alignedData);
        }
      });

      if (slicedData.size === 0) {
        alert("切片后没有有效的数据！");
        return;
      }

      const normalizedData = [];
      const allDates = new Set();
      slicedData.forEach((alignedData, stockCode) => {
        alignedData.forEach(item => allDates.add(item['日期']));

        const basePrice = 100;
        let previousPrice = basePrice;

        const normalizedPrices = Array.from(allDates).sort().map(date => {
          const record = alignedData.find(item => item['日期'] === date);
          if (record) {
            if (date === alignedData[0]['日期']) {
              previousPrice = basePrice;
              return { 日期: date, 归一化股价: basePrice.toFixed(2) };
            } else {
              const currentPrice = previousPrice * (1 + record['涨跌幅'] / 100);
              previousPrice = currentPrice;
              return { 日期: date, 归一化股价: currentPrice.toFixed(2) };
            }
          } else {
            // 如果没有数据，用上一个有效价格填充
            return { 日期: date, 归一化股价: previousPrice.toFixed(2) };
          }
        });

        normalizedData.push({
          stockCode,
          data: normalizedPrices,
        });
      });

      const sortedDates = Array.from(allDates).sort();

      const dynamicData = sortedDates.map(date => {
        const entry = { 日期: date };
        normalizedData.forEach(stock => {
          const priceData = stock.data.find(item => item.日期 === date);
          entry[stock.stockCode] = priceData ? parseFloat(priceData['归一化股价']) : null;
        });
        return entry;
      });

      this.dynamicStockData = dynamicData;
      this.dataPointsToDisplayAtBeat = dynamicData;
    },
    onStockSelected(stockCode, stockName, dataPeriod) {
      if (this.selectedStockCode.includes(stockCode)) {
        alert(`${stockCode} 已经在比较列表中！`);
        return;
      }
      this.selectedPeriod = dataPeriod;
      api.get(`/stock/history`, { params: { symbol: stockCode, period: this.selectedPeriod } })
        .then(response => {
          const stockHistoryData = response.data;

          // 添加新股票的名称和代码
          this.selectedStockCode.push(stockCode);
          this.selectedStockName.push(stockName);

          // 添加最新的股价数据
          const latestData = stockHistoryData[stockHistoryData.length - 1];
          const latestClose = latestData['收盘'];
          this.currentClose.push(latestData['收盘']);

          // 保存历史数据
          this.stockHistoryData.set(stockName, stockHistoryData);

          // 更新卡片列表
          this.stockCardList.push({
            stockCode,
            stockName,
            currentClose: latestClose,
          });

          // 如果超过 10 个，移除最早的一个
          if (this.selectedStockCode.length > this.maxStocks) {
            const removedStockCode = this.selectedStockCode.shift();
            this.selectedStockName.shift();
            this.currentClose.shift();
            this.stockHistoryData.delete(removedStockCode);

            // 从卡片列表中移除对应的卡片
            const removedIndex = this.stockCardList.findIndex(
              card => card.stockCode === removedStockCode
            );
            if (removedIndex !== -1) {
              this.stockCardList.splice(removedIndex, 1);
            }
          }
          this.normalizeData();
          this.setFullData(this.dynamicStockData);
          this.updateChartSeries();
        })
        .catch(error => {
          console.error("Error fetching stock history:", error);
        });
    },
    initChart() {

      this.chartOption = {
        tooltip: {
          trigger: 'axis',
        },
        legend: {
          data: [], // 图例初始化为空
        },
        series: [], // 初始化为空数组
      };
    },
    updateChartSeries() {
      if (!this.dynamicStockData || this.dynamicStockData.length === 0) {
        console.warn("没有可用的动态数据");
        return;
      }

      // 1. 获取 X 轴日期范围
      const xAxisData = this.dynamicStockData.map(item => item['日期']);

      // 2. 动态生成 series 数据
      const series = Array.from(this.stockHistoryData.keys()).map((stockCode, index) => ({
        name: stockCode,
        type: 'line',
        data: this.dynamicStockData.map(item => item[stockCode]), // 使用归一化股价数据
        smooth: true,
        lineStyle: {
          width: 2,
          color: this.rainbowColors[index % this.rainbowColors.length], // 设置线条颜色
        },
      }));

      // 3. 更新图表选项
      this.chartOption = {
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: xAxisData, // 使用动态生成的日期作为 X 轴数据
          boundaryGap: false,
          axisLabel: {
            color: '#ffffff',
          },
        },
        yAxis: {
          type: 'value',
          name: '归一化股价',
          axisLabel: {
            color: '#ffffff',
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#ddd',
            },
          },
        },
        legend: {
          data: Array.from(this.stockHistoryData.keys()), // 图例显示所有股票代码
          textStyle: {
            color: '#ffffff',
          },
        },
        dataZoom: [
          {
            type: 'slider',
            start: 0,
            end: 100,
          },
          {
            type: 'inside',
            start: 0,
            end: 100,
          },
        ],
        series, // 更新 series 数据
      };
    },
    whenValueUpdated() {
      // 获取所有股票卡片元素
      const cards = this.$el.querySelectorAll('.stock-card');

      if (!cards || cards.length === 0) {
        console.warn("没有找到任何股票卡片！");
        return;
      }

      // 移除所有卡片的特效
      cards.forEach(card => {
        card.classList.remove('highlighted'); // 移除高亮效果
      });

      // 确定当前需要高亮的卡片索引
      if (this.currentCardIndex === undefined || this.currentCardIndex >= cards.length) {
        this.currentCardIndex = 0; // 如果没有设置或越界，从第一个开始
      }

      const currentCard = cards[this.currentCardIndex];

      // 添加高亮效果
      currentCard.classList.add('highlighted');

      // 设置光晕颜色
      const currentGlowColor = this.rainbowColors[this.currentCardIndex % this.rainbowColors.length];
      currentCard.style.boxShadow = `0 0 20px ${currentGlowColor}, 0 0 40px ${currentGlowColor}`;

      // 设置动画完成后自动清除效果
      currentCard.addEventListener(
        'animationend',
        () => {
          currentCard.classList.remove('highlighted');
        },
        { once: true }
      );

      // 更新索引以循环选择
      this.currentCardIndex = (this.currentCardIndex + 1) % cards.length;
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
  background-color: #000000c7;
  border-radius: 12px;
}

.trend-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.cards-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin: 20px 0;
}

.stock-card {
  color: #ffffff;
  /* 卡片内容文字颜色 */
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
  width: 150px;
  transition: background-color 0.3s;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stock-card.highlighted {
  transform: scale(1.2);
  /* 放大 1.2 倍 */
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  /* 默认光晕效果，具体颜色由 JS 动态设置 */
}

.stock-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.stock-card p {
  margin: 0;
  font-size: 14px;
}


.button-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

button {
  background-color: #007bff;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}
</style>