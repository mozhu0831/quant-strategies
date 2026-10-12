
import pandas as pd
import numpy as np

def calculate_metrics(daily_returns, annual_risk_free_rate=0.04):
    daily_returns = daily_returns.dropna()

    if daily_returns.empty:
        raise ValueError("Cannot calculate metrics: no valid returns.")

    # Total cumulative return
    total_return = (1 + daily_returns).prod() - 1

    # Compound annual growth rate (CAGR)
    years = len(daily_returns) / 252
    cagr = (1 + total_return) ** (1 / years) - 1

    # Annualized volatility
    volatility = daily_returns.std() * np.sqrt(252)

    daily_rf = (1 + annual_risk_free_rate) ** (1 / 252) - 1

    # Annualized Sharpe ratio
    excess_returns = daily_returns - daily_rf
    excess_std = excess_returns.std()

    if excess_std == 0:
        sharpe = np.nan
    else:
        sharpe = (
            excess_returns.mean() / excess_std
        ) * np.sqrt(252)

    # Maximum drawdown
    cumulative_growth = (1 + daily_returns).cumprod()
    running_peak = cumulative_growth.cummax().clip(lower=1.0)
    drawdown = cumulative_growth / running_peak - 1
    max_drawdown = drawdown.min()

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": max_drawdown,
    }


# --------------------------------------------------
# 2. Load historical price data
# --------------------------------------------------

prices = pd.read_csv(
    "prices.csv",
    index_col=0,
    parse_dates=True
).sort_index()


# --------------------------------------------------
# 3. Define momentum strategy parameters
# --------------------------------------------------

lookback = 126
skip_recent = 21

# Your current universe has only three stocks.
# Select the single stock with the strongest momentum.
top_n = 1


# --------------------------------------------------
# 4. Calculate momentum signals
# --------------------------------------------------

# Compare the price 21 trading days ago with the price
# 126 trading days ago, excluding the most recent 21 days.
momentum = prices.shift(skip_recent) / prices.shift(lookback) - 1

# Rank stocks from strongest to weakest momentum.
# Rank 1 represents the strongest momentum.
ranking = momentum.rank(
    axis=1,
    ascending=False,
    method="first"
)

# Select the top-ranked stocks.
positions = (
    (ranking <= top_n)
    .where(momentum.notna())
    .astype(float)
)

# Convert selected stocks into portfolio weights.
# With top_n = 1, the selected stock receives a 100% weight.
row_totals = positions.sum(axis=1).replace(0, np.nan)
positions = positions.div(row_totals, axis=0)


# --------------------------------------------------
# 5. Rebalance monthly
# --------------------------------------------------

# Convert the months into a Series so shift(-1) moves
# the next row's value, rather than shifting month labels.
month = pd.Series(
    prices.index.to_period("M"),
    index=prices.index
)

# Identify the final trading date of each month.
month_end = month.ne(month.shift(-1))

# Keep signals only on month-end dates.
positions.loc[~month_end, :] = np.nan

# Carry the last month-end portfolio weights forward.
positions = positions.ffill()

# Apply each new portfolio target from the following
# trading day to avoid using a signal on the same day's return.
positions = positions.shift(1)


# --------------------------------------------------
# 6. Calculate gross strategy returns
# --------------------------------------------------

returns = prices.pct_change()

gross_returns = (
    positions * returns
).sum(axis=1, min_count=1).dropna()


# --------------------------------------------------
# 7. Calculate turnover and transaction costs
# --------------------------------------------------

# Treat missing portfolio weights as cash / no position.
weights = positions.fillna(0.0)

# Compare today's weights with the previous trading day's weights.
# This also captures the initial investment automatically.
previous_weights = weights.shift(1).fillna(0.0)

turnover = (
    weights - previous_weights
).abs().sum(axis=1)

# Assumed transaction cost per dollar traded.
# 10 basis points = 0.10% = 0.001.
transaction_cost_bps = 10
cost_rate = transaction_cost_bps / 10_000

# Estimate transaction costs as a fraction of portfolio value.
trading_costs = turnover * cost_rate

# Align costs with the dates used to calculate strategy returns.
trading_costs = trading_costs.reindex(
    gross_returns.index
).fillna(0.0)

# Net daily returns after estimated transaction costs.
net_returns = gross_returns - trading_costs


# --------------------------------------------------
# 8. Compare gross and net performance
# --------------------------------------------------

for label, daily_returns in [
    ("Gross (before transaction costs)", gross_returns),
    ("Net (after transaction costs)", net_returns),
]:
    print(f"\nMomentum Performance — {label}")

    metrics = calculate_metrics(daily_returns)

    for metric, value in metrics.items():
        if metric == "Sharpe Ratio":
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value:.2%}")

print(f"\nSelected stocks per rebalance: {top_n}")
print(f"Transaction cost assumption: {transaction_cost_bps} bps per dollar traded")
