import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("FMP_KEY")

def senate_trades_by_name(name: str):
    """
    Retrieves senate trading activity data for a specific senator by name.
    
    Parameters:
    - name (str): The name of the senator for which to retrieve trading data
    
    Returns:
    - dict: JSON response containing senate trading information including trade details,
            dates, ticker symbols, and transaction amounts for the specified senator
    """
    url = f"https://financialmodelingprep.com/stable/senate-trades-by-name?name={name}&apikey={api_key}"
    response = requests.get(url)
    return response.json()

def get_company_profile(ticker: str):
    """
    Retrieves the company profile information for a given stock ticker symbol.
    
    Parameters:
    - ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT') for which to retrieve company profile data
    
    Returns:
    - dict: JSON response containing company profile information including company name, 
            description, industry, sector, market cap, and other fundamental data
    """
    url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    return response.json()
