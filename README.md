# Quantitative Trading Strategies: Momentum vs. Mean Reversion

A backtesting and performance analysis project comparing two quantitative equity strategies—**Cross-Sectional Momentum** and **Short-Term Mean Reversion**—against equal-weight benchmarks across 50 US large-cap stocks from 2020 to 2025.

The goal of this project is to evaluate how these strategies behave across different market environments (the 2020 COVID shock, the 2022 rate-hike selloff, and the post-2023 tech rally), with a specific focus on the impact of **turnover and transaction costs** on net performance.

---

## 1. Overview & Data Setup

- **Universe:** 50 liquid US large-cap stocks diversified across all 11 GICS sectors (Tech, Healthcare, Financials, Consumer, Energy, Industrials, etc.).
- **Evaluation Period:** January 2, 2020 to December 31, 2025 (1,509 trading days). Price data from 2019 is included as a warm-up period so rolling indicators have enough history from day one.
- **Data Source:** Daily adjusted close prices fetched via `yfinance` to account for splits and dividends.
- **Execution Timing:** To prevent lookahead bias, all signals are calculated at the close of day $t$ and executed on day $t+1$ using a 1-day lag (`positions.shift(1)`).
- **Drawdown Calculation:** Peak equity is clipped at $1.0$ (`cummax().clip(lower=1.0)`) so maximum drawdown is measured against initial capital.
- **Risk-Free Rate:** 4.0% annualized risk-free rate used for excess returns, Sharpe ratio, and CAPM alpha.

---

## 2. Strategy Descriptions

### Strategy 1: Cross-Sectional Momentum (126-21)
- **Concept:** Buys intermediate-term winners. We look back roughly 6 months (126 trading days) and skip the most recent month (21 trading days) to avoid short-term reversal noise (following the Jegadeesh & Titman momentum framework).
- **Signal Formula:**
  $$\text{Momentum}_{i,t} = \frac{P_{i,t-21}}{P_{i,t-147}} - 1$$
- **Portfolio Construction:** Ranks the 50 stocks by momentum and selects the top 5 (top 10% decile), equal-weighted at 20% each.
- **Rebalance:** Monthly at month-end, executed at the close of $t+1$.

### Strategy 2: Short-Term Mean Reversion (5-Day)
- **Concept:** A short-term contrarian strategy that buys oversold stocks, betting that sharp weekly drops are driven by temporary liquidity imbalances and market overreaction that will mean-revert.
- **Signal Formula:**
  $$\text{Reversal}_{i,t} = \frac{P_{i,t}}{P_{i,t-5}} - 1$$
- **Portfolio Construction:** Ranks the 50 stocks by 5-day return and selects the 5 worst performers, equal-weighted at 20% each.
- **Rebalance:** Every 5 trading days, executed at the close of $t+1$.

### Benchmarks
1. **Buy-and-Hold Equal-Weight (Market Benchmark):** Allocates $1/N = 2\%$ to each stock at inception and lets positions drift. This serves as our primary market benchmark for CAPM beta and alpha since it has zero turnover.
2. **Daily-Rebalanced Equal-Weight:** Rebalances all 50 stocks back to equal weights daily, capturing intraday price divergence and mechanical turnover.

---

## 3. Performance Summary (2020–2025)

Backtest results over the full 2020–2025 period:

| Metric | Benchmark (Buy & Hold) | Benchmark (Daily Rebal) | Momentum (Gross) | Momentum (Net 10 bps) | Mean Reversion (Gross) | Mean Reversion (Net 10 bps) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Return** | 212.81% | 164.74% | 396.93% | **372.05%** | 180.22% | **64.93%** |
| **CAGR (Annual Return)** | 20.99% | 17.67% | 30.72% | **29.61%** | 18.79% | **8.72%** |
| **Annualized Volatility**| 21.68% | 20.63% | 28.61% | **28.61%** | 29.80% | **29.78%** |
| **Sharpe Ratio (4% Rf)**| 0.81 | 0.70 | 0.94 | **0.91** | 0.60 | **0.30** |
| **Max Drawdown** | -33.91% | -34.75% | -31.63% | **-31.71%** | -47.24% | **-47.68%** |
| **Calmar Ratio** | 0.62 | 0.51 | 0.97 | **0.93** | 0.40 | **0.18** |
| **Market Beta ($\beta$)** | 1.00 | 0.91 | 1.07 | **1.07** | 1.09 | **1.09** |
| **Annualized Alpha ($\alpha$)** | 0.00% | -1.47% | +8.26% | **+7.40%** | -1.38% | **-10.21%** |
| **Annual Turnover** | 0.00% | 273.13% | 858.94% | **858.94%** | 8866.79% | **8866.79%** |

