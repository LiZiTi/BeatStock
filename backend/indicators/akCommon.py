import akshare as ak
from config.cached_akshare_request import cached_akshare_request

@cached_akshare_request
def getAMarketStocks():
    stock_info = ak.stock_info_a_code_name()
    return stock_info

@cached_akshare_request
def getStockBasic(symbol:str):
    stock_info = ak.stock_individual_info_em(symbol)
    return stock_info

def getStockCodeWithFlag(stock_code:str):
    symbol = ""
    if stock_code.startswith("6"):
        symbol = f"sh{stock_code}"
    elif stock_code.startswith("0") or stock_code.startswith("3"):
        symbol = f"sz{stock_code}"
    elif stock_code.startswith("8"):
        symbol = f"bj{stock_code}"
    else:
        symbol = stock_code 
    return symbol