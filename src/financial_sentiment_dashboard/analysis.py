import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf
from scipy import stats

def analyze_trends(df, time_period='daily'):
    """
    Analyze sentiment trends over different time periods.
    
    Args:
        df (pandas.DataFrame): DataFrame with sentiment data
        time_period (str): 'daily', 'weekly', or 'monthly'
    
    Returns:
        pandas.DataFrame: Aggregated sentiment trends
    """
    # Ensure datetime format
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    
    # Group by time period
    if time_period == 'weekly':
        df['period'] = df['publishedAt'].dt.isocalendar().week
    elif time_period == 'monthly':
        df['period'] = df['publishedAt'].dt.month
    else:  # daily
        df['period'] = df['publishedAt'].dt.date
    
    # Calculate sentiment distributions
    sentiment_dist = df.groupby(['period', 'sentiment']).size().unstack(fill_value=0)
    
    # Calculate percentages
    sentiment_dist_pct = sentiment_dist.div(sentiment_dist.sum(axis=1), axis=0) * 100
    
    return {
        'counts': sentiment_dist,
        'percentages': sentiment_dist_pct
    }

def calculate_statistics(df):
    """
    Calculate various statistics from the sentiment data.
    
    Args:
        df (pandas.DataFrame): DataFrame with sentiment data
    
    Returns:
        dict: Dictionary containing various statistics
    """
    stats = {
        'total_articles': len(df),
        'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
        'avg_confidence': df['confidence_score'].mean(),
        'sentiment_by_confidence': df.groupby('sentiment')['confidence_score'].mean().to_dict()
    }
    
    # Calculate daily sentiment shifts
    daily_sentiment = df.groupby(pd.to_datetime(df['publishedAt']).dt.date)['sentiment'].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else None
    )
    stats['sentiment_shifts'] = (daily_sentiment != daily_sentiment.shift()).sum()
    
    # Calculate volatility (how much sentiment changes)
    sentiment_numeric = pd.get_dummies(df['sentiment'])
    stats['sentiment_volatility'] = sentiment_numeric.std().mean()
    
    return stats

def get_trending_topics(df, n_topics=5):
    """
    Identify trending topics in the news headlines.
    
    Args:
        df (pandas.DataFrame): DataFrame with news headlines
        n_topics (int): Number of top topics to return
    
    Returns:
        dict: Dictionary of trending topics and their frequencies
    """
    # Combine all titles
    all_titles = ' '.join(df['title'].dropna())
    
    # Simple word frequency analysis (could be enhanced with NLP)
    words = all_titles.lower().split()
    word_freq = pd.Series(words).value_counts()
    
    # Remove common words (simple stopwords)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    word_freq = word_freq[~word_freq.index.isin(stopwords)]
    
    return word_freq.head(n_topics).to_dict()

def load_stock_data(symbol):
    """Load stock data for analysis"""
    try:
        file_path = f"resources/stock_data_{symbol}.csv"
        # Fix date parsing and ensure numeric columns
        df = pd.read_csv(file_path)
        
        # Print columns for debugging
        print(f"Available columns: {df.columns.tolist()}")
        
        # Convert index to datetime
        df['Date'] = pd.to_datetime(df.index)
        df = df.set_index('Date')
        
        # Ensure numeric types for calculations
        # Use only columns that exist in the data
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"No data file found for {symbol}")
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")

def technical_analysis(df):
    """Perform technical analysis on stock data"""
    analysis = {}
    
    try:
        # Calculate moving averages
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        # Calculate daily returns
        df['Returns'] = df['Close'].pct_change()
        
        # Volatility (standard deviation of returns)
        analysis['volatility'] = df['Returns'].std() * np.sqrt(252)  # Annualized
        
        # Trend analysis
        analysis['trend'] = 'Upward' if df['Close'].iloc[-1] > df['MA20'].iloc[-1] else 'Downward'
        
        # Trading volume analysis
        if 'Volume' in df.columns:
            analysis['avg_volume'] = df['Volume'].mean()
            analysis['volume_trend'] = 'Increasing' if df['Volume'].iloc[-1] > df['Volume'].mean() else 'Decreasing'
        
        return analysis
    except Exception as e:
        print(f"Error in technical analysis: {str(e)}")
        return {}

