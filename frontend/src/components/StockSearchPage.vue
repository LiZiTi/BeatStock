<template>
    <div class="stock-search-page">
        <!-- 搜索框 -->
        <div class="search-container faded" @mouseenter="resetSearchOpacity">
            <div class="search-row">
                <select v-model="stockPeriod" class="search-select">
                    <option value="daily">日数据</option>
                    <option value="weekly">周数据</option>
                </select>
                <input v-model="searchQuery" type="text" placeholder="请输入股票代码或名称" class="search-input"
                    @input="onSearch" />
            </div>
            <ul class="dropdown" v-if="filteredStocks.length > 0" @mouseenter="resetSearchOpacity">
                <li v-for="(stock, index) in filteredStocks.slice(0, 10)" :key="index" class="dropdown-item"
                    @click="selectStock(stock)">
                    {{ stock.code }} - {{ stock.name }}
                </li>
            </ul>
        </div>

        <!-- 股票基本信息小页面 -->
        <transition name="fade">
            <div v-if="showStockInfo" class="stock-info-popup">
                <h3>股票基本信息</h3>
                <table class="info-table">
                    <tbody>
                        <tr v-for="(info, index) in stockInfo" :key="index">
                            <td class="info-item">{{ info.item }}</td>
                            <td class="info-value">{{ info.value }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </transition>
    </div>
</template>

<script>
import { api } from "@/axiosConfig";

export default {
    name: "StockSearchPage",
    data() {
        return {
            stocks: [], // 保存所有股票数据
            stockPeriod: "daily", // 默认选择日数据
            searchQuery: "", // 搜索框内容
            filteredStocks: [], // 下拉候选股票
            stockInfo: [], // 选中股票的基本信息
            showStockInfo: false, // 控制股票信息小页面显示
        };
    },
    methods: {
        // 加载所有股票数据
        async fetchStocks() {
            try {
                const response = await api.get("/stock-a");
                if (response.data.status === "success") {
                    this.stocks = response.data.data;
                } else {
                    console.error("Failed to fetch stock data:", response.data.message);
                }
            } catch (error) {
                console.error("Error fetching stock data:", error);
            }
        },
        // 搜索逻辑
        onSearch() {
            const query = this.searchQuery.trim();
            if (!query) {
                this.filteredStocks = [];
                return;
            }
            const isNumber = /^\d+$/.test(query); // 判断是否是数字
            this.filteredStocks = this.stocks.filter((stock) =>
                isNumber
                    ? stock.code.includes(query) // 数字模糊匹配代码
                    : stock.name.includes(query) // 汉字模糊匹配名称
            );
        },
        // 选中候选股票
        async selectStock(stock) {
            // 回写搜索框
            this.searchQuery = `${stock.code} - ${stock.name}`;
            // 清空候选列表
            this.filteredStocks = [];
            // 查询股票基本信息
            await this.fetchStockInfo(stock.code);
            // 发送股票代码消息给上级页面
            this.$emit("stockSelected", stock.code,stock.name,this.stockPeriod);
            // 显示股票基本信息小页面
            this.showStockInfo = true;

            // 5 秒后渐隐，并设置搜索框半透明
            setTimeout(() => {
                this.showStockInfo = false; // 隐藏股票信息框
                this.setSearchOpacity(); // 将搜索框设置为半透明
            }, 5000);
        },
        // 查询股票基本信息
        async fetchStockInfo(stockCode) {
            try {
                const response = await api.get(`/stock-info/${stockCode}`);
                if (response.data.status === "success") {
                    this.stockInfo = response.data.data;
                } else {
                    console.error("Failed to fetch stock info:", response.data.message);
                    this.stockInfo = [];
                }
            } catch (error) {
                console.error("Error fetching stock info:", error);
                this.stockInfo = [];
            }
        },
        // 鼠标进入时恢复透明度
        resetSearchOpacity() {
            const container = this.$el.querySelector(".search-container");
            container.classList.remove("faded");
        },
        // 鼠标离开时设置透明度
        setSearchOpacity() {
            const container = this.$el.querySelector(".search-container");
            container.classList.add("faded");
        },
    },
    async mounted() {
        await this.fetchStocks();
    },
};
</script>

<style scoped>
.stock-search-page {
    width: 100%;
    height: 36px;
    max-width: 300px;
    margin: 0 auto;
    margin-top: 8px;
    margin-bottom: 24px;
    padding: 8x;
    text-align: center;
}

.search-container {
    position: relative;
    margin-bottom: 20px;
    display: inline-block;
    transition: opacity 0.5s ease;
}

.search-container.faded {
    opacity: 0.5;
}

.search-row {
    display: flex;
    align-items: center;
    gap: 8px; /* 控制 select 和 input 的间距 */
}

.search-select {
    width: auto;
    padding: 10px 15px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    outline: none;
    box-sizing: border-box;
    appearance: none; /* 移除浏览器默认样式 */
}

.search-input {
    flex-grow: 1;
    width: 240px;
    padding: 10px 15px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    outline: none;
    box-sizing: border-box;
}

.dropdown {
    margin: 0;
    padding: 0;
    list-style: none;
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    max-height: 200px;
    overflow-y: auto;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 10;
}

.dropdown-item {
    padding: 10px 15px;
    font-size: 14px;
    color: #333;
    cursor: pointer;
}

.dropdown-item:hover {
    background-color: #f1f1f1;
}

.stock-info-popup {
    color: whitesmoke;
    position: fixed;
    /* 固定定位 */
    bottom: 20px;
    /* 距离页面底部20px */
    right: 20px;
    /* 距离页面右侧20px */
    width: 268px;
    /* 与搜索框宽度一致 */
    background-color: #040404c4;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 20;
    transition: opacity 1s ease;
}

.info-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    /* 设置字体大小 */
}

.info-table td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.info-table .info-item {
    font-weight: bold;
    color: #f0f0f0;
}

.info-table .info-value {
    color: #fcfcfc;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 1s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>