from indicators.macroIndicators import load_indicators
from app.main import app
import uvicorn
import threading

def load_indicators_async():
    """异步加载指标数据，避免阻塞启动"""
    try:
        load_indicators()
        print("指标数据加载完成")
    except Exception as e:
        print(f"指标数据加载失败: {e}")

if __name__ == "__main__":
    # 在后台线程中加载指标数据
    loader_thread = threading.Thread(target=load_indicators_async, daemon=True)
    loader_thread.start()
    
    # 立即启动服务
    uvicorn.run(app, host="127.0.0.1", port=8088) 