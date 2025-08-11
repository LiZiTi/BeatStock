<template>
  <div class="stock-statistic-view">
    <div class="left-area">
      <!-- 上面的部分 -->
      <div class="upper-container">
        <div class="chart-container">
          <v-chart ref="distributionChart" :option="distributionChartOption" autoresize />
        </div>
      </div>

      <!-- 中间的指标部分 -->
      <div v-if="currentStockName" class="middle-container">
        <div class="indicator-row">
          <span class="indicator-item">
            <span class="label">股票名称：</span>
            <span class="value" :style="{ color: currentStockColor }">{{ currentStockName }}</span>
          </span>
          <span class="indicator-item">
            <span class="label">涨跌幅：</span>
            <span class="value" :style="{ color: currentStockColor }">{{ currentStockChange }}%</span>
          </span>
          <span class="indicator-item">
            <span class="label">60日涨幅：</span>
            <span class="value" :style="{ color: currentStockColor }">{{ currentStock60R }}%</span>
          </span>
          <span class="indicator-item">
            <span class="label">成交额：</span>
            <span class="value" :style="{ color: currentStockColor }">{{ currentStockMount }}</span>
          </span>
          <span class="indicator-item">
            <span class="label">换手率：</span>
            <span class="value" :style="{ color: currentStockColor }">{{ currentStockHandR }}%</span>
          </span>
        </div>
      </div>

      <!-- 下面的部分 -->
      <div class="lower-container">
        <div class="chart-container">
          <v-chart ref="chartInstance" :option="chartOption" autoresize />
        </div>
      </div>
    </div>
    <div class="right-area">
      <h3>横向整理筹码集中股</h3>
      <vxe-table :data="sidewaysStocks" border round height="85%" size="large" align="center"
        :row-config="{ isCurrent: true, isHover: true }" stripe show-header :column-config="{ resizable: true, width: 'auto' }">
        <vxe-column field="代码" title="代码"></vxe-column>
        <vxe-column field="名称" title="名称"></vxe-column>
        <vxe-column field="涨跌幅" title="涨跌幅" sortable></vxe-column>
      </vxe-table>
    </div>
  </div>
</template>


<script>
import VChart from 'vue-echarts';
import 'echarts';
import DancerPageBase from '../components/DancerPageBase.vue';
import { api } from "@/axiosConfig";