*Note: Market Beta and Annualized Alpha are computed via CAPM linear regression against the Buy-and-Hold benchmark using daily excess returns.*

---

## 4. Turnover & Transaction Cost Takeaways

- **Cost Assumption:** 10 bps (0.10%) per trade applied to two-sided portfolio weight changes on each rebalance:
  $$\text{Cost}_t = 0.0010 \times \sum_{i=1}^N |w_{i,t} - w_{i,t-1}|$$

- **Momentum handles costs well:**
  - With monthly rebalancing, annual turnover is **858.94%** (roughly 8.6 full portfolio turnovers a year).
  - Trading costs reduce CAGR from 30.72% to 29.61% (only a **1.11% drag**), leaving a solid net Sharpe of **0.91** and **+7.40% annual alpha**.

- **Mean Reversion is crushed by turnover:**
  - Rebalancing every 5 days creates an annual turnover of **8,866.79%** (about 88 portfolio turns a year).
  - Trading costs wipe out **10.07% of annual return**, dropping CAGR from 18.79% down to 8.72% and pushing alpha deeply negative to **-10.21%**.
  - **Key takeaway:** A fast mean reversion signal might look fine on paper before costs, but it cannot be traded with naive market orders. In live trading, a strategy like this would require passive limit orders, execution algorithms (TWAP/VWAP), or maker fee rebates to survive.

---

## 5. Limitations & Future Improvements

1. **Survivorship Bias:** The 50 stocks were selected from current large-cap leaders. In a production backtest, we would use point-in-time index constituent data to include stocks that were acquired, delisted, or lost market cap.
2. **Execution Modeling:** The backtest assumes execution at the close of day $t+1$. In real trading, there is overnight gap risk, bid-ask spread variation, and market impact for larger orders.
3. **Risk & Volatility:** Both strategies have a beta above 1.0 and suffered large drawdowns during the March 2020 market crash (-31.7% and -47.7%). Adding volatility targeting or sector exposure constraints would help smooth out the risk profile.
4. **Long-Only Constraint:** The strategies are currently long-only. A market-neutral long/short version would need to account for stock borrow costs and locate availability, especially on high-beta names.

---

## 6. Project Structure

```
quant-strategies/
├── metrics.py            # Performance metrics (CAGR, Sharpe, Max Drawdown, Alpha, Beta, Turnover)
├── download_data.py      # Data downloader for 50 stocks via yfinance (2019-2025)
├── benchmark.py          # Buy-and-Hold and Daily-Rebalanced benchmarks
├── momentum.py           # 126-day momentum strategy with 21-day skip
├── mean_reversion.py     # 5-day mean reversion strategy
├── compare.py            # Strategy comparison runner and chart generator
├── main.py               # Master script to run the entire pipeline
├── prices.csv            # Cached price matrix (50 stocks, 2019-2025)
├── requirements.txt      # Python dependencies
└── outputs/              # Saved charts
    ├── benchmark.png
    ├── momentum.png
    ├── mean_reversion.png
    └── strategy_comparison.png
```

---

## 7. How to Run

```bash
# 1. Clone repository
git clone https://github.com/mozhu0831/quant-strategies.git
cd quant-strategies

# 2. Set up virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run the backtest
python main.py
```
This will run all benchmarks and strategies, print the comparison table, and save the summary charts to the `outputs/` folder.
