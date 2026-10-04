"""
Stock Market Analysis
---------------------
Analyze historical stock prices to identify trends and patterns.
Visualize performance against moving averages and trading volume.

Libraries: pandas, numpy, matplotlib, seaborn, yfinance
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "SPY"]
START_DATE = "2021-01-01"
END_DATE = "2026-10-04"

SMA_WINDOWS = (20, 50, 200)
VOLUME_MA_WINDOW = 20
VOLATILITY_WINDOW = 30
RSI_WINDOW = 14

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHART_DIR = BASE_DIR / "charts"
OUTPUT_DIR = BASE_DIR / "outputs"

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (14, 7)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11


def ensure_dirs() -> None:
    for folder in (DATA_DIR, CHART_DIR, OUTPUT_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _download_one(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download a single ticker. Retry a few times because yfinance can lock its cache."""
    last_error = None
    for attempt in range(1, 4):
        try:
            frame = yf.download(
                ticker,
                start=start,
                end=end,
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if frame.empty:
                raise RuntimeError(f"{ticker}: empty download")
            frame = frame.rename(columns=str.title)
            out = pd.DataFrame(
                {
                    "Close": frame["Close"].squeeze(),
                    "Volume": frame["Volume"].squeeze(),
                }
            )
            out.columns = pd.MultiIndex.from_product([["Close", "Volume"], [ticker]])
            return out
        except Exception as exc:  # noqa: BLE001 — keep the pipeline moving across tickers
            last_error = exc
            print(f"  retry {attempt}/3 for {ticker}: {exc}")
    raise RuntimeError(f"Failed to download {ticker}: {last_error}")


def download_prices(tickers: list[str], start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Download adjusted OHLCV data from Yahoo Finance, one ticker at a time."""
    print(f"Downloading {tickers} from {start} to {end} ...")
    pieces = []
    failed = []
    for ticker in tickers:
        try:
            pieces.append(_download_one(ticker, start, end))
            print(f"  downloaded {ticker}")
        except Exception as exc:  # noqa: BLE001
            failed.append(ticker)
            print(f"  skipped {ticker}: {exc}")

    if not pieces:
        raise RuntimeError("Yahoo Finance returned no data. Check network access.")

    raw = pd.concat(pieces, axis=1).sort_index()
    close = raw["Close"].copy()
    volume = raw["Volume"].copy()

    empty_cols = [col for col in close.columns if close[col].isna().all()]
    if empty_cols:
        print(f"Dropping empty tickers: {empty_cols}")
        close = close.drop(columns=empty_cols)
        volume = volume.drop(columns=empty_cols, errors="ignore")

    close = close.sort_index().ffill()
    volume = volume.reindex(close.index).fillna(0)

    missing = close.isna().mean()
    if (missing > 0.05).any():
        print("Warning: some tickers have more than 5% missing closes:")
        print(missing[missing > 0.05].to_string())

    if failed:
        print(f"Tickers that could not be downloaded: {failed}")

    close.to_csv(DATA_DIR / "adjusted_close.csv")
    volume.to_csv(DATA_DIR / "volume.csv")
    print(f"Saved raw series to {DATA_DIR}")
    return close, volume


def daily_returns(close: pd.DataFrame) -> pd.DataFrame:
    """Simple daily percentage returns."""
    filled = close.ffill()
    return filled.pct_change(fill_method=None).dropna(how="all")


def cumulative_returns(returns: pd.DataFrame) -> pd.DataFrame:
    return (1 + returns).cumprod() - 1


def rolling_volatility(returns: pd.DataFrame, window: int) -> pd.DataFrame:
    """Annualized rolling volatility from daily returns (252 trading days)."""
    return returns.rolling(window).std() * np.sqrt(252)


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index using simple moving averages of gains/losses."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def max_drawdown(close: pd.Series) -> float:
    running_max = close.cummax()
    drawdown = close / running_max - 1
    return float(drawdown.min())


def summary_table(close: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker in close.columns:
        price = close[ticker].dropna()
        ret = returns[ticker].dropna()
        if price.empty or ret.empty:
            continue
        total_return = price.iloc[-1] / price.iloc[0] - 1
        ann_return = (1 + total_return) ** (252 / len(ret)) - 1
        ann_vol = ret.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol else np.nan
        rows.append(
            {
                "ticker": ticker,
                "start_price": round(price.iloc[0], 2),
                "end_price": round(price.iloc[-1], 2),
                "total_return_pct": round(total_return * 100, 2),
                "annualized_return_pct": round(ann_return * 100, 2),
                "annualized_volatility_pct": round(ann_vol * 100, 2),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_drawdown(price) * 100, 2),
                "avg_daily_return_pct": round(ret.mean() * 100, 4),
            }
        )
    table = pd.DataFrame(rows).set_index("ticker")
    table.to_csv(OUTPUT_DIR / "summary_statistics.csv")
    return table


def plot_close_with_sma(close: pd.DataFrame, ticker: str) -> None:
    price = close[ticker].dropna()
    fig, ax = plt.subplots()
    ax.plot(price.index, price, color="#1f77b4", linewidth=1.4, label="Adj Close")
    colors = ["#ff7f0e", "#2ca02c", "#d62728"]
    for window, color in zip(SMA_WINDOWS, colors):
        sma = price.rolling(window).mean()
        ax.plot(sma.index, sma, color=color, linewidth=1.2, label=f"SMA {window}")
    ax.set_title(f"{ticker} Price vs Moving Averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker}_price_sma.png", dpi=150)
    plt.close(fig)


def plot_volume(volume: pd.DataFrame, ticker: str) -> None:
    vol = volume[ticker].dropna()
    vol_ma = vol.rolling(VOLUME_MA_WINDOW).mean()
    fig, ax = plt.subplots()
    ax.bar(vol.index, vol, color="#9ecae1", width=1.0, label="Daily volume")
    ax.plot(vol_ma.index, vol_ma, color="#08306b", linewidth=1.5, label=f"{VOLUME_MA_WINDOW}-day avg volume")
    ax.set_title(f"{ticker} Trading Volume")
    ax.set_xlabel("Date")
    ax.set_ylabel("Shares traded")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker}_volume.png", dpi=150)
    plt.close(fig)


def plot_normalized_performance(close: pd.DataFrame) -> None:
    """Index each series to 100 at the first common date."""
    aligned = close.dropna(how="any")
    if aligned.empty:
        aligned = close.dropna(how="all")
    if aligned.empty:
        print("Skipping normalized performance chart: no price data.")
        return
    indexed = aligned / aligned.iloc[0] * 100
    fig, ax = plt.subplots()
    for ticker in indexed.columns:
        ax.plot(indexed.index, indexed[ticker], linewidth=1.5, label=ticker)
    ax.set_title("Normalized Performance (Start = 100)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Indexed price")
    ax.legend(ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "normalized_performance.png", dpi=150)
    plt.close(fig)


def plot_correlation(returns: pd.DataFrame) -> None:
    if returns.shape[1] < 2:
        print("Skipping correlation heatmap: need at least two tickers.")
        return
    corr = returns.corr()
    corr.to_csv(OUTPUT_DIR / "return_correlation.csv")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax, square=True)
    ax.set_title("Daily Return Correlation")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "return_correlation.png", dpi=150)
    plt.close(fig)


def plot_volatility(returns: pd.DataFrame) -> None:
    vol = rolling_volatility(returns, VOLATILITY_WINDOW)
    fig, ax = plt.subplots()
    for ticker in vol.columns:
        ax.plot(vol.index, vol[ticker], linewidth=1.2, label=ticker)
    ax.set_title(f"{VOLATILITY_WINDOW}-Day Annualized Rolling Volatility")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility")
    ax.legend(ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "rolling_volatility.png", dpi=150)
    plt.close(fig)


def plot_rsi(close: pd.DataFrame, ticker: str) -> None:
    values = rsi(close[ticker], RSI_WINDOW)
    fig, ax = plt.subplots()
    ax.plot(values.index, values, color="#6a3d9a", linewidth=1.3, label=f"RSI {RSI_WINDOW}")
    ax.axhline(70, color="#d62728", linestyle="--", linewidth=1, label="Overbought (70)")
    ax.axhline(30, color="#2ca02c", linestyle="--", linewidth=1, label="Oversold (30)")
    ax.set_ylim(0, 100)
    ax.set_title(f"{ticker} Relative Strength Index")
    ax.set_xlabel("Date")
    ax.set_ylabel("RSI")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker}_rsi.png", dpi=150)
    plt.close(fig)


def plot_drawdown(close: pd.DataFrame, ticker: str) -> None:
    price = close[ticker].dropna()
    drawdown = price / price.cummax() - 1
    fig, ax = plt.subplots()
    ax.fill_between(drawdown.index, drawdown, 0, color="#d62728", alpha=0.45)
    ax.plot(drawdown.index, drawdown, color="#7f0000", linewidth=0.8)
    ax.set_title(f"{ticker} Drawdown from Peak")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker}_drawdown.png", dpi=150)
    plt.close(fig)


def plot_volume_vs_return(close: pd.DataFrame, volume: pd.DataFrame, ticker: str) -> None:
    """Scatter of daily return vs log volume to check volume-price relationship."""
    ret = close[ticker].pct_change()
    log_vol = np.log1p(volume[ticker])
    frame = pd.DataFrame({"daily_return": ret, "log_volume": log_vol}).dropna()
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=frame,
        x="log_volume",
        y="daily_return",
        ax=ax,
        alpha=0.35,
        s=18,
        color="#1f77b4",
        edgecolor=None,
    )
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(f"{ticker} Daily Return vs Log Volume")
    ax.set_xlabel("log(1 + volume)")
    ax.set_ylabel("Daily return")
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker}_volume_vs_return.png", dpi=150)
    plt.close(fig)


def print_insights(table: pd.DataFrame, returns: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("SUMMARY STATISTICS")
    print("=" * 72)
    print(table.to_string())

    best = table["total_return_pct"].idxmax()
    worst = table["total_return_pct"].idxmin()
    most_vol = table["annualized_volatility_pct"].idxmax()
    best_sharpe = table["sharpe_ratio"].idxmax()

    spy_corr = returns.corr().loc[:, "SPY"].drop(labels=["SPY"], errors="ignore")
    closest_to_market = spy_corr.abs().idxmax() if not spy_corr.empty else "n/a"

    print("\n" + "=" * 72)
    print("KEY FINDINGS")
    print("=" * 72)
    print(f"- Highest total return: {best} ({table.loc[best, 'total_return_pct']:.2f}%).")
    print(f"- Lowest total return: {worst} ({table.loc[worst, 'total_return_pct']:.2f}%).")
    print(f"- Highest annualized volatility: {most_vol} ({table.loc[most_vol, 'annualized_volatility_pct']:.2f}%).")
    print(f"- Best Sharpe ratio (return per unit of risk): {best_sharpe} ({table.loc[best_sharpe, 'sharpe_ratio']:.2f}).")
    if closest_to_market != "n/a":
        print(
            f"- Closest daily-return correlation with SPY: {closest_to_market} "
            f"({spy_corr.loc[closest_to_market]:.2f})."
        )
    print("- SMA 20/50/200 charts show short-, medium-, and long-term trend direction.")
    print("- Volume spikes often line up with large price moves (see volume vs return plots).")
    print("- RSI above 70 / below 30 flags potentially stretched short-term conditions.")


def main() -> None:
    ensure_dirs()
    close, volume = download_prices(TICKERS, START_DATE, END_DATE)
    returns = daily_returns(close)
    cum = cumulative_returns(returns)
    cum.to_csv(OUTPUT_DIR / "cumulative_returns.csv")
    returns.to_csv(OUTPUT_DIR / "daily_returns.csv")

    table = summary_table(close, returns)

    print("Building charts ...")
    plot_normalized_performance(close)
    plot_correlation(returns)
    plot_volatility(returns)

    focus = ["AAPL", "NVDA", "SPY"]
    for ticker in focus:
        if ticker not in close.columns:
            continue
        plot_close_with_sma(close, ticker)
        plot_volume(volume, ticker)
        plot_rsi(close, ticker)
        plot_drawdown(close, ticker)
        plot_volume_vs_return(close, volume, ticker)

    # SMA snapshots for remaining names so the full universe is covered.
    for ticker in close.columns:
        if ticker not in focus:
            plot_close_with_sma(close, ticker)

    print_insights(table, returns)
    print(f"\nCharts saved to: {CHART_DIR}")
    print(f"Tables saved to: {OUTPUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
