<template>
  <div class="fund-flow">
    <div class="table-section">
      <!-- 使用 vxe-table 组件 -->
      <vxe-table :data="orderedSectors" border round height="100%" size="large" align="center"
        :row-config="{ isCurrent: true, isHover: true }" :column-config="{ resizable: true, width: 'auto' }" stripe
        show-header>
        <vxe-column field="名称" title="概念版块"></vxe-column>
        <vxe-column field="今日涨跌幅" title="今日涨跌幅%" sortable>
          <template #default="{ row }">
            {{ row['今日涨跌幅'] }}
          </template>
        </vxe-column>
        <vxe-column field="5日涨跌幅" title="5日涨跌幅%" sortable>
          <template #default="{ row }">
            {{ row['5日涨跌幅'] }}
          </template>
        </vxe-column>
        <vxe-column field="10日涨跌幅" title="10日涨跌幅%" sortable>
          <template #default="{ row }">
            {{ row['10日涨跌幅'] }}
          </template>
        </vxe-column>
        <vxe-column field="今日主力净流入-净额" title="今日主力净流入(亿)" sortable>
          <template #default="{ row }">
            {{ (row['今日主力净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
        <vxe-column field="5日主力净流入-净额" title="5日主力净流入(亿)" sortable>
          <template #default="{ row }">
            {{ (row['5日主力净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
        <vxe-column field="10日主力净流入-净额" title="10日主力净流入(亿)" sortable>
          <template #default="{ row }">
            {{ (row['10日主力净流入-净额'] / 1e8).toFixed(2) }}
          </template>
        </vxe-column>
        <vxe-column field="今日主力净流入最大股" title="今日主力流入最大股"></vxe-column>
        <vxe-column field="5日主力净流入最大股" title="5日主力流入最大股"></vxe-column>
        <vxe-column field="10日主力净流入最大股" title="10日主力流入最大股"></vxe-column>
      </vxe-table>
    </div>

    <div class="info-section" v-if="industryValue">
      <div class="info-item">
        <span>概念:</span>
        <strong>{{ industryValue }}</strong>
      </div>
      <div class="info-item">
        <span>今日:</span>
        <strong>{{ todayValue }}</strong>
      </div>
      <div class="info-item">
        <span>5日:</span>
        <strong>{{ fiveDayValue }}</strong>
      </div>
      <div class="info-item">
        <span>10日:</span>
        <strong>{{ tenDayValue }}</strong>
      </div>
    </div>

    <div class="middle-section">
      <v-chart ref="chartInstance" :option="chartOption" autoresize style="height: 100%;" />
    </div>
  </div>
</template>


<script>
import { api } from "@/axiosConfig";
import VChart from 'vue-echarts';
import 'echarts';
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
  extends: DancerPageBase,
  name: "ConceptFundFlowCharts",
  pageName: '概念资金流',
  components: {
    VChart
  },
  computed: {
    pageNameForTemplate() {
      return this.$options.pageName; // 从静态属性中获取
    },
  },
  data() {
    return {
      chartOption: {},
      orderedSectors: [],

      ft: [],
      f5: [],
      f10: [],

      industryValue: null, // 示例值
      todayValue: null,
      fiveDayValue: null,
      tenDayValue: null,
    };
  },
  mounted() {
    this.fetchFundFlowData();
  },
  methods: {
    afterComputeDataPointsPerBeat() {

    },
    clearChartData() {

      this.displayDates = [];
      this.ft = [];
      this.f5 = [];
      this.f10 = [];

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

      this.displayDates = this.orderedSectors.map((item) => item.名称);
      this.ft = this.orderedSectors.map((item) => (item["今日主力净流入-净额"] / 1e8).toFixed(2));
      this.f5 = this.orderedSectors.map((item) => (item["5日主力净流入-净额"] / 1e8).toFixed(2));
      this.f10 = this.orderedSectors.map((item) => (item["10日主力净流入-净额"] / 1e8).toFixed(2));


      if (this.$refs.chartInstance) {
        this.$refs.chartInstance.setOption({
          xAxis: { data: this.displayDates },
          series: [
            { data: this.ft },
            { data: this.f5 },
            { data: this.f10 },
          ],
        });
      }
    },
    updateChartDataPoint(dataPoint) {
      console.log(dataPoint)
      this.displayDates.push(dataPoint["名称"])
      this.ft.push((dataPoint["今日主力净流入-净额"] / 1e8).toFixed(2));
      this.f5.push((dataPoint["5日主力净流入-净额"] / 1e8).toFixed(2));
      this.f10.push((dataPoint["10日主力净流入-净额"] / 1e8).toFixed(2));

      this.industryValue = dataPoint["名称"];
      this.todayValue = (dataPoint["今日主力净流入-净额"] / 1e8).toFixed(2) + "亿";
      this.fiveDayValue = (dataPoint["5日主力净流入-净额"] / 1e8).toFixed(2) + "亿";
      this.tenDayValue = (dataPoint["10日主力净流入-净额"] / 1e8).toFixed(2) + "亿";

      if (this.maxDisplayPoints > 0) {
        while (this.displayDates.length > this.maxDisplayPoints) {
          this.displayDates.shift();
          this.ft.shift();
          this.f5.shift();
          this.f10.shift();
        }
      }

      this.chartOption.xAxis.data = this.displayDates;
      this.chartOption.series[0].data = this.ft;
      this.chartOption.series[1].data = this.f5;
      this.chartOption.series[2].data = this.f10;

    },
    async fetchFundFlowData() {
      try {
        const response = await api.get("/sector-fund-flow-all", { params: { sector_type: "概念资金流" } });

        this.orderedSectors = response.data.orderedSectors;
        console.log(this.orderedSectors)
        this.setFullData(this.orderedSectors)
        this.initCharts();
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    initCharts() {
      // 确保接口数据格式正确
      if (!this.orderedSectors || this.orderedSectors.length === 0) {
        console.error("数据为空或格式错误：");
        return;
      }

      this.displayDates = this.orderedSectors.map((item) => item.名称);
      this.ft = this.orderedSectors.map((item) => (item["今日主力净流入-净额"] / 1e8).toFixed(2));
      this.f5 = this.orderedSectors.map((item) => (item["5日主力净流入-净额"] / 1e8).toFixed(2));
      this.f10 = this.orderedSectors.map((item) => (item["10日主力净流入-净额"] / 1e8).toFixed(2));
      // 生成图表选项
      this.chartOption = {
        legend: {
          data: ['今日主力净流入-净额', '5日主力净流入-净额', '10日主力净流入-净额'],
          top: '5%',
          textStyle: {
            color: "#EAEAEA",
          },
        },
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
        xAxis: {
          type: 'category',
          data: this.displayDates,
          axisLabel: {
            rotate: 45,
            interval: 0
          },
          axisLine: {
            lineStyle: {
              color: "#EAEAEA",
            },
          },
        },
        yAxis: {
          type: 'value',
          name: '金额（亿）',
          axisLine: {
            lineStyle: {
              color: "#EAEAEA",
            },
          },
          axisLabel: {
            formatter: '{value} 亿'
          }
        },
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
          // 今日主力净流入-净额
          {
            name: '今日主力净流入-净额',
            type: 'bar',
            stack: '总量',
            data: this.ft,
            barWidth: '20%',
            itemStyle: {
              color: (params) => params.value >= 0 ? '#EA4335' : '#34A853'
            },
            z: 2
          },
          // 5日主力净流入-净额（堆叠柱子）
          {
            name: '5日主力净流入-净额',
            type: 'bar',
            stack: '总量',
            data: this.f5,
            barWidth: '20%',
            itemStyle: {
              color: '#FBBC05'
            },
            z: 1
          },
          // 10日主力净流入-净额（堆叠柱子）
          {
            name: '10日主力净流入-净额',
            type: 'bar',
            stack: '总量',
            data: this.f10,
            barWidth: '20%',
            itemStyle: {
              color: '#4285F4'
            },
            z: 3
          }
        ]
      };
    }
  }
};
</script>

<style scoped>
.fund-flow {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #000000c7;
  border-radius: 12px;
}

.info-section {
  margin-top: 36px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 0 auto;
  gap: 66px;
  height: 15%;
  padding: 0 20px;
  border-bottom: 1px solid #444;
}

.info-item {
  flex: 1;
  text-align: center;
  font-size: 18px;
  color: #eaeaea;
  font-weight: bold;
  width: 100px;
}

.info-item span {
  display: block;
}

.info-item strong {
  display: block;
  margin-top: 5px;
  font-size: 20px;
  color: #eeff00;
  /* 强调值的颜色 */
  font-weight: bold;
}

.middle-section {
  height: 55%;
  width: 100%;
  margin-top: 20px;
}

.table-section {
  margin-top: 12px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 30%;
  width: 100%;
  border-bottom: 1px solid #444;
}
</style>
