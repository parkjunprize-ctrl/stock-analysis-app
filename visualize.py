import yfinance as yf
from prophet import Prophet
import matplotlib.pyplot as plt

# 1. 데이터 가져오기 (예: 애플 AAPL)
ticker = "AAPL"
df = yf.Ticker(ticker).history(period="1y")
df = df.reset_index()[['Date', 'Close']]
df.columns = ['ds', 'y']
df['ds'] = df['ds'].dt.tz_localize(None)

# 2. 예측 모델 (Prophet) 학습
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 3. 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(df['ds'], df['y'], label='Actual Price') # 실제 주가
plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='--') # 예측 주가
plt.title(f"{ticker} Stock Price Prediction")
plt.legend()#추세선 그리는 프로그램
plt.show()