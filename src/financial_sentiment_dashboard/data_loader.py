# data_loader.py (Updated for Python 3.12+)
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import yfinance as yf
import investpy

# Load .env file from project root
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(env_path)

def contains_financial_data(text):
    """Check if text contains numbers, percentages, or financial indicators"""
    if not text:
        return False
    
    # Pattern for numbers, percentages, and currency
    patterns = [
        r'\$\d+(?:\.\d+)?',  # Currency with dollar sign
        r'\d+(?:\.\d+)?%',   # Percentages
        r'\d+(?:\.\d+)?',    # Numbers
        r'(?:billion|million|trillion)',  # Financial scale words
        r'(?:USD|EUR|GBP)',  # Currency codes
    ]
    
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

def get_financial_news(query="stocks", from_days_ago=1, language="en", page_size=10):
    """Fetch financial news from NewsAPI"""
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("Missing NEWS_API_KEY in environment variables")

    today = datetime.now(timezone.utc)
    from_date = (today - timedelta(days=from_days_ago)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{query} AND (market OR price OR percent OR rate)",
        "from": from_date,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": news_api_key
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError(f"Error fetching data from NewsAPI: {response.text}")

    data = response.json()
    articles = data.get("articles", [])[:10]  # Get first 10 articles
    
    df = pd.DataFrame(articles)
    return df[["title", "description", "publishedAt"]]

def load_local_data(file_path):
    """
    Load data from a local CSV or Excel file into a Pandas DataFrame.

    :param file_path: Path to the CSV or Excel file.
    :return: A Pandas DataFrame containing the loaded data.
    """
    if file_path.lower().endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.lower().endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .csv or .xlsx file.")

def fetch_related_financial_data(news_df):
    """Fetch related financial data files for each news headline"""
    data_sources = []
    
    # Limit to top 5 most common companies for speed
    common_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    for symbol in common_symbols[:3]:  # Only use first 3 for faster execution
        try:
            print(f"Fetching data for {symbol}...")
            
            # Fetch only 7 days of stock data
            stock_data = yf.download(
                symbol,
                start=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d'),
                progress=False
            )
            
            if not stock_data.empty:
                # Save stock price data
                file_path = f"resources/stock_data_{symbol}.csv"
                stock_data.to_csv(file_path)
                data_sources.append({
                    'symbol': symbol,
                    'data_type': 'stock_prices',
                    'file_path': file_path,
                    'data_points': len(stock_data)
                })
                print(f"Saved stock data for {symbol}")
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            continue
    
    # Create DataFrame and save data source mapping
    if data_sources:
        sources_df = pd.DataFrame(data_sources)
        sources_df.to_csv("resources/data_sources.csv", index=False)
        print(f"Saved {len(data_sources)} data sources to data_sources.csv")
        return sources_df
    else:
        print("No financial data sources were collected")
        return pd.DataFrame()

def extract_company_symbols(text):
    """Extract company symbols from text"""
    # Common company names and their symbols
    company_mapping = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'nvidia': 'NVDA',
        'meta': 'META',
        'facebook': 'META',
        'netflix': 'NFLX'
    }
    
    found_symbols = set()
    text = text.lower()
    
    # Look for company names in text
    for company, symbol in company_mapping.items():
        if company in text:
            found_symbols.add(symbol)
    
    # Look for stock symbols in text (assumed to be in uppercase)
    symbol_pattern = r'\b[A-Z]{1,5}\b'  # 1-5 uppercase letters
    import re
    potential_symbols = re.findall(symbol_pattern, text.upper())
    
    # Verify if potential symbols are valid
    for symbol in potential_symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Quick check if it's a valid symbol
            if ticker.info.get('regularMarketPrice'):
                found_symbols.add(symbol)
        except:
            continue
    
    return list(found_symbols)

# Direct execution test
if __name__ == "__main__":
    try:
        print("Testing data loader...")
        
        # Create resources directory
        Path("resources").mkdir(exist_ok=True)
        
        # Step 1: Fetch news
        print("\nFetching financial news...")
        df_news = get_financial_news(query="tech stocks", from_days_ago=2)
        df_news.to_csv("resources/news_data.csv", index=False)
        print(f"Saved {len(df_news)} news articles to news_data.csv")
        
        # Step 2: Fetch related financial data
        print("\nFetching related financial data...")
        sources_df = fetch_related_financial_data(df_news)
        
        # Print summary
        print("\nSummary:")
        print(f"- News articles collected: {len(df_news)}")
        print(f"- Financial datasets collected: {len(sources_df) if not sources_df.empty else 0}")
        print("\nCheck the 'resources' directory for the collected data files.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
