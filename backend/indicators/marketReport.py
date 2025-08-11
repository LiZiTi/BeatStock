from indicators.common import NP2Dict
from indicators.common import convert_value
import pandas as pd
import akshare as ak
import numpy as np
from config.cached_akshare_request import cached_akshare_request
import json
import os
from pathlib import Path
import random

@cached_akshare_request
def get_cpi_data():
    """
    获取中国 CPI 月率报告，返回最近一条非 NaN 的数据。

    Returns:
        dict: 包含日期和 CPI 值的字典。
    """
    # 获取中国 CPI 月率数据
    df = ak.macro_china_cpi_monthly()
    
    # 筛选出今值不为 NaN 的记录
    filtered_df = df[df['今值'].notna()]
    
    # 提取最近一条记录
    lr = filtered_df.tail(1)
    
    # 返回字典
    return {
        "CPI": NP2Dict(lr)
    }

# 获取 LPR 品种数据
@cached_akshare_request
def get_lpr_data():
    lpr_data = ak.macro_china_lpr()
    lr = lpr_data.tail(1)
    return {
        "LPR":NP2Dict(lr)
    }

# 获取宏观经济杠杆率
@cached_akshare_request
def get_macro_leverage_data():

    # 获取宏观杠杆率数据
    macro_leverage_data = ak.macro_cnbs()
    
    # 提取最近一条数据
    lr = macro_leverage_data.tail(1)
    return {
        "宏观杠杆率":NP2Dict(lr)
    }

# 获取上证实时行情
@cached_akshare_request
def get_stock_zh_real_time():
    stock_zh_index_spot_em_df = ak.stock_zh_index_spot_em(symbol="上证系列指数")
    filtered_df = stock_zh_index_spot_em_df[stock_zh_index_spot_em_df['代码'] == "000001"]
    return {
        "上证行情":NP2Dict(filtered_df)
    }

# 获取经典巴菲特指标
@cached_akshare_request
def get_class_buffet_indice():
    buffett_data = ak.stock_buffett_index_lg()
    lr = buffett_data.tail(1)
    return {
        "巴菲特指标": NP2Dict(lr)
    }

# 获取当日总成交额
# @cached_akshare_request
def get_market_total_amount():
    df = ak.stock_zh_a_spot_em()
    total_amount = df['成交额'].sum()
    return {
        "市场总成交金额":total_amount
    } 

# 获取市场资金流
@cached_akshare_request
def get_market_fund_flow():
    stock_market_fund_flow_df = ak.stock_market_fund_flow()
    stock_market_fund_flow_df['日期'] = pd.to_datetime(stock_market_fund_flow_df['日期']).dt.strftime('%Y-%m-%d')
    lr = stock_market_fund_flow_df.tail(1)
    return {
        "报告日期":lr['日期'].values[0],
        "市场资金流": NP2Dict(lr)
    }

# 统计股票数据
@cached_akshare_request
def fetch_stock_data():
    """
    统计股票涨跌幅的分布情况，并返回符合需求的字典格式。

    Returns:
        dict: 各涨跌幅区间的统计及上涨、平盘、下跌家数。
    """
    # 获取股票数据
    stock_data = ak.stock_zh_a_spot_em()

    # 确保涨跌幅为浮点类型，并排除 NaN 数据
    stock_data['涨跌幅'] = pd.to_numeric(stock_data['涨跌幅'], errors='coerce')
    stock_data = stock_data.dropna(subset=['涨跌幅'])

    # 自定义涨跌幅区间
    bins = [-float('inf'), -10, -5, -2, 2, 5, 10, float('inf')]  # 自定义区间
    labels = [
        '跌幅超过-10%',
        '跌幅-10%到-5%',
        '跌幅-5%到-2%',
        '震荡-2%到2%',
        '涨幅2%到5%',
        '涨幅5%到10%',
        '涨幅超过10%',
    ]

    # 使用 pd.cut 对涨跌幅进行分组统计
    stock_data['涨跌幅区间'] = pd.cut(stock_data['涨跌幅'], bins=bins, labels=labels, right=False)

    # 统计各区间股票数量，确保返回所有区间
    range_counts = stock_data['涨跌幅区间'].value_counts().reindex(labels, fill_value=0)

    # 将区间标签与数量一起打包为字典
    range_dict = {label: convert_value(range_counts[label]) for label in labels}

    # 统计上涨、平盘、下跌家数
    up_count = stock_data[stock_data['涨跌幅'] > 0].shape[0]
    flat_count = stock_data[stock_data['涨跌幅'] == 0].shape[0]
    down_count = stock_data[stock_data['涨跌幅'] < 0].shape[0]

    # 构建最终返回字典
    result = {
        "股票涨跌分布": range_dict,  # 现在是带有标签的涨跌区间分布
        "股票上涨家数": up_count,
        "股票平盘家数": flat_count,
        "股票下跌家数": down_count,
    }

    return result

