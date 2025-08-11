import akshare as ak
from indicators.common import repair_dataframe_data
from config.cached_akshare_request import cached_akshare_request

@cached_akshare_request
def get_stock_fund_flow(stock_code):
    # 根据股票代码的首位字符判断市场
    if stock_code.startswith('6'):
        market = 'sh'
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        market = 'sz'
    elif stock_code.startswith('8'):
        market = 'bj'
    else:
        raise ValueError("无效的股票代码，必须以6、0、3、8开头")

    # 调用 akshare 接口获取资金流向数据
    df = ak.stock_individual_fund_flow(stock=stock_code, market=market)

    # 返回获取的数据
    df = repair_dataframe_data(df)
    return df.to_dict(orient='records')