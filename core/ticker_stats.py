"""Valuation/profitability fundamentals + risk/performance metrics for a
ticker, shown below the price chart.

Fundamentals (P/E, P/B, PEG, dividend yield, beta) come straight from
yfinance's `Ticker.info` snapshot - Yahoo publishes these directly, no
calculation needed. `dividendYield` there is already a percentage number
(e.g. `4.46` means 4.46%), confirmed by inspecting real tickers - not a
fraction, don't multiply by 100.

Sharpe, Sortino, and alpha are NOT provided by yfinance and are computed
here from trailing 1-year daily returns. Methodology (documented since
these are opinionated, not looked up):
- Period: trailing 1 year of daily closes.
- Risk-free rate: latest 10-year Treasury yield (^TNX), annualized -
  falls back to a fixed 4% if that ticker is ever unavailable.
- Benchmark for alpha: S&P 500 (^GSPC).
- Annualization: daily mean * 252 trading days, daily std * sqrt(252).
- Alpha is CAPM alpha: actual annualized return minus the return CAPM
  would predict given the ticker's beta and the benchmark's return.
"""

from __future__ import annotations

import logging
import math

import yfinance as yf
from pydantic import BaseModel

logger = logging.getLogger(__name__)

TRADING_DAYS_PER_YEAR = 252
BENCHMARK_TICKER = "^GSPC"
RISK_FREE_TICKER = "^TNX"  # CBOE 10-year Treasury yield index, quoted as e.g. 4.25 -> 4.25%
FALLBACK_RISK_FREE_RATE = 0.04


class TickerStats(BaseModel):
    ticker: str
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    peg_ratio: float | None = None
    dividend_yield: float | None = None
    beta: float | None = None
    alpha: float | None = None
    sharpe_ratio: float | None = None
    sortino_ratio: float | None = None


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return None if math.isnan(parsed) else parsed


def _risk_free_rate() -> float:
    try:
        history = yf.Ticker(RISK_FREE_TICKER).history(period="5d")
        if history.empty:
            return FALLBACK_RISK_FREE_RATE
        return float(history["Close"].iloc[-1]) / 100
    except Exception:
        logger.exception("Failed to fetch risk-free rate, using %.0f%% fallback", FALLBACK_RISK_FREE_RATE * 100)
        return FALLBACK_RISK_FREE_RATE


def fetch_ticker_stats(ticker: str) -> TickerStats:
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info or {}

    stats = TickerStats(
        ticker=ticker,
        pe_ratio=_safe_float(info.get("trailingPE")),
        pb_ratio=_safe_float(info.get("priceToBook")),
        peg_ratio=_safe_float(info.get("trailingPegRatio")) or _safe_float(info.get("pegRatio")),
        dividend_yield=_safe_float(info.get("dividendYield")),
        beta=_safe_float(info.get("beta")),
    )

    # Sharpe/Sortino/alpha need historical returns - best-effort, so a
    # failure here still ships the fundamentals gathered above.
    try:
        history = yf_ticker.history(period="1y", interval="1d")["Close"].dropna()
        benchmark = yf.Ticker(BENCHMARK_TICKER).history(period="1y", interval="1d")["Close"].dropna()
        if len(history) < 30 or len(benchmark) < 30:
            return stats

        returns = history.pct_change().dropna()
        risk_free_annual = _risk_free_rate()
        excess_returns = returns - (risk_free_annual / TRADING_DAYS_PER_YEAR)

        std_all = returns.std()
        if std_all and std_all > 0:
            stats.sharpe_ratio = round(
                float(excess_returns.mean() / std_all * math.sqrt(TRADING_DAYS_PER_YEAR)), 3
            )

        downside = returns[returns < 0]
        downside_std = downside.std() if len(downside) > 1 else None
        if downside_std and downside_std > 0:
            stats.sortino_ratio = round(
                float(excess_returns.mean() / downside_std * math.sqrt(TRADING_DAYS_PER_YEAR)), 3
            )

        if stats.beta is not None:
            benchmark_returns = benchmark.pct_change().dropna()
            stock_r, bench_r = returns.align(benchmark_returns, join="inner")
            if len(stock_r) > 0:
                stock_annual = stock_r.mean() * TRADING_DAYS_PER_YEAR
                bench_annual = bench_r.mean() * TRADING_DAYS_PER_YEAR
                expected_return = risk_free_annual + stats.beta * (bench_annual - risk_free_annual)
                stats.alpha = round(float(stock_annual - expected_return), 4)
    except Exception:
        logger.exception("Failed to compute risk/performance stats for %s", ticker)

    return stats
