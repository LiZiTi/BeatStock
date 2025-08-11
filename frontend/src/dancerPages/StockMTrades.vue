<template>
    <div id="main" class="stock-detail-view">
        <StockSearchPage @stockSelected="onStockSelected" />
        <table class="indicator-table" v-if="totalVolume">
            <thead>
                <tr>
                    <th>总成交量</th>
                    <th>总成交额</th>
                    <th>主动买入量</th>
                    <th>主动买入额</th>
                    <th>主动卖出量</th>
                    <th>主动卖出额</th>
                    <th>中性交易量</th>
                    <th>中性交易额</th>
                </tr>
            </thead>
            <tbody>
                <tr ref="tableRow">
                    <td>{{ (totalVolume / 10000).toFixed(2) }}万手</td>
                    <td>{{ (totalAmount / 1e8).toFixed(2) }} 亿</td>
                    <td>{{ (totalBuyVolume / 10000).toFixed(2) }}万手</td>
                    <td>{{ (totalBuyAmount / 1e8).toFixed(2) }} 亿</td>
                    <td>{{ (totalSellVolume / 10000).toFixed(2) }}万手</td>
                    <td>{{ (totalSellAmount / 1e8).toFixed(2) }} 亿</td>
                    <td>{{ (totalNaturalVolume / 10000).toFixed(2) }}万手</td>
                    <td>{{ (totalNaturalAmount / 1e8).toFixed(2) }} 亿</td>
                </tr>
            </tbody>
        </table>
        <div id="indicator-values" class="indicator-values" v-if="currentTime">
            <div class="value-item">
                <span class="label">时间：</span>
                <span class="value animated-span">{{ currentTime }}</span>
            </div>
            <div class="value-item">
                <span class="label">价格：</span>
                <span class="value animated-span">{{ currentPrice }}</span>
            </div>
            <div class="value-item">
                <span class="label">成交量：</span>
                <span class="value animated-span">{{ currentVolume }}手</span>
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
import StockSearchPage from "../components/StockSearchPage.vue";
import DancerPageBase from '../components/DancerPageBase.vue';

