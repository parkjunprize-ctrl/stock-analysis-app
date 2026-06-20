import yfinance as yf
import pandas as pd
import pandas_ta as ta
from prophet import Prophet
import matplotlib.pyplot as plt

# 1. 데이터 수집
ticker = "IBM"
df = yf.Ticker(ticker).history(period="1y")
df = df.reset_index()[['Date', 'Close']]
df.columns = ['ds', 'y']
df['ds'] = df['ds'].dt.tz_localize(None)

# 2. 기술적 지표 추가 (RSI: 과열/침체 판단)
df['rsi'] = ta.rsi(df['y'], length=14)
df = df.fillna(0) # 데이터가 없는 시작 부분은 0으로 채움

# 3. 모델 학습 (추세 + RSI 변수)
model = Prophet()
model.add_regressor('rsi')
model.fit(df)

# 4. 미래 30일 예측
future = model.make_future_dataframe(periods=30)
future['rsi'] = 50 # 미래의 RSI는 중간값인 50으로 가정
forecast = model.predict(future)

# 5. 결과 시각화
plt.figure(figsize=(12, 6))
plt.plot(df['ds'], df['y'], label='Actual Price (Historical)')
plt.plot(forecast['ds'], forecast['yhat'], label='Forecast with RSI', linestyle='--')
plt.title(f"{ticker} Stock Price Prediction (Trend + RSI)")
plt.legend()
plt.grid(True)
plt.show()