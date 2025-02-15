"""
Financial Sentiment Dashboard
----------------------------
A package for analyzing sentiment in financial news and creating interactive dashboards.
"""

from data_loader import fetch_related_financial_data, get_financial_news
from analysis import run_analysis
from sentiment import analyze_sentiment
from visualize import visualize_all_data

__version__ = '0.1.0'
__author__ = 'MD.SAMEER SAYED'

__all__ = [
    'fetch_related_financial_data',
    'get_financial_news',
    'run_analysis',
    'analyze_sentiment',
    'visualize_all_data'
]
