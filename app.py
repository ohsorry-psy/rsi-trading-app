
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="RSI 다이버전스 정신과 트레이딩", layout="wide")
st.title("📊 RSI 다이버전스 정신과 트레이딩")
st.markdown("""
RSI 다이버전스를 이용해 매수/매도 타이밍을 포착해보세요.  
종목 코드를 입력하고 분석 버튼을 눌러주세요!
""")

symbol = st.text_input("종목 코드 (예: AAPL, 005930.KS, 012450.KS)", value="AAPL")
start_date = st.date_input("시작일", pd.to_datetime("2023-01-01"))
end_date = st.date_input("종료일", pd.to_datetime("2024-04-03"))

if st.button("📈 분석 시작"):
    with st.spinner("데이터 불러오는 중..."):
        data = yf.download(symbol, start=start_date, end=end_date)

    if data.empty:
        st.error("데이터가 없습니다. 종목 코드를 다시 확인해주세요.")
    else:
        close = data['Close'].squeeze()
        data['RSI'] = ta.momentum.RSIIndicator(close=close, window=14).rsi().squeeze()

        def find_bullish_divergence(df):
            points = []
            for i in range(30, len(df)):
                p_now = float(df['Close'].iloc[i])
                p_prev = float(df['Close'].iloc[i-10:i].min())
                r_now = float(df['RSI'].iloc[i])
                r_prev = float(df['RSI'].iloc[i-10:i].min())
                if p_now < p_prev and r_now > r_prev:
                    points.append(i)
            return points

        def find_bearish_divergence(df):
            points = []
            for i in range(30, len(df)):
                p_now = float(df['Close'].iloc[i])
                p_prev = float(df['Close'].iloc[i-10:i].max())
                r_now = float(df['RSI'].iloc[i])
                r_prev = float(df['RSI'].iloc[i-10:i].max())
                if p_now > p_prev and r_now < r_prev:
                    points.append(i)
            return points

        bullish_points = find_bullish_divergence(data)
        bearish_points = find_bearish_divergence(data)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7))
        ax1.plot(data['Close'], label='Close Price')
        ax1.scatter(data.iloc[bullish_points].index, data['Close'].iloc[bullish_points], color='green', label='Bullish Divergence')
        ax1.scatter(data.iloc[bearish_points].index, data['Close'].iloc[bearish_points], color='red', label='Bearish Divergence')
        ax1.legend()
        ax1.set_title(f'{symbol} Price with RSI Divergence')

        ax2.plot(data['RSI'], label='RSI', color='purple')
        ax2.axhline(30, color='gray', linestyle='--')
        ax2.axhline(70, color='gray', linestyle='--')
        ax2.legend()

        st.pyplot(fig)

        st.markdown("### 📋 포착된 다이버전스 개수")
        st.write(f"🟢 Bullish: {len(bullish_points)}개")
        st.write(f"🔴 Bearish: {len(bearish_points)}개")

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button("📥 차트 이미지 다운로드", data=buf.getvalue(), file_name=f"{symbol}_rsi_divergence.png", mime="image/png")
