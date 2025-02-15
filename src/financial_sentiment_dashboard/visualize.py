import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import glob
from scipy import stats
import ast
import json

def load_analysis_results():
    """Load all analysis results files"""
    results_files = glob.glob("resources/analysis_results_*.csv")
    all_results = {}
    
    for file in results_files:
        try:
            symbol = file.split('_')[-1].split('.')[0]
            df = pd.read_csv(file)
            
            # Convert the first row to a dictionary
            data = df.iloc[0].to_dict()
            
            # Parse the nested dictionaries
            for key in ['technical', 'statistical', 'price']:
                if key in data and isinstance(data[key], str):
                    try:
                        # Remove any single quotes and replace with double quotes
                        cleaned_str = data[key].replace("'", '"')
                        # Parse the JSON string
                        data[key] = json.loads(cleaned_str)
                    except json.JSONDecodeError:
                        try:
                            # Fallback to ast.literal_eval
                            data[key] = ast.literal_eval(data[key])
                        except:
                            print(f"Warning: Could not parse {key} data for {symbol}")
                            data[key] = {}
            
            all_results[symbol] = data
            print(f"Successfully loaded data for {symbol}")
            
        except Exception as e:
            print(f"Error loading {symbol}: {str(e)}")
            continue
    
    return all_results, results_files

def get_company_name(symbol):
    """Get company name from symbol"""
    company_names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc. (Google)',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.'
    }
    return company_names.get(symbol, symbol)

def plot_price_comparisons(results, selected_symbols):
    """Plot price comparisons across stocks"""
    try:
        symbols = [s for s in selected_symbols if s in results]
        prices = []
        
        for symbol in symbols:
            price = results[symbol].get('price', {}).get('last_price', 0)
            if isinstance(price, str):
                price = float(price.replace('$', '').replace(',', ''))
            prices.append(price)
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(symbols, prices, color='skyblue')
        plt.title('Stock Price Comparison')
        plt.ylabel('Price ($)')
        plt.grid(True, alpha=0.3)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.2f}',
                    ha='center', va='bottom')
        
        plt.savefig('resources/price_comparison.png')
        plt.close()
    except Exception as e:
        print(f"Error in price comparison plot: {str(e)}")

def plot_volatility_comparison(results, selected_symbols):
    """Plot volatility comparison"""
    try:
        symbols = [s for s in selected_symbols if s in results]
        volatilities = []
        
        for symbol in symbols:
            vol = results[symbol].get('technical', {}).get('volatility', 0)
            if isinstance(vol, str):
                vol = float(vol.strip('%')) / 100
            volatilities.append(vol)
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(symbols, volatilities, color='salmon')
        plt.title('Stock Volatility Comparison')
        plt.ylabel('Volatility (Annualized)')
        plt.grid(True, alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2%}',
                    ha='center', va='bottom')
        
        plt.savefig('resources/volatility_comparison.png')
        plt.close()
    except Exception as e:
        print(f"Error in volatility comparison plot: {str(e)}")

def plot_returns_distribution(results, selected_symbols):
    """Plot returns distribution"""
    plt.figure(figsize=(12, 6))
    
    for symbol in selected_symbols:
        if symbol in results:
            mean_return = results[symbol]['statistical']['daily_return_mean']
            std_return = results[symbol]['statistical']['daily_return_std']
            
            x = np.linspace(mean_return - 3*std_return, mean_return + 3*std_return, 100)
            y = stats.norm.pdf(x, mean_return, std_return)
            
            plt.plot(x, y, label=f"{symbol} (μ={mean_return:.2%}, σ={std_return:.2%})")
    
    plt.title('Daily Returns Distribution')
    plt.xlabel('Return')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    plt.savefig('resources/returns_distribution.png')
    plt.close()

