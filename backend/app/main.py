import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from indicators.buffettIndicator import merge_buffett_indicator
from indicators.buffettIndicator import periodic_buffett_index
from indicators.macroIndicators import get_data_from_cache_or_api
from indicators.fundFlow import analyze_market_fund_indicator
from indicators.fundFlow import get_today_area_head_stocks
from indicators.stockFinance import get_stock_history, get_stock_roe_history, get_stock_cyq_data,analyze_stock_discreteness
from indicators.estFundFlow import calculate_rt_top_bottom_five
from indicators.stockFundFlow import get_stock_fund_flow
from indicators.stockshares import get_top_10_shareholders
from indicators.estFundFlow import calculate_top_bottom_five
from indicators.estFundFlow import calculate_sector_all
from indicators.estFundFlow import load_sector_fund_flow_history
from indicators.beatChart import AUDIO_FILES_DIR
from indicators.beatChart import scan_audio_files
from indicators.beatChart import extract_beat_times
from indicators.akCommon import getAMarketStocks
from indicators.akCommon import getStockBasic
from indicators.stockTrades import get_stock_minute_trades
from indicators.stockStatistic import stock_statistic
from indicators.stockStatistic import get_might_sideways_stocks
from indicators.marketReport import fetch_all_data
import os


app = FastAPI()

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以指定特定的域名，或使用 ["*"] 来允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有的 HTTP 方法（如 GET, POST 等）
    allow_headers=["*"],  # 允许所有的 HTTP 请求头
)


# 使用通用方法获取不同指标的数据
@app.get("/api/cache/{indicator}")
def get_indicator_data(indicator: str):
    return get_data_from_cache_or_api(indicator)


# 获取巴菲特指标
@app.get("/api/buffett-indicator")
def get_buffett_indicator():
    data = merge_buffett_indicator()
    return data

# 获取巴菲特指标
@app.get("/api/buffett-indicator-p")
def get_buffett_indicator_p(periodic:int):
    data = periodic_buffett_index(periodic)
    return data

# 获取资金流
@app.get("/api/market-fund-flow")
def get_fund_flow():
    result = analyze_market_fund_indicator()
    return result

# 获取资金流
@app.get("/api/sector-fund-flow-all")
def get_fund_flow_all(sector_type: str):
    result = calculate_sector_all(sector_type)
    return result

# 获取资金流
@app.get("/api/sector-fund-flow")
def get_fund_flow(sector_type: str):
    result = calculate_top_bottom_five(sector_type)
    return result

# 获取资金流
@app.get("/api/sector-fund-flow-rt")
def get_fund_flow(sector_type: str):
    result = calculate_rt_top_bottom_five(sector_type)
    return result

# 获取历史行情
@app.get("/api/sector-fund-flow-his")
def get_fund_flow(sector_type: str,symbol:str):
    result = load_sector_fund_flow_history(sector_type,symbol)
    return result


# 获取板块龙头股
@app.get("/api/head-stocks")
def get_head_stocks(sector_type: str, symbol: str):
    top_stocks = get_today_area_head_stocks(sector_type, symbol)
    return top_stocks


# 获取股票历史行情
@app.get("/api/stock/history")
def stock_history(symbol: str, period: str = "daily", adjust: str = ""):
    history = get_stock_history(symbol,period)
    return history

# 获取筹码是否盘整
@app.get("/api/stock/sideways")
def stock_chips_sideways(symbol: str):
    try:
        # 调用分析函数
        result = analyze_stock_discreteness(symbol)
        
        # 返回 JSON 响应
        return JSONResponse(content=result)
    except Exception as e:
        # 捕获异常并返回错误信息
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    
    
@app.get("/api/stock-sw")
def stock_might_sideways_stocks():
    try:
        # 调用分析函数
        result = get_might_sideways_stocks()
        
        # 返回 JSON 响应
        return JSONResponse(content=result)
    except Exception as e:
        # 捕获异常并返回错误信息
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    
# 获取筹码分布
@app.get("/api/stock/chips")
def stock_chips(symbol: str):
    result = get_stock_cyq_data(symbol)
    return result


