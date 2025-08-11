import akshare as ak
import pandas as pd
from fuzzywuzzy import process
from config.cached_akshare_request import cached_akshare_request

@cached_akshare_request
def load_concept_name_mapping(threshold=55):
    """
    加载同花顺到东方财富的概念名称映射表。
    
    参数:
    - threshold (int): 模糊匹配的阈值，相似度超过该值才认为是匹配，默认55。
    
    返回:
    - pd.DataFrame: 包含同花顺和东方财富概念名称映射关系的 DataFrame。
    """
    # 1. 获取同花顺和东方财富的概念资金流数据
    ths_df = ak.stock_fund_flow_concept(symbol="即时")
    eastmoney_df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")

    # 提取概念名称列
    ths_concepts = ths_df['行业'].unique()
    eastmoney_concepts = eastmoney_df['名称'].unique()

    # 2. 创建映射字典
    concept_mapping = {}

    # 3. 模糊匹配同花顺的概念到东方财富的概念
    for ths_name in ths_concepts:
        match = process.extractOne(ths_name, eastmoney_concepts, scorer=process.fuzz.ratio)
        if match and match[1] >= threshold:  # 设置匹配阈值
            concept_mapping[ths_name] = match[0]

    # 4. 转换为 DataFrame
    mapping_df = pd.DataFrame(list(concept_mapping.items()), columns=["同花顺概念名称", "东方财富概念名称"])
    
    return mapping_df


def get_eastmoney_concept_name(ths_concept_name):
    """
    根据同花顺的概念名称查询映射的东方财富概念名称。
    
    参数:
    - ths_concept_name (str): 同花顺的概念名称。
    - mapping_df (pd.DataFrame): 同花顺到东方财富的概念名称映射表。
    
    返回:
    - str: 东方财富的概念名称，如果未找到匹配则返回 None。
    """

    mapping_df = load_concept_name_mapping(55)
    
    result = mapping_df[mapping_df["同花顺概念名称"] == ths_concept_name]["东方财富概念名称"]
    if not result.empty:
        return result.values[0]  # 返回匹配的东方财富概念名称
    else:
        return None  # 未找到匹配概念