def create_summary_table(results, selected_symbols):
    """Create a summary table of key metrics"""
    summary_data = []
    
    for symbol in selected_symbols:
        if symbol in results:
            data = {
                'Symbol': symbol,
                'Company': get_company_name(symbol),
                'Last Price': f"${results[symbol]['price']['last_price']:,.2f}",
                'Price Change %': f"{results[symbol]['price']['price_change']:.2f}%",
                'Volatility': f"{results[symbol]['technical']['volatility']:.2%}",
                'Trend': results[symbol]['technical']['trend'],
                'Sharpe Ratio': f"{results[symbol]['statistical']['sharpe_ratio']:.2f}"
            }
            summary_data.append(data)
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_html('resources/summary_table.html', index=False)
    return summary_df

def plot_price_ranges(results, selected_symbols):
    """Plot price ranges for each stock"""
    symbols = [s for s in selected_symbols if s in results]
    highs = [results[s]['price']['highest_price'] for s in symbols]
    lows = [results[s]['price']['lowest_price'] for s in symbols]
    current = [results[s]['price']['last_price'] for s in symbols]
    
    plt.figure(figsize=(10, 6))
    plt.vlines(symbols, lows, highs, color='gray', alpha=0.5, linewidth=2)
    plt.scatter(symbols, current, color='red', s=100, zorder=5, label='Current Price')
    
    # Add price labels
    for i, symbol in enumerate(symbols):
        plt.text(i, highs[i], f'${highs[i]:,.2f}', ha='center', va='bottom')
        plt.text(i, lows[i], f'${lows[i]:,.2f}', ha='center', va='top')
        plt.text(i, current[i], f'${current[i]:,.2f}', ha='center', va='bottom', color='red')
    
    plt.title('Stock Price Ranges')
    plt.ylabel('Price ($)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('resources/price_ranges.png')
    plt.close()

def visualize_all_data():
    """Main function to create all visualizations"""
    try:
        print("Loading analysis results...")
        results, results_files = load_analysis_results()
        
        if not results:
            print("No analysis results found. Please run analysis.py first.")
            return
        
        # Show available companies
        print("\nAvailable analysis results:")
        available_symbols = list(results.keys())
        for idx, symbol in enumerate(available_symbols, 1):
            company_name = get_company_name(symbol)
            print(f"{idx}. {company_name} ({symbol})")
        
        # Get user selection
        print("\nSelect companies to visualize (comma-separated numbers, or 'all'):")
        selection = input("Your choice: ").strip().lower()
        
        if selection == 'all':
            selected_symbols = available_symbols
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                selected_symbols = [available_symbols[i] for i in indices if 0 <= i < len(available_symbols)]
            except:
                print("Invalid selection. Using all available companies.")
                selected_symbols = available_symbols
        
        print(f"\nCreating visualizations for: {', '.join(selected_symbols)}")
        
        # Create all plots with better error handling
        try:
            plot_price_comparisons(results, selected_symbols)
            print("Created price comparison plot")
        except Exception as e:
            print(f"Error creating price comparison: {str(e)}")
            
        try:
            plot_volatility_comparison(results, selected_symbols)
            print("Created volatility comparison plot")
        except Exception as e:
            print(f"Error creating volatility comparison: {str(e)}")
            
        try:
            plot_returns_distribution(results, selected_symbols)
            print("Created returns distribution plot")
        except Exception as e:
            print(f"Error creating returns distribution: {str(e)}")
            
        try:
            plot_price_ranges(results, selected_symbols)
            print("Created price ranges plot")
        except Exception as e:
            print(f"Error creating price ranges: {str(e)}")
        
        # Create summary table
        try:
            summary_df = create_summary_table(results, selected_symbols)
            print("\nSummary Statistics:")
            print("-" * 50)
            print(summary_df.to_string())
        except Exception as e:
            print(f"Error creating summary table: {str(e)}")
        
        print("\nVisualizations saved:")
        print("1. Price Comparison (price_comparison.png)")
        print("2. Volatility Comparison (volatility_comparison.png)")
        print("3. Returns Distribution (returns_distribution.png)")
        print("4. Price Ranges (price_ranges.png)")
        print("5. Summary Table (summary_table.html)")
        
    except Exception as e:
        print(f"Error in visualization: {str(e)}")

if __name__ == "__main__":
    visualize_all_data()
