import yfinance as yf
import matplotlib.pyplot as plt

def plot_pivot_analysis(ticker_symbol):
    # 1. 데이터 수집 (최근 30일치로 추세 확인)
    df = yf.Ticker(ticker_symbol).history(period="30d")
    
    # 2. 피봇 포인트 계산 (전일 고, 저, 종가 기준)
    yesterday = df.iloc[-2]
    high, low, close = yesterday['High'], yesterday['Low'], yesterday['Close']
    
    pivot = (high + low + close) / 3
    r2 = pivot + (high - low)
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    
    # 3. 결과 출력
    print(f"--- {ticker_symbol} 단기 지지/저항선 ---")
    print(f"2차 저항선 (R2): {r2:,.0f}원/달러")
    print(f"1차 저항선 (R1): {r1:,.0f}원/달러")
    print(f"피봇 기준점 (P): {pivot:,.0f}원/달러")
    print(f"1차 지지선 (S1): {s1:,.0f}원/달러")
    print(f"2차 지지선 (S2): {s2:,.0f}원/달러")
    
    # 4. 그래프 시각화
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Price', color='black', alpha=0.6)
    
    levels = {'R2': r2, 'R1': r1, 'P': pivot, 'S1': s1, 'S2': s2}
    colors = {'R2': 'red', 'R1': 'salmon', 'P': 'orange', 'S1': 'skyblue', 'S2': 'blue'}
    
    for name, val in levels.items():
        plt.axhline(y=val, color=colors[name], linestyle='--', alpha=0.7, label=f'{name}: {val:,.0f}')
        
    plt.title(f"{ticker_symbol} Short-term Pivot Analysis")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.show()

# 실행
plot_pivot_analysis("AAPL")