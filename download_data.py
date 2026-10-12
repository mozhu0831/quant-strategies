from pathlib import Path
import yfinance as yf
import pandas as pd

TICKERS_50 = [
    # Information Technology
    "AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "CSCO", "ORCL",
    # Financials
    "JPM", "BAC", "GS", "MS", "WFC", "BLK", "C",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "LLY",
    # Consumer Discretionary
    "AMZN", "HD", "MCD", "NKE", "LOW", "SBUX",
    # Communication Services
    "GOOGL", "META", "DIS", "CMCSA", "NFLX",
    # Industrials
    "CAT", "HON", "UNP", "GE", "BA",
    # Consumer Staples
    "PG", "KO", "PEP", "COST",
    # Energy
    "XOM", "CVX", "COP",
    # Utilities
    "NEE", "SO",
    # Materials
    "LIN", "APD",
    # Real Estate
    "PLD",
]


def download_price_data(
    tickers=None,
    start_date="2019-01-01",
    end_date="2026-01-01",
    output_path="prices.csv"
):
    if tickers is None:
        tickers = TICKERS_50

    print(f"Downloading {len(tickers)} tickers from {start_date} to {end_date}...")
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )

    if data is None or data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    if "Close" in data.columns:
        prices = data["Close"]
    else:
        prices = data

    prices = prices[sorted(tickers)].copy()
    prices.index.name = "Date"

    # Forward-fill / back-fill minor single-day gaps if any
    prices = prices.ffill().bfill()

    base_dir = Path(__file__).parent
    prices.to_csv(base_dir / output_path)

    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    prices.to_csv(data_dir / Path(output_path).name)

    print(f"Saved {prices.shape[1]} tickers ({prices.shape[0]} rows) to {output_path}")
    return prices


if __name__ == "__main__":
    download_price_data()
