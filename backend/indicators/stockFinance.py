import akshare as ak
from indicators.common import repair_dataframe_data,NP2Dict
from config.cached_akshare_request import cached_akshare_request
import pandas as pd
from datetime import datetime, timedelta

@cached_akshare_request
def get_financial_data(stock_code, start_year=""):
   return ak.stock_financial_analysis_indicator(stock_code,start_year)

def analyze_indicator(value, name, thresholds):
    """
    根据设定的阈值对每个指标进行分析，并给出相应的语言描述。

    参数:
    value: 指标的值
    name: 指标名称
    thresholds: 阈值字典，包含 "low", "high" 和 "excellent" 的标准

    返回:
    分析描述
    """
    if value < thresholds['low']:
        return f"{name} 值为 {value:.2f}，低于阈值 {thresholds['low']}，表明公司在此指标上表现较差。"
    elif value < thresholds['high']:
        return f"{name} 值为 {value:.2f}，在合理区间 ({thresholds['low']}-{thresholds['high']})，表现中规中矩。"
    else:
        return f"{name} 值为 {value:.2f}，高于阈值 {thresholds['high']}，表现优秀。"


def calculate_roe_with_analysis(df):
    """
    计算净资产收益率（ROE）并提供语言分析描述。

    参数：
    df: 包含财务数据的 DataFrame

    返回：
    带有 ROE 计算结果和分析描述的 DataFrame
    """
    # 确保所有相关列都存在
    required_columns = ['销售净利率(%)', '总资产周转率(次)', '资产负债率(%)']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"输入数据缺少必要的列: {required_columns}")

    # 阈值设定
    thresholds = {
        '销售净利率(%)': {'low': 3, 'high': 10},
        '总资产周转率(次)': {'low': 0.5, 'high': 2},
        '资产负债率(%)': {'low': 30, 'high': 70}
    }

    # 创建用于存储语言分析描述的列表
    analysis_descriptions = []

    # 计算权益乘数 = 1 / (1 - 资产负债率)
    df['权益乘数'] = 1 / (1 - (df['资产负债率(%)'] / 100))

    # 计算 ROE = 销售净利率 * 总资产周转率 * 权益乘数
    df['ROE(%)'] = (df['销售净利率(%)'] / 100) * df['总资产周转率(次)'] * df['权益乘数'] * 100

    # 对每个指标进行分析并生成语言描述
    for i, row in df.iterrows():
        analysis = []
        analysis.append(f"日期: {row['日期']}")

        # 分析销售净利率
        analysis.append(analyze_indicator(row['销售净利率(%)'], '销售净利率(%)', thresholds['销售净利率(%)']))

        # 分析总资产周转率
        analysis.append(analyze_indicator(row['总资产周转率(次)'], '总资产周转率(次)', thresholds['总资产周转率(次)']))

        # 分析资产负债率
        analysis.append(analyze_indicator(row['资产负债率(%)'], '资产负债率(%)', thresholds['资产负债率(%)']))

        # 分析权益乘数
        analysis.append(
            f"权益乘数的计算结果为 {row['权益乘数']:.2f}。权益乘数反映了公司的杠杆水平，数值越高意味着公司利用了更多的负债。")

        # 分析 ROE
        roe_analysis = f"计算得出 ROE 为 {row['ROE(%)']:.2f}%。"
        if row['ROE(%)'] > 15:
            roe_analysis += " ROE 高于 15%，表明公司净资产收益率较高，盈利能力强。"
        elif row['ROE(%)'] < 5:
            roe_analysis += " ROE 低于 5%，表明公司净资产收益率较低，盈利能力较弱。"
        else:
            roe_analysis += " ROE 在合理范围内。"
        analysis.append(roe_analysis)

        # 将分析添加到列表
        analysis_descriptions.append("\n".join(analysis))

    # 将语言描述作为新列加入 DataFrame
    df['分析描述'] = analysis_descriptions

    return df[['日期', '销售净利率(%)', '总资产周转率(次)', '资产负债率(%)', '权益乘数', 'ROE(%)', '分析描述']]

def get_stock_roe_history(symbol):
    df = get_financial_data(symbol)
    df = calculate_roe_with_analysis(df)
    df = repair_dataframe_data(df)
    return df.to_dict(orient='records')

@cached_akshare_request
def get_stock_history(stock_code, period="daily", adjust=""):
    stock_zh_a_hist_df = ak.stock_zh_a_hist(stock_code, period, adjust)
    df = repair_dataframe_data(stock_zh_a_hist_df)
    return df.to_dict(orient='records')

@cached_akshare_request
def get_stock_cyq_data(stock_code):
    chip_data = ak.stock_cyq_em(symbol=stock_code)
    df = repair_dataframe_data(chip_data)
    return df.to_dict(orient='records')


def normalize_data(data, method='minmax'):
    """
    对数据进行归一化处理。
    参数:
    - data (Series): 输入数据
    - method (str): 归一化方法，默认 'minmax'
    返回:
    - Series: 归一化后的数据
    """
    if method == 'minmax':
        min_val = data.min()
        max_val = data.max()
        if max_val == min_val:  # 避免除零错误
            return data - min_val
        return (data - min_val) / (max_val - min_val)
    else:
        raise ValueError("Unsupported normalization method. Only 'minmax' is allowed.")

