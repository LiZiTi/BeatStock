import pandas as pd
import akshare as ak
from config.cached_akshare_request import cached_akshare_request

# 定义常量
BASE_PE_RATIO = 15  # 基准市盈率
BASE_INTEREST_RATE = 0.035  # 基准利率
BASE_CPI = 0.02  # 目标CPI
BASE_LEVERAGE_RATE = 0.5  # 基准杠杆率

# 获取经典的巴菲特指标
@cached_akshare_request
def get_buffett_data():
    buffett_data = ak.stock_buffett_index_lg()
    return buffett_data

# 获取中国 CPI 月率报告
@cached_akshare_request
def get_cpi_data():
    cpi_data = ak.macro_china_cpi_monthly()
    return cpi_data

# 获取 LPR 品种数据
@cached_akshare_request
def get_lpr_data():
    lpr_data = ak.macro_china_lpr()
    return lpr_data

# 获取宏观经济杠杆率
@cached_akshare_request
def get_macro_leverage_data():
    macro_leverage_data = ak.macro_cnbs()
    return macro_leverage_data

# 获取主板市盈率
@cached_akshare_request
def get_pe_data():
    pe_data = ak.stock_market_pe_lg(symbol="上证")
    return pe_data

# 获取上证指数的历史行情
@cached_akshare_request
def get_stock_zh_index_data():
    stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol="sh000001")
    return stock_zh_index_daily_em_df

# 获取上证指数的实时行情
def get_stock_zh_real_time():
    stock_zh_index_spot_em_df = ak.stock_zh_index_spot_em(symbol="上证系列指数")
    filtered_df = stock_zh_index_spot_em_df[stock_zh_index_spot_em_df['代码'] == "000001"]
    return filtered_df


# 统一所有数据到 "日" 单位，填充缺失的日期
def fill_daily_data(monthly_data, start_date, end_date, date_column):
    monthly_data[date_column] = pd.to_datetime(monthly_data[date_column])
    date_range = pd.date_range(start=start_date, end=end_date)
    daily_data = pd.DataFrame({date_column: date_range})
    daily_data = pd.merge_asof(daily_data, monthly_data.sort_values(date_column), on=date_column, direction='backward')
    return daily_data

# @cached(ttl=CACHE_TTL, serializer=JsonSerializer())
def merge_buffett_indicator():
    """合并所有数据集并计算巴菲特指标"""
    # 获取最新数据
    buffett_data = get_buffett_data()
    cpi_data = get_cpi_data()
    lpr_data = get_lpr_data()
    macro_leverage_data = get_macro_leverage_data()
    pe_data = get_pe_data()
    stock_zh_index_daily_df = get_stock_zh_index_data()

    # 将日期列转换为 datetime 类型
    buffett_data['日期'] = pd.to_datetime(buffett_data['日期'])
    cpi_data['日期'] = pd.to_datetime(cpi_data['日期'])
    lpr_data['TRADE_DATE'] = pd.to_datetime(lpr_data['TRADE_DATE'])
    macro_leverage_data['年份'] = pd.to_datetime(macro_leverage_data['年份'], format='%Y-%m')
    pe_data['日期'] = pd.to_datetime(pe_data['日期'])
    stock_zh_index_daily_df['date'] = pd.to_datetime(stock_zh_index_daily_df['date'])

    # 合并数据
    merged_data = pd.merge(buffett_data, cpi_data[['日期', '今值']], on='日期', how='left')
    merged_data = pd.merge(merged_data, lpr_data[['TRADE_DATE', 'LPR1Y']], left_on='日期', right_on='TRADE_DATE', how='left')
    merged_data = pd.merge(merged_data, macro_leverage_data[['年份', '政府部门']], left_on='日期', right_on='年份', how='left')
    merged_data = pd.merge(merged_data, pe_data[['日期', '平均市盈率']], on='日期', how='left')
    merged_data = pd.merge(merged_data, stock_zh_index_daily_df[['date', 'open', 'high', 'low', 'close', 'volume']],
                           left_on='日期', right_on='date', how='left')

    # 填充缺失值
    merged_data.fillna(method='ffill', inplace=True)
    merged_data.fillna(method='bfill', inplace=True)

    # 计算经典的巴菲特指标并保留 3 位小数
    merged_data['经典巴菲特指标'] = (merged_data['总市值'] / merged_data['GDP']).round(3)

    # 计算优化后的巴菲特指标并保留 3 位小数
    merged_data['优化巴菲特指标'] = merged_data.apply(calculate_optimized_buffett_index, axis=1)

    # 进一步确保所有数值列保留 3 位小数
    merged_data[['经典巴菲特指标', '优化巴菲特指标']] = merged_data[['经典巴菲特指标', '优化巴菲特指标']].round(3)

    # 检查巴菲特数据和指数数据的最新日期，如果指数数据有更新，则推算巴菲特指标
    buffett_latest_date = merged_data['日期'].max()
    stock_latest_date = stock_zh_index_daily_df['date'].max()

    if buffett_latest_date < stock_latest_date:
        merged_data = calculate_missing_buffett_index(merged_data, stock_zh_index_daily_df, buffett_latest_date)

    # 将日期格式统一为 yyyy-mm-dd
    merged_data['日期'] = merged_data['日期'].dt.strftime('%Y-%m-%d')

    # 返回需要的列
    df = merged_data[['日期', '收盘价', '总市值', 'GDP', '经典巴菲特指标', '优化巴菲特指标', 'open', 'high', 'low', 'close', 'volume']]
    return df.to_dict(orient='records')