@cached_akshare_request
def get_section_fund_flow():
    """
    获取行业和概念板块资金流入的前五名和后五名，排除无效数据（主力净流入为空或 NaN），
    并直接返回行业资金前三、行业资金后三、概念资金前三、概念资金后三。

    Returns:
        dict: 包含行业和概念板块资金流的详细排名及详细信息。
    """
    # 获取行业和概念板块资金流数据
    df_hy = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
    df_gn = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")

    # 排除无效数据（主力净流入为空或 NaN）
    df_hy = df_hy[df_hy['今日主力净流入-净额'].notna() & (df_hy['今日主力净流入-净额'] != "")]
    df_gn = df_gn[df_gn['今日主力净流入-净额'].notna() & (df_gn['今日主力净流入-净额'] != "")]

    total_amount = round(df_hy['今日主力净流入-净额'].sum()/1e8,2)

    # 提取行业和概念前五名和后五名
    hy_top = df_hy.head(3)
    hy_bottom = df_hy.tail(3)[::-1]  # 反转后五名
    gn_top = df_gn.head(3)
    gn_bottom = df_gn.tail(3)[::-1]  # 反转后五名

    # 构建最终返回字典
    result = {
        "行业资金前三": NP2Dict(hy_top),
        "行业资金后三": NP2Dict(hy_bottom),
        "概念资金前三": NP2Dict(gn_top),
        "概念资金后三": NP2Dict(gn_bottom),
        "实时主力净流入":total_amount
    }

    return result

    

def get_user_data_directory():
    """
    根据操作系统获取用户的文档目录，默认写入当前用户的系统文件夹。

    Returns:
        str: 当前用户的文档目录路径。
    """
    home = Path.home()
    if os.name == 'nt':  # Windows
        return home / "Documents" / "ElonMarketData"
    elif os.name == 'posix':  # macOS / Linux
        return home / "Documents" / "ElonMarketData"
    else:
        return home / "ElonMarketData"  # 默认路径

def fetch_all_data():
    """
    整合所有数据获取函数，返回一个包含所有键值对的单层大字典。
    并将数据以 JSON 格式写入用户文档目录，文件名为 'market_data_报告日期.json'。
    
    Returns:
        dict: 包含多个数据来源的整合字典，所有键值对为平铺结构，值为基本数据类型。
    """
    try:
        all_data = {}
        functions = [
            get_cpi_data,
            get_lpr_data,
            get_macro_leverage_data,
            get_stock_zh_real_time,
            get_class_buffet_indice,
            get_market_total_amount,
            get_market_fund_flow,
            fetch_stock_data,
            get_section_fund_flow,
        ]

        for func in functions:
            result = {key:value for key, value in func().items()}
            all_data.update(result)

        all_data.update({"投资名言":generate_investment_advice()})
        # 提取报告日期
        report_date = all_data.get("报告日期", "unknown_date")

        # 动态获取用户文档目录
        user_data_directory = get_user_data_directory()
        os.makedirs(user_data_directory, exist_ok=True)  # 确保目录存在

        # 生成文件名
        file_path = user_data_directory / f"market-data_{report_date}.json"

        # 将数据写入到 JSON 文件中，覆盖写入
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)

        print(f"数据已写入文件: {file_path}")

        return all_data

    except Exception as e:
        return {"error": str(e)}
    
