import yfinance as yf
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union

class TickerArgs(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol (e.g., 'AAPL', 'MSFT').")

class HistoricalDataArgs(TickerArgs):
    period: Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']] = Field('1mo', description="The period for which to retrieve historical data.")
    interval: Optional[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']] = Field('1d', description="The data interval.")

class FinancialsArgs(TickerArgs):
    freq: Optional[Literal['yearly', 'quarterly', 'trailing']] = Field('yearly', description="The frequency of financial data ('yearly', 'quarterly', or 'trailing').")

class EarningsDatesArgs(TickerArgs):
    limit: Optional[int] = Field(12, description="The maximum number of upcoming and recent earnings dates to return.")

def get_stock_info(args: TickerArgs) -> dict:
    """
    Retrieves a wealth of information about a stock.

    Args:
        args (TickerArgs): An object containing the ticker symbol.

    Returns:
        dict: A dictionary containing comprehensive information about the stock.
    """
    ticker = yf.Ticker(args.ticker)
    return ticker.info

def get_historical_market_data(args: HistoricalDataArgs) -> str:
    """
    Retrieves historical market data for a given stock ticker.

    Args:
        args (HistoricalDataArgs): An object containing the ticker symbol, period, and interval.

    Returns:
        str: A JSON string representing the historical market data.
    """
    ticker = yf.Ticker(args.ticker)
    hist = ticker.history(period=args.period, interval=args.interval)
    return hist.to_json()

def get_actions(args: TickerArgs) -> dict:
    """
    Retrieves corporate actions (dividends, splits, capital gains) for a stock.

    Args:
        args (TickerArgs): An object containing the ticker symbol.

    Returns:
        dict: A dictionary containing DataFrames for dividends, splits, and capital gains.
    """
    ticker = yf.Ticker(args.ticker)
    return {
        "dividends": ticker.dividends.to_json(),
        "splits": ticker.splits.to_json(),
        "capital_gains": ticker.capital_gains.to_json()
    }

def get_financials(args: FinancialsArgs) -> dict:
    """
    Retrieves financial statements for a stock.

    Args:
        args (FinancialsArgs): An object containing the ticker symbol and frequency.

    Returns:
        dict: A dictionary of JSON strings for the income statement, balance sheet, and cash flow statement.
    """
    ticker = yf.Ticker(args.ticker)
    return {
        "income_statement": ticker.income_stmt.to_json(),
        "balance_sheet": ticker.balance_sheet.to_json(),
        "cash_flow": ticker.cashflow.to_json()
    }

def get_earnings(args: FinancialsArgs) -> dict:
    """
    Retrieves earnings data for a stock.

    Args:
        args (FinancialsArgs): An object containing the ticker symbol and frequency.

    Returns:
        dict: A dictionary containing JSON strings for earnings data.
    """
    ticker = yf.Ticker(args.ticker)
    return {
        "earnings": ticker.earnings.to_json()
    }

def get_earnings_dates(args: EarningsDatesArgs) -> str:
    """
    Retrieves earnings dates for a stock.

    Args:
        args (EarningsDatesArgs): An object containing the ticker symbol and a limit for the number of dates.

    Returns:
        str: A JSON string representing the earnings dates.
    """
    ticker = yf.Ticker(args.ticker)
    return ticker.earnings_dates.to_json()

def get_recommendations(args: TickerArgs) -> str:
    """
    Retrieves analyst recommendations for a stock.

    Args:
        args (TickerArgs): An object containing the ticker symbol.

    Returns:
        str: A JSON string representing analyst recommendations.
    """
    ticker = yf.Ticker(args.ticker)
    return ticker.recommendations.to_json()

def get_shareholders(args: TickerArgs) -> dict:
    """
    Retrieves shareholder information for a stock.

    Args:
        args (TickerArgs): An object containing the ticker symbol.

    Returns:
        dict: A dictionary containing JSON strings for major, institutional, and mutual fund holders.
    """
    ticker = yf.Ticker(args.ticker)
    return {
        "major_holders": ticker.major_holders.to_json(),
        "institutional_holders": ticker.institutional_holders.to_json(),
        "mutualfund_holders": ticker.mutualfund_holders.to_json()
    }
