# ==============================
# 📊 Portfolio Performance Dashboard
# ==============================

# ==============================
# Importing Libraries
# ==============================

import pandas as pd             # Data handling (tables, time series, returns)
import numpy as np              # Numerical operations (used for volatility scaling)
import matplotlib.pyplot as plt # Plotting charts
import yfinance as yf           # Downloading stock data from Yahoo Finance
import streamlit as st          # Building interactive web app UI

# ==============================
# App Title
# ==============================

st.title("Portfolio Performance Dashboard")

# ==============================
# Sidebar Inputs
# ==============================

st.sidebar.header("Portfolio Settings")

# User inputs tickers (comma-separated)
tickers_input = st.sidebar.text_input(
    "Tickers (comma-separated)",
    "AAPL, JPM, JNJ, NFLX, TSLA"
)

# User inputs portfolio weights (must sum to 1)
tickers_input = tickers_input.upper()
weights_input = st.sidebar.text_input(
    "Weights (must sum to 1)",
    "0.2, 0.2, 0.2, 0.2, 0.2"
)

# Risk-free rate used in Sharpe ratio calculation
risk_free_rate = st.sidebar.number_input(
    "Risk-Free Rate",
    value=0.03
)

# ==============================
# Validate Empty Inputs
# ==============================

# Ensure user enters at least one ticker
if not tickers_input.strip():
    st.error("Please enter at least one stock ticker.")
    st.stop()

# Ensure weights are provided
if not weights_input.strip():
    st.error("Please enter portfolio weights.")
    st.stop()

# ==============================
# Process Inputs
# ==============================

# Convert tickers into list format
tickers = [t.strip().upper() for t in tickers_input.split(",")]

# Convert weights into float values
try:
    weights = [float(w) for w in weights_input.split(",")]
except ValueError:
    st.error("Weights must be valid numbers separated by commas.")
    st.stop()

# Validation checks
if len(tickers) != len(weights):
    st.error("Number of tickers must match number of weights.")
    st.stop()

# Ensure weights sum to 1 (fully invested portfolio)
if abs(sum(weights) - 1) > 0.01:
    st.error("Weights must sum to 1.")
    st.stop()

# Combine tickers and weights into dictionary
portfolio = dict(zip(tickers, weights))

# ==============================
# Date Range
# ==============================

# Define analysis period (past 1 year)
end_date = pd.Timestamp.now()
start_date = end_date - pd.DateOffset(years=1)

# ==============================
# Download Stock Data
# ==============================

prices = pd.DataFrame()

# Loop through each stock and download price data
for symbol in portfolio:
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    # Fix MultiIndex column issue if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Prefer Adjusted Close (accounts for dividends/splits)
    if "Adj Close" in data.columns:
        prices[symbol] = data["Adj Close"]
    elif "Close" in data.columns:
        prices[symbol] = data["Close"]
    else:
        st.warning(f"No usable data for {symbol}")

# Stop execution if no valid data was retrieved
if prices.empty:
    st.error("No valid stock data found. Check your tickers.")
    st.stop()

# ==============================
# Benchmark (Market Comparison)
# ==============================

# SPY = ETF tracking S&P 500 (used as market benchmark)
benchmark = yf.download("SPY", start=start_date, end=end_date, progress=False)

# Fix column format if needed
if isinstance(benchmark.columns, pd.MultiIndex):
    benchmark.columns = benchmark.columns.get_level_values(0)

# Select appropriate price column
if "Adj Close" in benchmark.columns:
    benchmark = benchmark["Adj Close"]
else:
    benchmark = benchmark["Close"]

# ==============================
# Returns Calculation
# ==============================

# Daily returns for each stock
# Formula: (Price_today / Price_yesterday) - 1
daily_returns = prices.pct_change().dropna()

# Benchmark returns
benchmark_returns = benchmark.pct_change().dropna()

# Align dates to ensure matching time periods
common_index = daily_returns.index.intersection(benchmark_returns.index)
daily_returns = daily_returns.loc[common_index]
benchmark_returns = benchmark_returns.loc[common_index]

# Portfolio returns (weighted sum of individual returns)
portfolio_returns = sum(
    weight * daily_returns[symbol]
    for symbol, weight in portfolio.items()
)

# ==============================
# Performance Metrics
# ==============================

# Total return over the period
# Formula: (1 + r1)(1 + r2)...(1 + rn) - 1
portfolio_total = (1 + portfolio_returns).prod() - 1
benchmark_total = (1 + benchmark_returns).prod() - 1

# Volatility (risk measure)
# Standard deviation of returns × sqrt(252) to annualize
portfolio_vol = portfolio_returns.std() * np.sqrt(252)
benchmark_vol = benchmark_returns.std() * np.sqrt(252)

# Sharpe Ratio (risk-adjusted return)
# Formula: (Return - Risk-Free Rate) / Volatility
portfolio_sharpe = (portfolio_total - risk_free_rate) / portfolio_vol
benchmark_sharpe = (benchmark_total - risk_free_rate) / benchmark_vol

# Individual stock total returns
individual_returns = (1 + daily_returns).prod() - 1

# ==============================
# Display Key Metrics
# ==============================

col1, col2, col3 = st.columns(3)

col1.metric("Portfolio Return", f"{portfolio_total:.2%}")
col2.metric("Benchmark (SPY)", f"{benchmark_total:.2%}")
col3.metric("Portfolio Sharpe", f"{portfolio_sharpe:.2f}")

# Performance comparison vs benchmark
if portfolio_total > benchmark_total:
    st.success(f"🟢 Outperforming by {(portfolio_total - benchmark_total):.2%}")
else:
    st.error(f"🔴 Underperforming by {(portfolio_total - benchmark_total):.2%}")

st.markdown("---")

# ==============================
# Volatility & Sharpe Comparison
# ==============================

col1, col2 = st.columns(2)

col1.metric("Portfolio Volatility", f"{portfolio_vol:.2%}")
col2.metric("Benchmark Volatility", f"{benchmark_vol:.2%}")

col1.metric("Portfolio Sharpe", f"{portfolio_sharpe:.2f}")
col2.metric("Benchmark Sharpe", f"{benchmark_sharpe:.2f}")

# ==============================
# Growth of $1 Chart
# ==============================

st.subheader("Growth of $1 Investment")

# Cumulative returns (growth of $1 invested)
portfolio_cum = (1 + portfolio_returns).cumprod()
benchmark_cum = (1 + benchmark_returns).cumprod()

fig, ax = plt.subplots(figsize=(10,5))

# Plot portfolio vs benchmark growth
ax.plot(portfolio_cum, label="Portfolio")
ax.plot(benchmark_cum, label="SPY")

ax.set_title("Portfolio vs Benchmark")
ax.legend()

st.pyplot(fig)

# ==============================
# Individual Stock Returns Table
# ==============================

st.subheader("Individual Stock Returns")

# Create table of each stock's total return
df = pd.DataFrame({
    "Stock": individual_returns.index,
    "Return": individual_returns.values
})

# Display formatted table
st.dataframe(df.style.format({"Return": "{:.2%}"}))
