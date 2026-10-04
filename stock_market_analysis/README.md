# Stock Market Analysis

Analyze historical stock-market data to identify trends and patterns in prices over time, then compare performance against moving averages and trading volume.

This project fulfills **PR Final Project – Task 5: Stock Market Analysis**.

## What the analysis covers

- Download of daily adjusted prices and volume from **Yahoo Finance** via `yfinance`
- Trend detection with **20 / 50 / 200-day simple moving averages**
- Trading-volume patterns vs a 20-day average volume
- Normalized performance (all series start at 100) for fair comparison
- Daily-return **correlation** across tickers
- Rolling **30-day annualized volatility**
- **RSI (14)** as a short-term momentum indicator
- Drawdowns from peak price
- Volume vs return scatter plots
- Summary metrics: total return, annualized return, volatility, Sharpe ratio, max drawdown

## Universe and period

| Item | Choice |
| --- | --- |
| Tickers | AAPL, MSFT, GOOGL, AMZN, NVDA, SPY |
| Start | 2021-01-01 |
| End | 2026-10-04 |
| Price field | Adjusted close (`auto_adjust=True`) |

SPY is included as a broad U.S. market benchmark (S&P 500 ETF).

## Tools / libraries

- **pandas** — load, clean, and join time series
- **NumPy** — returns, annualization, RSI math
- **matplotlib** and **seaborn** — charts and the correlation heatmap
- **yfinance** — Yahoo Finance historical prices

## How to run

From this folder:

```bash
pip install -r requirements.txt
python stock_analysis.py
```

Internet access is required on the first run so `yfinance` can download prices. After a successful run you will have:

```
stock_market_analysis/
├── stock_analysis.py
├── requirements.txt
├── README.md
├── data/                 # adjusted_close.csv, volume.csv
├── charts/               # PNG figures
└── outputs/              # summary tables and return series
```

## Assumptions (documented as required)

1. **Adjusted close** is the correct series for return and trend work because it accounts for splits and dividends.
2. Missing prices are **forward-filled**. Gaps under 5% of the sample are treated as non-trading days or short outages, not as true missing history.
3. Returns are **simple daily percentage changes**, not log returns. Annualization uses **252 trading days**.
4. Sharpe ratio uses a **0% risk-free rate**. That keeps the metric transparent; it is not a full CAPM estimate.
5. SMA windows **20 / 50 / 200** are conventional short-, medium-, and long-term trend filters used by market technicians.
6. RSI uses a **14-day** simple average of gains and losses (Wilder-style window, SMA implementation). Readings above 70 / below 30 are treated as stretched, not as automatic buy/sell signals.
7. NVDA, AAPL, and SPY get the full chart pack (price+SMA, volume, RSI, drawdown, volume vs return). Other tickers still get price+SMA charts plus the shared universe plots.
8. This is **descriptive analysis**, not investment advice and not a trading strategy backtest.
9. Yahoo Finance data can be revised after the fact. Results depend on the snapshot downloaded at runtime.

## Results from the latest run (data through 2026-10-04)

| Ticker | Total return | Ann. return | Ann. volatility | Sharpe | Max drawdown |
| --- | ---: | ---: | ---: | ---: | ---: |
| NVDA | 1693.24% | 65.55% | 50.58% | 1.30 | -66.34% |
| GOOGL | 301.79% | 27.49% | 31.28% | 0.88 | -44.32% |
| AAPL | 165.61% | 18.60% | 27.70% | 0.67 | -33.36% |
| MSFT | 149.33% | 17.30% | 27.30% | 0.63 | -37.15% |
| SPY | 125.31% | 15.24% | 16.64% | 0.92 | -24.50% |
| AMZN | 57.86% | 8.30% | 35.07% | 0.24 | -56.15% |

- NVDA led both total return and Sharpe, but with the deepest drawdown and highest volatility.
- SPY had the lowest volatility and a stronger Sharpe than AAPL/MSFT despite a smaller total return.
- AAPL had the highest daily-return correlation with SPY (~0.71).
- AMZN lagged the group on return and Sharpe over this window.

Re-run `python stock_analysis.py` to refresh numbers if Yahoo revises history.

## How to read the charts

- **Price vs SMA**: price above a rising 200-day SMA is a long-term uptrend; a 20-day cross of the 50-day SMA is a shorter-term shift.
- **Volume**: unusually high bars next to large price moves show where participation was concentrated.
- **Normalized performance**: isolates relative strength regardless of the raw share price.
- **Correlation heatmap**: high correlation with SPY means the name moved with the market on a daily basis.
- **Drawdown**: peak-to-trough pain; useful when comparing “high return” names that also had deep slumps.

## Original work

All source code and documentation in this repository were written for this assignment. Do not copy classmates’ work. If you reuse a public dataset definition (Yahoo Finance / yfinance), keep the attribution as shown above.

## Submission

1. Create a GitHub repository.
2. Upload this folder (source, README, charts, and outputs).
3. Send the repository URL to your instructor.

Good luck with the project.
