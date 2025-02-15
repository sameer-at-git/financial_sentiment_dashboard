import os
import pandas as pd
from pathlib import Path

from data_loader import get_financial_news, fetch_related_financial_data
from analysis import run_analysis
from sentiment import analyze_sentiment
from visualize import visualize_all_data

def create_resources_directory():
    """Create resources directory if it doesn't exist."""
    Path("resources").mkdir(exist_ok=True)

def process_financial_data(
    source="api",
    file_path=None,
    query="stocks",
    days_ago=7,
    save_intermediates=True
):
    """
    Main function to process financial data and generate analysis.
    """
    try:
        # Create resources directory
        create_resources_directory()
        
        # Step 1: Load and analyze stock data
        print("Running stock analysis...")
        stock_data = fetch_related_financial_data(pd.DataFrame())  # Initialize with empty DataFrame
        analysis_results = run_analysis()
        
        # Step 2: Load and analyze news data
        print("\nProcessing news data...")
        if source.lower() == "api":
            df = get_financial_news(
                query=query,
                from_days_ago=days_ago,
                language="en",
                page_size=100
            )
        elif source.lower() == "file":
            if not file_path:
                raise ValueError("file_path must be provided when source is 'file'")
            df = pd.read_csv(file_path)
        else:
            raise ValueError("source must be either 'api' or 'file'")

        if save_intermediates:
            df.to_csv("resources/news_data.csv", index=False)
            print("Saved raw data to resources/news_data.csv")

        # Step 3: Sentiment Analysis
        print("Performing sentiment analysis...")
        sentiment_results = analyze_sentiment(df["title"].tolist())
        df_with_sentiment = pd.concat([df, sentiment_results], axis=1)

        if save_intermediates:
            df_with_sentiment.to_csv("resources/news_with_sentiment.csv", index=False)
            print("Saved sentiment analysis to resources/news_with_sentiment.csv")

        # Step 4: Generate Visualizations
        print("\nGenerating visualizations...")
        visualize_all_data()
        
        return df_with_sentiment, analysis_results

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Process data from NewsAPI
        df_result, analysis_results = process_financial_data(
            source="api",
            query="tech stocks",
            days_ago=7
        )
        
        print("Data processing completed successfully!")
        print(f"Processed {len(df_result)} articles")
        
    except Exception as e:
        print(f"Program failed: {str(e)}")
