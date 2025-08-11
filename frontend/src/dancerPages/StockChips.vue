<template>
  <div id="main" class="stock-detail-view">
    <StockSearchPage @stockSelected="onStockSelected" />
    <div id="indicator-values" class="indicator-values" v-if="currentDate">
      <div class="value-item">
        <span class="label">日期</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentDate }}
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">平均成本</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentAvgPrice }}
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">获利比例：</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ currentProfitRatios }}%
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">70%高</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ current70High }}
          </span>
        </span>
      </div>
      <div class="value-item">
        <span class="label">70%低</span>
        <span class="value">
          <span class="highlight" :style="indexValueStyle">
            {{ current70Low }}
          </span>
        </span>
      </div>
    </div>
    <VChart :option="chartOption" ref="chartInstance" autoresize class="trend-container" />
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';
import StockSearchPage from "../components/StockSearchPage.vue";
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
  extends: DancerPageBase,
  pageName: '个股筹码分布',
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
      avgCosts: [],
      profitRatios: [],
      low90Costs: [],
      high90Costs: [],

      currentDate:null,
      currentProfitRatios:null,
      currentAvgPrice:null,
      current70High:null,
      current70Low:null,
    };
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

      this.displayDates = [];
      this.avgCosts = [];
      this.profitRatios = [];
      this.low90Costs = [];
      this.high90Costs = [];

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
      this.avgCosts = this.fullData.map((item) => item['平均成本']);
      this.profitRatios = this.fullData.map((item) => (item['获利比例'] * 100).toFixed(2));
      this.low90Costs = this.fullData.map((item) => item['70成本-低']);
      this.high90Costs = this.fullData.map((item) => item['70成本-高']);

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: this.displayDates },
          series: [
            { data: this.avgCosts },
            { data: this.profitRatios },
            { data: this.low90Costs },
            { data: this.high90Costs },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {

      this.displayDates.push(dataPoint["日期"])
      this.avgCosts.push(dataPoint["平均成本"].toFixed(2));
      this.profitRatios.push((dataPoint["获利比例"] * 100).toFixed(2));
      this.low90Costs.push(dataPoint["70成本-低"].toFixed(2));
      this.high90Costs.push(dataPoint["70成本-高"].toFixed(2));

      this.currentProfitRatios = (dataPoint["获利比例"] * 100).toFixed(2)
      this.currentAvgPrice = (dataPoint["平均成本"]).toFixed(2)
      this.current70Low = (dataPoint["70成本-低"]).toFixed(2)
      this.current70High = (dataPoint["70成本-高"]).toFixed(2)
      this.currentDate = (dataPoint["日期"] * 100).toFixed(2)

      if (this.maxDisplayPoints > 0) {
        while (this.displayDates.length > this.maxDisplayPoints) {
          this.displayDates.shift();
          this.avgCosts.shift();
          this.profitRatios.shift();
          this.low90Costs.shift();
          this.high90Costs.shift();
        }
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.avgCosts;
      this.chartOption.series[1].data = this.profitRatios;
      this.chartOption.series[2].data = this.low90Costs;
      this.chartOption.series[3].data = this.high90Costs;
    },
    onStockSelected(stockCode, stockName, dataPeriod) {
      this.selectedStockCode = stockCode;
      this.selectedStockName = stockName;
      this.selectedPeriod = dataPeriod;
      this.loadStockHistory();
    },
    loadStockHistory() {
      api.get('/stock/chips', { params: { symbol: this.selectedStockCode } })
        .then(response => {
          const chipData = response.data;
          if (chipData && chipData.length) {
            this.createChartOption(chipData);
            this.setFullData(chipData)
          }
        })
        .catch(error => {
          console.error('Error fetching chip data:', error);
        });
    },
    createChartOption(chipData) {
      this.displayDates = chipData.map((item) => item['日期']);
      this.avgCosts = chipData.map((item) => item['平均成本']);
      this.profitRatios = chipData.map((item) => (item['获利比例'] * 100).toFixed(2));
      this.low90Costs = chipData.map((item) => item['70成本-低']);
      this.high90Costs = chipData.map((item) => item['70成本-高']);

      this.chartOption = {
        color: ['#FF6347', '#32CD32', '#1E90FF'],
        legend: {
          data: ['平均成本', '获利比例', '70% 成本区间'],
          textStyle: {
            color: '#ffffff',
          },
        },
        dataZoom: [
          {
            type: 'slider',
            start: 0,
            end: 100,
            textStyle: {
              color: '#ffffff',
            },
          },
          {
            type: 'inside',
            start: 0,
            end: 100,
          },
        ],
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
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.displayDates,
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
            data: this.avgCosts,
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
            data: this.profitRatios,
            smooth: true,
            lineStyle: {
              color: '#32CD32',
              width: 2,
            },
          },
          {
            name: '70% 成本区间（低）',
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
            data: this.low90Costs,
          },
          {
            name: '70% 成本区间（高）',
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
            data: this.high90Costs
          },
        ],
      };
    }
  }
};
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
  margin-top: 36px;
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