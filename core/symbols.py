"""Shape checks for ticker symbols.

Format only - they don't prove the security exists. They keep arbitrary user
input out of yfinance calls and the database.

- is_us_symbol: US-style (AMD, TSLA, BRK-B). Matches the CHECK constraint on
  explanation_requests.ticker, so it gates anything that writes a ticker.
- is_valid_symbol: also allows Canadian listings (XEQT.TO on the TSX, FBAL.NE
  on NEO, .V on TSX Venture) for read-only market data.
"""

import re

US_SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}(-[A-Z])?$")
SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}(-[A-Z])?(\.(TO|NE|V))?$")


def is_us_symbol(symbol: str) -> bool:
    return US_SYMBOL_PATTERN.fullmatch(symbol) is not None


def is_valid_symbol(symbol: str) -> bool:
    return SYMBOL_PATTERN.fullmatch(symbol) is not None
