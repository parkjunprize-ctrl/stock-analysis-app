from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from prophet import Prophet

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/predict/{symbol}")
async def get_stock(symbol: str):
    # 1. 데이터 가져오기
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="1y") # 1년치 데이터로 학습
    df = history.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']
    df['ds'] = df['ds'].dt.tz_localize(None)

    # 2. 예측 모델 (Prophet) 실행
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30) # 30일 예측
    forecast = model.predict(future)

    # 3. 데이터 결합
    result = []
    for i in range(len(forecast)):
        result.append({
            "date": forecast.iloc[i]['ds'].strftime("%Y-%m-%d"),
            "actual": df.iloc[i]['y'] if i < len(df) else None,
            "forecast": forecast.iloc[i]['yhat']
        })
    return result