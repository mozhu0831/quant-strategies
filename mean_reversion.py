import pandas as pd
import numpy as np


def calculate_metrics(daily_returns, annual_risk_free_rate=0.04):
    daily_returns = daily_returns.dropna()

    # Total return
    total_return = (1 + daily_returns).prod() - 1

    # CAGR
    years = len(daily_returns) / 252
    cagr = (1 + total_return) ** (1 / years) - 1

    # Annualized volatility
    volatility = daily_returns.std() * np.sqrt(252)

    # Daily risk-free rate
    daily_rf = (1 + annual_risk_free_rate) ** (1 / 252) - 1

    # Sharpe ratio using excess returns
    excess_returns = daily_returns - daily_rf
    sharpe = (
        excess_returns.mean() / excess_returns.std()
    ) * np.sqrt(252)

    # Maximum drawdown, including initial capital
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


# Load historical prices
prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)

print("Dataset shape:", prices.shape)
print("First date:", prices.index.min())
print("Last date:", prices.index.max())
print("Number of stocks:", prices.shape[1])
print("Missing prices:", prices.isna().sum().sum())
print("Duplicate dates:", prices.index.duplicated().sum())

# Calculate daily returns
returns = prices.pct_change()

# 1. Measure each stock's return over the previous 5 trading days
lookback = 5
past_returns = prices / prices.shift(lookback) - 1

# 2. Select the stock with the lowest past return
ranking = past_returns.rank(axis=1, ascending=True, method="first")
signals = (ranking == 1).astype(float)

# Keep positions missing until sufficient historical data exists
signals.loc[past_returns.notna().sum(axis=1) == 0, :] = np.nan

# 3. Rebalance every 5 trading days
rebalance_dates = pd.Series(
    np.arange(len(prices)) % 5 == 0,
    index=prices.index
)

signals.loc[~rebalance_dates, :] = np.nan

# Carry forward the last selected stock
positions = signals.ffill()

# Use the signal with a one-day lag
positions = positions.shift(1)


# Diagnostic: distinguish actual position changes from missing values
position_changes = positions.fillna(0).ne(
    positions.shift(1).fillna(0)
).any(axis=1)

print("\nActual position changes:")
print(position_changes[position_changes].head(15))

print("\nNumber of actual position changes:")
print(position_changes.sum())

print("\nFirst valid portfolio position:")
print(positions.dropna(how="all").head())


# 4. Calculate gross strategy returns (before costs)
gross_strategy_returns = (positions * returns).sum(
    axis=1, min_count=1
).dropna()

# Calculate portfolio turnover from daily weight changes
turnover = positions.fillna(0).diff().abs().sum(axis=1)

# Assume 10 basis points per dollar traded
transaction_cost_bps = 10
cost_rate = transaction_cost_bps / 10_000

# Calculate trading costs and align them with portfolio returns
trading_costs = turnover * cost_rate
trading_costs = trading_costs.reindex(
    gross_strategy_returns.index
).fillna(0)

# Net returns after estimated transaction costs
net_strategy_returns = gross_strategy_returns - trading_costs

# 5. Compare gross and net performance
for label, daily_returns in [
    ("Gross (before transaction costs)", gross_strategy_returns),
    ("Net (after transaction costs)", net_strategy_returns),
]:
    print(f"\nMean Reversion Performance — {label}")

    metrics = calculate_metrics(daily_returns)

    for metric, value in metrics.items():
        if metric == "Sharpe Ratio":
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value:.2%}")
