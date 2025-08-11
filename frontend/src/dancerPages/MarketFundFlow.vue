<template>
  <div class="fund-flow">
    <div class="title-section">
      <h2>{{ lastFundInfo["日期"] }}&nbsp;&nbsp;总成交额：{{ totalAmount }}亿</h2>
    </div>
    <div class="upper-section" v-if="totalAmount">
      <vxe-table :data="recent100Market" border round height="100%" size="large" align="center"
        :row-config="{ isCurrent: true, isHover: true }" :column-config="{ resizable: true, width: 'auto' }" stripe
        show-header>
        <vxe-column field="日期" title="日期" sortable></vxe-column>
        <vxe-column field="上证-收盘价" title="上证-收盘价" sortable></vxe-column>
        <vxe-column field="上证-涨跌幅" title="上证-涨跌幅%" sortable>
          <template #default="{ row }">
            {{ row['上证-涨跌幅'] }}
          </template>
        </vxe-column>
        <vxe-column field="深证-收盘价" title="深证-收盘价" sortable></vxe-column>
        <vxe-column field="深证-涨跌幅" title="深证-涨跌幅%" sortable>
          <template #default="{ row }">
            {{ row['深证-涨跌幅'] }}
          </template>
        </vxe-column>
        <vxe-column field="主力净流入-净额" title="主力净流入-净额(亿)" sortable>
          <template #default="{ row }">
            {{ (row['主力净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
        <vxe-column field="中单净流入-净额" title="中单净流入-净额(亿)" sortable>
          <template #default="{ row }">
            {{ (row['中单净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
        <vxe-column field="小单净流入-净额" title="小单净流入-净额(亿)" sortable>
          <template #default="{ row }">
            {{ (row['小单净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
      </vxe-table>
    </div>
    <div class="upper-section" v-if="lastMainInflow">
      <div class="info-item"
        :class="{ 'positive-value': parseFloat(lastMainInflow) >= 0, 'negative-value': parseFloat(lastMainInflow) < 0 }">
        <span>日期：</span>
        <strong>{{ lastDate }}</strong>
      </div>
      <div class="info-item"
        :class="{ 'positive-value': parseFloat(lastMainInflow) >= 0, 'negative-value': parseFloat(lastMainInflow) < 0 }">
        <span>主力净流入：</span>
        <strong>{{ lastMainInflow }}亿</strong>
      </div>
      <div class="info-item"
        :class="{ 'positive-value': parseFloat(lastMidInflow) >= 0, 'negative-value': parseFloat(lastMidInflow) < 0 }">
        <span>中单净流入：</span>
        <strong>{{ lastMidInflow }}亿</strong>
      </div>
      <div class="info-item"
        :class="{ 'positive-value': parseFloat(lastMinInflow) >= 0, 'negative-value': parseFloat(lastMinInflow) < 0 }">
        <span>小单净流入：</span>
        <strong>{{ lastMinInflow }}亿</strong>
      </div>
    </div>
    <div class="bottom-section">
      <v-chart ref="chartInstance" :option="chartOption" autoresize style="height: 100%;" />
    </div>
  </div>
</template>

<style scoped>
.fund-flow {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #000000c7;
}

.upper-section {
  height: 20%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  color: #eeff00;
  transition: transform 0.3s ease;
}

.bottom-section {
  height: 60%;
  width: 100%;
  margin-top: 20px;
}

.positive-value strong {
  color: red;
}

.negative-value strong {
  color: greenyellow;
}

.info-item {
  flex: 1;
  text-align: center;
  font-size: 18px;
  color: #eaeaea;
  font-weight: bold;
  width: 100px;
}

table {
  border-collapse: collapse;
  color: white;
  font-size: 16px;

}

th,
td {
  padding: 10px;
  text-align: left;
  border: 1px solid white;
  text-align: center;
}

th {
  background-color: #444;
  text-align: center;
}

td {
  background-color: #333;
}

.title-section {
  text-align: center;
  color: pink;
}
</style>

<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
  extends: DancerPageBase,
  pageName: '市场资金流',
  components: {
    VChart
  },
  data() {
    return {
      lastDate: null,
      lastMainInflow: null,
      lastMidInflow: null,
      lastMinInflow: null,

      recent100Market: [],
      totalAmount: null,
      chartOption: null,

      mainInflow: [],
      midInflow: [],
      minInflow: [],
      bullbearScore: [],
      lastFundInfo: {}
    };
  },
  async mounted() {
    try {
      const response = await api.get("/market-fund-flow");
      this.recent100Market = response.data.recent_market_data;
      this.totalAmount = response.data.total_market_amount.toFixed(2);
      if (this.recent100Market.length > 0) {
        this.lastFundInfo = this.recent100Market[this.recent100Market.length - 1]
      }
      this.setFullData(this.recent100Market);
      this.createBarChart();
    } catch (error) {
      console.error("Failed to fetch fund flow data", error);
    }
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

      this.displayDates = [];
      this.mainInflow = [];
      this.midInflow = [];
      this.minInflow = [];
      this.bullbearScore = [];

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

      console.log('fullfillAllData')

      const categories = this.recent100Market.map((item) => item.日期);
      const mainInflow = this.recent100Market.map((item) => (item["主力净流入-净额"] / 10000 / 10000).toFixed(2));
      const midInflow = this.recent100Market.map((item) => (item["中单净流入-净额"] / 10000 / 10000).toFixed(2));
      const minInflow = this.recent100Market.map((item) => (item["小单净流入-净额"] / 10000 / 10000).toFixed(2));
      const bullbearScore = this.recent100Market.map((item) => (item["多空评分"]).toFixed(2));

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: categories },
          series: [
            { data: mainInflow },
            { data: midInflow },
            { data: minInflow },
            { data: bullbearScore },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {

      this.displayDates.push(dataPoint["日期"])
      this.mainInflow.push((dataPoint["主力净流入-净额"] / 1e8).toFixed(2));
      this.midInflow.push((dataPoint["中单净流入-净额"] / 1e8).toFixed(2));
      this.minInflow.push((dataPoint["小单净流入-净额"] / 1e8).toFixed(2));
      this.bullbearScore.push(dataPoint["多空评分"].toFixed(2));

      this.lastDate = dataPoint["日期"];
      this.lastMainInflow = (dataPoint["主力净流入-净额"] / 1e8).toFixed(2);
      this.lastMidInflow = (dataPoint["中单净流入-净额"] / 1e8).toFixed(2);
      this.lastMinInflow = (dataPoint["小单净流入-净额"] / 1e8).toFixed(2);

      if (this.maxDisplayPoints > 0) {
        while (this.displayDates.length > this.maxDisplayPoints) {
          this.displayDates.shift();
          this.mainInflow.shift();
          this.midInflow.shift();
          this.minInflow.shift();
          this.bullbearScore.shift();
        }
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.mainInflow;
      this.chartOption.series[1].data = this.midInflow;
      this.chartOption.series[2].data = this.minInflow;
      this.chartOption.series[3].data = this.bullbearScore;
    },
    createBarChart() {
      const categories = this.recent100Market.map((item) => item.日期);
      const mainInflow = this.recent100Market.map((item) => (item["主力净流入-净额"] / 10000 / 10000).toFixed(2));
      const midInflow = this.recent100Market.map((item) => (item["中单净流入-净额"] / 10000 / 10000).toFixed(2));
      const minInflow = this.recent100Market.map((item) => (item["小单净流入-净额"] / 10000 / 10000).toFixed(2));
      const bullbearScore = this.recent100Market.map((item) => (item["多空评分"]).toFixed(2));

      this.chartOption = {
        textStyle: {
          color: '#ffffff'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: { color: '#ffffff', fontSize: 12 },
        },
        legend: {
          data: ['主力净流入', '中单净流入', '小单净流入', '资金多空评分'],
          textStyle: { color: '#ffffff' },
        },
        xAxis: {
          type: 'category',
          data: categories,
        },
        yAxis: [
          {
            type: 'value',
            name: '金额（亿元）',
            min: (value) => Math.min(0, value.min),
            max: (value) => Math.max(0, value.max),
          },
          {
            type: 'value',
            name: '多空评分',
            position: 'right',
            min: 0,
            max: 100,
          }
        ],
        dataZoom: [
          {
            type: 'slider', // 滑动条类型
            start: 0,       // 默认显示全部
            end: 100
          },
          {
            type: 'inside', // 鼠标滚轮缩放类型
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: '主力净流入',
            type: 'bar',
            stack: '总量',
            data: mainInflow,
            itemStyle: {
              color: '#EA4335',  // Red for positive, green for negative
            },
          },
          {
            name: '中单净流入',
            type: 'bar',
            stack: '总量',
            data: midInflow,
            itemStyle: {
              color: '#4285F4',  // Red for positive, green for negative
            },
          },
          {
            name: '小单净流入',
            type: 'bar',
            stack: '总量',
            data: minInflow,
            itemStyle: {
              color: '#34A853',  // Red for positive, green for negative
            },
          },
          {
            name: '资金多空评分',
            type: 'line',
            yAxisIndex: 1,
            data: bullbearScore,
            lineStyle: { color: 'yellow ', width: 2 },
            smooth: true,
          },
        ],
      };
    },
  },
};
</script>
