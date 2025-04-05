#!/usr/bin/env python3
"""
Alpaca Market Data Explorer

A standalone script for exploring market data using the Alpaca API.
This script provides a more advanced interface for retrieving and analyzing
market data beyond what's available in the standard demo.
"""

import sys
import datetime
from data import get_data_manager

def get_date_input(prompt, default=None):
    """Get a date input from the user with validation."""
    while True:
        date_str = input(prompt)
        if not date_str and default:
            return default
        
        try:
            # Parse date in YYYY-MM-DD format
            parts = date_str.split('-')
            if len(parts) != 3:
                print("Invalid date format. Please use YYYY-MM-DD.")
                continue
                
            year, month, day = map(int, parts)
            return datetime.datetime(year, month, day)
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD format.")


def get_timeframe_input():
    """Get a valid timeframe input from the user."""
    valid_timeframes = ["1Min", "5Min", "15Min", "30Min", "1Hour", "1Day", "1Week", "1Month"]
    
    print("\nAvailable timeframes:")
    for i, tf in enumerate(valid_timeframes, 1):
        print(f"{i}. {tf}")
    
    while True:
        try:
            choice = int(input("\nSelect timeframe (1-8): "))
            if 1 <= choice <= 8:
                return valid_timeframes[choice-1]
            print("Please enter a number between 1 and 8.")
        except ValueError:
            print("Please enter a valid number.")


def get_symbols_input(asset_type):
    """Get symbol input from the user."""
    print(f"\nEnter {asset_type} symbol(s) separated by commas")
    if asset_type == "crypto":
        print("Example formats: BTC/USD, ETH/USD")
    else:
        print("Example formats: AAPL, MSFT, GOOGL")
    
    symbols_input = input("> ")
    return [s.strip() for s in symbols_input.split(",")]


def explore_stock_data():
    """Interface for exploring stock market data."""
    print("\n===== Stock Market Data Explorer =====")
    
    # Get data manager
    data_mgr = get_data_manager()
    
    # Get symbols
    symbols = get_symbols_input("stock")
    if not symbols:
        print("No symbols provided. Returning to main menu.")
        return
    
    # Get timeframe
    timeframe = get_timeframe_input()
    
    # Get start and end dates
    now = datetime.datetime.now()
    default_end = now
    default_start = now - datetime.timedelta(days=30)
    
    print("\nEnter date range (YYYY-MM-DD format, press Enter for defaults)")
    start = get_date_input(f"Start date [{default_start.strftime('%Y-%m-%d')}]: ", default_start)
    end = get_date_input(f"End date [{default_end.strftime('%Y-%m-%d')}]: ", default_end)
    
    # Get limit
    try:
        limit_input = input("\nEnter maximum number of bars [100]: ")
        limit = int(limit_input) if limit_input else 100
    except ValueError:
        limit = 100
    
    print("\nRetrieving data...")
    
    try:
        # Get bars
        bars = data_mgr.get_stock_bars(
            symbol=symbols[0] if len(symbols) == 1 else symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit
        )
        
        # Print bars
        print(f"\nFound {len(bars)} bars for {', '.join(symbols)}")
        data_mgr.print_bars(bars)
        
        # Save to CSV option
        if input("\nWould you like to save this data to CSV? (y/n): ").lower() == 'y':
            filename = input("Enter filename (default: stock_data.csv): ") or "stock_data.csv"
            
            if hasattr(bars, 'df'):  # Multi-symbol case
                bars.df.to_csv(filename)
            else:  # Single symbol case
                bars.to_csv(filename)
                
            print(f"Data saved to {filename}")
    
    except Exception as e:
        print(f"Error retrieving data: {e}")


def explore_crypto_data():
    """Interface for exploring cryptocurrency market data."""
    print("\n===== Cryptocurrency Market Data Explorer =====")
    
    # Get data manager
    data_mgr = get_data_manager()
    
    # Get symbols
    symbols = get_symbols_input("crypto")
    if not symbols:
        print("No symbols provided. Returning to main menu.")
        return
    
    # Get timeframe
    timeframe = get_timeframe_input()
    
    # Get start and end dates
    now = datetime.datetime.now()
    default_end = now
    default_start = now - datetime.timedelta(days=7)
    
    print("\nEnter date range (YYYY-MM-DD format, press Enter for defaults)")
    start = get_date_input(f"Start date [{default_start.strftime('%Y-%m-%d')}]: ", default_start)
    end = get_date_input(f"End date [{default_end.strftime('%Y-%m-%d')}]: ", default_end)
    
    # Get limit
    try:
        limit_input = input("\nEnter maximum number of bars [100]: ")
        limit = int(limit_input) if limit_input else 100
    except ValueError:
        limit = 100
    
    print("\nRetrieving data...")
    
    try:
        # Get bars
        bars = data_mgr.get_crypto_bars(
            symbol=symbols[0] if len(symbols) == 1 else symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit
        )
        
        # Print bars
        print(f"\nFound {len(bars)} bars for {', '.join(symbols)}")
        data_mgr.print_bars(bars)
        
        # Save to CSV option
        if input("\nWould you like to save this data to CSV? (y/n): ").lower() == 'y':
            filename = input("Enter filename (default: crypto_data.csv): ") or "crypto_data.csv"
            
            if hasattr(bars, 'df'):  # Multi-symbol case
                bars.df.to_csv(filename)
            else:  # Single symbol case
                bars.to_csv(filename)
                
            print(f"Data saved to {filename}")
    
    except Exception as e:
        print(f"Error retrieving data: {e}")


def main():
    """Main function to run the data explorer."""
    print("\n====================================")
    print("   ALPACA MARKET DATA EXPLORER")
    print("====================================\n")
    
    while True:
        print("\nSelect an option:")
        print("1. Explore Stock Market Data")
        print("2. Explore Cryptocurrency Data")
        print("3. Exit")
        
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            
            if choice == 1:
                explore_stock_data()
            elif choice == 2:
                explore_crypto_data()
            elif choice == 3:
                print("\nExiting data explorer. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nExiting data explorer. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main() 