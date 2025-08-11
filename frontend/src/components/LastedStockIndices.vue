<template>
  <div class="chart-container">
    <v-chart :option="chartOption" autoresize class="chart" />
  </div>
</template>

<script>
import { xlApi } from "@/axiosConfig";
import indicesJson from "@/constants/top_49_indices.json";
import ECharts from "vue-echarts";
import "echarts";

export default {
  components: {
    "v-chart": ECharts,
  },
  data() {
    return {
      indicesData: [],
      chartOption: {},
    };
  },
  mounted() {
    this.initializeIndicesData();
    this.fetchRealTimeData();
  },
  methods: {
    initializeIndicesData() {
      // 先从 JSON 文件中读取并展示名称和代码
      this.indicesData = indicesJson.map((index) => ({
        名称: index.name,
        代码: index.code,
        最新价: null,
        涨跌幅: null,
        涨跌额: null,
        昨收: null,
        今开: null,
        最高: null,
        最低: null,
        成交量: null,
        成交额: null,
      }));
    },
    async fetchRealTimeData() {
      try {
        // 获取实时行情数据
        const response = await xlApi.get("/stock_zh_index_spot_sina");
        const realTimeData = response.data;

        // 更新指数的实时数据
        this.indicesData = this.indicesData
          .map((index) => {
            const matchedData = realTimeData.find((item) => item.代码 === index.代码);
            if (matchedData) {
              return {
                ...index,
                最新价: matchedData.最新价,
                涨跌幅: matchedData.涨跌幅,
                涨跌额: matchedData.涨跌额,
                昨收: matchedData.昨收,
                今开: matchedData.今开,
                最高: matchedData.最高,
                最低: matchedData.最低,
                成交量: matchedData.成交量,
                成交额: matchedData.成交额,
              };
            }
            return null;
          })
          .filter((index) => index !== null);

        // 去重处理
        this.indicesData = this.indicesData.filter(
          (index, idx, self) => idx === self.findIndex((t) => t.代码 === index.代码)
        );

        // 更新图表
        this.updateChartOption();
      } catch (error) {
        console.error("获取实时数据失败:", error);
      }
    },
    updateChartOption() {
      // 根据涨跌幅排序
      const sortedData = [...this.indicesData].sort((a, b) => b.涨跌幅 - a.涨跌幅);

      // 更新图表配置
      this.chartOption = {
        tooltip: {
          trigger: "item",
          formatter: (params) => {
            const data = params.data;
            return `
              <strong>${data.名称} (${data.代码})</strong><br/>
              最新价: ${data.最新价}<br/>
              涨跌额: ${data.涨跌额}<br/>
              涨跌幅: ${data.涨跌幅}%<br/>
              昨收: ${data.昨收}<br/>
              今开: ${data.今开}<br/>
              最高: ${data.最高}<br/>
              最低: ${data.最低}<br/>
              成交量: ${this.formatVolume(data.成交量)}<br/>
              成交额: ${this.formatAmount(data.成交额)}
            `;
          },
        },
        xAxis: {
          type: "value",
          name: "涨跌幅 (%)",
          splitLine: { show: false },
        },
        yAxis: {
          type: "category",
          data: sortedData.map((item) => `${item.名称}`),
        },
        series: [
          {
            name: "涨跌幅",
            type: "bar",
            data: sortedData.map((item) => ({
              value: item.涨跌幅,
              ...item,
            })),
            itemStyle: {
              color: (params) => {
                const value = params.data.涨跌幅;
                // 根据涨跌幅大小来设置颜色的浓度
                const baseColor = value > 0 ? [255, 77, 79] : [43, 255, 0]; // 红色系或绿色系
                const intensity = Math.min(Math.abs(value) /16, 1); // 控制浓度，值范围 [0, 1]
                return `rgba(${baseColor[0]}, ${baseColor[1]}, ${baseColor[2]}, ${intensity})`;
              },
            },
            label: {
              show: true,
              position: "right",
              formatter: "{c}%",
              color: "#ffffff",
            },
          },
        ],
      };
    },
    formatVolume(volume) {
      return volume ? volume.toLocaleString() : "-";
    },
    formatAmount(amount) {
      return amount ? amount.toLocaleString() : "-";
    },
  },
};
</script>



<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  padding: 20px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
