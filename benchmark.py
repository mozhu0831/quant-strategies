import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_metrics(daily_returns):
    daily_returns = daily_returns.dropna()

    # Total return
    total_return = (1 + daily_returns).prod() - 1

    # CAGR
    year = len(daily_returns) / 252
    cagr = (1 + total_return) ** (1 / year) - 1

    # Annualized volatility
    volatility = daily_returns.std() * np.sqrt(252)

    # Sharpe ratio
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

    # Maximum drawdown
    cumulative_growth = (1 + daily_returns).cumprod()
    running_peak = cumulative_growth.cummax()
    drawdown = cumulative_growth / running_peak - 1
    max_drawdown = drawdown.min()

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": max_drawdown,
    }


prices = pd.read_csv("prices.csv", index_col = 0, parse_dates = True)

returns = prices.pct_change()

print("Price data:")
print(prices.head())

print("\nDaily returns:")
print(returns.head())

weights = np.array([1/3, 1/3, 1/3])
portfolio_returns = (returns * weights).sum(axis = 1, min_count = 3)

metrics = calculate_metrics(portfolio_returns)

print("\nPortfolio Performance Metrics:")
for metric, value in metrics.items():
    if metric == "Sharpe Ratio":
        print(f"{metric}: {value:.2f}")
    else:
        print(f"{metric}: {value:.2%}")


print("\nDaily portfolio returns:")
print(portfolio_returns.head())

initial_capital = 1000
cumulative_returns = (1 + portfolio_returns.fillna(0)).cumprod()
portfolio_value = initial_capital * cumulative_returns

print("\nPortfolio value:")
print(portfolio_value.tail())

print("\nFinal portfolio value:")
print(round((portfolio_value.iloc[-1]), 3))

plt.plot(portfolio_value.index, portfolio_value)
plt.title("Daily Rebalanced Equal-weight portfolio")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.grid(True)
plt.show()