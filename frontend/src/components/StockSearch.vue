<template>
    <div class="search-page">
      <div class="search-container">
        <select>
          <option value="daily">日数据</option>
          <option value="weekly">周数据</option>
        </select>
        <input
          type="text"
          v-model="searchCode"
          class="search-input"
          placeholder="输入股票代码..."
          @keyup.enter="searchStock"
        />
        <button class="search-button" @click="searchStock">
          🔍
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import Swal from 'sweetalert2';
  
  export default {
    data() {
      return {
        searchCode: ""
      };
    },
    methods: {
      searchStock() {
        const isValidCode = /^\d{6}$/.test(this.searchCode); // 检查是否为6位数字
        if (!isValidCode) {
          Swal.fire({
            icon: 'error',
            title: '无效股票代码',
            text: '请输入一个有效的6位股票代码！',
            confirmButtonColor: '#FF4B4B'
          });
          return;
        }
        this.$emit("stock-selected", this.searchCode);
      }
    }
  };
  </script>
  
  <style scoped>
  .search-page {
    display: flex;
    height: 100%;
    width: 100%;
    justify-content: center;
    align-items: center;
    background-color: #252A34;
  }
  
  .search-container {
    position: relative;
    width: 300px;
  }
  
  .search-input {
    width: 100%;
    padding: 0.8rem;
    padding-right: 3rem; /* 留出右侧空间给搜索按钮 */
    border-radius: 20px;
    border: 1px solid #ddd;
    font-size: 1rem;
    /* background-color: #252A34; */
    color: #252A34;
    outline: none;
  }
  
  .search-button {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    border: none;
    background: none;
    color: #FF4B4B;
    font-size: 1.2rem;
    cursor: pointer;
    outline: none;
  }
  
  .search-input:focus {
    border-color: #ff4b4b;
    box-shadow: 0 0 5px rgba(255, 75, 75, 0.5);
  }
  
  .search-button:hover {
    color: #e85353;
  }
  </style>
  