import os
import pandas as pd
from datetime import datetime
from pathlib import Path

def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text):
        return ""
    
    text = str(text).strip()
    text = text.replace('\n', ' ').replace('\r', '')
    return ' '.join(text.split())

def format_date(date_str):
    """
    Convert various date formats to a standardized ISO format.
    Returns None if conversion fails.
    """
    try:
        if pd.isna(date_str):
            return None
        
        date = pd.to_datetime(date_str)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def ensure_directory(directory_path):
    """Create directory if it doesn't exist."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_project_root():
    """Get the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def save_dataframe(df, filename, directory='resources'):
    """
    Save DataFrame to CSV with proper directory handling.
    
    Args:
        df (pandas.DataFrame): DataFrame to save
        filename (str): Name of the file (with .csv extension)
        directory (str): Directory to save the file in
    """
    ensure_directory(directory)
    file_path = os.path.join(directory, filename)
    df.to_csv(file_path, index=False)
    return file_path

def load_dataframe(filename, directory='resources'):
    """
    Load DataFrame from CSV with proper error handling.
    
    Args:
        filename (str): Name of the file (with .csv extension)
        directory (str): Directory to load the file from
    """
    file_path = os.path.join(directory, filename)
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading {file_path}: {str(e)}")

def clean_dataframe(df):
    """
    Clean a DataFrame by:
    - Removing duplicate rows
    - Handling missing values
    - Cleaning text columns
    """
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Clean text columns (title and description)
    if 'title' in df.columns:
        df['title'] = df['title'].apply(clean_text)
    if 'description' in df.columns:
        df['description'] = df['description'].apply(clean_text)
    
    # Format dates
    if 'publishedAt' in df.columns:
        df['publishedAt'] = df['publishedAt'].apply(format_date)
    
    # Drop rows where title is empty
    df = df.dropna(subset=['title'])
    
    return df
