import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 1. 데이터 수집
ticker = "AAPL"
df = yf.Ticker(ticker).history(period="1y")
df = df.reset_index()

# 2. 데이터 준비 및 지표 추가
df['ma_20'] = df['Close'].rolling(window=20).mean()
df = df.dropna()  # NaN 값 제거

# 3. 모델 학습 데이터셋 (training_df)
# 타겟은 다음날 종가(shift -1)이므로, 마지막 행은 예측할 타겟이 없어서 dropna()로 제거
df['target'] = df['Close'].shift(-1)
training_df = df.dropna().copy() 

features = ['Close', 'Volume', 'ma_20']
X = training_df[features]
y = training_df['target']

# 4. 스케일링
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. 신경망 모델 (MLP)
model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, random_state=42)
model.fit(X_scaled, y)

# 6. 예측값 생성 및 할당
training_df['prediction'] = model.predict(X_scaled)

# 7. 내일 예측값 계산 (가장 최근 데이터를 사용)
latest_data = X_scaled[-1].reshape(1, -1)
next_day_price = model.predict(latest_data)
next_date = training_df['Date'].iloc[-1] + pd.Timedelta(days=1)

# 8. 그래프 그리기
# 8. 그래프 그리기 (최근 1개월만 확대)
plt.figure(figsize=(12, 6))

# 마지막 30일치 데이터만 슬라이싱
recent_df = training_df.iloc[-30:]

plt.plot(recent_df['Date'], recent_df['Close'], label='Actual Price', alpha=0.6)
plt.plot(recent_df['Date'], recent_df['ma_20'], label='MA_20', color='orange')
plt.plot(recent_df['Date'], recent_df['prediction'], label='MLP Prediction', linestyle='--')

# 내일의 예측값 점 찍기 (더 크게, 눈에 띄게)
plt.scatter(next_date, next_day_price, color='red', s=200, label='Tomorrow Prediction', zorder=10)

# 내일의 가격 수치 표시 (점 옆에 텍스트)
plt.text(next_date, next_day_price, f'  {next_day_price[0]:.2f}', fontsize=12, color='red', fontweight='bold')

plt.title(f"{ticker} Recent Price & Tomorrow's Prediction")
plt.legend()
plt.grid(True)
plt.show()

print(f"내일 예측 주가: {next_day_price[0]:.2f} 달러")