# Systematic Equity Research: Cross-Sectional Momentum & Mean Reversion

An institutional-grade quantitative backtesting framework evaluating two canonical equity factor anomalies—**Intermediate-Term Cross-Sectional Momentum** and **Short-Term Mean Reversion**—against both Buy-and-Hold and Daily-Rebalanced equal-weight market benchmarks over a complete 6-year market cycle (2020–2025).

---

## 1. Project Overview & Data Hygiene

- **Investment Universe:** 50 liquid US large-cap equities diversified across all 11 GICS sectors (Tech, Financials, Healthcare, Consumer, Energy, Industrials, etc.).
- **Timeline & Frequency:** Daily frequency from **2020-01-02 to 2025-12-31** (1,509 trading days, 5.99 years). Historical data from 2019 is ingested as a warm-up window to seed the 147-day rolling lookbacks without truncating the evaluation window.
- **Pricing & Corporate Actions:** Adjusted closing prices reflecting dividend reinvestments and stock splits, downloaded via Yahoo Finance API (`yfinance`).
- **Lookahead Bias Prevention:** Signals are computed using closing prices at day $t$, while target portfolio weights are delayed by a strict 1-day execution lag (`positions.ffill().shift(1)`). Returns are realized between Close $t$ and Close $t+1$, preventing same-bar lookahead leakage.
- **Capital Drawdown Anchoring:** Peak equity is clipped at $1.0$ (`cummax().clip(lower=1.0)`) to ensure maximum drawdown accurately reflects capital impairment against initial funding rather than fictitious pre-inception peaks.
- **Risk-Free Rate:** A constant $4.0\%$ annual benchmark rate ($r_{f,\text{daily}} = (1 + 0.04)^{1/252} - 1$) applied consistently across Sharpe, Alpha, and Excess Return calculations.

---

## 2. Strategy Formulations

### Strategy 1: Cross-Sectional Momentum (126-21)
- **Economic Hypothesis:** Exploits intermediate-term price continuation driven by institutional capital reallocation and investor underreaction to earnings and macroeconomic trends. The 21-day skip isolates the 6-month drift from short-term 1-month reversal noise (Jegadeesh & Titman).
- **Signal Definition:**
  $$\text{Momentum}_{i,t} = \frac{P_{i,t-21}}{P_{i,t-147}} - 1$$
- **Portfolio Construction:** Cross-sectional ranking across the 50-stock universe; selects the top decile ($\text{top\_n} = 5$, top 10%) with equal weight ($w_{i} = 20\%$).
- **Rebalancing Cadence:** Monthly on the final trading day of each month, executed at market close $t+1$.

### Strategy 2: Short-Term Mean Reversion (5-Day)
- **Economic Hypothesis:** Exploits weekly overreaction, liquidity shocks, and temporary supply-demand imbalances in single equities. Assumes extreme short-term losers bounce back as liquidity providers absorb order flow.
- **Signal Definition:**
  $$\text{Reversal}_{i,t} = \frac{P_{i,t}}{P_{i,t-5}} - 1$$
- **Portfolio Construction:** Cross-sectional ranking across the 50-stock universe; selects the bottom decile ($\text{top\_n} = 5$, most oversold) with equal weight ($w_{i} = 20\%$).
- **Rebalancing Cadence:** Every 5 trading days, executed at market close $t+1$.

### Benchmark Definitions
1. **Buy-and-Hold Equal-Weight (Market Benchmark):** Allocates $1/N = 2.0\%$ at inception ($2020-01-02$) and lets weights drift unmanaged. Serves as the independent CAPM market benchmark ($R_{m,t}$) with $0\%$ rebalancing turnover.
2. **Daily-Rebalanced Equal-Weight:** Rebalances daily back to strict $2.0\%$ weights across all 50 stocks, tracking intra-day weight drift and mechanical turnover.

---

## 3. Performance & Risk Attribution Summary (2020–2025)

The table below summarizes empirical backtest results evaluated across the common 2020–2025 window:

