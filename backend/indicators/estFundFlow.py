import akshare as ak
import pandas as pd
from functools import reduce
from config.cached_akshare_request import cached_akshare_request
from indicators.common import repair_dataframe_data

@cached_akshare_request
def getSectionFundFlow(indicator="今日", sector_type="行业资金流"):
    """
    获取板块资金流排名数据

    参数:
        indicator (str): 时间指标。选项为 "今日"、"5日" 或 "10日"。
        sector_type (str): 板块类型。选项为 "行业资金流"、"概念资金流" 或 "地域资金流"。

    返回:
        DataFrame: 包含板块资金流排名数据的 DataFrame。
    """
    try:
        # 获取数据
        stock_sector_fund_flow_rank_df = ak.stock_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)
        return stock_sector_fund_flow_rank_df
    except Exception as e:
        print(f"获取数据出错: {e}")
        return None
    


def getConceptFundFlowHist(symbol="锂电池"):
    """
    获取指定概念的历史资金流数据

    参数:
        symbol (str): 概念名称，例如 "锂电池"

    返回:
        DataFrame: 包含概念历史资金流数据的 DataFrame
    """
    try:
        # 获取数据
        stock_concept_fund_flow_hist_df = ak.stock_concept_fund_flow_hist(symbol=symbol)
        return stock_concept_fund_flow_hist_df.to_dict(orient='records')
    except Exception as e:
        print(f"获取数据出错: {e}")
        return None
    


def getSectorFundFlowHist(symbol="电源设备"):
    """
    获取指定行业的历史资金流数据

    参数:
        symbol (str): 行业名称，例如 "电源设备"

    返回:
        DataFrame: 包含行业历史资金流数据的 DataFrame
    """
    try:
        # 获取数据
        stock_sector_fund_flow_hist_df = ak.stock_sector_fund_flow_hist(symbol=symbol)
        return stock_sector_fund_flow_hist_df.to_dict(orient='records')
    except Exception as e:
        print(f"获取数据出错: {e}")
        return None
    
def load_sector_fund_flow_history(sector_type="行业资金流",symbol=""):
    if sector_type == "行业资金流":
        return getSectorFundFlowHist(symbol)
    elif sector_type == "概念资金流":
        return getConceptFundFlowHist(symbol)
    else:
        return None

def normalize_scores(merged_df):
    """
    将评分归一化到 -10 到 10 之间，-10 表示评分最差，10 表示评分最好。

    参数:
        merged_df (DataFrame): 包含行业资金流数据和评分列的 DataFrame。

    返回:
        DataFrame: 添加了归一化评分的新 DataFrame。
    """
    min_score = merged_df['score'].min()
    max_score = merged_df['score'].max()
    
    # 归一化到 -10 到 10，并保留两位小数
    merged_df['normalized_score'] = merged_df['score'].apply(
        lambda x: round(-10 + 20 * (x - min_score) / (max_score - min_score), 2)
    )
    
    return merged_df



def calculate_top_bottom_five(sector_type="行业资金流"):
    """
    计算资金排名前五和后五的行业。

    获取每个行业的 "今日"、"5日" 和 "10日" 的资金数据，
    并根据 "名称" 列合并，
    对每个行业的资金情况进行评分，
    最后选出前5名和后5名。

    返回:
        tuple: 包含前5名和后5名行业数据的两个 DataFrame。
    """
    try:
        indicators = ["今日", "5日", "10日"]
        dfs = {}

        # 获取不同时间指标的数据并重命名列
        for indicator in indicators:
            df = getSectionFundFlow(indicator=indicator, sector_type=sector_type)
            if df is not None:
                dfs[indicator] = df
            else:
                print(f"获取 {indicator} 数据失败")
                return None, None

        # 根据 '名称' 列进行合并
        merged_df = dfs["今日"].merge(dfs["5日"], on='名称', how='inner').merge(dfs["10日"], on='名称', how='inner')

        # 确定用于评分的列名
        main_net_inflow_cols = {
            "今日": "今日主力净流入-净额",
            "5日": "5日主力净流入-净额",
            "10日": "10日主力净流入-净额"
        }

        # 检查必要的列是否存在
        for col in main_net_inflow_cols.values():
            if col not in merged_df.columns:
                print(f"无法找到必要的列进行评分: {col}")
                return None, None

        # 计算评分，使用主力净流入-净额
        weights = {"今日": 0.8, "5日": 0.1, "10日": 0.1}
        merged_df['score'] = sum(
            weights[indicator] * merged_df[main_net_inflow_cols[indicator]]
            for indicator in indicators
        )

        # 调用 normalize_scores 函数对评分进行归一化
        merged_df = normalize_scores(merged_df)

        # 使用归一化后的评分来排序
        merged_df = merged_df.sort_values(by='normalized_score', ascending=False)
        top5 = merged_df.head(5)
        bottom5 = merged_df.tail(5)


        # 返回包含所有信息的 DataFrame
        return {
                "top5":top5.to_dict(orient='records'),
                "tail5":bottom5.to_dict(orient='records')
        }
    except Exception as e:
        print(f"计算过程中出现错误: {e}")
        return None, None
    
def calculate_rt_top_bottom_five(sector_type="行业资金流"):
    """
    计算资金排名前五和后五的行业。

    获取每个行业的 "今日"、"5日" 和 "10日" 的资金数据，
    并根据 "名称" 列合并，
    对每个行业的资金情况进行评分，
    最后选出前5名和后5名。

    返回:
        tuple: 包含前5名和后5名行业数据的两个 DataFrame。
    """
    try:
        df = getSectionFundFlow(indicator="今日", sector_type=sector_type)
        # 使用归一化后的评分来排序
        df = df.sort_values(by='今日主力净流入-净额', ascending=False)
        total_amount = round(df['今日主力净流入-净额'].sum()/1e8,2)
        top3 = df.head(3)
        bottom3 = df.tail(3)

        # 返回包含所有信息的 DataFrame
        return {
                "now_top5":top3.to_dict(orient='records'),
                "now_tail5":bottom3.to_dict(orient='records'),
                "now_amount":total_amount
        }
    except Exception as e:
        print(f"计算过程中出现错误: {e}")
        return None, None

def calculate_sector_all(sector_type="行业资金流"):
    """
    计算资金排名前五和后五的行业。

    获取每个行业的 "今日"、"5日" 和 "10日" 的资金数据，
    并根据 "名称" 列合并，
    对每个行业的资金情况进行评分，
    最后选出前5名和后5名。

    返回:
        tuple: 包含前5名和后5名行业数据的两个 DataFrame。
    """
    try:
        indicators = ["今日", "5日", "10日"]
        dfs = {}

        # 获取不同时间指标的数据并重命名列
        for indicator in indicators:
            df = getSectionFundFlow(indicator=indicator, sector_type=sector_type)
            dfs[indicator] = df

        merged_df = dfs["今日"]
        # 根据 '名称' 列进行合并
        if dfs["5日"] is not None:
            merged_df = merged_df.merge(dfs["5日"], on='名称', how='inner')
        if dfs["10日"] is not None:
            merged_df = merged_df.merge(dfs["10日"], on='名称', how='inner')

        merged_df = repair_dataframe_data(merged_df)
        return {
                "orderedSectors":merged_df.to_dict(orient='records')
        }
    except Exception as e:
        print(f"计算过程中出现错误: {e}")
        return None, None
    