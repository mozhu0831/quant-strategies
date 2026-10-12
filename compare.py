
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load historical prices
prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)

# Calculate daily stock returns
returns = prices.pct_change()

# 1. Equal-weight benchmark (daily rebalanced)
weights = np.array([1/3, 1/3, 1/3])
benchmark_returns = (returns * weights).sum(axis=1, min_count=3)

# 2. Momentum strategy
lookback = 126
momentum = prices / prices.shift(lookback) - 1

# Select the highest-momentum stock each day
ranking = momentum.rank(axis=1, ascending=False)
positions = (ranking == 1).astype(float)

# Rebalance at month-end
month = prices.index.to_period("M")
month_end = month != month.shift(-1)
positions.loc[~month_end, :] = np.nan
positions = positions.ffill()

# Apply each signal to the following day's return
positions = positions.shift(1)
momentum_returns = (positions * returns).sum(axis=1, min_count=1)

# 3. Calculate cumulative growth
benchmark_growth = (1 + benchmark_returns.fillna(0)).cumprod()
momentum_growth = (1 + momentum_returns.fillna(0)).cumprod()

# Normalize both portfolios to start at $1
benchmark_growth = benchmark_growth / benchmark_growth.iloc[0]
momentum_growth = momentum_growth / momentum_growth.iloc[0]

# 4. Plot
plt.figure(figsize=(12, 6))
plt.plot(benchmark_growth.index, benchmark_growth, label="Equal-Weight Benchmark")
plt.plot(momentum_growth.index, momentum_growth, label="Momentum Strategy")

plt.title("Momentum Strategy vs Equal-Weight Benchmark")
plt.xlabel("Date")
plt.ylabel("Portfolio Growth ($1 Initial Investment)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()