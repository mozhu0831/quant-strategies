# Quantitative Equity Trading Strategies Research

An independent quantitative research and backtesting framework exploring two systematic equity strategies—**Momentum** and **Short-Term Mean Reversion**—against both daily-rebalanced and buy-and-hold equal-weight benchmarks over the 2020–2025 market cycle across a **50-stock sector-balanced large-cap US universe**.

---

## 1. Project Architecture

```
quant-strategies/
│
├── metrics.py            # Quantitative performance metrics & drawdown calculation
├── download_data.py      # Automated Yahoo Finance download (50 tickers with 2019 warm-up)
├── benchmark.py          # Daily-rebalanced and buy-and-hold equal-weight benchmarks
├── momentum.py           # Monthly 126-day momentum strategy (21-day skip, top_n=5)
├── mean_reversion.py     # 5-day reversal strategy (5-day rebalance frequency, top_n=5)
├── compare.py            # Head-to-head comparison engine and summary table
├── main.py               # Master end-to-end research pipeline runner
│
├── prices.csv            # Split- and dividend-adjusted daily close prices (50 stocks, 2019-2025)
├── requirements.txt      # Python dependencies
└── outputs/              # Performance charts
    ├── benchmark.png
    ├── momentum.png
    ├── mean_reversion.png
    └── strategy_comparison.png
```

---

## 2. Strategy Specifications

### A. Momentum Strategy (`momentum.py`)
- **Signal Formation Window:** 126 trading days (~6 calendar months).
- **Lag Window (Skip):** 21 trading days (~1 calendar month) to eliminate short-term reversal noise:
  $$\text{Momentum}_t = \frac{P_{t-21}}{P_{t-147}} - 1$$
- **Stock Selection:** Top decile (`top_n = 5`), equal-weighted at 20% each, neutral average rank tie-breaking.
- **Rebalancing Cadence:** Monthly at month-end.
- **Execution Lag:** 1 trading day (`shift(1)`), executing Close-to-Close from the subsequent day.
- **Transaction Costs:** 10 basis points per dollar traded.

### B. Mean-Reversion Strategy (`mean_reversion.py`)
- **Signal Formation Window:** 5 trading days:
  $$\text{Reversal}_t = \frac{P_t}{P_{t-5}} - 1$$
- **Stock Selection:** Lowest return decile (`top_n = 5`), equal-weighted at 20% each.
- **Rebalancing Cadence:** Every 5 trading days.
- **Execution Lag:** 1 trading day (`shift(1)`).
- **Transaction Costs:** 10 basis points per dollar traded.

### C. Benchmarks (`benchmark.py`)
1. **Daily-Rebalanced Equal-Weight Benchmark:** Rebalances back to $1/N$ daily across all 50 stocks.
2. **Buy-and-Hold Equal-Weight Benchmark:** Allocates $1/N$ at inception and allows portfolio weights to drift with individual stock prices (zero turnover).

---

## 3. Standardized Performance Metrics (`metrics.py`)

All metrics are evaluated across an **identical common window** (`2020-01-02` to `2025-12-31`) using a consistent **4% annual risk-free rate**:
- **Total Return:** $\prod_{t=1}^T (1 + R_t) - 1$
- **CAGR:** $(1 + \text{Total Return})^{252 / T} - 1$
- **Annualized Volatility:** $\sigma(R_t) \times \sqrt{252}$
- **Sharpe Ratio:** $\frac{\text{mean}(R_t - r_{f,\text{daily}})}{\sigma(R_t - r_{f,\text{daily}})} \times \sqrt{252}$, where $r_{f,\text{daily}} = (1 + 0.04)^{1/252} - 1$
- **Maximum Drawdown:** Anchored to initial investment capital ($1.0$).
- **Calmar Ratio:** $\frac{\text{CAGR}}{|\text{Max Drawdown}|}$
- **Market Beta:** $\beta = \frac{\text{Cov}(R_t - r_{f,\text{daily}}, R_{m,t} - r_{f,\text{daily}})}{\text{Var}(R_{m,t} - r_{f,\text{daily}})}$, evaluated against the Buy & Hold equal-weight market portfolio.
- **Annualized Alpha:** $\alpha_{\text{annual}} = (\mathbb{E}[R_t - r_f] - \beta \mathbb{E}[R_{m,t} - r_f]) \times 252$
- **Annual Turnover Rate:** $\frac{\sum \text{turnover}_t}{\text{Years}}$, where 100% turnover represents trading 100% of portfolio equity.

---

## 4. Empirical Performance Summary (2020–2025, 50 Stocks, `top_n = 5`)

| Strategy / Portfolio | Total Return | CAGR | Volatility | Sharpe (4%) | Max Drawdown | Calmar | Beta | Alpha | Turnover/yr |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benchmark (Daily Rebal Gross)** | 164.74% | 17.67% | 20.63% | 0.70 | -34.75% | 0.51 | 0.91 | -1.47% | 273.13% |
| **Benchmark (Buy-and-Hold Drift)**| 212.81% | 20.99% | 21.68% | 0.81 | -33.91% | 0.62 | 1.00 | 0.00% | 0.00% |
| **Momentum (Net 10 bps)** | **372.05%** | **29.61%** | **28.61%** | **0.91** | **-31.71%** | **0.93** | 1.07 | **+7.40%** | 858.94% |
| **Mean Reversion (Net 10 bps)** | 64.93% | 8.72% | 29.78% | 0.30 | -47.68% | 0.18 | 1.09 | -10.21% | 8866.79% |

---

## 5. Technical Assumptions & Research Limitations

1. **Survivorship Bias:** Static 50 large-cap US equities selected ex-post. In production, point-in-time historical index constituents should be used.
2. **Execution Model:** Signal generation at Close $T$ assumes execution at Close $T$ (Market-on-Close order assumption). Live execution typically incurs overnight gap risk and next-day open slippage.
3. **Transaction Cost Model:** Constant 10 bps fee does not capture spread variation or market impact during high-volatility regimes.

---

## 6. How to Run

```bash
pip install -r requirements.txt
python main.py
```
