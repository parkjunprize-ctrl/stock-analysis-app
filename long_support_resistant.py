import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

# 1. 데이터 수집
ticker = "NVDA" 
df = yf.Ticker(ticker).history(period="1y")
df = df.reset_index()


# 2. 지표 계산
df['ma_50'] = df['Close'].rolling(window=50).mean()
df['std_50'] = df['Close'].rolling(window=50).std()
df = df.dropna()

# 3. 내일 주가 예측 (MLP 학습)
df['target'] = df['Close'].shift(-1)
training_df = df.dropna().copy()
X = training_df[['Close', 'Volume', 'ma_50']]
y = training_df['target']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, random_state=42).fit(X_scaled, y)

next_day_pred = model.predict(X_scaled[-1].reshape(1, -1))[0]
next_date = training_df['Date'].iloc[-1] + pd.Timedelta(days=1)

# 4. 지지/저항선 값 계산
ma = training_df['ma_50'].iloc[-1]
std = training_df['std_50'].iloc[-1]
levels = {"R2": ma + (std * 2), "R1": ma + std, "MA50": ma, "S1": ma - std, "S2": ma - (std * 2)}

# 5. 그래프 그리기
plt.figure(figsize=(14, 7))
plt.plot(training_df['Date'], training_df['Close'], label='Actual Price', color='black', alpha=0.3)

# 지지/저항선 가로선
colors = {'R2': 'red', 'R1': 'salmon', 'MA50': 'orange', 'S1': 'skyblue', 'S2': 'blue'}
for name, val in levels.items():
    plt.axhline(y=val, color=colors[name], linestyle='--', alpha=0.6, label=f'{name}: {val:.2f}')

# 내일 예측값
plt.scatter(next_date, next_day_pred, color='red', s=200, zorder=10, label='Tomorrow Pred')
plt.text(next_date, next_day_pred, f' {next_day_pred:.2f}', fontsize=12, fontweight='bold')

plt.title(f"{ticker} Technical Analysis: Prediction & Support/Resistance")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()

# 6. 결과값 텍스트 출력
print(f"--- {ticker} 분석 결과 ---")
print(f"내일 예측 주가: {next_day_pred:.2f} 달러")
print("-" * 20)
for name, val in levels.items():
    print(f"{name}: {val:.2f}")