# 动态推算缺失的巴菲特指标
def calculate_missing_buffett_index(merged_data, stock_data, buffett_latest_date):
    stock_latest_date = stock_data['date'].max()
    missing_dates = pd.date_range(start=buffett_latest_date + pd.Timedelta(days=1), end=stock_latest_date)

    last_known_row = merged_data[merged_data['日期'] == buffett_latest_date].iloc[0]

    for missing_date in missing_dates:
        stock_row = stock_data[stock_data['date'] == missing_date]
        if stock_row.empty:
            break

        index_change_ratio = (stock_row['close'].values[0] - last_known_row['close']) / last_known_row['close']

        new_row = {
            '日期': missing_date,
            '收盘价': stock_row['close'].values[0],
            '总市值': last_known_row['总市值'] * (1 + index_change_ratio),
            'GDP': last_known_row['GDP'],
            '经典巴菲特指标': last_known_row['经典巴菲特指标'] * (1 + index_change_ratio),
            '优化巴菲特指标': last_known_row['优化巴菲特指标'] * (1 + index_change_ratio),
            'open': stock_row['open'].values[0],
            'high': stock_row['high'].values[0],
            'low': stock_row['low'].values[0],
            'close': stock_row['close'].values[0],
            'volume': stock_row['volume'].values[0]
        }

        merged_data = pd.concat([merged_data, pd.DataFrame([new_row])], ignore_index=True)
        last_known_row = new_row

    merged_data = merged_data.sort_values(by='日期').reset_index(drop=True)
    return merged_data


# 计算优化后的巴菲特指标
def calculate_optimized_buffett_index(row):
    market_cap = row['总市值']
    gdp = row['GDP']
    pe_ratio = row['平均市盈率']
    interest_rate = row['LPR1Y'] / 100  # 转换为小数形式
    leverage_ratio = row['政府部门'] / 100  # 转换为小数形式
    inflation_rate = row['今值'] / 100  # 转换为小数形式

    buffett_index = market_cap / gdp

    alpha = 0.2
    beta = 0.15
    gamma = 0.1
    delta = 0.1

    pe_adjustment = 1 + alpha * (pe_ratio / BASE_PE_RATIO)
    interest_adjustment = 1 - beta * (interest_rate / BASE_INTEREST_RATE)
    leverage_adjustment = 1 + gamma * (leverage_ratio / BASE_LEVERAGE_RATE)
    inflation_adjustment = 1 + delta * (inflation_rate / BASE_CPI)

    optimized_buffett_index = buffett_index * pe_adjustment * interest_adjustment * leverage_adjustment * inflation_adjustment
    return round(optimized_buffett_index, 3)


def periodic_buffett_index(period=5):
    """
    根据指定的周期对上证指数和巴菲特指标进行汇总处理。
    :param data: merge_buffett_indicator 输出的 DataFrame 数据
    :param period: 周期天数 (int)，大于 0
    :return: 一个包含周期数据的 DataFrame
    """
    data = pd.DataFrame(merge_buffett_indicator())
    
    data = data.sort_values(by='日期').reset_index(drop=True)

    # 计算最大整数倍
    total_rows = len(data)
    max_multiple = total_rows // period
    effective_rows = max_multiple * period

    # 截取后 effective_rows 条数据
    data = data.tail(effective_rows)

    # 创建周期索引
    data['周期'] = data.index // period

    # 定义聚合方法
    agg_funcs = {
        '日期': 'last',  # 日期取周期最后一天的日期
        'open': 'first',  # 开盘价取周期第一天的值
        'high': 'max',    # 最高价取周期内的最大值
        'low': 'min',     # 最低价取周期内的最小值
        'close': 'last',  # 收盘价取周期最后一天的值
        'volume': 'sum',  # 成交量取周期内的总和
        '经典巴菲特指标': 'mean',  # 经典巴菲特指标取周期内的平均值
        '优化巴菲特指标': 'mean'   # 优化巴菲特指标取周期内的平均值
    }

    # 按周期索引聚合
    periodic_data = data.groupby('周期').agg(agg_funcs).reset_index(drop=True)
    # 保留巴菲特指标值的精度为 3 位小数
    periodic_data['经典巴菲特指标'] = periodic_data['经典巴菲特指标'].round(3)
    periodic_data['优化巴菲特指标'] = periodic_data['优化巴菲特指标'].round(3)
    # 返回结果
    return periodic_data.to_dict(orient='records')