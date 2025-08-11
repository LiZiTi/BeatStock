from indicators.macroIndicators import load_indicators
from app.main import app
import uvicorn

if __name__ == "__main__":
    load_indicators()

    uvicorn.run(app, host="127.0.0.1", port=8088) 