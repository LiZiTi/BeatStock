import pandas as pd
from config.cached_akshare_request import cached_akshare_request
import akshare as ak
from indicators.akCommon import getStockCodeWithFlag
from indicators.common import convert_value

@cached_akshare_request
def get_stock_minute_trades(symbol: str):
    """
    将秒级交易数据聚合到分钟级别，并计算总成交量、总成交额、总主动买入量、总主动买入额、总主动卖出量、总主动卖出额。
    
    :param symbol: 股票代码
    :return: 一个包含多个字段的字典，包含：
             - minuteTrade: 包含按分钟聚合的实时交易数据
             - totalVolume: 总成交量
             - totalAmount: 总成交额
             - totalBuyVolume: 总主动买入量
             - totalBuyAmount: 总主动买入额
             - totalSellVolume: 总主动卖出量
             - totalSellAmount: 总主动卖出额
    """
    
    # 获取数据
    symbol = getStockCodeWithFlag(symbol)
    data = ak.stock_zh_a_tick_tx_js(symbol)
    
    # 确保时间列转换为标准时间格式
    data['成交时间'] = pd.to_datetime(data['成交时间'], format='%H:%M:%S')

    # 提取分钟级时间戳
    data['分钟时间'] = data['成交时间'].dt.strftime('%H:%M')

    # 计算汇总指标
    total_volume = data['成交量'].sum()  # 总成交量
    total_amount = data['成交金额'].sum()  # 总成交额

    # 计算买盘、卖盘和中性盘的各项指标
    total_buy_volume = data[data['性质'] == '买盘']['成交量'].sum()  # 总主动买入量
    total_buy_amount = data[data['性质'] == '买盘']['成交金额'].sum()  # 总主动买入额

    total_sell_volume = data[data['性质'] == '卖盘']['成交量'].sum()  # 总主动卖出量
    total_sell_amount = data[data['性质'] == '卖盘']['成交金额'].sum()  # 总主动卖出额

    total_neutral_volume = data[data['性质'] == '中性盘']['成交量'].sum()  # 中性盘成交量
    total_neutral_amount = data[data['性质'] == '中性盘']['成交金额'].sum()  # 中性盘成交额

    # 按分钟时间分组聚合
    aggregated = data.groupby('分钟时间').apply(
        lambda group: pd.Series({
            '成交价格': group.iloc[-1]['成交价格'],  # 取最后一笔交易的价格
            '成交量': group['成交量'].sum(),         # 分钟内的总成交量
            '成交额': (group['成交价格'] * group['成交量']).sum(),  # 总成交额
            '主动买入量': group[group['性质'] == '买盘']['成交量'].sum(),  # 主动买入量
            '主动买入额': (group[group['性质'] == '买盘']['成交价格'] * group[group['性质'] == '买盘']['成交量']).sum(),  # 主动买入额
            '主动卖出量': group[group['性质'] == '卖盘']['成交量'].sum(),  # 主动卖出量
            '主动卖出额': (group[group['性质'] == '卖盘']['成交价格'] * group[group['性质'] == '卖盘']['成交量']).sum(),  # 主动卖出额
            '性质': '买盘' if group[group['性质'] == '买盘']['成交量'].sum() >=
                         group[group['性质'] == '卖盘']['成交量'].sum() else '卖盘'  # 判断性质
        })
    ).reset_index()

    # 返回最终的JSON格式数据
    result = {
        "minuteTrade": aggregated.to_dict(orient='records'),
        "totalVolume": convert_value(total_volume),
        "totalAmount": convert_value(total_amount),
        "totalBuyVolume": convert_value(total_buy_volume),
        "totalBuyAmount": convert_value(total_buy_amount),
        "totalSellVolume": convert_value(total_sell_volume),
        "totalSellAmount": convert_value(total_sell_amount),
        "totalNaturalVolume":convert_value(total_neutral_volume),
        "totalNaturalAmount":convert_value(total_neutral_amount),
    }
    
    return result
