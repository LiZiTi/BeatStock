<template>
  <div class="economic-chart-wrapper">
    <div class="economic-chart-content">
      <!-- 导航栏，包含标题和返回按钮 -->
      <div class="chart-header">
        <div class="nav-left">
          <img src="@/assets/logo.png" alt="Logo" class="nav-logo" />
          <h2 class="chart-title">
            {{ isHistoricalChart ? selectedIndex.name + " 历史行情" : "中国主要股指实时行情" }}
          </h2>
        </div>
        <button v-if="isHistoricalChart" @click="goBack" class="switch-button">返回</button>
      </div>
      <div class="four-in-one-chart-wrapper">
        <v-chart ref="chart" :option="chartOption" autoresize class="chart" @click="handleBarClick" />

      </div>
    </div>
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
      isHistoricalChart: false,
      loading: false, // 添加 loading 状态
      selectedIndex: null,
      highlightedIndices: ["sh000001", "sz399001", "sz399006"], // 需要强调的指数代码
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
          backgroundColor: "rgba(0, 0, 0, 0.7)",
          textStyle: {
            color: "#FFFFFF",
          },
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
          axisLabel: {
            color: "#FFFFFF",
          },
        },
        yAxis: {
          type: "category",
          data: sortedData.map((item) => item.代码),
          axisLabel: {
            formatter: (value) => {
              const index = sortedData.find((item) => item.代码 === value);
              return `{value|${index.名称} }`;
            },
            rich: {
              value: {
                color: "#FFFFFF",
                fontWeight: "bold",
              },
              highlighted: {
                color: "#FFD700",
                fontWeight: "bold",
              },
            },
          },
        },
        series: [
          {
            type: "bar",
            data: sortedData.map((item) => ({
              value: item.涨跌幅,
              itemStyle: {
                color: this.getBarColor(item.涨跌幅, item.代码),
              },
              ...item,
            })),
            emphasis: {
              focus: 'series',
            },
            label: {
              show: true,
              position: "right",
              formatter: "{b}",
            },
            cursor: 'pointer',
          },
        ],
      };
    },
    handleBarClick(params) {
      if (!params.data) return;

      // 显示加载动画
      this.loading = true;
      const { 代码, 名称 } = params.data;
      this.selectedIndex = { code: 代码, name: 名称 };
      this.isHistoricalChart = true;

      // 获取历史数据
      this.fetchHistoricalData(代码);
    },
    async fetchHistoricalData(code) {
      try {
        // 获取历史行情数据，调用对应的 API
        const response = await xlApi.get(`/stock_zh_index_daily`, {
          params: {
            symbol: code,
          },
        });
        const historicalData = response.data;

        // 格式化日期为 yyyy-mm-dd
        const formattedData = historicalData.map((item) => {
          const date = new Date(item.date);
          const formattedDate = date.toISOString().split('T')[0]; // 转换为 yyyy-mm-dd 格式
          return {
            ...item,
            date: formattedDate,
          };
        });

        // 更新图表配置为历史数据
        this.chartOption = {
          tooltip: {
            trigger: "axis",
            backgroundColor: "rgba(0, 0, 0, 0.7)",
            textStyle: {
              color: "#FFFFFF",
            },
            axisPointer: {
              type: "cross",
            },
          },
          xAxis: {
            type: "category",
            data: formattedData.map((item) => item.date),
            axisLabel: {
              color: "#FFFFFF",
            },
          },
          yAxis: {
            type: "value",
            axisLabel: {
              color: "#FFFFFF",
            },
          },
          series: [
            {
              name: `${this.selectedIndex.name} 历史行情`,
              type: "line",
              data: formattedData.map((item) => item.close), // 假设返回的数据中包含收盘价字段
              itemStyle: {
                color: "#FFD700",
              },
            },
          ],
          dataZoom: [
            {
              type: 'slider', // 通过滑动条控制
              start: 90, // 从 80% 开始
              end: 100, // 到 100% 结束，默认显示最新的 20%
            },
            {
              type: 'inside', // 支持鼠标滚轮缩放
              start: 90,
              end: 100,
            }
          ],
        };
        this.loading = false; // 确保无论成功与否都能隐藏 loading
      } catch (error) {
        this.loading = false; // 确保无论成功与否都能隐藏 loading
        console.error("获取历史数据失败:", error);
      }
    },
    goBack() {
      this.isHistoricalChart = false;
      this.selectedIndex = null;
      this.updateChartOption();
    },
    getBarColor(change, code) {
      const isHighlighted = this.highlightedIndices.includes(code);
      if (change > 0) {
        return isHighlighted ? "#ff7f50" : `rgba(255, 0, 0, ${Math.min(1, change / 10)})`;
      } else if (change < 0) {
        return isHighlighted ? "#32cd32" : `rgba(0, 255, 0, ${Math.min(1, Math.abs(change) / 10)})`;
      }
      return "#808080";
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
.highlighted {
  color: #ffd700 !important;
  /* 强调黄色 */
}

.economic-chart-wrapper {
  position: relative;
  width: 100%;
  padding-top: 48%;
  /* 使用 61.8% 来实现黄金比例 */
  box-sizing: border-box;
  transition: transform 1s ease, transform 1s ease;
  /* 平滑过渡效果 */
}

.economic-chart-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  /* 可选的内边距 */
  box-sizing: border-box;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  /* 左右对齐 */
  align-items: center;
  /* 垂直居中对齐 */
  margin-bottom: 20px;
  background: #22224400;
  padding: 10px;
  border-bottom: 2px solid #00d9ffa2;
}

.nav-left {
  display: flex;
  align-items: center;
}

.nav-logo {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.chart-title {
  font-size: 1rem;
  font-weight: bold;
  color: #ffffff;
  /* 标题文本颜色 */
  margin: 0;
}

.four-in-one-chart-wrapper {
  position: relative;
  width: 100%;
  height: 600px;
  /* 可以根据需求调整 */
  box-sizing: border-box;
  padding: 20px;
  transition: transform 0.3s ease;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.switch-button {
  background: rgba(0, 247, 255, 0.1);
  color: #00eaff;
  border: 1px solid #00eaff;
  padding: 5px 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.3s, box-shadow 0.3s, transform 0.3s;
}

.switch-button:hover {
  background: #00eaff;
  color: #000;
  box-shadow: 0 0 10px #00eaff, 0 0 20px #00eaff;
  transform: translateY(-2px);
}

.switch-button:active {
  transform: translateY(0);
  box-shadow: 0 0 5px #00eaff;
}
</style>
