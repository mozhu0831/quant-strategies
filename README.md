# Quantitative Equity Strategies: Momentum vs. Short-Term Mean Reversion

A systematic backtest and transaction cost analysis comparing **Cross-Sectional Momentum** and **Short-Term Mean Reversion** against equal-weight benchmarks on 50 US large-cap equities (2020–2025).

The primary focus is evaluating gross-to-net alpha decay under realistic execution friction and turnover constraints across three distinct macro regimes: the 2020 liquidity shock, the 2022 rate cycle, and the 2023–2025 tech dispersion.

---

## 1. Overview & Data Hygiene

- **Universe:** 50 liquid US large-cap equities diversified across all 11 GICS sectors (Tech, Healthcare, Financials, Consumer, Energy, Industrials, etc.).
- **Evaluation Window:** January 2, 2020 to December 31, 2025 (1,509 trading days, ~6.0 years). Data from 2019 is ingested as a warm-up window to seed the 147-day rolling lookbacks without truncating the evaluation period.
- **Data Source:** Split- and dividend-adjusted closing prices downloaded via `yfinance`.
- **Execution Timing & Indexing:** Signals are computed using closing prices at day $t$, shifted forward by 1 trading day (`positions.shift(1)`), and earn the close-to-close return of day $t+1$ ($\frac{P_{t+1}}{P_t} - 1$). This structure models next-day execution while strictly eliminating same-bar lookahead leakage.
- **Drawdown Measurement:** Peak-to-trough drawdowns are computed against cumulative growth $C_t = \prod_{i=1}^t (1 + R_i)$. The historical high-watermark is floored at initial capital $1.0$ via `cummax().clip(lower=1.0)` so that drawdown calculations are never anchored below starting equity if an initial loss occurs.
- **Risk-Free Rate:** A constant $4.0\%$ annualized benchmark rate ($r_{f,\text{daily}} = (1 + 0.04)^{1/252} - 1$) applied across excess return, Sharpe ratio, and CAPM alpha regressions.

---

## 2. Strategy Specifications

### Strategy 1: Cross-Sectional Momentum (126-21)
- **Economic Rationale:** Captures intermediate-term trend continuation driven by institutional capital flows and earnings underreaction, while skipping the recent 21 trading days (~1 month) to isolate the 6-month drift from short-term reversal effects (following Jegadeesh & Titman).
- **Signal Definition:**
  $$\text{Momentum}_{i,t} = \frac{P_{i,t-21}}{P_{i,t-147}} - 1$$
- **Portfolio Construction:** Cross-sectional ranking across the 50-stock universe; selects the top decile ($\text{top\_n} = 5$, top 10%) with equal weight ($w_{i} = 20\%$).
- **Rebalancing:** Monthly on the final trading day of each month, executed for day $t+1$.

### Strategy 2: Short-Term Mean Reversion (5-Day)
- **Economic Rationale:** Exploits weekly overreaction, liquidity shocks, and short-term supply-demand imbalances in single equities, betting on rapid price normalization as liquidity providers absorb order imbalances.
- **Signal Definition:**
  $$\text{Reversal}_{i,t} = \frac{P_{i,t}}{P_{i,t-5}} - 1$$
- **Portfolio Construction:** Cross-sectional ranking across the 50-stock universe; selects the bottom decile ($\text{top\_n} = 5$, most oversold) with equal weight ($w_{i} = 20\%$).
- **Rebalancing:** Periodic every 5 trading days, executed for day $t+1$.

### Benchmarks
1. **Buy-and-Hold Equal-Weight (Market Benchmark):** Allocates $1/N = 2\%$ at inception ($2020-01-02$) and lets weights drift unmanaged. Serves as the primary CAPM market benchmark ($R_{m,t}$) with zero rebalancing turnover.
2. **Daily-Rebalanced Equal-Weight:** Rebalances all 50 stocks back to strict $2\%$ weights daily, tracking intra-day weight divergence and mechanical turnover.

