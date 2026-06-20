import os
# ... (다른 import 문들)

app = Flask(__name__)

# [테스트용 로그 강제 출력]
print("--- 서버가 시작되었습니다! ---")
from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta

app = Flask(__name__)

def get_analysis_data(ticker, period):
    # 1. 데이터 기간 및 간격 설정
    interval = "1h" if period == "5d" else "1d"
    
    # 2. 데이터 가져오기
    if period == "5d":
        start_date = datetime.now() - timedelta(days=7)
        df = yf.Ticker(ticker).history(start=start_date, interval=interval)
    else:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
    
    if df is None or df.empty:
        return None, None
        
    # 3. 계산 로직 (들여쓰기 및 변수 할당 오류 수정)
    if period != "5d":
        std_dev = df['Close'].std() 
        current_price = df['Close'].iloc[-1]
        # 증권사에서 확인한 '현재가(증권사)'와 '내 프로그램의 현재가' 차이 계산
    # 예: 증권사 가격이 75,000원인데 내 프로그램이 72,000원이라면 차액 3,000원을 더해줌
    
        
        # 계산할 때 gap을 반영
        h = (current_price + (std_dev * 0.5)) 
        l = (current_price - (std_dev * 0.5)) 
        c = current_price 
    else:
        last = df.iloc[-1]
        h, l, c = last['High'], last['Low'], last['Close']

    pivot = (h + l + c) / 3
    
    levels = {
        "R2": pivot + (h - l), "R1": (2 * pivot) - l,
        "P": pivot, "S1": (2 * pivot) - h, "S2": pivot - (h - l)
    }
    return df, levels

def get_chart_html(df, levels, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='black')))
    
    colors = {'R2': 'red', 'R1': 'salmon', 'P': 'orange', 'S1': 'skyblue', 'S2': 'blue'}
    for name, value in levels.items():
        fig.add_hline(y=value, line_dash="dash", line_color=colors[name], 
                      annotation_text=f"{name}: {value:,.0f}")

    fig.update_layout(title=f"{ticker} 분석", hovermode='x unified', height=500, dragmode='pan')
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/', methods=['GET', 'POST'])
def index():
    ticker = request.form.get('ticker', '005930.KS')
    period = request.form.get('period', '3mo')
    data, chart = None, None
    
    if request.method == 'POST':
        df, levels = get_analysis_data(ticker, period)
        if df is not None:
            data = {k: f"{v:,.0f}" for k, v in levels.items()}
            chart = get_chart_html(df, levels, ticker)
            
    return render_template('index.html', data=data, chart=chart, current_period=period)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)