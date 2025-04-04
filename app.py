import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go

st.set_page_config(page_title="RSI 다이버전스 정신과 트레이딩", layout="wide")
st.title("🧠 RSI 다이버전스 정신과 트레이딩")

# 📌 Sidebar 옵션
symbol = st.sidebar.text_input("종목 심볼 (예: AAPL, PLTR, 005930.KS)", value="PLTR")
start_date = st.sidebar.date_input("시작 날짜", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("종료 날짜", value=pd.to_datetime("today"))

# 📈 데이터 다운로드
data = yf.download(symbol, start=start_date, end=end_date)

if data.empty:
    st.warning("해당 기간에 데이터가 없습니다. 다른 종목이나 기간을 입력해 주세요.")
    st.stop()

# ✅ RSI 계산
close = data['Close'].squeeze()
data['RSI'] = ta.momentum.RSIIndicator(close=close, window=14).rsi().squeeze()

# ✅ 일목균형표 계산
ichimoku = ta.trend.IchimokuIndicator(high=data['High'], low=data['Low'])
data['Ichimoku Base'] = ichimoku.ichimoku_base_line()
data['Ichimoku Conversion'] = ichimoku.ichimoku_conversion_line()

# ✅ 다이버전스 탐지 함수들
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

# ✅ Plotly로 인터랙티브 차트 생성
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))

# 매수/매도 포인트
fig.add_trace(go.Scatter(
    x=data.index[bullish_points],
    y=data['Close'].iloc[bullish_points],
    mode='markers',
    marker=dict(color='green', size=10, symbol='triangle-up'),
    name='🟢 Bullish',
    text=[f"RSI: {data['RSI'].iloc[i]:.2f}<br>Price: {data['Close'].iloc[i]:.2f}" for i in bullish_points],
    hoverinfo='text+x+y'
))

fig.add_trace(go.Scatter(
    x=data.index[bearish_points],
    y=data['Close'].iloc[bearish_points],
    mode='markers',
    marker=dict(color='red', size=10, symbol='triangle-down'),
    name='🔴 Bearish',
    text=[f"RSI: {data['RSI'].iloc[i]:.2f}<br>Price: {data['Close'].iloc[i]:.2f}" for i in bearish_points],
    hoverinfo='text+x+y'
))

# ✅ 일목균형표 선 추가
fig.add_trace(go.Scatter(x=data.index, y=data['Ichimoku Base'], mode='lines', name='Ichimoku Base', line=dict(dash='dot')))
fig.add_trace(go.Scatter(x=data.index, y=data['Ichimoku Conversion'], mode='lines', name='Ichimoku Conversion', line=dict(dash='dot')))

fig.update_layout(title=f"{symbol} 가격 차트와 RSI 다이버전스 및 일목균형표", height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# ✅ RSI 따로 시각화 (하단 날짜 맞춤)
rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
rsi_fig.add_shape(type='line', x0=data.index[0], y0=30, x1=data.index[-1], y1=30,
                 line=dict(color='gray', dash='dash'))
rsi_fig.add_shape(type='line', x0=data.index[0], y0=70, x1=data.index[-1], y1=70,
                 line=dict(color='gray', dash='dash'))
rsi_fig.update_layout(title='RSI 지표', height=300, xaxis_rangeslider_visible=False)
st.plotly_chart(rsi_fig, use_container_width=True)
