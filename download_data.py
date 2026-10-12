import yfinance as yf
import pandas as pd

# Initial test
tickers = ["AAPL", "MSFT", "JPM"]

# Download prices
prices = yf.download(
    tickers,
    start="2020-01-01",
    end="2026-01-01",
    auto_adjust=True,
    progress=False
)

prices = prices["Close"]
