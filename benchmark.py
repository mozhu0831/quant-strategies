from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from metrics import calculate_metrics, format_metrics


def run_benchmark(
    prices_path="prices.csv",
    eval_start="2020-01-02",
    eval_end="2025-12-31",
    save_fig=True,
):
    base_dir = Path(__file__).parent
    file_path = base_dir / prices_path

    if not file_path.exists():
        raise FileNotFoundError(f"Prices file not found: {file_path}")

    prices = pd.read_csv(file_path, index_col=0, parse_dates=True).sort_index()

    returns = prices.pct_change()
    returns_eval = returns.loc[eval_start:eval_end].copy()
    if returns_eval.empty:
        raise ValueError(f"No return data available between {eval_start} and {eval_end}.")

    num_stocks = prices.shape[1]
    weights = np.ones(num_stocks) / num_stocks

    # 1. Daily-rebalanced equal-weight benchmark
    daily_rebal_returns = (returns_eval * weights).sum(
        axis=1, min_count=num_stocks
    ).dropna()

    # Calculate daily rebalance turnover from intraday weight drift
    gross_growth_stocks = 1.0 + returns_eval
    portfolio_growth = 1.0 + daily_rebal_returns
    drifted_weights = (gross_growth_stocks.div(portfolio_growth, axis=0)) / num_stocks
    daily_turnover = (drifted_weights - (1.0 / num_stocks)).abs().sum(axis=1)

    # 2. Buy-and-hold equal-weight benchmark
    base_idx = prices.loc[:eval_start].index
    base_date = base_idx[-2] if len(base_idx) >= 2 else base_idx[-1]
    bnh_growth = (prices.loc[base_date:eval_end] / prices.loc[base_date]).mean(axis=1)
    bnh_returns = bnh_growth.pct_change().dropna().loc[eval_start:eval_end]

    m_daily = calculate_metrics(
        daily_rebal_returns,
        annual_risk_free_rate=0.04,
        benchmark_returns=bnh_returns,
        turnover=daily_turnover,
    )
    m_bnh = calculate_metrics(
        bnh_returns,
        annual_risk_free_rate=0.04,
        benchmark_returns=bnh_returns,
        turnover=0.0,
    )

    print("\nBenchmark Performance (2020-2025):")
    print("\nDaily-Rebalanced Equal-Weight:")
    print(format_metrics(m_daily))
    print("\nBuy-and-Hold Equal-Weight:")
    print(format_metrics(m_bnh))

    daily_growth = (1.0 + daily_rebal_returns).cumprod()
    daily_growth = daily_growth / daily_growth.iloc[0]

    bnh_growth = (1.0 + bnh_returns).cumprod()
    bnh_growth = bnh_growth / bnh_growth.iloc[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_growth.index, daily_growth, label="Daily-Rebalanced Equal-Weight")
    ax.plot(bnh_growth.index, bnh_growth, label="Buy-and-Hold Equal-Weight", linestyle="--")
    ax.set_title("Benchmark Growth ($1 Initial Investment)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if save_fig:
        out_dir = base_dir / "outputs"
        out_dir.mkdir(exist_ok=True)
        fig.savefig(out_dir / "benchmark.png", dpi=150)

    plt.close(fig)

    return {
        "daily_rebalanced_returns": daily_rebal_returns,
        "daily_rebalanced_metrics": m_daily,
        "daily_turnover": daily_turnover,
        "bnh_returns": bnh_returns,
        "bnh_metrics": m_bnh,
    }


if __name__ == "__main__":
    run_benchmark()