# Importing the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st

# Title
st.title("Individual Stock Analysis")

# Sidebar
st.sidebar.header("Stock Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker", "^GSPC")
st.sidebar.markdown("**Time Period:** 6 Months")

# Downloading Data 
data = yf.download(ticker, period="6mo", auto_adjust=False)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
    
# Closing Price
close = data["Close"].squeeze()

# Moving Averages
data["MA20"] = close.rolling(window=20).mean()
data["MA50"] = close.rolling(window=50).mean()

# Calculating Values
current_price = close.iloc[-1]
ma_20 = close.iloc[-20:].mean()
ma_50 = close.iloc[-50:].mean()

# Calculating RSI
delta = close.diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))

# Add RSI to dataframe
data["RSI"] = rsi

# Current RSI
current_rsi = rsi.iloc[-1]

# Volatility
returns = close.pct_change()
volatility = returns.rolling(20).std() * np.sqrt(252)
current_vol = volatility.iloc[-1]

# Trend
if current_price > ma_20 > ma_50:
  trend = "Upward Trend"

elif current_price < ma_20 < ma_50:
  trend = "Downward Trend"

else:
  trend = "Mixed Trend"

# RSI Signal
if current_rsi > 70:
    rsi_signal = "Overbought (Sell Signal)"
elif current_rsi < 30:
    rsi_signal = "Oversold (Buy Signal)"
else:
    rsi_signal = "Neutral"

# Volatility Level
if current_vol > 0.40:
    vol_level = "High Volatility"
elif current_vol > 0.25:
    vol_level = "Medium Volatility"
else:
    vol_level = "Low Volatility"

# Recommendation
if trend == "Upward Trend" and current_rsi < 70:
    recommendation = "BUY 🟢"
elif trend == "Downward Trend" and current_rsi > 30:
    recommendation = "SELL 🔴"
else:
    recommendation = "HOLD 🟡"

#Metrics Row
col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", f"${current_price:.2f}")
col2.metric("20 Day MA", f"${ma_20:.2f}")
col3.metric("50 Day MA", f"${ma_50:.2f}")
col4.metric("RSI", f"{current_rsi:.2f}")

st.markdown("---")

# Price Chart
st.subheader("Price Chart with Moving Averages")

fig, ax = plt.subplots(figsize=(14,6))

ax.plot(close, label="Closing Price", linewidth=2)
ax.plot(data["MA20"], label="20 Day MA")
ax.plot(data["MA50"], label="50 Day MA")

ax.legend()
ax.set_title(f"{ticker} Price Analysis")

st.pyplot(fig)

# RSI Chart
st.subheader("RSI Indicator")

fig2, ax2 = plt.subplots(figsize=(14,4))

ax2.plot(data["RSI"], label="RSI")
ax2.axhline(70, linestyle="--")
ax2.axhline(30, linestyle="--")

ax2.set_title("RSI Indicator")
ax2.legend()

st.pyplot(fig2)

# Analysis Section
st.markdown("---")

st.subheader("Analysis Summary")

col1, col2, col3 = st.columns(3)

col1.info(f"Trend: {trend}")
col2.warning(f"RSI Signal: {rsi_signal}")
col3.success(f"Volatility: {vol_level}")

st.markdown("---")

st.subheader("Trading Recommendation")

st.markdown(f"## {recommendation}")

st.write(
    f"""
Based on the current trend ({trend}), 
RSI reading ({current_rsi:.2f}),
and volatility level ({vol_level}), 
the recommendation is **{recommendation}**.
"""
)