def generate_investment_advice():
    investment_quotes = [
        "投资最重要的原则是分散风险。\r\n 彼得·林奇",
        "投资是把钱放在你理解的地方。\r\n 约翰·博格尔",
        "在股市中，贪婪与恐惧常常主导决策。\r\n 本杰明·格雷厄姆",
        "成功的投资者是长期思考的。\r\n 沃伦·巴菲特",
        "市场短期是投票机，长期是称重机。\r\n 本杰明·格雷厄姆",
        "投资的最大敌人是自己。\r\n 彼得·林奇",
        "风险来自于你不知道自己在做什么。\r\n 沃伦·巴菲特",
        "在市场上赚到的钱，是保持冷静的人赚的。\r\n 约翰·博格尔",
        "真正的投资机会，往往是市场的恐慌时刻。\r\n 沃伦·巴菲特",
        "保持耐心，市场会奖励耐心的人。\r\n 约翰·博格尔",
        "你不必每天都赚很多钱，重要的是保持稳定。\r\n 彼得·林奇",
        "投资的秘诀是永远不亏损。\r\n 乔治·索罗斯",
        "优秀的投资者不仅是做出正确选择，而是能把握时机。\r\n 本杰明·格雷厄姆",
        "贪婪时要小心，恐惧时要大胆。\r\n 沃伦·巴菲特",
        "做投资，要有耐心，要有纪律。\r\n 彼得·林奇",
        "投资的关键是理解公司，而不是市场。\r\n 查尔斯·芒格",
        "价值投资就是买入你了解的公司，长期持有。\r\n 沃伦·巴菲特",
        "把所有鸡蛋放在同一个篮子里，但要小心持稳它。\r\n 安德鲁·卡内基",
        "买股票就像买公司，而不是买股票票。\r\n 沃伦·巴菲特",
        "不要为短期的波动而恐慌。\r\n 本杰明·格雷厄姆",
        "把未来的钱投资在能增长的地方。\r\n 约翰·博格尔",
        "投资就像种树，只有时间和耐心才能看到结果。\r\n 彼得·林奇",
        "不在乎短期的涨跌，专注长期。\r\n 沃伦·巴菲特",
        "投资的目标是通过时间的积累而获利。\r\n 本杰明·格雷厄姆",
        "不要试图预测市场，了解它的规律才是关键。\r\n 查尔斯·芒格",
        "成功的投资不仅仅是赚大钱，还是避免亏损。\r\n 乔治·索罗斯",
        "涨停板和跌停板不代表成功或失败，长期的回报才最重要。\r\n 彼得·林奇",
        "聪明的投资者是那些能从每一次失败中汲取教训的人。\r\n 沃伦·巴菲特",
        "好的投资决策来自于冷静的头脑，而不是市场的噪音。\r\n 查尔斯·芒格",
        "市场的反应是情绪化的，投资者要理性。\r\n 彼得·林奇",
        "抓住机会，而不是追逐市场。\r\n 本杰明·格雷厄姆",
        "长期来看，股市回报率总是正数。\r\n 约翰·博格尔",
        "赚钱是艰难的，保持赚钱更艰难。\r\n 彼得·林奇",
        "投资不是寻找短期利润，而是长期的成长。\r\n 沃伦·巴菲特",
        "每一个成功的投资者，背后都有长时间的积累。\r\n 查尔斯·芒格",
        "在投资上，最重要的是避免大的错误。\r\n 本杰明·格雷厄姆",
    ]

    # 从列表中随机选择一句
    return random.choice(investment_quotes)