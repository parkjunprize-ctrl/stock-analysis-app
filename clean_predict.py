import yfinance as yf
import pandas as pd
import pandas_ta as ta
from prophet import Prophet
import matplotlib.pyplot as plt

# 1. 데이터 수집
ticker = "AAPL"
df = yf.Ticker(ticker).history(period="6mo") # MA_20 계산을 위해 기간을 6개월로 늘림
df = df.reset_index()

# 컬럼명 통일
if 'Date' in df.columns: df = df.rename(columns={'Date': 'ds', 'Close': 'y'})
elif 'Datetime' in df.columns: df = df.rename(columns={'Datetime': 'ds', 'Close': 'y'})
else: df = df.iloc[:, [0, 4]]; df.columns = ['ds', 'y']

df['ds'] = df['ds'].dt.tz_localize(None)

# 2. 기술적 지표 추가
# RSI 계산
df['rsi'] = ta.rsi(df['y'], length=14)
# 20일 이동평균(MA_20) 계산
df['ma_20'] = df['y'].rolling(window=20).mean()

# NaN 값 제거 (지표 계산으로 생기는 앞부분 데이터 제거)
df = df.dropna()

# 3. 모델 학습
model = Prophet(changepoint_prior_scale=1.0, daily_seasonality=False)
model.add_regressor('rsi')
# 이동평균도 학습 변수로 추가할 수 있습니다 (필요 시 주석 해제)
# model.add_regressor('ma_20') 
model.fit(df)

# 4. 예측
future = model.make_future_dataframe(periods=7, freq='B')
future['rsi'] = df['rsi'].iloc[-1]
# future['ma_20'] = df['ma_20'].iloc[-1] # MA_20도 넣는다면 활성화
forecast = model.predict(future)

# 5. 결과 시각화
plt.figure(figsize=(12, 6))
plt.plot(df['ds'], df['y'], label='Actual Price', alpha=0.5)
plt.plot(df['ds'], df['ma_20'], label='MA_20 (Moving Average)', color='orange', linestyle='-')
plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', color='red', linestyle='--')
plt.title(f"{ticker} Price with MA_20 and Prediction")
plt.legend()
plt.grid(True)
plt.show()