| Metric | Buy & Hold Benchmark | Daily Rebal Benchmark | Momentum (Gross) | Momentum (Net 10 bps) | Mean Reversion (Gross) | Mean Reversion (Net 10 bps) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Return** | 212.81% | 164.74% | 396.93% | **372.05%** | 180.22% | **64.93%** |
| **CAGR (Ann. Return)** | 20.99% | 17.67% | 30.72% | **29.61%** | 18.79% | **8.72%** |
| **Annualized Volatility**| 21.68% | 20.63% | 28.61% | **28.61%** | 29.80% | **29.78%** |
| **Sharpe Ratio (4% Rf)**| 0.81 | 0.70 | 0.94 | **0.91** | 0.60 | **0.30** |
| **Max Drawdown (MDD)** | -33.91% | -34.75% | -31.63% | **-31.71%** | -47.24% | **-47.68%** |
| **Calmar Ratio** | 0.62 | 0.51 | 0.97 | **0.93** | 0.40 | **0.18** |
| **Market Beta ($\beta$)** | 1.00 | 0.91 | 1.07 | **1.07** | 1.09 | **1.09** |
| **Annualized Alpha ($\alpha$)** | 0.00% | -1.47% | +8.26% | **+7.40%** | -1.38% | **-10.21%** |
| **Annual Turnover** | 0.00% | 273.13% | 858.94% | **858.94%** | 8866.79% | **8866.79%** |

*Note: Market Beta and Annualized Alpha are computed via CAPM regression on daily excess returns against the unmanaged Buy-and-Hold benchmark.*

---

## 4. Execution Friction & Turnover Drag

- **Transaction Cost Model:** A proportional 10 basis points ($0.0010$) cost rate is levied on two-sided portfolio weight changes at each rebalance:
  $$\text{Trading Cost}_t = \text{Cost Rate} \times \sum_{i=1}^N |w_{i,t} - w_{i,t-1}|$$
- **Momentum Friction Resilience:**
  - Annual turnover is **858.94%** (~8.6 portfolio replacements per year).
  - Friction slippage erodes only **1.11% CAGR** ($30.72\% \rightarrow 29.61\%$), preserving strong statistical edge with net Sharpe of **0.91** and annualized net alpha of **+7.40%**.
- **Mean Reversion Friction Collapse:**
  - Rebalancing every 5 trading days produces an extreme annual turnover of **8,866.79%** (~88.7 portfolio turns per year).
  - Transaction costs shave off **10.07% annualized return** ($18.79\% \rightarrow 8.72\%$), collapsing the net Sharpe to **0.30** and driving alpha to **-10.21%**.
  - *Finding:* Naive market-order execution completely eradicates short-term reversal premiums. Deploying mean reversion in production requires limit-order market making, execution algorithms (TWAP/VWAP), or maker-taker exchange fee rebates.

---

## 5. Methodological Limitations & Risk Factors

1. **Survivorship Bias:** The 50-stock basket consists of current large-cap constituents selected ex-post. A production-grade backtest requires point-in-time constituent membership dynamically tracking index inclusions and delistings.
2. **Execution Realism:** Signals formed at Close $t$ assume execution at Close $t$ price (Market-on-Close simulation). Live trading is vulnerable to overnight gap risk, bid-ask spread variations, and next-day Open market impact.
3. **Regime Vulnerability:** 
   - Both strategies hold a market beta $> 1.0$ and experienced severe drawdown during the March 2020 liquidity shock (-31.7% and -47.7%).
   - Momentum exhibits substantial volatility (28.61%) and sharp drawdowns during factor rotations (e.g., 2022 tech compression). Introducing dynamic volatility targeting or sector exposure constraints is recommended.
4. **Capacity & Short Constraints:** Strategies are long-only. If extended to a long-short market-neutral implementation, short-borrow locate fees, recall risks, and margin requirements on high-beta losers would further compress net returns.

---

## 6. Repository Architecture

```
quant-strategies/
├── metrics.py            # Return, risk, drawdown, CAPM alpha/beta, and turnover engine
├── download_data.py      # Automated Yahoo Finance data ingestion (50 stocks across 11 sectors)
├── benchmark.py          # Buy-and-Hold vs Daily-Rebalanced equal-weight benchmarks
├── momentum.py           # Monthly 126-day momentum strategy with 21-day skip
├── mean_reversion.py     # 5-day reversal strategy with 5-day rebalance frequency
├── compare.py            # Multi-strategy comparison engine and summary output
├── main.py               # Master end-to-end execution pipeline
├── prices.csv            # Pre-fetched adjusted close price matrix (2019–2025)
├── requirements.txt      # Dependency specification
└── outputs/              # Generated high-resolution performance plots
    ├── benchmark.png
    ├── momentum.png
    ├── mean_reversion.png
    └── strategy_comparison.png
```

---

## 7. Quickstart & Reproduction

To reproduce all backtests, comparison tables, and visual outputs:

```bash
# 1. Clone repository
git clone https://github.com/mozhu0831/quant-strategies.git
cd quant-strategies

# 2. Set up virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Execute full backtest pipeline
python main.py
```
Outputs and performance figures are automatically populated in the terminal and saved to the `outputs/` directory.