export default {
    extends: DancerPageBase,
    pageName: '个股交易详情',
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
            currentClass: "value", // 当前样式名
            selectedStockCode: null, // 当前选中的股票
            selectedStockName: null,
            selectedPeriod: 'weekly',
            prices: [],
            volumes: [],
            minPrice: 0,
            maxPrice: 0,

            currentTime: null,
            currentPrice: null,
            currentVolume: null,
            currentNature: null,

            totalVolume: 0,
            totalAmount: 0,
            totalBuyVolume: 0,
            totalBuyAmount: 0,
            totalSellVolume: 0,
            totalSellAmount: 0,
            totalNaturalVolume: 0,
            totalNaturalAmount: 0,
            rainbowColors: [
                'rgba(255, 0, 0, 0.8)',    // 红色
                'rgba(255, 165, 0, 0.8)',  // 橙色
                'rgba(255, 255, 0, 0.8)',  // 黄色
                'rgba(0, 255, 0, 0.8)',    // 绿色
                'rgba(0, 255, 255, 0.8)',  // 青色
                'rgba(0, 0, 255, 0.8)',    // 蓝色
                'rgba(128, 0, 128, 0.8)'   // 紫色
            ]
        };
    },
    computed: {
        indicatorColor() {
            return this.currentNature === '买盘' ? '#EA4335' : '#34A853'; // 买盘红色，卖盘绿色
        },
    },
    methods: {
        afterComputeDataPointsPerBeat() {
            this.minPrice = Math.min(...this.prices);
            this.maxPrice = Math.max(...this.prices);
        },
        clearChartData() {
            this.displayDates = [];
            this.prices = [];
            this.volumes = [];

            this.minPrice = 0;
            this.maxPrice = 0;

            if (this.$refs.chartInstance) {
                this.$refs.chartInstance.setOption({
                    xAxis: { data: this.displayDates },
                    series: [
                        { data: [] },
                        { data: [] },
                    ],
                });
            }
        },
        fullfillAllData() {
            this.displayDates = this.fullData.map(item => item.分钟时间);
            this.prices = this.fullData.map(item => item.成交价格);
            this.volumes = this.fullData.map(item => ({
                value: item.成交量, // 成交量
                itemStyle: {
                    color: item.性质 === '买盘' ? '#EA4335' : '#34A853', // 根据性质动态设置颜色
                },
            }));

            this.minPrice = Math.min(...this.prices);
            this.maxPrice = Math.max(...this.prices);

            if (this.$refs.chartInstance) {
                this.$refs.chartInstance.setOption({
                    xAxis: { data: this.displayDates },
                    series: [
                        { data: this.prices },
                        { data: this.volumes },
                    ],
                });
            }
        },
        updateChartDataPoint(dataPoint) {
            this.displayDates.push(dataPoint["分钟时间"])
            this.prices.push(dataPoint["成交价格"].toFixed(2));
            this.volumes.push({
                value: dataPoint["成交量"], // 动态插入带颜色的成交量数据
                itemStyle: {
                    color: dataPoint["性质"] === '买盘' ? '#EA4335' : '#34A853', // 根据性质设置颜色
                },
            });

            this.currentTime = dataPoint["分钟时间"];
            this.currentPrice = dataPoint["成交价格"];
            this.currentVolume = dataPoint["成交量"];

            this.whenValueUpdated(dataPoint['性质'])
            this.updateTableColors()

            this.chartOption.xAxis.data = this.displayDates;
            this.chartOption.series[0].data = this.prices;
            this.chartOption.series[1].data = this.volumes;
        },
        onStockSelected(stockCode, stockName, dataPeriod) {
            this.selectedStockCode = stockCode;
            this.selectedStockName = stockName;
            this.selectedPeriod = dataPeriod;
            this.loadStockHistory();
        },
        loadStockHistory() {
            api.get('/stock-mt/' + this.selectedStockCode)
                .then(response => {
                    const tradeData = response.data;

                    this.totalVolume = tradeData.totalVolume;
                    this.totalAmount = tradeData.totalAmount;
                    this.totalBuyVolume = tradeData.totalBuyVolume;
                    this.totalBuyAmount = tradeData.totalBuyAmount;
                    this.totalSellVolume = tradeData.totalSellVolume;
                    this.totalSellAmount = tradeData.totalSellAmount;
                    this.totalNaturalAmount = tradeData.totalNaturalAmount;
                    this.totalNaturalVolume = tradeData.totalNaturalVolume;

                    this.createChartOption(tradeData.minuteTrade);
                    this.setFullData(tradeData.minuteTrade)

                })
                .catch(error => {
                    console.error('Error fetching chip data:', error);
                });
        },
        createChartOption(tradeData) {
            // 准备数据
            this.displayDates = tradeData.map(item => item.分钟时间);
            this.prices = tradeData.map(item => item.成交价格);
            this.volumes = tradeData.map(item => ({
                value: item.成交量, // 成交量
                itemStyle: {
                    color: item.性质 === '买盘' ? '#EA4335' : '#34A853', // 根据性质动态设置颜色
                },
            }));

            // 计算价格范围
            this.minPrice = Math.min(...this.prices);
            this.maxPrice = Math.max(...this.prices);

            // 构建图表配置
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
                    data: ['价格趋势', '成交量'],
                    top: 30,
                    textStyle: {
                        color: '#EAEAEA',
                    },
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '10%',
                    containLabel: true,
                },
                xAxis: {
                    type: 'category',
                    data: this.displayDates,
                    axisLabel: {
                        color: '#EAEAEA',
                        rotate: 45,
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#EAEAEA',
                        },
                    },
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '价格',
                        position: 'left',
                        min: this.minPrice, // 最小值设置为数据中的最小价格
                        max: this.maxPrice, // 最大值设置为数据中的最大价格
                        axisLine: {
                            lineStyle: {
                                color: '#EAEAEA',
                            },
                        },
                        axisLabel: {
                            color: '#EAEAEA',
                        },
                    },
                    {
                        type: 'value',
                        name: '成交量',
                        position: 'right',
                        axisLine: {
                            lineStyle: {
                                color: '#EAEAEA',
                            },
                        },
                        axisLabel: {
                            color: '#EAEAEA',
                        },
                    },
                ],
                dataZoom: [
                    {
                        type: 'slider',
                        start: 0,
                        end: 100
                    },
                    {
                        type: 'inside',
                        start: 0,
                        end: 100
                    }
                ],
                series: [
                    {
                        name: '价格趋势',
                        type: 'line',
                        data: this.prices,
                        smooth: true,
                        lineStyle: {
                            color: '#4285F4',
                            width: 2,
                        },
                    },
                    {
                        name: '成交量',
                        type: 'bar',
                        yAxisIndex: 1,
                        data: this.volumes,
                        barWidth: '20%', // 控制柱状图的宽度
                    },
                ],
            };
        },
        whenValueUpdated(bs) {
            // 选择所有带有指定 class 的元素
            const elements = this.$el.querySelectorAll('.animated-span');

            if (!elements || elements.length === 0) {
                return;
            }

            elements.forEach((element) => {
                // 设置光晕颜色
                const currentGlowColor = this.rainbowColors[this.currentColorIndex];
                element.style.textShadow = `0 0 10px ${currentGlowColor}, 0 0 20px ${currentGlowColor}`;
                element.style.color = bs === '买盘' ? '#EA4335' : '#34A853'; // 根据性质动态设置颜色
                this.currentColorIndex = (this.currentColorIndex + 1) % this.rainbowColors.length;

                // 强制触发动画
                element.classList.remove('enlarged');
                void element.offsetWidth; // 强制 DOM 重绘
                element.classList.add('enlarged');

                // 动画结束后清除类名
                element.addEventListener(
                    'animationend',
                    () => {
                        element.classList.remove('enlarged');
                    },
                    { once: true }
                );
            });
        },
        updateTableColors() {
            const tds = this.$refs.tableRow.querySelectorAll('td');
            tds.forEach(td => {
                td.style.color = this.rainbowColors[Math.floor(Math.random() * this.rainbowColors.length)];
            });
        },
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

.middle-section {
    height: 70%;
    width: 100%;
    margin-top: 20px;
}

.indicator-values {
    height: 15%;
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
    font-size: 1.6rem;
    transition: font-size 0.1s ease, text-shadow 0.1s ease;
    color: #FBBC05;
}

.value.enlarged {
    font-size: 3rem;
    animation: pulse 0.1s ease;
}

/* 动画效果 */
@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

.indicator-table {
    width: 80%;
    height: 15%;
    border-collapse: collapse;
    text-align: center;
    margin: 0 auto;
}

.indicator-table th,
.indicator-table td {
    padding: 8px;
    border: 1px solid #ddd;
}

.indicator-table th {
    background-color: #000000ca;
}

.indicator-table td {
    color: yellow;
    background-color: #000000ac;
}
</style>