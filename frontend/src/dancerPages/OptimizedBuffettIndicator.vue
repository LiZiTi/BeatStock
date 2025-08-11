<template>
    <div class="fund-flow">
        <div class="info-section">
            <div class="value-item">
                <span class="label">计算日期</span>
                <span class="value">
                    <span class="highlight">
                        {{ dateValueLastest }}
                    </span>
                </span>
            </div>
            <div class="value-item">
                <span class="label">上证指数</span>
                <span class="value">
                    <span class="highlight">
                        {{ indexValueLastest }}
                    </span>
                </span>
            </div>
            <div class="value-item">
                <span class="label">经巴指数</span>
                <span class="value">
                    <span class="highlight">
                        {{ classicBuffettLatest }}
                    </span>
                </span>
            </div>
            <div class="value-item">
                <span class="label">新巴指数</span>
                <span class="value">
                    <span class="highlight">
                        {{ optimizedBuffettLatest}}
                    </span>
                </span>
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
    name: "OptimizeBuffett",
    pageName: '优化巴菲特指标',
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
            dateValueLastest: null,
            indexValueLastest: null,
            classicBuffettLatest: null,
            optimizedBuffettLatest: null,

            displayShanghaiData: [],
            displayClassicBuffettIndex: [],
            displayOptimizedBuffettIndex: [],
        };
    },
    mounted() {
        this.fetchBuffettData();
    },
    methods: {
        afterComputeDataPointsPerBeat() {

        },
        clearChartData() {
            this.displayDates = [];
            this.displayShanghaiData = [];
            this.displayClassicBuffettIndex = [];
            this.displayOptimizedBuffettIndex = [];

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

            // 设置全量数据到展示变量
            this.displayDates = this.fullData.map((data) => data["日期"]);

            this.displayShanghaiData = this.fullData.map((data) => [
                data["open"],
                data["close"],
                data["low"],
                data["high"],
            ]);
            this.displayClassicBuffettIndex = this.fullData.map(
                (data) => data["经典巴菲特指标"]
            );

            this.displayOptimizedBuffettIndex = this.fullData.map(
                (data) => data["优化巴菲特指标"]
            );

            // 更新图表以展示全量数据
            if (this.$refs.chartInstance) {

                this.$refs.chartInstance.setOption({
                    xAxis: { data: this.displayDates },
                    series: [
                        { data: this.displayShanghaiData }, // 全量 K 线图数据
                        { data: this.displayClassicBuffettIndex }, // 全量经巴指数数据
                        { data: this.displayOptimizedBuffettIndex }, // 全量新巴指数数据
                    ],
                });
            }
        },
        updateChartDataPoint(dataPoint) {
            this.displayDates.push(dataPoint["日期"]);
            this.displayShanghaiData.push([
                dataPoint["open"],
                dataPoint["close"],
                dataPoint["low"],
                dataPoint["high"],
            ]);
            this.displayClassicBuffettIndex.push(dataPoint["经典巴菲特指标"]);
            this.displayOptimizedBuffettIndex.push(dataPoint["优化巴菲特指标"]);

            this.dateValueLastest = dataPoint["日期"];
            this.indexValueLastest = dataPoint["close"];
            this.classicBuffettLatest = dataPoint["经典巴菲特指标"];
            this.optimizedBuffettLatest = dataPoint["优化巴菲特指标"];

            this.currentIndex += 1;

            while (this.displayDates.length > this.maxDisplayPoints) {
                this.displayDates.shift();
                this.displayShanghaiData.shift();
                this.displayClassicBuffettIndex.shift();
                this.displayOptimizedBuffettIndex.shift();
            }

            this.chartOption.xAxis.data = this.displayDates;
            this.chartOption.series[0].data = this.displayShanghaiData;
            this.chartOption.series[1].data = this.displayClassicBuffettIndex;
            this.chartOption.series[2].data = this.displayOptimizedBuffettIndex;
        },
        async fetchBuffettData() {
            try {
                const response = await api.get("/buffett-indicator-p", {
                    params: {
                        periodic: 5,
                    }
                });
                const data = response.data;
                this.setFullData(data)
                this.initCharts();
            } catch (error) {
                console.error("Failed to fetch data: ", error);
            }
        },
        initCharts() {
            const dates = this.fullData.map((item) => item.日期);
            const shanghaiIndexData = this.fullData.map((item) => [
                item.open,
                item.close,
                item.low,
                item.high,
            ]);
            const classicBuffettIndex = this.fullData.map((item) => item.经典巴菲特指标);
            const optimizedBuffettIndex = this.fullData.map((item) => item.优化巴菲特指标);
            this.dateValueLastest = dates.slice(-1)[0];
            this.indexValueLastest = shanghaiIndexData.slice(-1)[0][1];
            this.classicBuffettLatest = classicBuffettIndex.slice(-1)[0];
            this.optimizedBuffettLatest = optimizedBuffettIndex.slice(-1)[0];

            // 单一图表配置
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
                    data: ["上证指数", "经典巴菲特指标", "优化巴菲特指标"],
                    textStyle: {
                        color: "#EAEAEA", // 调整为浅色文字颜色
                    },
                },
                xAxis: {
                    type: "category",
                    data: dates,
                    axisPointer: {
                        type: "shadow",
                    },
                    splitLine: {
                        show: false,
                    },
                    axisLine: {
                        lineStyle: {
                            color: "#EAEAEA", // 浅色轴线
                        },
                    },
                },
                yAxis: [
                    {
                        type: "value",
                        scale: true,
                        name: "上证指数",
                        splitLine: {
                            show: false,
                        },
                        axisLine: {
                            lineStyle: {
                                color: "#EAEAEA", // 浅色轴线
                            },
                        },
                    },
                    {
                        type: "value",
                        scale: true,
                        name: "巴菲特指标",
                        splitLine: {
                            show: false,
                        },
                        axisLine: {
                            lineStyle: {
                                color: "#EAEAEA", // 浅色轴线
                            },
                        },
                    },
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
                        name: "上证指数",
                        type: "candlestick",
                        data: shanghaiIndexData,
                    },
                    {
                        name: "经典巴菲特指标",
                        type: "line",
                        yAxisIndex: 1,
                        data: classicBuffettIndex,
                        smooth: true,
                        lineStyle: {
                            color: "#FBBC05", // 使用红色系线条
                        },
                    },
                    {
                        name: "优化巴菲特指标",
                        type: "line",
                        yAxisIndex: 1,
                        data: optimizedBuffettIndex,
                        smooth: true,
                        lineStyle: {
                            color: "#4285F4 ", // 使用绿色系线条
                        },
                    },
                ],
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
    height: 80%;
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

.value-item {
  color: #EAEAEA;
  margin: 0 25px;
  display: flex;
  /* 使用 flex 布局 */
  flex-direction: column;
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
  color: #ffe600;
  font-weight: bold;
}
</style>