import numpy as np
import pandas as pd

# Performance measurement metrics for backtest evaluation
def calculate_metrics(
    daily_returns,
    annual_risk_free_rate=0.04,
    benchmark_returns=None,
    turnover=None,
):
    clean_returns = daily_returns.dropna()
    if clean_returns.empty:
        raise ValueError("Cannot calculate metrics on empty returns.")

    # Total return
    total_return = np.prod(1 + clean_returns) - 1
    years = len(clean_returns) / 252

    # CAGR
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else np.nan

    # Annualized volatility
    volatility = clean_returns.std() * np.sqrt(252)

    daily_rf = (1 + annual_risk_free_rate) ** (1 / 252) - 1
    excess_returns = clean_returns - daily_rf
    excess_std = excess_returns.std()

    # Sharpe Ratio
    sharpe = (excess_returns.mean() / excess_std) * np.sqrt(252) if excess_std > 0 else np.nan

    # Max drawdown (clip peak to 1.0 to measure drawdown against initial invested capital)
    cumulative_growth = (1 + clean_returns).cumprod()
    running_peak = cumulative_growth.cummax().clip(lower=1.0)
    drawdown = cumulative_growth / running_peak - 1
    max_drawdown = drawdown.min()

    # Calmar ratio
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else np.nan

    # CAPM regression on daily excess returns against unmanaged market benchmark
    if benchmark_returns is not None:
        aligned = pd.concat([clean_returns, benchmark_returns], axis=1, join="inner").dropna()
        s_excess = aligned.iloc[:, 0] - daily_rf
        b_excess = aligned.iloc[:, 1] - daily_rf
        b_var = b_excess.var()
        if b_var > 0:
            beta = s_excess.cov(b_excess) / b_var
            alpha_daily = s_excess.mean() - beta * b_excess.mean()
            annual_alpha = alpha_daily * 252
        else:
            beta, annual_alpha = np.nan, np.nan
    else:
        beta, annual_alpha = np.nan, np.nan

    # Annual turnover rate
    if turnover is not None:
        if isinstance(turnover, (pd.Series, pd.DataFrame)):
            tot_turnover = turnover.reindex(clean_returns.index).fillna(0.0).sum()
            if isinstance(tot_turnover, pd.Series):
                tot_turnover = tot_turnover.sum()
        else:
            tot_turnover = float(turnover)
        annual_turnover = tot_turnover / years if years > 0 else np.nan
    else:
        annual_turnover = np.nan

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": max_drawdown,
        "Calmar Ratio": calmar,
        "Market Beta": beta,
        "Annualized Alpha": annual_alpha,
        "Annual Turnover": annual_turnover,
    }

# Format metrics for output
def format_metrics(metrics):
    lines = []
    format_pct = {
        "Total Return",
        "CAGR",
        "Annualized Volatility",
        "Maximum Drawdown",
        "Annualized Alpha",
        "Annual Turnover",
    }
    format_dec = {"Sharpe Ratio", "Calmar Ratio", "Market Beta"}

    for k, v in metrics.items():
        if np.isnan(v):
            continue
        if k in format_pct:
            lines.append(f"{k}: {v:.2%}")
        elif k in format_dec:
            lines.append(f"{k}: {v:.2f}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)