# 获取股票ROE数据
@app.get("/api/stock/roe")
def stock_roe(symbol: str):
    roe = get_stock_roe_history(symbol)
    return roe


# 获取资金流向
@app.get("/api/stock/flow")
def stock_flow(symbol: str):
    flow = get_stock_fund_flow(symbol)
    return flow


# 获取十大股东信息
@app.get("/api/stock/share")
def stock_share(symbol: str):
    shares = get_top_10_shareholders(symbol)
    return shares

# 获取财经新闻
# @app.get("/api/news")
# def stock_share():
#     shares = analyze_news_sentiment()
#     return shares 

@app.get("/api/get_audio_files/")
async def get_audio_files():
    audio_files = scan_audio_files()
    return JSONResponse(content=audio_files)

@app.get("/api/getBeatTimes/")
async def get_visualization_data(audio_file_name: str):
    audio_file_path = os.path.join(AUDIO_FILES_DIR, audio_file_name)
    if not os.path.exists(audio_file_path):
        raise JSONResponse(content={"当前不存在任何mp3文件"}, status_code=500)

    try:
        # 提取节拍数据
        beatTimes = extract_beat_times(audio_file_path)
        # 返回数据
        response_data = {
            "beatTimes": beatTimes
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 提供音频文件的静态访问


app.mount("/audio_files", StaticFiles(directory=AUDIO_FILES_DIR), name="audio_files")

@app.get("/api/stock-a")
async def get_a_stock_info():
    """
    获取所有 A 股股票的名称与代码
    """
    try:
        # 获取数据
        stock_info = getAMarketStocks()
        # 转换为字典格式返回
        result = stock_info.to_dict(orient="records")
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
    
@app.get("/api/stock-info/{stock_code}")
async def get_stock_info(stock_code: str):
    """
    获取指定股票的基本信息
    """
    try:
        # 调用 akshare 接口获取数据
        stock_info = getStockBasic(stock_code)
        
        # 如果返回数据为空，返回 404 错误
        if stock_info.empty:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Stock not found"}
            )
        
        # 转换数据为 JSON 格式
        result = stock_info.to_dict(orient="records")
        
        # 返回成功的 JSON 响应
        return JSONResponse(
            status_code=200,
            content={"status": "success", "data": result}
        )
    except Exception as e:
        # 返回错误信息
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/stock-mt/{stock_code}")
async def get_stock_m_trades(stock_code: str):
    """
    获取指定股票的基本信息
    """
    try:
        # 调用 akshare 接口获取数据
        mt = get_stock_minute_trades(stock_code)
        
        # 如果返回的数据中没有 'minuteTrade' 或其为空，返回 404 错误
        if not mt.get("minuteTrade") or len(mt["minuteTrade"]) == 0:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Stock not found"}
            )
        
        # 返回成功的 JSON 响应
        return JSONResponse(
            status_code=200,
            content = mt
        )
    except Exception as e:
        # 返回错误信息
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/api/stock-sts")
async def get_stock_sts():
    """
    返回股票统计数据的接口
    """
    try:
        # 调用 stock_statistic 函数
        result = stock_statistic()
        # 将 DataFrame 转换为字典以支持 JSON 序列化
        result["筛选结果"]["前60家"] = result["筛选结果"]["前60家"].to_dict(orient="records")
        result["筛选结果"]["中间60家"] = result["筛选结果"]["中间60家"].to_dict(orient="records")
        result["筛选结果"]["后60家"] = result["筛选结果"]["后60家"].to_dict(orient="records")

        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

        

@app.get("/api/report-data")
async def get_all_data():
    """
    获取所有整合数据，并以 JSON 格式返回。
    """
    try:
        all_data = fetch_all_data()  # 调用数据获取函数
        return JSONResponse(content=all_data)  # 返回 JSON 格式的响应
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    