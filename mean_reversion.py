from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from metrics import calculate_metrics, format_metrics


def run_mean_reversion_strategy(
    prices_path="prices.csv",
    lookback=5,
    top_n=5,
    rebalance_freq=5,
    transaction_cost_bps=10,
    annual_risk_free_rate=0.04,
    eval_start="2020-01-02",
    eval_end="2025-12-31",
    save_fig=True,
):
    base_dir = Path(__file__).parent
    file_path = base_dir / prices_path

    if not file_path.exists():
        raise FileNotFoundError(f"Prices file not found: {file_path}")

    prices = pd.read_csv(file_path, index_col=0, parse_dates=True).sort_index()

    past_returns = prices / prices.shift(lookback) - 1.0

    ranking = past_returns.rank(axis=1, ascending=True, method="average")
    selected = (ranking <= top_n) & past_returns.notna()
    positions = selected.astype(float)

    row_totals = positions.sum(axis=1).replace(0.0, np.nan)
    positions = positions.div(row_totals, axis=0)

    rebalance_dates = pd.Series(
        np.arange(len(prices)) % rebalance_freq == 0,
        index=prices.index
    )

    positions.loc[~rebalance_dates, :] = np.nan
    positions = positions.ffill().shift(1)

    returns = prices.pct_change()
    eval_mask = (positions.index >= eval_start) & (positions.index <= eval_end)
    positions_eval = positions.loc[eval_mask].copy()
    returns_eval = returns.loc[eval_mask].copy()

    gross_returns = (positions_eval * returns_eval).sum(
        axis=1, min_count=1
    ).dropna()

    weights = positions_eval.fillna(0.0)
    previous_weights = weights.shift(1).fillna(0.0)
    turnover = (weights - previous_weights).abs().sum(axis=1)

    cost_rate = transaction_cost_bps / 10_000.0
    trading_costs = (turnover * cost_rate).reindex(gross_returns.index).fillna(0.0)
    net_returns = gross_returns - trading_costs

    # Buy-and-hold benchmark for alpha and beta calculation
    base_idx = prices.loc[:eval_start].index
    base_date = base_idx[-2] if len(base_idx) >= 2 else base_idx[-1]
    bnh_growth = (prices.loc[base_date:eval_end] / prices.loc[base_date]).mean(axis=1)
    bnh_returns = bnh_growth.pct_change().dropna().loc[eval_start:eval_end]

    metrics_gross = calculate_metrics(
        gross_returns,
        annual_risk_free_rate,
        benchmark_returns=bnh_returns,
        turnover=turnover,
    )
    metrics_net = calculate_metrics(
        net_returns,
        annual_risk_free_rate,
        benchmark_returns=bnh_returns,
        turnover=turnover,
    )

    print("\nMean Reversion Performance (2020-2025):")
    print("\nGross:")
    print(format_metrics(metrics_gross))
    print("\nNet (10 bps):")
    print(format_metrics(metrics_net))

    gross_growth = (1.0 + gross_returns).cumprod()
    gross_growth = gross_growth / gross_growth.iloc[0]

    net_growth = (1.0 + net_returns).cumprod()
    net_growth = net_growth / net_growth.iloc[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(gross_growth.index, gross_growth, label="Mean Reversion (Gross)")
    ax.plot(net_growth.index, net_growth, label="Mean Reversion (Net)", linestyle="--")
    ax.set_title("Mean Reversion Strategy Growth ($1 Initial Investment)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if save_fig:
        out_dir = base_dir / "outputs"
        out_dir.mkdir(exist_ok=True)
        fig.savefig(out_dir / "mean_reversion.png", dpi=150)

    plt.close(fig)

    return {
        "gross_returns": gross_returns,
        "net_returns": net_returns,
        "metrics_gross": metrics_gross,
        "metrics_net": metrics_net,
        "positions": positions_eval,
        "turnover": turnover,
    }


if __name__ == "__main__":
    run_mean_reversion_strategy()
