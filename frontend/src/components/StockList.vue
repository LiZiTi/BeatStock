<template>
  <div class="combined-page">
    <!-- 左侧 25% 的强4股票部分 -->
    <div class="stock-groups strong-stocks">
      <div class="group">
        <h4 class="group-title" style="color: red;">
          {{ fundFlowData.name }}:牛四
        </h4>
        <div class="stock-cards">
          <div class="stock-card" v-for="stock in top_stocks.slice(0, 4)" :key="stock.代码" @click="handleCardClick(stock.代码)">
            <div class="card-header">
              <span class="stock-name">{{ stock.名称 }}</span>
              <span class="stock-code">{{ stock.代码 }}</span>
            </div>
            <div class="card-body">
              <div v-for="(value, key) in stockInfo(stock)" :key="key" class="info-row">
                <span class="info-key">{{ key }}</span>
                <span :class="[
                  'info-value',
                  {
                    positive:
                      (['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) > 0) ||
                      (!['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) > 0),
                    negative:
                      (['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) < 0) ||
                      (!['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) < 0),
                  },
                ]">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 中间 50% 的图表部分 (页面 a) -->
    <div class="fund-flow">
      <v-chart ref="fundFlowChart" :option="chartOption" autoresize style="height: 100%; width: 100%;" />
    </div>

    <!-- 右侧 25% 的弱4股票部分 -->
    <div class="stock-groups weak-stocks">
      <div class="group">
        <h4 class="group-title" style="color: green;">
          {{ fundFlowData.name }}:熊四
        </h4>
        <div class="stock-cards">
          <div class="stock-card" v-for="stock in tail_stocks.slice(0, 4)" :key="stock.代码" @click="handleCardClick(stock.代码)">
            <div class="card-header">
              <span class="stock-name">{{ stock.名称 }}</span>
              <span class="stock-code">{{ stock.代码 }}</span>
            </div>
            <div class="card-body">
              <div v-for="(value, key) in stockInfo(stock)" :key="key" class="info-row">
                <span class="info-key">{{ key }}</span>
                <span :class="[
                  'info-value',
                  {
                    positive:
                      (['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) > 0) ||
                      (!['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) > 0),
                    negative:
                      (['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) < 0) ||
                      (!['涨跌幅', '振幅', '换手率'].includes(key) &&
                        parseFloat(value) < 0),
                  },
                ]">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from "@/axiosConfig";
import VChart from "vue-echarts";
import "echarts";

export default {
  name: "CombinedPage",
  components: {
    VChart,
  },
  data() {
    return {
      chartOption: {},
      top_stocks: [],
      tail_stocks: [],
    };
  },
  props: {
    fundFlowData: {
      type: Object,
      required: true
    }
  },
  watch: {
    fundFlowData: {
      handler(newData) {
        console.log(newData)
        this.handlePropChange(newData.type, newData.name);
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    async loadFundHis(s,n) {
      try {
        const response = await api.get("/sector-fund-flow-his", {
          params: {
            sector_type: s,
            symbol: n,
          },
        });
        const data = response.data;
        this.initChart(data);
      } catch (error) {
        console.error("Failed to fetch data: ", error);
      }
    },
    async loadStocks(s,n){
      try {
        let url = "/head-stocks";
        const response = await api.get(url, {
          params: {
            sector_type: s,
            symbol: n,
          },
        });
        this.top_stocks = response.data.top_stocks;
        this.tail_stocks = response.data.tail_stocks;
      } catch (error) {
        console.error("Failed to fetch stock data", error);
      }
    },
    initChart(data) {
      const dates = [];
      const mainNetAmounts = [];
      const mediumNetAmounts = [];
      const smallNetAmounts = [];

      data.forEach((item) => {
        dates.push(item["日期"]);
        mainNetAmounts.push((item["主力净流入-净额"] / 10000).toFixed(2));
        mediumNetAmounts.push((item["中单净流入-净额"] / 10000).toFixed(2));
        smallNetAmounts.push((item["小单净流入-净额"] / 10000).toFixed(2));
      });

      this.chartOption = {
        color: ["#FF5733", "#33FF57", "#3357FF"],
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
          formatter: function (params) {
            let result = params[0].name + "<br/>";
            params.forEach((item) => {
              result +=
                item.marker +
                item.seriesName +
                ": " +
                item.value +
                " 万<br/>";
            });
            return result;
          },
        },
        legend: {
          data: ["主力净流入-净额", "中单净流入-净额", "小单净流入-净额"],
          textStyle: {
            color: "#fff",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "15%",
          containLabel: true,
        },
        dataZoom: [
          {
            type: "slider",
            show: true,
            xAxisIndex: [0],
            start: 80,
            end: 100,
            bottom: "5%",
            textStyle: {
              color: "#fff",
            },
          },
          {
            type: "inside",
            xAxisIndex: [0],
            start: 60,
            end: 100,
          },
        ],
        xAxis: {
          type: "category",
          data: dates,
          axisLabel: {
            interval: 0,
            rotate: 45,
            textStyle: {
              color: "#fff",
            },
          },
          axisLine: {
            lineStyle: {
              color: "#fff",
            },
          },
        },
        yAxis: {
          type: "value",
          name: "净额 (万)",
          axisLabel: {
            textStyle: {
              color: "#fff",
            },
          },
          axisLine: {
            lineStyle: {
              color: "#fff",
            },
          },
          splitLine: {
            lineStyle: {
              color: "#555",
            },
          },
        },
        series: [
          {
            name: "主力净流入-净额",
            type: "bar",
            stack: "总量",
            data: mainNetAmounts,
          },
          {
            name: "中单净流入-净额",
            type: "bar",
            stack: "总量",
            data: mediumNetAmounts,
          },
          {
            name: "小单净流入-净额",
            type: "bar",
            stack: "总量",
            data: smallNetAmounts,
          },
        ],
      };
    },
    async handlePropChange(newFundFlowType, newFundFlowName) {
      if (!newFundFlowType || !newFundFlowName) {
        return;
      }
      this.loadFundHis(newFundFlowType,newFundFlowName)
      this.loadStocks(newFundFlowType,newFundFlowName)
    },
    stockInfo(stock) {
      return {
        最新价: stock.最新价,
        涨跌幅: stock.涨跌幅 ? `${stock.涨跌幅}%` : "N/A",
        成交量: stock.成交量 ?? "N/A",
        成交额: stock.成交额
          ? (stock.成交额 / 10000 / 10000).toFixed(2) + "亿"
          : "N/A",
      };
    },
    handleCardClick(stockCode) {
      this.$emit("stock-selected", stockCode);
    },
  }
};
</script>

<style scoped>
.combined-page {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
}

.fund-flow {
  background-color: #252A34;
  padding: 20px;
  width: 50%;
  height: 100%;
  border-radius: 12px;
}

.strong-stocks {
  border-radius: 12px;
  padding: 2rem;
  width: 25%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.weak-stocks {
  border-radius: 12px;
  padding: 2rem;
  width: 25%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.group {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.group-title {
  color: #eaeaea;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.stock-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 定义每行 2 列 */
  gap: 1.5rem;
  padding: 1rem 0;
}


.group-divider {
  width: 5rem;
}

.stock-card {
  background-color: #252a34;
  color: #eaeaea;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  width: 100%;
  min-width: 160px;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(30, 144, 255, 0.4);
}

.stock-card:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 20px rgba(232, 64, 3, 0.4);
}

.card-header {
  font-weight: bold;
  font-size: 1.2rem;
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.stock-name {
  margin-bottom: 0.2rem;
  text-align: center;
  color: rgb(0, 229, 255);
}

.stock-code {
  font-size: 0.9rem;
  color: yellow;
  text-align: center;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.info-value.positive {
  color: #ff4b4b;
}

.info-value.negative {
  color: #3adf00;
}

.fund-flow-data {
  text-align: center;
  color: #000000;
  margin-top: 1rem;
}
</style>
