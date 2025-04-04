import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go

# ----------------------
# 화면 설정
# ----------------------
st.set_page_config(page_title="RSI 다이버전스 정신과 트레이딩", layout="wide")
st.title("🧠 RSI 다이버전스 정신과 트레이딩")

# ----------------------
# 자발된 값 선택
# ----------------------
symbol = st.sidebar.text_input("특정 종목 코드 (예: AAPL, 005930.KS, 012450.KQ)", value="AAPL")
start_date = st.sidebar.date_input("건조 시작일", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("건조 종료일", pd.to_datetime("today"))

# ----------------------
# 데이터 보기
# ----------------------
data = yf.download(symbol, start=start_date, end=end_date)

if data.empty:
    st.error("건조한 값이 없습니다. 종목 코드를 확인해주세요.")
    st.stop()

# ----------------------
# RSI 계산
# ----------------------
if 'Close' not in data.columns or data['Close'].empty:
    st.error("❌ 'Close' 데이터가 비어 있습니다.")
    st.stop()

close = data['Close']
if close.ndim > 1:
    close = close.squeeze()

try:
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi().squeeze()
    data['RSI'] = rsi
    data = data.dropna(subset=['RSI'])
except Exception as e:
    st.error(f"RSI 계산 중 오류 발생: {e}")
    st.stop()

# ----------------------
# 다이버전스 패턴 필터
# ----------------------
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

# ----------------------
# 차트 구조 (Plotly)
# ----------------------
price_trace = go.Scatter(
    x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')
)
bullish_trace = go.Scatter(
    x=data.iloc[bullish_points].index,
    y=data['Close'].iloc[bullish_points],
    mode='markers',
    marker=dict(color='green', size=10, symbol='triangle-up'),
    name='🟢 Bullish Divergence',
    hovertext=[
        f"RSI: {data['RSI'].iloc[i]:.2f}<br>Price: {data['Close'].iloc[i]:.2f}"
        for i in bullish_points
    ],
    hoverinfo="text"
)
bearish_trace = go.Scatter(
    x=data.iloc[bearish_points].index,
    y=data['Close'].iloc[bearish_points],
    mode='markers',
    marker=dict(color='red', size=10, symbol='triangle-down'),
    name='🔴 Bearish Divergence',
    hovertext=[
        f"RSI: {data['RSI'].iloc[i]:.2f}<br>Price: {data['Close'].iloc[i]:.2f}"
        for i in bearish_points
    ],
    hoverinfo="text"
)
rsi_trace = go.Scatter(
    x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')
)
line_30 = go.Scatter(x=data.index, y=[30]*len(data), mode='lines', name='30', line=dict(dash='dot', color='gray'))
line_70 = go.Scatter(x=data.index, y=[70]*len(data), mode='lines', name='70', line=dict(dash='dot', color='gray'))

fig = go.Figure()
fig.add_trace(price_trace)
fig.add_trace(bullish_trace)
fig.add_trace(bearish_trace)
fig.update_layout(
    title=f"{symbol} 가격차트",
    height=500,
    margin=dict(t=30, b=10)
)

fig_rsi = go.Figure()
fig_rsi.add_trace(rsi_trace)
fig_rsi.add_trace(line_30)
fig_rsi.add_trace(line_70)
fig_rsi.update_layout(
    title="RSI Indicator",
    height=300,
    margin=dict(t=10)
)

# ----------------------
# 보이기
# ----------------------
st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig_rsi, use_container_width=True)
