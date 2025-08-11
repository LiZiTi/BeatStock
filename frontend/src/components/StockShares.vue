<template>
  <div id="main" class="stock-detail-view">
    <!-- 当加载完成时显示股东持股数量的柱状图 -->
    <VChart
        :option="chartOption"
        autoresize
        ref="chart"
        class="chart-container"
    />
  </div>
</template>

<script>
import VChart from 'vue-echarts';
import 'echarts';
import { api } from "@/axiosConfig";

export default {
  components: {
    VChart
  },
  data() {
    return {
      shareholderData: [], // 保存获取到的股东数据
      chartOption: null // 图表的配置选项
    };
  },
  props: {
    stockCode: {
      type: String,
      required: true // 父组件必须传递股票代码
    }
  },
  watch: {
    stockCode(stockCode) {
      if (stockCode) {
        this.fetchShareholderData(stockCode); // 调用异步方法获取股东数据
      }
    }
  },
  methods: {
    async fetchShareholderData(stockCode) {
      try {
        const response = await api.get(`/stock/share`, { params: { symbol: stockCode } });
        console.log(response.data);
        this.shareholderData = response.data.股东;
        this.shareholderData.sort((a, b) => b.持股数 - a.持股数); // 按持股数量由大到小排序
        this.generateChartOption();
      } catch (error) {
        console.error("Error fetching shareholder data:", error);
      }
    },
    generateChartOption() {
      // 生成图表的配置项
      const serialNumbers = this.shareholderData.map((item, index) => `第${this.shareholderData.length - index}名`);
      const scaledScores = this.shareholderData.map((item, index) => {
        let scaledValue = 50; // 默认值
        if (this.shareholderData.length > 1) {
          const minScore = this.shareholderData[this.shareholderData.length - 1].持股数;
          const maxScore = this.shareholderData[0].持股数;
          scaledValue = ((item.持股数 - minScore) / (maxScore - minScore) * 100).toFixed(2);
        }
        // 依次减少 5%
        scaledValue = scaledValue * (1 - 0.05 * index);

        return {
          value: scaledValue,
          股东名称: item.股东名称,
          股东性质: item.股东性质,
          股份类型: item.股份类型,
          originalValue: (item.持股数 / 10000).toFixed(2), // 保存原始的持股数以万为单位
          占总流通股本持股比例: item.占总流通股本持股比例,
          增减: item.增减,
          变动比率: item.变动比率
        };
      });

      this.chartOption = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            const data = params[0].data;
            return `
              <strong>股东名称:</strong> ${data.股东名称}<br/>
              <strong>持股数:</strong> ${data.originalValue} 万股<br/>
              <strong>股东性质:</strong> ${data.股东性质}<br/>
              <strong>股份类型:</strong> ${data.股份类型}<br/>
              <strong>占总流通股本持股比例:</strong> ${data.占总流通股本持股比例}%<br/>
              <strong>增减:</strong> ${data.增减}<br/>
              <strong>变动比率:</strong> ${data.变动比率}%
            `;
          }
        },
        xAxis: {
          type: 'value',
          boundaryGap: [0, 0.01],
          min: 0,
          max: 100, // 将持股数缩放到0-100
          name: '持股数 (万股)'
        },
        yAxis: {
          type: 'category',
          inverse: true, // 逆序显示
          axisTick: {show: false},
          axisLine: {show: false},
          data: serialNumbers // 显示序号
        },
        series: [
          {
            name: '持股数',
            type: 'bar',
            data: scaledScores,
            label: {
              show: true,
              position: 'insideLeft',
              formatter: (params) => params.data.股东名称,
              fontSize: 10
            },
            itemStyle: {
              color: (params) => {
                const rate = params.data.变动比率;
                if (rate > 0) {
                  return 'red';
                } else if (rate < 0) {
                  return 'green';
                } else {
                  return 'white';
                }
              }
            }
          }
        ]
      };
    }
  }
};
</script>

<style scoped>
.stock-detail-view {
  width: 100%;
  height: 100%;
  padding: 26px;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
