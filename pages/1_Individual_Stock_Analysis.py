# ==============================
# Importing Libraries
# ==============================

import pandas as pd             # Data manipulation (DataFrames, rolling calculations)
import numpy as np              # Numerical operations (used here for sqrt in volatility)
import matplotlib.pyplot as plt # Plotting charts (price + RSI)
import yfinance as yf           # Fetching stock market data from Yahoo Finance
import streamlit as st          # Building the web app interface

# ==============================
# App Title
# ==============================

st.title("Individual Stock Analysis")  # Main app title

# ==============================
# Sidebar (User Input)
# ==============================

st.sidebar.header("Stock Settings")

# User inputs stock ticker (default = S&P 500 index)
ticker = st.sidebar.text_input("Enter Stock Ticker", "^GSPC")

# Fixed time period for analysis
st.sidebar.markdown("**Time Period:** 6 Months")

# ==============================
# Downloading Data (with validation)
# ==============================

try:
    data = yf.download(ticker, period="6mo", auto_adjust=False, progress=False)

    # Fix column format if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Check if data is empty OR missing Close column
    if data.empty or "Close" not in data.columns:
        st.error(f"Invalid ticker: '{ticker}'. Please enter a valid stock symbol.")
        st.stop()

except Exception as e:
    st.error(f"Error retrieving data for '{ticker}'. Please try another ticker.")
    st.stop()

# ==============================
# Moving Averages (Trend Indicators)
# ==============================

# 20-day moving average → short-term trend
data["MA20"] = close.rolling(window=20).mean()

# 50-day moving average → medium-term trend
data["MA50"] = close.rolling(window=50).mean()

# Current values of price and moving averages
current_price = close.iloc[-1]
ma_20 = close.iloc[-20:].mean()
ma_50 = close.iloc[-50:].mean()

# ==============================
# RSI (Relative Strength Index)
# ==============================

# RSI measures momentum (how fast price is rising/falling)
# Range: 0–100
# >70 = Overbought (possible sell signal)
# <30 = Oversold (possible buy signal)

# Day-to-day price change
delta = close.diff()

# Separate gains (positive changes) and losses (negative changes)
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

# 14-day average gain and loss
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

# Relative Strength (RS)
rs = avg_gain / avg_loss

# RSI formula
rsi = 100 - (100 / (1 + rs))

# Add RSI to dataframe for plotting
data["RSI"] = rsi

# Current RSI value
current_rsi = rsi.iloc[-1]

# ==============================
# Volatility (Risk Measure)
# ==============================

# Daily returns (percentage change in price)
returns = close.pct_change()

# Rolling 20-day standard deviation of returns
# Multiply by sqrt(252) to annualize (252 trading days/year)
volatility = returns.rolling(20).std() * np.sqrt(252)

# Current volatility
current_vol = volatility.iloc[-1]

# ==============================
# Trend Classification
# ==============================

# Determines direction using price and moving averages
# Uptrend: Price > MA20 > MA50
# Downtrend: Price < MA20 < MA50
# Otherwise: Mixed

if current_price > ma_20 > ma_50:
    trend = "Upward Trend"
elif current_price < ma_20 < ma_50:
    trend = "Downward Trend"
else:
    trend = "Mixed Trend"

# ==============================
# RSI Signal Interpretation
# ==============================

if current_rsi > 70:
    rsi_signal = "Overbought (Sell Signal)"
elif current_rsi < 30:
    rsi_signal = "Oversold (Buy Signal)"
else:
    rsi_signal = "Neutral"

# ==============================
# Volatility Classification
# ==============================

# Categorizing risk level based on volatility
if current_vol > 0.40:
    vol_level = "High Volatility"
elif current_vol > 0.25:
    vol_level = "Medium Volatility"
else:
    vol_level = "Low Volatility"

# ==============================
# Trading Recommendation Logic
# ==============================

# Combines:
# - Trend (direction)
# - RSI (momentum/extremes)
#
# Logic:
# Buy → Uptrend + not overbought
# Sell → Downtrend + not oversold
# Hold → Otherwise

if trend == "Upward Trend" and current_rsi < 70:
    recommendation = "BUY 🟢"
elif trend == "Downward Trend" and current_rsi > 30:
    recommendation = "SELL 🔴"
else:
    recommendation = "HOLD 🟡"

# ==============================
# Metrics Display (Dashboard)
# ==============================

# Display key values in columns
col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", f"${current_price:.2f}")
col2.metric("20 Day MA", f"${ma_20:.2f}")
col3.metric("50 Day MA", f"${ma_50:.2f}")
col4.metric("RSI", f"{current_rsi:.2f}")

st.markdown("---")

# ==============================
# Price Chart
# ==============================

st.subheader("Price Chart with Moving Averages")

fig, ax = plt.subplots(figsize=(14,6))

# Plot closing price and moving averages
ax.plot(close, label="Closing Price", linewidth=2)
ax.plot(data["MA20"], label="20 Day MA")
ax.plot(data["MA50"], label="50 Day MA")

ax.legend()
ax.set_title(f"{ticker} Price Analysis")

# Display chart in Streamlit
st.pyplot(fig)

# ==============================
# RSI Chart
# ==============================

st.subheader("RSI Indicator")

fig2, ax2 = plt.subplots(figsize=(14,4))

# Plot RSI line
ax2.plot(data["RSI"], label="RSI")

# Overbought (70) and oversold (30) thresholds
ax2.axhline(70, linestyle="--")
ax2.axhline(30, linestyle="--")

ax2.set_title("RSI Indicator")
ax2.legend()

st.pyplot(fig2)

# ==============================
# Analysis Summary
# ==============================

st.markdown("---")
st.subheader("Analysis Summary")

col1, col2, col3 = st.columns(3)

# Display interpreted signals
col1.info(f"Trend: {trend}")
col2.warning(f"RSI Signal: {rsi_signal}")
col3.success(f"Volatility: {vol_level}")

st.markdown("---")

# ==============================
# Final Recommendation Output
# ==============================

st.subheader("Trading Recommendation")

# Large display of recommendation
st.markdown(f"## {recommendation}")

# Explanation of decision
st.write(
    f"""
Based on the current trend ({trend}), 
RSI reading ({current_rsi:.2f}),
and volatility level ({vol_level}), 
the recommendation is **{recommendation}**.
"""
)