# 获取集中度的三个部分均值
def calculate_mean_segments(series):
    n = len(series)
    if n < 3:  # 数据量太少无法分段，直接返回 NaN
        return None, None, None
    # 分段索引
    segment_size = n // 3
    first_segment = series.iloc[:segment_size].mean()  # 前 30%
    middle_segment = series.iloc[segment_size:2 * segment_size].mean()  # 中间 30%
    last_segment = series.iloc[2 * segment_size:].mean()  # 后 30%
    return first_segment, middle_segment, last_segment

@cached_akshare_request
def analyze_stock_discreteness(
    symbol, 
    his_days=200,
    window_sizes=[5, 10, 15, 20], 
    price_fluctuation_limits=[0.05, 0.07, 0.10, 0.12], 
    normalize_method='minmax'
):
    """
    分析股票在多个时间滑动窗口内是否满足横盘和筹码集中度提高的条件。

    参数:
    - symbol (str): 股票代码。
    - window_sizes (list): 滑动窗口大小列表（单位：交易日）。
    - price_fluctuation_limits (list): 股价波动范围列表，与窗口大小一一对应。
    - normalize_method (str): 数据归一化方法，默认 'minmax'。

    返回:
    - dict: 以窗口大小为 key，每个 key 对应一个 DataFrame 结果。
    """
    # 检查输入有效性
    if len(window_sizes) != len(price_fluctuation_limits):
        raise ValueError("window_sizes 和 price_fluctuation_limits 长度必须相等")
    
    # 获取筹码数据
    stock_cyq_em_df = ak.stock_cyq_em(symbol=symbol, adjust="")
    
    # 获取今天的日期
    end_date = datetime.today().strftime('%Y%m%d')
    
    # 获取200天之前的日期
    start_date = (datetime.today() - timedelta(days=his_days)).strftime('%Y%m%d')
    
    # 获取历史行情数据
    stock_zh_a_hist_df = ak.stock_zh_a_hist(
        symbol=symbol, 
        period="daily", 
        start_date=start_date, 
        end_date=end_date, 
        adjust=""
    )
    
    # 转换日期格式
    stock_cyq_em_df['日期'] = pd.to_datetime(stock_cyq_em_df['日期'])
    stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
    
    # 找到最大开始日期，确保数据日期范围一致
    max_start_date = max(stock_cyq_em_df['日期'].min(), stock_zh_a_hist_df['日期'].min())
    stock_cyq_em_df = stock_cyq_em_df[stock_cyq_em_df['日期'] >= max_start_date]
    stock_zh_a_hist_df = stock_zh_a_hist_df[stock_zh_a_hist_df['日期'] >= max_start_date]
    
    # 合并数据
    merged_df = pd.merge(stock_cyq_em_df, stock_zh_a_hist_df, on='日期', how='inner')
    
    # 数据归一化
    merged_df['成交量归一化'] = normalize_data(merged_df['成交量'], normalize_method)
    merged_df['换手率归一化'] = normalize_data(merged_df['换手率'], normalize_method)
    merged_df['股价归一化'] = normalize_data(merged_df['收盘'], normalize_method)
    
    # 汇总结果
    results_by_window = {}
    for window_size, price_fluctuation_limit in zip(window_sizes, price_fluctuation_limits):
        window_results = []
        for i in range(len(merged_df) - window_size + 1):
            window = merged_df.iloc[i:i + window_size]
            
            # 提取窗口信息
            start_date = window['日期'].iloc[0]
            end_date = window['日期'].iloc[-1]
            
            # 计算横盘条件：最高价和最低价的波动幅度 <= 对应的 price_fluctuation_limit
            max_price = window['收盘'].max()
            min_price = window['收盘'].min()
            avg_price = window['收盘'].mean()
            price_stable = (max_price - min_price) / avg_price <= price_fluctuation_limit
            
            # 筹码集中度分段均值计算
            chips_70_first, chips_70_middle, chips_70_last = calculate_mean_segments(window['70集中度'])
            chips_90_first, chips_90_middle, chips_90_last = calculate_mean_segments(window['90集中度'])
    
            # 判断分段均值是否单调递减
            chips_70_concentration = chips_70_first >= chips_70_middle >= chips_70_last
            chips_90_concentration = chips_90_first >= chips_90_middle >= chips_90_last
    
            # 筹码集中度提高条件
            concentration_improving = chips_70_concentration and chips_90_concentration
            
            # 计算变异系数（CV）作为离散度
            volume_discreteness = window['成交量归一化'].std() / window['成交量归一化'].mean()
            turnover_rate_discreteness = window['换手率归一化'].std() / window['换手率归一化'].mean()
            price_discreteness = window['股价归一化'].std() / window['股价归一化'].mean()
            
            # 汇总结果
            result = {
                "起始日期": start_date,
                "终止日期": end_date,
                "是否横盘": price_stable,
                "是否筹码集中": concentration_improving,
                "成交量变异系数": volume_discreteness,
                "换手率变异系数": turnover_rate_discreteness,
                "股价变异系数": price_discreteness
            }
            window_results.append(result)
        
        # 将结果存入以窗口大小为 key 的字典
        results_by_window[window_size] = NP2Dict(repair_dataframe_data(pd.DataFrame(window_results).tail(5)))
    
    return results_by_window