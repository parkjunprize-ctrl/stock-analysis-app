from flask import Flask, render_template, request
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.signal import argrelextrema

app = Flask(__name__)

def get_advanced_analysis(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    if hist.empty or len(hist) < 5: return None, None # 데이터가 너무 적으면 리턴
    
    info = stock.info
    price = info.get('currentPrice') or hist['Close'].iloc[-1]
    eps = info.get('forwardEps') or 0
    fair_value = eps * 18
    
    order = 1 if period == "5d" else 3
    max_idx = argrelextrema(hist['High'].values, np.greater_equal, order=order)[0]
    min_idx = argrelextrema(hist['Low'].values, np.less_equal, order=order)[0]
    
    recent_max = sorted(list(set(hist['High'].iloc[max_idx].values)), reverse=True)
    recent_min = sorted(list(set(hist['Low'].iloc[min_idx].values)))
    
    # [핵심 수정] 데이터가 충분하지 않을 때의 방어 로직
    if len(recent_max) < 2 or len(recent_min) < 2:
        return hist, {"알림": "데이터 부족으로 지지/저항선 산출 불가"}

    r2, r1 = recent_max[0], recent_max[1]
    s1, s2 = recent_min[1], recent_min[0]
    
    buy_1 = s1 * 1.01
    buy_2 = s2 * 1.01
    sell_1 = r1 * 0.99
    sell_2 = r2 * 0.99
    
    levels = {
        "적정가": f"${fair_value:.2f}",
        "2차 매도": f"${sell_2:.2f}",
        "1차 매도": f"${sell_1:.2f}",
        "1차 매수": f"${buy_1:.2f}",
        "2차 매수": f"${buy_2:.2f}",
        "2차 저항선": f"${r2:.2f}",
        "1차 저항선": f"${r1:.2f}",
        "1차 지지선": f"${s1:.2f}",
        "2차 지지선": f"${s2:.2f}"
    }
    return hist, levels

@app.route('/', methods=['GET', 'POST'])
def index():
    ticker = request.form.get('ticker', 'AAPL')
    period = request.form.get('period', '1mo') 
    
    hist, levels = None, None
    chart_html = None
    
    if request.method == 'POST':
        try:
            # 기존 함수를 호출하되, 에러 발생 시를 대비
            hist, levels = get_advanced_analysis(ticker, period)
            
# 지지/저항선 처리 (안전하게 수정됨)
            if levels and isinstance(levels, dict):
                for name, val in levels.items():
                    if '저항' in name or '지지' in name:
                        try:
                                # 문자열에서 $ 제거 후 숫자 변환 시도
                            clean_val = str(val).replace('$', '')
                            fig.add_hline(y=float(clean_val), line_dash="dash", annotation_text=name)
                        except (ValueError, TypeError):
                                # 숫자가 아니면 그냥 넘어감 (서버가 죽지 않음)
                            continue
                chart_html = pio.to_html(fig, full_html=False)
        except Exception as e:
            print(f"DEBUG ERROR: {e}") # 로그에 에러를 찍어서 확인하게 함
            
    return render_template('index.html', data=levels, chart=chart_html, ticker=ticker)

if __name__ == '__main__':
    app.run(debug=True)