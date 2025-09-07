import yfinance as yf

def get_stock_info(ticker: str) -> dict:
    """
    Retrieves a wealth of information about a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
        dict: A dictionary containing comprehensive information about the stock.
    """
    stock = yf.Ticker(ticker)
    return stock.info

def get_historical_market_data(ticker: str, period: str = '1mo', interval: str = '1d') -> str:
    """
    Retrieves historical market data for a given stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        period (str): The period for which to retrieve historical data.
                      Valid periods: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
                      Default is '1mo'.
        interval (str): The data interval.
                        Valid intervals: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
                        Default is '1d'.

    Returns:
        str: A JSON string representing the historical market data.
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist.to_json()

def get_actions(ticker: str) -> dict:
    """
    Retrieves corporate actions (dividends, splits, capital gains) for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
        dict: A dictionary containing JSON strings for dividends, splits, and capital gains.
    """
    stock = yf.Ticker(ticker)
    return {
        "dividends": stock.dividends.to_json(),
        "splits": stock.splits.to_json(),
        "capital_gains": stock.capital_gains.to_json()
    }

def get_financials(ticker: str, freq: str = 'yearly') -> dict:
    """
    Retrieves financial statements for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        freq (str): The frequency of financial data ('yearly' or 'quarterly'). Default is 'yearly'.

    Returns:
        dict: A dictionary of JSON strings for the income statement, balance sheet, and cash flow statement.
    """
    stock = yf.Ticker(ticker)
    if freq == 'quarterly':
        income_stmt = stock.quarterly_income_stmt
        balance_sheet = stock.quarterly_balance_sheet
        cash_flow = stock.quarterly_cashflow
    else:
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
    
    return {
        "income_statement": income_stmt.to_json() if income_stmt is not None else '{}',
        "balance_sheet": balance_sheet.to_json() if balance_sheet is not None else '{}',
        "cash_flow": cash_flow.to_json() if cash_flow is not None else '{}'
    }

def get_earnings(ticker: str, freq: str = 'yearly') -> dict:
    """
    Retrieves earnings data for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        freq (str): The frequency of earnings data ('yearly' or 'quarterly'). Default is 'yearly'.

    Returns:
        dict: A dictionary containing a JSON string for earnings data.
    """
    stock = yf.Ticker(ticker)
    if freq == 'quarterly':
        earnings_data = stock.quarterly_earnings
    else:
        earnings_data = stock.earnings

    return {
        "earnings": earnings_data.to_json() if earnings_data is not None else '{}'
    }

def get_earnings_dates(ticker: str, limit: int = 12) -> str:
    """
    Retrieves earnings dates for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        limit (int): The maximum number of upcoming and recent earnings dates to return. Default is 12.

    Returns:
        str: A JSON string representing the earnings dates, or an empty JSON object if none are found.
    """
    stock = yf.Ticker(ticker)
    earnings_dates_df = stock.get_earnings_dates(limit=limit)
    if earnings_dates_df is not None:
        return earnings_dates_df.to_json()
    return "{}"

def get_recommendations(ticker: str) -> str:
    """
    Retrieves analyst recommendations for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
        str: A JSON string representing analyst recommendations, or an empty JSON object if none are found.
    """
    stock = yf.Ticker(ticker)
    recommendations_df = stock.recommendations
    if recommendations_df is not None:
        return recommendations_df.to_json()
    return "{}"

def get_shareholders(ticker: str) -> dict:
    """
    Retrieves shareholder information for a stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
        dict: A dictionary containing JSON strings for major, institutional, and mutual fund holders.
    """
    stock = yf.Ticker(ticker)
    
    major_holders_df = stock.major_holders
    institutional_holders_df = stock.institutional_holders
    mutualfund_holders_df = stock.mutualfund_holders

    return {
        "major_holders": major_holders_df.to_json() if major_holders_df is not None else "{}",
        "institutional_holders": institutional_holders_df.to_json() if institutional_holders_df is not None else "{}",
        "mutualfund_holders": mutualfund_holders_df.to_json() if mutualfund_holders_df is not None else "{}"
    }