def statistical_analysis(df):
    """Perform statistical analysis on stock data"""
    try:
        # Calculate returns if not already calculated
        if 'Returns' not in df.columns:
            df['Returns'] = df['Close'].pct_change()
            
        stats_data = {
            'daily_return_mean': df['Returns'].mean(),
            'daily_return_std': df['Returns'].std(),
            'skewness': stats.skew(df['Returns'].dropna()),
            'kurtosis': stats.kurtosis(df['Returns'].dropna()),
            'sharpe_ratio': (df['Returns'].mean() / df['Returns'].std()) * np.sqrt(252) if df['Returns'].std() != 0 else 0
        }
        
        # Add volume correlation if volume data exists
        if 'Volume' in df.columns:
            stats_data['price_correlation'] = df['Close'].corr(df['Volume'])
            
        return stats_data
    except Exception as e:
        print(f"Error in statistical analysis: {str(e)}")
        return {}

def price_analysis(df):
    """Analyze price movements and patterns"""
    try:
        price_data = {
            'highest_price': df['High'].max(),
            'lowest_price': df['Low'].min(),
            'price_range': df['High'].max() - df['Low'].min(),
            'avg_price': df['Close'].mean(),
            'price_std': df['Close'].std(),
            'last_price': df['Close'].iloc[-1],
            'price_change': ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        }
        return price_data
    except Exception as e:
        print(f"Error in price analysis: {str(e)}")
        return {}

def run_analysis():
    """Main function to run the analysis"""
    try:
        # Check if resources directory exists
        if not Path("resources").exists():
            print("Resources directory not found. Please run data_loader.py first.")
            return None
            
        # Load data sources
        try:
            sources_df = pd.read_csv("resources/data_sources.csv")
            available_symbols = [file.split('_')[2].split('.')[0] 
                               for file in sources_df['file_path'] 
                               if 'stock_data' in file]
        except FileNotFoundError:
            print("data_sources.csv not found. Please run data_loader.py first.")
            return None
        
        # Remove duplicates and sort
        available_symbols = sorted(list(set(available_symbols)))
        
        if not available_symbols:
            print("No stock data files found. Please run data_loader.py first.")
            return None
        
        print("\nAvailable stocks for analysis:")
        for idx, symbol in enumerate(available_symbols, 1):
            print(f"{idx}. {symbol}")
        
        # Get user choice
        while True:
            try:
                choice = int(input("\nEnter the number of the stock to analyze (1-3): ")) - 1
                if 0 <= choice < len(available_symbols):
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        symbol = available_symbols[choice]
        print(f"\nAnalyzing {symbol}...")
        
        # Load and analyze data
        df = load_stock_data(symbol)
        
        if df.empty:
            print(f"No data available for {symbol}")
            return None
            
        # Run analyses
        tech_analysis = technical_analysis(df)
        stats_analysis = statistical_analysis(df)
        price_data = price_analysis(df)
        
        # Print results
        print("\n" + "="*50)
        print(f"Analysis Results for {symbol}")
        print("="*50)
        
        if tech_analysis:
            print("\n1. Technical Analysis:")
            print("-"*30)
            for key, value in tech_analysis.items():
                if isinstance(value, float):
                    print(f"{key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
        
        if stats_analysis:
            print("\n2. Statistical Analysis:")
            print("-"*30)
            for key, value in stats_analysis.items():
                print(f"{key.replace('_', ' ').title()}: {value:.4f}")
        
        if price_data:
            print("\n3. Price Analysis:")
            print("-"*30)
            for key, value in price_data.items():
                if isinstance(value, float):
                    print(f"{key.replace('_', ' ').title()}: ${value:.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Save analysis results
        analysis_results = {
            'symbol': symbol,
            'technical': tech_analysis,
            'statistical': stats_analysis,
            'price': price_data
        }
        
        # Save to CSV
        results_df = pd.DataFrame([analysis_results])
        results_df.to_csv(f"resources/analysis_results_{symbol}.csv", index=False)
        print(f"\nAnalysis results saved to resources/analysis_results_{symbol}.csv")
        
        return analysis_results
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return None

if __name__ == "__main__":
    run_analysis()
