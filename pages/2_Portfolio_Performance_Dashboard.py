# Portfolio Performance Dashboard

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st

st.title("📊 Portfolio Performance Dashboard")

# Sidebar Inputs
st.sidebar.header("Portfolio Settings")

tickers_input = st.sidebar.text_input(
    "Tickers (comma-separated)",
    "AAPL,JPM,JNJ,NFLX,TSLA"
)

weights_input = st.sidebar.text_input(
    "Weights (must sum to 1)",
    "0.2,0.2,0.2,0.2,0.2"
)

risk_free_rate = st.sidebar.number_input("Risk-Free Rate", value=0.03)

# Convert inputs
tickers = [t.strip().upper() for t in tickers_input.split(",")]
weights = [float(w) for w in weights_input.split(",")]

# Validation
if len(tickers) != len(weights):
    st.error("Tickers and weights must match.")
    st.stop()

if abs(sum(weights) - 1) > 0.01:
    st.error("Weights must sum to 1.")
    st.stop()

portfolio = dict(zip(tickers, weights))

# Dates
end_date = pd.Timestamp.now()
start_date = end_date - pd.DateOffset(years=1)

# Download prices
prices = pd.DataFrame()

for symbol in portfolio:
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if "Adj Close" in data.columns:
        prices[symbol] = data["Adj Close"]
    elif "Close" in data.columns:
        prices[symbol] = data["Close"]
    else:
        st.warning(f"No usable data for {symbol}")

for symbol in portfolio:
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    if "Adj Close" in data.columns:
    prices[symbol] = data["Adj Close"]
    elif "Close" in data.columns:
        prices[symbol] = data["Close"]
    else:
        st.warning(f"No price data for {symbol}")

benchmark = yf.download("SPY", start=start_date, end=end_date, progress=False)
if isinstance(benchmark.columns, pd.MultiIndex):
    benchmark.columns = benchmark.columns.get_level_values(0)

if "Adj Close" in benchmark.columns:
    benchmark = benchmark["Adj Close"]
else:
    benchmark = benchmark["Close"]

# Returns
daily_returns = prices.pct_change().dropna()
benchmark_returns = benchmark.pct_change().dropna()

# Align dates
common_index = daily_returns.index.intersection(benchmark_returns.index)
daily_returns = daily_returns.loc[common_index]
benchmark_returns = benchmark_returns.loc[common_index]

# Portfolio returns
portfolio_returns = sum(
    weight * daily_returns[symbol]
    for symbol, weight in portfolio.items()
)

# Metrics
portfolio_total = (1 + portfolio_returns).prod() - 1
benchmark_total = (1 + benchmark_returns).prod() - 1

portfolio_vol = portfolio_returns.std() * np.sqrt(252)
benchmark_vol = benchmark_returns.std() * np.sqrt(252)

portfolio_sharpe = (portfolio_total - risk_free_rate) / portfolio_vol
benchmark_sharpe = (benchmark_total - risk_free_rate) / benchmark_vol

individual_returns = (1 + daily_returns).prod() - 1

# =====================
# DISPLAY
# =====================

col1, col2, col3 = st.columns(3)
col1.metric("Portfolio Return", f"{portfolio_total:.2%}")
col2.metric("Benchmark (SPY)", f"{benchmark_total:.2%}")
col3.metric("Sharpe Ratio", f"{portfolio_sharpe:.2f}")

# Performance message
if portfolio_total > benchmark_total:
    st.success(f"Outperforming by {(portfolio_total - benchmark_total):.2%} 🟢")
else:
    st.error(f"Underperforming by {(portfolio_total - benchmark_total):.2%} 🔴")

# Volatility + Sharpe
col1, col2 = st.columns(2)
col1.metric("Portfolio Volatility", f"{portfolio_vol:.2%}")
col2.metric("Benchmark Volatility", f"{benchmark_vol:.2%}")

col1.metric("Portfolio Sharpe", f"{portfolio_sharpe:.2f}")
col2.metric("Benchmark Sharpe", f"{benchmark_sharpe:.2f}")

# Growth Chart
st.subheader("Growth of $1 Investment")

portfolio_cum = (1 + portfolio_returns).cumprod()
benchmark_cum = (1 + benchmark_returns).cumprod()

fig, ax = plt.subplots()
ax.plot(portfolio_cum, label="Portfolio")
ax.plot(benchmark_cum, label="SPY")
ax.legend()

st.pyplot(fig)

# Table
st.subheader("Individual Stock Returns")

df = pd.DataFrame({
    "Stock": individual_returns.index,
    "Return": individual_returns.values
})

st.dataframe(df.style.format({"Return": "{:.2%}"}))
