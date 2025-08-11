import axios from 'axios';

class AkToolsApi {
  constructor(baseURL) {
    this.apiClient = axios.create({
      baseURL: baseURL,
      timeout: 10000,
    });
  }

  // 全球 GDP 增长率数据
  async getGlobalGDP() {
    return await this.apiClient.get('/macro_global_gdp');
  }

  // 中国年度 GDP 数据
  async getChinaGDP() {
    return await this.apiClient.get('/macro_china_gdp_yearly');
  }

  // 添加更多接口...
}

export default new AkToolsApi('http://localhost:8080/api/public');
