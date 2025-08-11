<template>
  <div id="main" class="stock-detail-view">
    <StockSearchPage @stockSelected="onStockSelected" />
    <div id="indicator-values" class="indicator-values" v-if="currentROE">
      <div class="value-item">
        <span class="label">ROE：</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentROE }}%
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">销售净利率：</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentXL }}%
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">总资产周转率：</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentZZ }}%
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">资产负债率：</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentZF }}%
          </span>
        </span>
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
  pageName: '个股ROE%',
  components: {
    VChart,
    StockSearchPage,
  },
  props: {
    stockCode: {
      type: String,
      required: true // 父组件必须传递股票代码
    }
  },
  data() {
    return {
      selectedStockCode: null, // 当前选中的股票
      selectedStockName:null,
      selectedPeriod: 'weekly',
      roeValues: [],
      netProfitMargin: [],
      assetTurnover: [],
      debtRatio: [],
      currentROE:null,
      currentXL:null,
      currentZZ:null,
      currentZF:null,
    };
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

      this.displayDates = [];
      this.roeValues = [];
      this.netProfitMargin = [];
      this.assetTurnover = [];
      this.debtRatio = [];

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: [] },
          series: [
            { data: [] },
            { data: [] },
            { data: [] },
            { data: [] },
          ],
        });
      }
    },
    fullfillAllData() {
      this.displayDates = this.fullData.map(item => item['日期']);
      this.roeValues = this.fullData.map(item => ({
        value: item['ROE(%)'].toFixed(2),
        ...item // 将其他数据也传入 tooltip 中
      }));
      this.netProfitMargin = this.fullData.map(item => ({
        value: item['销售净利率(%)'].toFixed(2),
        ...item
      }));
      this.assetTurnover = this.fullData.map(item => ({
        value: item['总资产周转率(次)'].toFixed(2),
        ...item
      }));
      this.debtRatio = this.fullData.map(item => ({
        value: item['资产负债率(%)'].toFixed(2),
        ...item
      }));


      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: this.displayDates },
          series: [
            { data: this.roeValues },
            { data: this.netProfitMargin },
            { data: this.assetTurnover },
            { data: this.debtRatio },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {

      this.displayDates.push(dataPoint["日期"])
      this.roeValues.push(dataPoint["ROE(%)"].toFixed(2));
      this.netProfitMargin.push(dataPoint["销售净利率(%)"].toFixed(2));
      this.assetTurnover.push(dataPoint["总资产周转率(次)"].toFixed(2));
      this.debtRatio.push(dataPoint["资产负债率(%)"].toFixed(2));

      this.currentROE = dataPoint["ROE(%)"].toFixed(2)
      this.currentXL = dataPoint["销售净利率(%)"].toFixed(2)
      this.currentZZ = dataPoint["总资产周转率(次)"].toFixed(2)
      this.currentZF = dataPoint["资产负债率(%)"].toFixed(2)

      if (this.maxDisplayPoints > 0) {
        while (this.displayDates.length > this.maxDisplayPoints) {
          this.displayDates.shift();
          this.roeValues.shift();
          this.netProfitMargin.shift();
          this.assetTurnover.shift();
          this.debtRatio.shift();
        }
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.roeValues;
      this.chartOption.series[1].data = this.netProfitMargin;
      this.chartOption.series[2].data = this.assetTurnover;
      this.chartOption.series[3].data = this.debtRatio;
    },
    onStockSelected(stockCode, stockName, dataPeriod) {
      this.selectedStockCode = stockCode;
      this.selectedStockName = stockName;
      this.selectedPeriod = dataPeriod;
      this.loadStockHistory();
    },
    loadStockHistory() {
      api.get(`/stock/roe`, { params: { symbol: this.selectedStockCode } })
        .then(response => {
          const roeHistory = response.data;
          this.displayHistory(roeHistory); // 更新图表数据
          this.setFullData(roeHistory)
        })
        .catch(error => {
          console.error("Error fetching stock history:", error);
        });
    },
    displayHistory(roeData) {
      // 将数据从 API 响应中映射到图表中
      this.displayDates = roeData.map(item => item['日期']);
      this.roeValues = roeData.map(item => ({
        value: item['ROE(%)'].toFixed(2),
        ...item // 将其他数据也传入 tooltip 中
      }));
      this.netProfitMargin = roeData.map(item => ({
        value: item['销售净利率(%)'].toFixed(2),
        ...item
      }));
      this.assetTurnover = roeData.map(item => ({
        value: item['总资产周转率(次)'].toFixed(2),
        ...item
      }));
      this.debtRatio = roeData.map(item => ({
        value: item['资产负债率(%)'].toFixed(2),
        ...item
      }));

      // 更新图表配置
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
          data: ['ROE(%)', '销售净利率(%)', '总资产周转率(次)', '资产负债率(%)'],
          top: '5%',
          textStyle: {
            color: '#ffffff'
          }
        },
        xAxis: {
          type: 'category',
          data: this.displayDates
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
            start: 0,
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
            data: this.roeValues,
            lineStyle: {
              width: 4 // 线条加粗
            },
            z: 3 // 设置为最上层
          },
          {
            name: '销售净利率(%)',
            type: 'line',
            data: this.netProfitMargin,
            z: 2 // 第二层级
          },
          {
            name: '总资产周转率(次)',
            type: 'line',
            data: this.assetTurnover,
            z: 1 // 第三层级
          },
          {
            name: '资产负债率(%)',
            type: 'line',
            data: this.debtRatio,
            z: 1 // 第三层级
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
  background-color: #000000c7;
  border-radius: 12px;
}

.trend-container {
  width: 100%;
  height: 100%;
  position: relative;
}


.indicator-values {
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
  color: #FBBC05;
  font-size: 1.6rem;
  /* 数据值字体大小 */
}

.highlight {
  font-size: 1.5em;
  /* 突出值字体大小 */
  color: #34A853;
  font-weight: bold;
}
</style>