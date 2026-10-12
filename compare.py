from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from benchmark import run_benchmark
from mean_reversion import run_mean_reversion_strategy
from metrics import calculate_metrics
from momentum import run_momentum_strategy


def run_comparison(
    prices_path="prices.csv",
    eval_start="2020-01-02",
    eval_end="2025-12-31",
    save_fig=True,
):
    base_dir = Path(__file__).parent

    bench_results = run_benchmark(
        prices_path=prices_path,
        eval_start=eval_start,
        eval_end=eval_end,
        save_fig=save_fig,
    )

    mom_results = run_momentum_strategy(
        prices_path=prices_path,
        eval_start=eval_start,
        eval_end=eval_end,
        save_fig=save_fig,
    )

    mr_results = run_mean_reversion_strategy(
        prices_path=prices_path,
        eval_start=eval_start,
        eval_end=eval_end,
        save_fig=save_fig,
    )

    bnh_returns = bench_results["bnh_returns"]

    series_info = [
        ("Benchmark (Daily Rebal)", bench_results["daily_rebalanced_returns"], bench_results.get("daily_turnover")),
        ("Benchmark (Buy & Hold)", bnh_returns, 0.0),
        ("Momentum (Net)", mom_results["net_returns"], mom_results["turnover"]),
        ("Mean Reversion (Net)", mr_results["net_returns"], mr_results["turnover"]),
    ]

    returns_dict = {name: ret for name, ret, _ in series_info}
    combined_returns = pd.DataFrame(returns_dict).dropna()

    rows = []
    for name, ret, turnover in series_info:
        m = calculate_metrics(
            ret,
            annual_risk_free_rate=0.04,
            benchmark_returns=bnh_returns,
            turnover=turnover,
        )
        rows.append({
            "Strategy": name,
            "Total Return": f"{m['Total Return']:.2%}",
            "CAGR": f"{m['CAGR']:.2%}",
            "Volatility": f"{m['Annualized Volatility']:.2%}",
            "Sharpe (4%)": f"{m['Sharpe Ratio']:.2f}",
            "Max Drawdown": f"{m['Maximum Drawdown']:.2%}",
            "Calmar": f"{m['Calmar Ratio']:.2f}",
            "Beta": f"{m['Market Beta']:.2f}",
            "Alpha": f"{m['Annualized Alpha']:.2%}",
            "Turnover/yr": f"{m['Annual Turnover']:.2%}",
        })

    summary_df = pd.DataFrame(rows)
    print("\nStrategy Comparison (2020-2025):")
    print(summary_df.to_string(index=False))

    cumulative_growth = (1.0 + combined_returns).cumprod()
    cumulative_growth = cumulative_growth / cumulative_growth.iloc[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(cumulative_growth.index, cumulative_growth["Benchmark (Daily Rebal)"],
            label="Benchmark (Daily Rebal)", color="black", linestyle="--", linewidth=1.2)
    ax.plot(cumulative_growth.index, cumulative_growth["Benchmark (Buy & Hold)"],
            label="Benchmark (Buy & Hold)", color="gray", linestyle=":", linewidth=1.2)
    ax.plot(cumulative_growth.index, cumulative_growth["Momentum (Net)"],
            label="Momentum (Net)", color="royalblue", linewidth=1.5)
    ax.plot(cumulative_growth.index, cumulative_growth["Mean Reversion (Net)"],
            label="Mean Reversion (Net)", color="crimson", linewidth=1.5)

    ax.set_title("Strategy Comparison vs Benchmarks (2020-2025)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth ($1 Invested)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if save_fig:
        out_dir = base_dir / "outputs"
        out_dir.mkdir(exist_ok=True)
        fig.savefig(out_dir / "strategy_comparison.png", dpi=150)

    plt.close(fig)
    return summary_df, combined_returns


if __name__ == "__main__":
    run_comparison()