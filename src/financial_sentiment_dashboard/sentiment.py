from transformers import pipeline
import pandas as pd
from pathlib import Path
import numpy as np

# Initialize sentiment pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(headlines):
    """
    Takes a list of financial headlines and returns a DataFrame with sentiment analysis.
    Also extracts financial indicators from headlines.
    """
    # Analyze sentiment
    results = sentiment_pipeline(headlines)
    sentiments = pd.DataFrame(results)
    sentiments.rename(columns={"label": "sentiment", "score": "confidence_score"}, inplace=True)
    
    # Add numerical sentiment (-1 for negative, 1 for positive)
    sentiments['sentiment_value'] = sentiments['sentiment'].map({'POSITIVE': 1, 'NEGATIVE': -1})
    
    return sentiments

# Direct execution test
if __name__ == "__main__":
    try:
        print("Testing sentiment analysis...")
        
        # Try to load saved news data first
        try:
            print("Looking for saved news data...")
            df = pd.read_csv("resources/news_data.csv")
            headlines = df["title"].tolist()
            print(f"Found {len(headlines)} headlines in news_data.csv")
        except FileNotFoundError:
            print("No saved news data found, using test headlines...")
            headlines = [
                "Stock market soars to new heights",
                "Major company files for bankruptcy",
                "Tech stocks show steady growth"
            ]

        # Analyze sentiments
        results = analyze_sentiment(headlines)
        
        # Create full results DataFrame
        if 'df' in locals():
            df_with_sentiment = pd.concat([df, results], axis=1)
        else:
            df_with_sentiment = pd.DataFrame({
                'title': headlines
            })
            df_with_sentiment = pd.concat([df_with_sentiment, results], axis=1)
        
        # Save results
        Path("resources").mkdir(exist_ok=True)
        df_with_sentiment.to_csv("resources/news_with_sentiment.csv", index=False)
        
        # Print detailed analysis
        print("\nDetailed Sentiment Analysis:")
        print("-" * 50)
        
        for idx, row in df_with_sentiment.iterrows():
            print(f"\nHeadline {idx + 1}: {row['title']}")
            print(f"Sentiment: {row['sentiment']}")
            print(f"Confidence: {row['confidence_score']:.4f}")
            print(f"Sentiment Value: {row['sentiment_value']}")
        
        # Calculate summary statistics
        sentiment_summary = {
            'Total Headlines': len(df_with_sentiment),
            'Positive Headlines': (df_with_sentiment['sentiment'] == 'POSITIVE').sum(),
            'Negative Headlines': (df_with_sentiment['sentiment'] == 'NEGATIVE').sum(),
            'Average Confidence': df_with_sentiment['confidence_score'].mean(),
            'Overall Sentiment': df_with_sentiment['sentiment_value'].mean()
        }
        
        # Add percentage calculations
        total = sentiment_summary['Total Headlines']
        sentiment_summary['Positive Percentage'] = (sentiment_summary['Positive Headlines'] / total) * 100
        sentiment_summary['Negative Percentage'] = (sentiment_summary['Negative Headlines'] / total) * 100
        
        print("\nSummary Statistics:")
        print("-" * 50)
        for key, value in sentiment_summary.items():
            if 'Percentage' in key:
                print(f"{key}: {value:.1f}%")
            else:
                print(f"{key}: {value:.2f}")
                
        print("\nResults saved to resources/news_with_sentiment.csv")
        print("Sentiment analysis completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
