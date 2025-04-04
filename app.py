
import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="RSI 다이버전스 정신과 트레이딩", layout="wide")
st.title("🧠 RSI 다이버전스 정신과 트레이딩")

# 📌 Sidebar: 종목, 기간 선택
ticker = st.sidebar.text_input("종목 코드 (예: 005930.KS, AAPL, PLTR)", value="005930.KS")
start_date = st.sidebar.date_input("시작일", value=datetime(2023, 1, 1))
end_date = st.sidebar.date_input("종료일", value=datetime.today())

# 📌 데이터 다운로드
data = yf.download(ticker, start=start_date, end=end_date)
if data.empty:
    st.error("데이터를 불러오지 못했습니다. 종목 코드를 확인해주세요.")
    st.stop()

data['RSI'] = ta.momentum.RSIIndicator(close=data['Close'], window=14).rsi()

# 📌 일목균형표 추가
ichimoku = ta.trend.IchimokuIndicator(high=data['High'], low=data['Low'])
data["tenkan"] = ichimoku.ichimoku_conversion_line()
data["kijun"] = ichimoku.ichimoku_base_line()

# 📌 다이버전스 찾기
def find_bullish_divergence(df):
    points = []
    for i in range(30, len(df)):
        price_now = float(df['Close'].iloc[i])
        price_prev = float(df['Close'].iloc[i-10:i].min())
        rsi_now = float(df['RSI'].iloc[i])
        rsi_prev = float(df['RSI'].iloc[i-10:i].min())
        if price_now < price_prev and rsi_now > rsi_prev:
            points.append(i)
    return points

def find_bearish_divergence(df):
    points = []
    for i in range(30, len(df)):
        price_now = float(df['Close'].iloc[i])
        price_prev = float(df['Close'].iloc[i-10:i].max())
        rsi_now = float(df['RSI'].iloc[i])
        rsi_prev = float(df['RSI'].iloc[i-10:i].max())
        if price_now > price_prev and rsi_now < rsi_prev:
            points.append(i)
    return points

bullish_points = find_bullish_divergence(data)
bearish_points = find_bearish_divergence(data)

# 📊 Plotly 시각화
fig = go.Figure()

# 캔들 차트 or 선 차트
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="종가", line=dict(color="blue")))

# 매수 시점 표시
fig.add_trace(go.Scatter(
    x=data.index[bullish_points],
    y=data['Close'].iloc[bullish_points],
    mode='markers',
    name='🟢 매수 다이버전스',
    marker=dict(color='green', size=10),
    hovertext=[f"RSI: {round(data['RSI'].iloc[i], 2)}<br>Price: {round(data['Close'].iloc[i], 2)}" for i in bullish_points]
))

# 매도 시점 표시
fig.add_trace(go.Scatter(
    x=data.index[bearish_points],
    y=data['Close'].iloc[bearish_points],
    mode='markers',
    name='🔴 매도 다이버전스',
    marker=dict(color='red', size=10),
    hovertext=[f"RSI: {round(data['RSI'].iloc[i], 2)}<br>Price: {round(data['Close'].iloc[i], 2)}" for i in bearish_points]
))

# 일목균형표 라인
fig.add_trace(go.Scatter(x=data.index, y=data['tenkan'], name='일목 전환선', line=dict(color='orange', dash='dot')))
fig.add_trace(go.Scatter(x=data.index, y=data['kijun'], name='일목 기준선', line=dict(color='purple', dash='dot')))

# RSI Subplot
rsi_trace = go.Scatter(x=data.index, y=data["RSI"], name="RSI", line=dict(color="purple"), yaxis="y2")

# Layout 설정
fig.add_trace(rsi_trace)
fig.update_layout(
    xaxis=dict(domain=[0, 1]),
    yaxis=dict(title="가격", side="left"),
    yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0, 100]),
    height=700,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True)