export default {
  extends: DancerPageBase,
  pageName: '个股统计分析',
  name: "StockStatisticView",
  components: {
    VChart,
  },
  computed: {
    currentStockColor() {
      return this.getGradientColor(this.currentStockChange);
    },
  },
  data() {
    return {
      currentStockName: null,
      currentStockChange: null,
      currentStock60R: null,
      currentStockMount: null,
      currentStockHandR: null,

      distributionChartOption: {}, // 上图配置
      sidewaysStocks: [],

      stockChanges: [],
      stockMount: [],
      stockHandR: [],
      stock60R: [],
      stockYearR: [],
    };
  },
  async mounted() {
    try {
      // 调用 API 获取数据
      let response = await api.get("/stock-sts");
      const responseData = response.data;

      // 设置图表配置
      this.setupCharts(responseData);

      response = await api.get("/stock-sw");
      this.sidewaysStocks = response.data;

    } catch (error) {
      console.error("Error fetching stock statistic data:", error);
    }
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

      this.displayDates = [];
      this.stockChanges = [];

      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: [] },
          series: [
            { data: [] },
          ],
        });
      }
    },
    fullfillAllData() {
      this.displayDates = this.fullData.map((stock) => stock["名称"]);
      this.stockChanges = this.fullData.map((stock) => stock["涨跌幅"]);


      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: this.displayDates },
          series: [
            { data: this.stockChanges },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {

      this.displayDates.push(dataPoint["名称"]);
      this.stockChanges.push({
        value: dataPoint["涨跌幅"],
        itemStyle: {
          color: this.getGradientColor(dataPoint["涨跌幅"]),
        },
      });

      this.currentStockName = dataPoint["名称"];
      this.currentStockChange = dataPoint["涨跌幅"];
      this.currentStockMount = ((dataPoint["成交额"]) / 1e8).toFixed(2);
      this.currentStockHandR = dataPoint["换手率"];
      this.currentStock60R = dataPoint["60日涨跌幅"];


      if (this.maxDisplayPoints > 0) {
        while (this.displayDates.length > this.maxDisplayPoints) {
          this.displayDates.shift();
          this.stockChanges.shift();
        }
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.stockChanges;
    },
    getGradientColor(value) {
      // 确保 value 的范围在 -20% 到 20% 之间
      const clampedValue = Math.max(-20, Math.min(20, value));

      // 将值映射到 [0, 1] 范围 (线性归一化)
      const normalizedValue = (clampedValue + 20) / 40;

      // 计算红、绿通道的权重
      const redWeight = normalizedValue; // 越接近 1 越红
      const greenWeight = 1 - normalizedValue; // 越接近 0 越绿

      // 根据权重生成颜色
      const red = Math.round(255 * redWeight);
      const green = Math.round(255 * greenWeight);
      const blue = 0; // 蓝色固定为 0

      // 返回 RGB 颜色
      return `rgb(${red}, ${green}, ${blue})`;
    },
    setupCharts(data) {
      // 上图：涨跌幅分布
      const distributionData = data["统计结果"]["涨跌幅分布"];
      const categories = Object.keys(distributionData);
      const values = Object.values(distributionData);

      const upCount = data["统计结果"]["上涨家数"];
      const flatCount = data["统计结果"]["平盘家数"];
      const downCount = data["统计结果"]["下跌家数"];

      this.distributionChartOption = {
        title: {
          text: `{red|上涨: ${upCount}}   {yellow|平盘: ${flatCount}}   {green|下跌: ${downCount}}`,
          left: "center",
          textStyle: {
            color: "#EAEAEA",
            fontSize: 24,
            rich: {
              red: {
                color: "#EA4335", // 红色
                fontWeight: "bold",
                fontSize: 24,
              },
              yellow: {
                color: "#FBB13C", // 黄色
                fontWeight: "bold",
                fontSize: 24,
              },
              green: {
                color: "#34A853", // 绿色
                fontWeight: "bold",
                fontSize: 24,
              },
            },
          },
        },
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: "category",
          data: categories,
          axisLabel: {
            rotate: 45,
            color: "#EAEAEA",
          },
        },
        yAxis: {
          type: "value",
          name: "数量",
          axisLabel: {
            color: "#EAEAEA",
          },
        },
        series: [
          {
            type: "bar",
            data: values,
            itemStyle: {
              color: "#4285F4",
            },
          },
        ],
      };

      // 下图：筛选结果（合并数据）
      const stocks = [
        ...data["筛选结果"]["前60家"],
        ...data["筛选结果"]["中间60家"],
        ...data["筛选结果"]["后60家"],
      ];
      this.setFullData(stocks)

      this.displayDates = stocks.map((stock) => stock["名称"]);
      this.stockChanges = stocks.map(stock => ({
        value: stock["涨跌幅"],
        itemStyle: {
          color: this.getGradientColor(stock["涨跌幅"]),
        },
      }));

      this.chartOption = {
        textStyle: {
          color: '#EAEAEA',
        },
        title: {
          text: "涨幅前-中-后各60家一览",
          left: "center",
          textStyle: {
            color: '#EAEAEA',
            fontSize: 12
          },
        },
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: "category",
          data: this.displayDates,
          axisLabel: {
            rotate: 45,
            color: "#EAEAEA",
          },
        },
        yAxis: {
          type: "value",
          name: "涨跌幅 (%)",
          axisLabel: {
            color: "#EAEAEA",
          },
        },
        series: [
          {
            type: "bar",
            data: this.stockChanges,
          },
        ],
      };
    },
  },
};
</script>

<style scoped>
.stock-statistic-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  /* 水平排列子元素 */
  background-color: #000000c7;
  border-radius: 12px;
  padding: 0;
  /* 移除内边距 */
}

.left-area {
  width: 80%;
  height: 100%;
}

.right-area {
  width: 20%;
  height: 100%;
}

.right-area h3{
  text-align: center;
}


/* 上层布局 */
.upper-container {
  display: flex;
  height: 30%;
  width: 100%;
  justify-content: center;
  align-items: center;
  margin-top: 12px;
}

/* 中间指标布局 */
.middle-container {
  height: 10%;
  width: 80%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  /* 使容器本身居中 */
  border-radius: 6px;
  background-color: rgba(0, 0, 0, 0.388);
}

.indicator-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  font-size: 1.2rem;
}

.indicator-item {
  color: #EAEAEA;
  font-weight: bold;
}

.label {
  margin-right: 5px;
}

/* 下层布局 */
.lower-container {
  height: 60%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 12px;
}

.chart-container {
  width: 100%;
  /* 确保图表占满父容器宽度 */
  height: 100%;
  padding: 0;
  /* 移除内边距 */
}
</style>
