from flask import Flask, render_template, request
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.signal import argrelextrema

app = Flask(__name__)

def get_advanced_analysis(ticker, period):
    stock = yf.Ticker(ticker)
    # [수정] 사용자가 선택한 period(5d, 1mo, 3mo)를 그대로 사용
    hist = stock.history(period=period)
    
    if hist.empty: return None, None
    
    # 1. 가치 평가 (기존과 동일)
    info = stock.info
    price = info.get('currentPrice') or hist['Close'].iloc[-1]
    eps = info.get('forwardEps') or 0
    fair_value = eps * 18
    
    # 2. [핵심] 기간별로 유연하게 극값 추출
    # 데이터 양에 따라 order를 조절 (5일치는 데이터가 적으니 order를 작게 설정)
    order = 1 if period == "5d" else 3
    
    max_idx = argrelextrema(hist['High'].values, np.greater_equal, order=order)[0]
    min_idx = argrelextrema(hist['Low'].values, np.less_equal, order=order)[0]
    
    # 중복 제거 및 정렬된 고점/저점 리스트
    recent_max = sorted(list(set(hist['High'].iloc[max_idx].values)), reverse=True)
    recent_min = sorted(list(set(hist['Low'].iloc[min_idx].values)))
    
    # 데이터가 적을 경우를 대비한 보정값
    # ... (데이터 가져오기 및 극값 계산 로직 이후) ...
    
    # 1. 시장 데이터 (지지/저항선)
    r2, r1 = recent_max[0], recent_max[1]
    s1, s2 = recent_min[1], recent_min[0]
    
    # 2. 전략적 매매 지점 (매수/매도 포인트)
    # 1차 매수: 1차 지지선에서 살짝 위 (반등 기대)
    # 2차 매수: 2차 지지선에서 살짝 위 (분할 매수)
    # 1차 매도: 1차 저항선에서 살짝 아래 (수익 확정)
    # 2차 매도: 2차 저항선에서 살짝 아래 (강력 익절)
    
    buy_1 = s1 * 1.01
    buy_2 = s2 * 1.01
    sell_1 = r1 * 0.99
    sell_2 = r2 * 0.99
    
    levels = {
        "적정가": f"${fair_value:.2f}",
        "--- 매매 지점 ---": "----------",
        "2차 매도": f"${sell_2:.2f}",
        "1차 매도": f"${sell_1:.2f}",
        "1차 매수": f"${buy_1:.2f}",
        "2차 매수": f"${buy_2:.2f}",
        "--- 기술적 기준선 ---": "----------",
        "2차 저항선": f"${r2:.2f}",
        "1차 저항선": f"${r1:.2f}",
        "1차 지지선": f"${s1:.2f}",
        "2차 지지선": f"${s2:.2f}"
    }
    return hist, levels

@app.route('/', methods=['GET', 'POST'])
def index():
    # 사용자가 선택한 티커와 기간을 가져옵니다. 기본값은 1mo(1달)
    ticker = request.form.get('ticker', 'AAPL')
    period = request.form.get('period', '1mo') 
    
    hist, levels = None, None
    chart_html = None
    
    if request.method == 'POST':
        hist, levels = get_advanced_analysis(ticker, period) # period 전달!
        if hist is not None:
            # 그래프 생성 로직
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Price'))
            for name, val in levels.items():
                if '저항' in name or '지지' in name:
                    fig.add_hline(y=float(val.replace('$','')), line_dash="dash", annotation_text=name)
            chart_html = pio.to_html(fig, full_html=False)
            
    return render_template('index.html', data=levels, chart=chart_html, ticker=ticker)

if __name__ == '__main__':
    app.run(debug=True)