---

## 3. Performance & Risk Attribution (2020–2025)

Empirical backtest metrics evaluated over the common 2020–2025 period:

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

*Note: Market Beta ($\beta$) and Annualized Alpha ($\alpha$) are estimated via OLS regression on daily excess returns against the unmanaged Buy-and-Hold market benchmark.*

---

## 4. Turnover & Execution Drag

- **Friction Model:** Linear 10 bps ($0.0010$) cost per dollar traded applied to daily two-sided portfolio weight changes:
  $$\text{Trading Cost}_t = 0.0010 \times \sum_{i=1}^N |w_{i,t} - w_{i,t-1}|$$

- **Momentum:** Controlled turnover allows high alpha retention. Monthly rebalancing generates an annual turnover of **858.94%** (~8.6 portfolio replacements per year). Friction drag accounts for only **1.11% CAGR** ($30.72\% \rightarrow 29.61\%$), preserving a net Sharpe of **0.91** and an annualized net alpha of **+7.40%**.

- **Mean Reversion:** High turnover causes catastrophic alpha decay. Rebalancing every 5 trading days produces an annual turnover of **8,866.79%** (~88.7 portfolio turns per year). Transaction costs erode **10.07% in annualized return** ($18.79\% \rightarrow 8.72\%$), dragging net alpha to **-10.21%** and Sharpe to **0.30**. 
  
  The signal demonstrates that short-horizon equity reversal cannot be monetized using aggressive market orders. Capturing this anomaly requires passive limit-order execution, maker fee rebates, or internalization.

---

## 5. Limitations & Model Assumptions

1. **Survivorship Bias:** The 50-stock basket is constructed from current large-cap constituents selected ex-post. A production backtest requires point-in-time constituent membership dynamically accounting for index deletions, acquisitions, and bankruptcies.
2. **Execution Realism:** Signals assume execution at the close of $t+1$ without modeling intraday spread widening, market impact, or auction mechanics during volatile periods.
3. **Macro Regime & Downside Exposure:** Both strategies exhibit market betas $> 1.0$ and experienced severe peak-to-trough drawdowns during the March 2020 liquidity shock (-31.7% and -47.7%). Momentum is also subject to sharp factor reversals during monetary tightening regimes (e.g., 2022). Risk-management overlays such as volatility targeting or sector neutrality are necessary to constrain factor concentration.
4. **Unconstrained Long-Only Structure:** Strategies are evaluated long-only. Extending the universe to a market-neutral long/short framework introduces short-borrow locate fees, recall risk, and hard-to-borrow constraints on oversold names.

---

## 6. Repository Architecture

```
quant-strategies/
├── metrics.py            # Performance metrics (CAGR, Sharpe, Max Drawdown, Alpha, Beta, Turnover)
├── download_data.py      # Automated Yahoo Finance data ingestion (50 stocks across 11 sectors)
├── benchmark.py          # Buy-and-Hold vs Daily-Rebalanced equal-weight benchmarks
├── momentum.py           # Monthly 126-day momentum strategy with 21-day skip
├── mean_reversion.py     # 5-day reversal strategy with 5-day rebalance frequency
├── compare.py            # Strategy comparison runner and chart generator
├── main.py               # Master end-to-end execution pipeline
├── prices.csv            # Cached split- and dividend-adjusted price matrix (2019–2025)
├── requirements.txt      # Dependency specification
└── outputs/              # Generated high-resolution performance plots
    ├── benchmark.png
    ├── momentum.png
    ├── mean_reversion.png
    └── strategy_comparison.png
```

---

## 7. Reproduction & Quickstart

```bash
# 1. Clone repository
git clone https://github.com/mozhu0831/quant-strategies.git
cd quant-strategies

# 2. Set up virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Execute backtest pipeline
python main.py
```
This runs the full data pipeline, executes all strategies and benchmarks, logs the comparison table to stdout, and exports figures to `outputs/`.
