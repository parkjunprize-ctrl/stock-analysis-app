from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta

app = Flask(__name__)

def get_analysis_data(ticker, period):
    interval = "1h" if period == "5d" else "1d"
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    
    if df is None or df.empty:
        return None, None
        
    current = df['Close'].iloc[-1]
    
    # 지지/저항 계산
    r2 = df['High'].rolling(60).max().iloc[-1]
    r1 = df['High'].rolling(20).max().iloc[-1]
    vwap = (df['Close'] * df['Volume']).sum() / df['Volume'].sum()
    s1 = df['Low'].rolling(20).min().iloc[-1]
    s2 = df['Low'].rolling(60).min().iloc[-1]
    
    # 매매 전략 로직
    signal = ""
    if current <= s1 * 1.01: # 1차 지지선 근처
        signal = "매수 고려 (1차 지지선 반등 확인)"
    elif current >= r1 * 0.99: # 1차 저항선 근처
        signal = "매도 고려 (1차 저항선 돌파 실패 시)"
    else:
        signal = "관망 (추세 확인 중)"

    levels = {
        "2차 저항(R2)": r2, "1차 저항(R1)": r1,
        "VWAP": vwap, "1차 지지(S1)": s1, "2차 지지(S2)": s2,
        "매매전략": signal
    }
    return df, levels
def get_chart_html(df, levels, ticker):
    fig = go.Figure()
    
    # x축을 보기 좋게 문자열로 변환
    df.index_str = df.index.strftime('%m-%d %H:%M')
    
    fig.add_trace(go.Scatter(x=df.index_str, y=df['Close'], name='Price', line=dict(color='black')))
    
    # 선 색상 설정
    colors = {
        "2차 저항(R2)": 'red', "1차 저항(R1)": 'salmon', 
        "VWAP(중요선)": 'purple', "1차 지지(S1)": 'skyblue', "2차 지지(S2)": 'blue'
    }
    
    for name, value in levels.items():
        fig.add_hline(y=value, line_dash="dash", line_color=colors[name], 
                      annotation_text=f"{name}: {value:,.0f}")

    fig.update_layout(
        title=f"{ticker} 분석 (VWAP 및 지지/저항)",
        hovermode='x unified', height=500, dragmode='pan',
        plot_bgcolor='white',
        xaxis=dict(type='category', showgrid=True, gridcolor='lightgray')
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/', methods=['GET', 'POST'])
def index():
    ticker = request.form.get('ticker', 'AAPL')
    period = request.form.get('period', '3mo')
    data, chart = None, None
    if request.method == 'POST':
        df, levels = get_analysis_data(ticker, period)
        if df is not None:
            data = {k: f"{v:,.0f}" for k, v in levels.items()}
            chart = get_chart_html(df, levels, ticker)
    return render_template('index.html', data=data, chart=chart, current_period=period)

if __name__ == '__main__':
    app.run()