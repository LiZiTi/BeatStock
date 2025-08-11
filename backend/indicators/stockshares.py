import akshare as ak
from indicators.common import repair_dataframe_data
from datetime import datetime
from config.cached_akshare_request import cached_akshare_request


def get_current_financial_year():
    now = datetime.now()
    if now.month > 3:
        return now.year
    else:
        return now.year - 5

@cached_akshare_request
def get_top_10_shareholders(stock_code):

    # 根据股票代码的开头添加前缀 "sh" 或 "sz"
    if stock_code.startswith("6"):
        symbol = f"sh{stock_code}"
    elif stock_code.startswith("0") or stock_code.startswith("3"):
        symbol = f"sz{stock_code}"
    elif stock_code.startswith("8"):
        symbol = f"bj{stock_code}"
    else:
        symbol = stock_code  # 如果是其他情况，保持原样

    year = get_current_financial_year()

    def get_latest_financial_report_date():
        quarter_dates = [f"{year}0331", f"{year}0630", f"{year}0930", f"{year}1231"]
        for date in quarter_dates[::-1]:
            try:
                sdf = ak.stock_gdfx_free_top_10_em(symbol=symbol, date=date)
                if not sdf.empty:
                    return date, sdf
            except:
                continue
        return None

    rd,df = get_latest_financial_report_date()
    df= repair_dataframe_data(df)
    return {
        '日期':rd,
        '股东':df.to_dict(orient='records')
    }
