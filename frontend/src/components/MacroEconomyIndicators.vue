<template>
    <div class="economic-chart-wrapper">
        <div class="economic-chart-content">
            <!-- 导航栏，包含标题和返回按钮 -->
            <div class="chart-header">
                <div class="nav-left">
                    <h2 class="chart-title">
                        <span v-if="isViewingIndicator"> - {{ currentIndicator.name }}</span>
                    </h2>
                </div>
                <div class="button-group">
                    <button class="switch-button" @click="toggleDataDisplay">{{ showAll ? '显示前20个' : '显示全部' }}</button>
                    <button v-if="isViewingIndicator" class="switch-button" @click="switchToIndicatorSet">返回</button>
                </div>
            </div>
            <!-- ECharts 图表组件 -->
            <v-chart ref="indicatorChart" :option="currentOption" autoresize @click="handleChartClick"
                class="chart-container" />
        </div>
    </div>
</template>

<script>
import ECharts from 'vue-echarts';
import 'echarts';
import { api } from '@/axiosConfig';
import indicators from '@/constants/indicators.json';

export default {
    name: 'EconomicChart',
    components: {
        'v-chart': ECharts,
    },
    data() {
        return {
            currentOption: null, // 当前图表配置（饼状图或指标历史行情）
            currentIndicator: null,
            isViewingIndicator: false, // 控制是否在查看单个指标的历史行情
            loading: false, // 添加 loading 状态
            showAll: false, // 控制是否显示全部
        };
    },
    mounted() {
        this.setupPieChart();
    },
    methods: {
        setupPieChart() {

            // 根据 showAll 状态动态获取数据数量
            const totalIndicators = Object.keys(indicators).length;
            const limit = this.showAll ? totalIndicators : Math.min(16, Math.ceil(totalIndicators / 2));

            // 生成饼状图数据
            const data = this.getPieChartData(limit);

            // 设置饼状图的配置
            this.currentOption = {
              tooltip: {
                    trigger: 'item',
                    backgroundColor: "rgba(0, 0, 0, 0.7)",
                    textStyle: {
                        color: "#FFFFFF",
                    },
                    formatter: (params) => {
                        const indicator = params.data.indicator;
                        return `
                <strong>${params.seriesName}</strong><br/>
                名称: ${params.name}<br/>
                权重: ${params.value}<br/>
                比例: ${params.percent}%<br/>
                描述: ${indicator ? indicator.description : '无详细描述'}
              `;
                    },
                },
                legend: {
                    type: 'scroll',
                    orient: 'vertical',
                    right: 10,
                    top: 20,
                    bottom: 20,
                    data: data.legendData,
                    textStyle: {
                        color: '#ffffff', // 将字体颜色设置为白色
                    },
                },
                series: [
                    {
                        name: '经济指标',
                        type: 'pie',
                        radius: '55%',
                        center: ['40%', '50%'],
                        data: data.seriesData,
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)',
                            },
                        },
                    },
                ],
            };
            this.isViewingIndicator = false; // 设为初始状态
        },
        getPieChartData(limit) {
            const legendData = [];
            const seriesData = [];

            Object.keys(indicators).slice(0, limit).forEach((key) => {
                const indicator = indicators[key];
                if (indicator.enable) {
                    legendData.push(indicator.name);
                    seriesData.push({
                        key: key,
                        name: indicator.name,
                        value: indicator.order || 1, // 使用 `order` 作为权重
                        indicator: indicator, // 保留指标信息，方便悬停和点击使用
                    });
                }
            });

            return {
                legendData,
                seriesData,
            };
        },
        handleChartClick(params) {
            if (params.data && params.data.indicator && params.data.key) {
                // 显示加载动画
                this.loading = true;
                // 显示该指标的历史行情
                this.showIndicatorHistory(params.data);
            } else {
                console.warn('No valid indicator key available for chart click.');
            }
        },
        showIndicatorHistory(indicator) {
            // 调用 API 获取历史数据并更新 currentOption
            const url = `/cache/${indicator.key}`;
            api.get(url).then((response) => {
                const historyData = response.data;

                if (!historyData) {
                    console.warn(`No valid history data available for indicator ${indicator.key}`);
                    this.loading = false; // 确保无论成功与否都能隐藏 loading
                    return;
                }

                // 更新 currentOption 配置项，设置为显示该指标的历史数据
                this.currentOption = {
                    tooltip: {
                        trigger: 'axis',
                        formatter: '{a} <br/>{b}: {c}',
                        backgroundColor: "rgba(0, 0, 0, 0.7)",
                        textStyle: {
                            color: "#FFFFFF",
                        },
                    },
                    legend: {
                        data: indicator.yFields,
                        textStyle: {
                            color: '#ffffff', // 图例文本颜色设置为亮白色
                        },
                    },
                    xAxis: {
                        type: 'category',
                        data: historyData.xData,
                    },
                    yAxis: {
                        type: 'value',
                    },
                    series: historyData.series,
                    dataZoom: [
                        {
                            type: 'slider', // 通过滑动条控制
                            start: 80, // 从 90% 开始
                            end: 100, // 到 100% 结束，默认显示最新的 10%
                        },
                        {
                            type: 'inside', // 支持鼠标滚轮缩放
                            start: 80,
                            end: 100,
                        }]
                };
                this.isViewingIndicator = true; // 标记为查看单个指标
                this.currentIndicator = indicator; // 设置当前查看的指标
            })
                .catch((error) => {
                    console.error(`Failed to load history data for indicator ${indicator.key}:`, error);
                })
                .finally(() => {
                    this.loading = false;
                })

        },
        toggleDataDisplay() {
            // 切换显示模式
            this.showAll = !this.showAll;
            // 更新图表数据
            this.setupPieChart();
        },
        switchToIndicatorSet() {
            // 返回指标集展示
            this.setupPieChart();
            this.currentIndicator = null; // 清除当前指标
            this.isViewingIndicator = false; // 恢复到查看指标集的状态
        },
    }
};
</script>

<style scoped>
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