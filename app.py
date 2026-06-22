import os
from flask import Flask, render_template, request
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from scipy.signal import argrelextrema

app = Flask(__name__)
API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', 'UITBLFWQX5DDBTXF')

def get_analysis(ticker):
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    hist, _ = ts.get_daily(symbol=ticker, outputsize='compact')
    hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # 지지/저항선 계산 로직 (기존 코드와 동일)
    order = 3
    max_idx = argrelextrema(hist['High'].values, np.greater_equal, order=order)[0]
    min_idx = argrelextrema(hist['Low'].values, np.less_equal, order=order)[0]
    
    recent_max = sorted(list(set(hist['High'].iloc[max_idx].values)), reverse=True)
    recent_min = sorted(list(set(hist['Low'].iloc[min_idx].values)))
    
    if len(recent_max) < 2 or len(recent_min) < 2: return hist, None

    r2, r1 = recent_max[0], recent_max[1]
    s1, s2 = recent_min[1], recent_min[0]
    
    levels = {
        "2차 매도": f"${r1 * 0.99:.2f}", "1차 매도": f"${r2 * 0.99:.2f}",
        "1차 매수": f"${s1 * 1.01:.2f}", "2차 매수": f"${s2 * 1.01:.2f}",
        "2차 저항": f"${r2:.2f}", "1차 저항": f"${r1:.2f}",
        "1차 지지": f"${s1:.2f}", "2차 지지": f"${s2:.2f}"
    }
    return hist, levels

@app.route('/', methods=['GET', 'POST'])
def index():
    ticker = request.form.get('ticker', 'AAPL')
    levels, chart_html = None, None
    
    if request.method == 'POST':
        try:
            hist, levels = get_analysis(ticker)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Price'))
            
            # 지지/저항선 차트 표시
            if levels:
                for name, val in levels.items():
                    if '저항' in name or '지지' in name:
                        fig.add_hline(y=float(val.replace('$','')), line_dash="dash", annotation_text=name)
            chart_html = pio.to_html(fig, full_html=False)
        except Exception as e:
            print(f"에러: {e}")
            
    return render_template('index.html', data=levels, chart=chart_html, ticker=ticker)

if __name__ == '__main__':
    app.run()