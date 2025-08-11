import akshare as ak
import pandas as pd
import numpy as np
from config.cached_akshare_request import cached_akshare_request
from indicators.common import repair_dataframe_data


# 设置阈值
NET_OUTFLOW_THRESHOLD = -35e9  # 资金净流出不超过 35 亿
TOP_N = 5  # 选取前 10 名的行业和概念版块


# Step 1: 获取大盘资金流数据
@cached_akshare_request
def get_market_fund_flow():
    stock_market_fund_flow_df = ak.stock_market_fund_flow()
    stock_market_fund_flow_df['日期'] = pd.to_datetime(stock_market_fund_flow_df['日期']).dt.strftime('%Y-%m-%d')
    stock_market_fund_flow_df = repair_dataframe_data(stock_market_fund_flow_df)
    return stock_market_fund_flow_df


# Merge all dataframes on '行业'
def merge_dataframes(df_list):
    df = df_list[0]
    for temp_df in df_list[1:]:
        df = pd.merge(df, temp_df, on='行业', how='outer', suffixes=('', '_y'))
    df = df.loc[:, ~df.columns.str.endswith('_y')]
    return df

# Convert percentage strings to floats
def convert_percentages(df, percentage_columns):
    def percent_to_float(x):
        if isinstance(x, str):
            return float(x.strip('%')) / 100
        else:
            return x

    for col in percentage_columns:
        df[col] = df[col].apply(percent_to_float)
    return df

# Compute z-scores for each variable
def compute_zscores(df, variables):
    for var in variables:
        mean = df[var].mean()
        std = df[var].std()
        if std != 0:
            df[var + '_zscore'] = (df[var] - mean) / std
        else:
            df[var + '_zscore'] = 0
    return df

def convert_df_to_dict(df):
    """
    将 pandas 数据框转换为字典并将 numpy 类型转换为 Python 内置类型
    """
    # 使用 applymap() 将所有单元格的数据类型转换为 Python 原生类型
    df = df.map(lambda x: x.item() if isinstance(x, (np.generic, np.bool_)) else x)
    return df.to_dict(orient="records")


def calculate_bull_bear_score(day_data):
    """
    计算多空力量的标准化得分。
    :param day_data: 单个交易日的数据
    :return: 标准化多空得分（0-100）
    """
    # 解析单个交易日的数据，保持各项净流入的正负性
    super_large_buy = day_data['超大单净流入-净额']
    large_buy = day_data['大单净流入-净额']
    medium_buy = day_data['中单净流入-净额']
    small_buy = day_data['小单净流入-净额']

    # 计算资金基数，即所有净流入的绝对值之和
    total_fund_flow = abs(super_large_buy) + abs(large_buy) + abs(medium_buy) + abs(small_buy)

    # 计算每个净流入的比例
    super_large_ratio = super_large_buy / total_fund_flow
    large_ratio = large_buy / total_fund_flow
    medium_ratio = medium_buy / total_fund_flow
    small_ratio = small_buy / total_fund_flow

    # 对比例进行加权计算
    super_large_score = super_large_ratio * 0.4
    large_score = large_ratio * 0.3
    medium_score = medium_ratio * 0.2
    small_score = small_ratio * 0.1

    # 计算总得分
    total_score = super_large_score + large_score + medium_score + small_score

    # 计算指数涨跌幅的影响
    index_change_score = (day_data['上证-涨跌幅'] + day_data['深证-涨跌幅']) / 200  # 取上证和深证涨跌幅的平均值

    # 最终得分，加权指数涨跌幅
    final_score = total_score * (1 + index_change_score)

    # 标准化得分，将总得分调整到 0 到 100 的范围
    standardized_score = 50 + final_score * 100
    standardized_score = max(0, min(100, standardized_score))

    return standardized_score


def calculate_multi_day_scores(data, days):
    """
    计算多空力量的近N日平均标准化得分。
    :param data: 包含资金流向和指数涨跌幅的 JSON 数据
    :param days: 最近N个交易日
    :return: 标准化多空得分（0-100）
    """
    if len(data) < days:
        return calculate_bull_bear_score(data[-1])  # 数据不足时返回最后一个交易日的得分

    recent_data = data[-days:]
    return calculate_bull_bear_score(recent_data[-1])

def analyze_market_fund_indicator():
    # 获取大盘资金流数据
    market_data = get_market_fund_flow()

    # 获取总成交额
    market_total_amount = get_market_total_amount()

    # 获取最近 100 天资金流向数据
    recent_100_market = market_data.tail(100).copy()

    # 计算最近 100 天的资金流向多空评分
    recent_100_market.loc[:, '多空评分'] = recent_100_market.apply(calculate_bull_bear_score, axis=1)

    # 转换数据为字典
    market_data_dict = convert_df_to_dict(recent_100_market)

    # 返回多空评分数据和总成交额
    return {
        "recent_market_data": market_data_dict,
        "total_market_amount": market_total_amount
    }


# 获取数据并缓存
@cached_akshare_request
def get_today_area_head_stocks(sector_type, symbol):
    """根据选择的行业或概念，获取龙头股信息（按成交额降序排名取前6个），并使用缓存"""

    # 根据 selectType 获取数据
    if sector_type == "行业资金流":
        stock_df = ak.stock_board_industry_cons_em(symbol)
    elif sector_type == "概念资金流":
        stock_df = ak.stock_board_concept_cons_em(symbol)
    else:
        raise ValueError("selectType 只能为 '行业资金流' 或 '概念资金流'")

    # 将需要的列转换为数值类型，避免排序时出错
    stock_df['涨跌幅'] = pd.to_numeric(stock_df['涨跌幅'], errors='coerce')
    stock_df['成交额'] = pd.to_numeric(stock_df['成交额'], errors='coerce')
    stock_df['换手率'] = pd.to_numeric(stock_df['换手率'], errors='coerce')

    # 按涨跌幅、成交额、换手率进行排序（值越大越好）
    top_stocks = stock_df.sort_values(by=['涨跌幅', '成交额', '换手率'], ascending=[False, False, False]).head(4)
    tail_stocks = stock_df.sort_values(by=['涨跌幅', '成交额', '换手率'], ascending=[False, False, False]).tail(4)

    return {
        "top_stocks": convert_df_to_dict(top_stocks),
        "tail_stocks": convert_df_to_dict(tail_stocks),
    }

def get_market_total_amount():
    df = ak.stock_zh_a_spot_em()
    total_amount = df['成交额'].sum()/1e8
    return round(total_amount,2)