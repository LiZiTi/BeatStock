import akshare as ak
import pandas as pd
import numpy as np
from config.cached_akshare_request import cached_akshare_request
from indicators.common import repair_dataframe_data,NP2Dict

def fetch_stock_data():
    """
    获取5000多只股票的最后一个交易日数据。
    :return: DataFrame 格式的股票数据
    """
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stock_zh_a_spot_em_df = repair_dataframe_data(stock_zh_a_spot_em_df)
    return stock_zh_a_spot_em_df

def analyze_stock_changes(stock_data):
    """
    统计股票涨跌幅的分布情况。
    :param stock_data: 股票数据 DataFrame
    :return: 统计结果字典
    """
    # 确保涨跌幅为浮点类型，并排除 NaN 数据
    stock_data['涨跌幅'] = pd.to_numeric(stock_data['涨跌幅'], errors='coerce')
    stock_data = stock_data.dropna(subset=['涨跌幅'])

    # 定义细化的涨跌幅区间（从 -10% 到 10%，间隔 1%）
    bins = np.concatenate([[-float('inf')], np.arange(-10, 11, 1), [float('inf')]])  # 添加低于 -10% 和高于 10% 的区间
    labels = (
        ['-10%'] +
        [f"{bins[i+1]}%" for i in range(1, len(bins) - 2)] +
        ['10%']
    )

    # 使用 pd.cut 对涨跌幅进行分组统计
    stock_data['涨跌幅区间'] = pd.cut(stock_data['涨跌幅'], bins=bins, labels=labels, right=False)

    # 统计各区间股票数量
    range_counts = stock_data['涨跌幅区间'].value_counts().sort_index()

    # 统计上涨、平盘、下跌家数
    up_count = stock_data[stock_data['涨跌幅'] > 0].shape[0]
    flat_count = stock_data[stock_data['涨跌幅'] == 0].shape[0]
    down_count = stock_data[stock_data['涨跌幅'] < 0].shape[0]

    return {
        "涨跌幅分布": range_counts.to_dict(),
        "上涨家数": up_count,
        "平盘家数": flat_count,
        "下跌家数": down_count,
    }

def get_sorted_stocks(stock_data, top_n=60):
    """
    按涨跌幅排序，获取前 N 家、中间 N 家和后 N 家股票信息。
    :param stock_data: 股票数据 DataFrame
    :param top_n: 每组股票数量
    :return: 包含前、中、后 N 家股票信息的字典
    """
    # 确保涨跌幅为浮点类型，并排除 NaN 数据
    stock_data['涨跌幅'] = pd.to_numeric(stock_data['涨跌幅'], errors='coerce')
    stock_data = stock_data.dropna(subset=['涨跌幅'])

    # 排序
    stock_data_sorted = stock_data.sort_values('涨跌幅', ascending=False)

    # 获取前、中、后 N 家股票信息
    top_stocks = stock_data_sorted.head(top_n)
    mid_start = len(stock_data_sorted) // 2 - top_n // 2
    mid_stocks = stock_data_sorted.iloc[mid_start : mid_start + top_n]
    bottom_stocks = stock_data_sorted.tail(top_n)

    return {
        "前{}家".format(top_n): top_stocks,
        "中间{}家".format(top_n): mid_stocks,
        "后{}家".format(top_n): bottom_stocks,
    }

def stock_statistic(top_n=60):
    """
    股票统计函数，包括涨跌幅分布统计以及前、中、后 N 家股票筛选。
    :param top_n: 每组股票数量，默认 60
    :return: 包括统计结果和筛选的股票信息的字典
    """
    # 获取股票数据
    stock_data = fetch_stock_data()

    # 分析涨跌幅分布
    analysis_result = analyze_stock_changes(stock_data)

    # 获取前、中、后 N 家股票信息
    sorted_stocks = get_sorted_stocks(stock_data, top_n=top_n)

    return {
        "统计结果": analysis_result,
        "筛选结果": sorted_stocks
    }

def get_might_sideways_stocks(
    lower_bound=-2, 
    upper_bound=2, 
    min_volume=30000, 
    min_turnover_rate=1.0, 
    max_60_day_change=0.1
):
    """
    获取涨跌幅在指定范围内且名称不包含 'ST' 的 A 股股票，支持筛选成交量、换手率和60日涨跌幅，仅保留代码、名称和涨跌幅。

    参数:
    - lower_bound (float): 涨跌幅的下限，默认 -2。
    - upper_bound (float): 涨跌幅的上限，默认 2。
    - min_volume (float): 最小成交量，默认 30000。
    - min_turnover_rate (float): 最小换手率，默认 1.0。
    - max_60_day_change (float): 60日涨跌幅的最大值，默认 0.1。

    返回:
    - DataFrame: 涨跌幅在指定范围内且满足其他条件的股票数据，仅包含代码、名称和涨跌幅。
    """
    # 获取 A 股最新行情
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()

    # 转换涨跌幅为浮点型（确保筛选操作有效）
    stock_zh_a_spot_em_df["涨跌幅"] = pd.to_numeric(stock_zh_a_spot_em_df["涨跌幅"], errors="coerce")
    stock_zh_a_spot_em_df["60日涨跌幅"] = pd.to_numeric(stock_zh_a_spot_em_df["60日涨跌幅"], errors="coerce")
    stock_zh_a_spot_em_df["成交量"] = pd.to_numeric(stock_zh_a_spot_em_df["成交量"], errors="coerce")
    stock_zh_a_spot_em_df["换手率"] = pd.to_numeric(stock_zh_a_spot_em_df["换手率"], errors="coerce")

    # 筛选涨跌幅在指定范围内的股票
    filtered_stocks = stock_zh_a_spot_em_df[
        (stock_zh_a_spot_em_df["涨跌幅"] >= lower_bound) & 
        (stock_zh_a_spot_em_df["涨跌幅"] <= upper_bound) & 
        (~stock_zh_a_spot_em_df["名称"].str.contains("ST", na=False)) & 
        (stock_zh_a_spot_em_df["成交量"] >= min_volume) & 
        (stock_zh_a_spot_em_df["换手率"] >= min_turnover_rate) & 
        (stock_zh_a_spot_em_df["60日涨跌幅"] <= max_60_day_change)
    ]

    # 只保留代码、名称和涨跌幅
    result = repair_dataframe_data(filtered_stocks[["代码", "名称", "涨跌幅"]])

    return NP2Dict(result)