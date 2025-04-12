"""
Test script for the AIBroker implementation.
This script tests the fixed functionality for buying stocks and getting market data.
"""

import os
import json
from dotenv import load_dotenv
from .ai_broker import AIBroker, UUIDEncoder

def test_broker_functionality():
    """Test the core functionality of the AIBroker class."""
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    if not os.environ.get("ALPACA_API_KEY") or not os.environ.get("ALPACA_SECRET_KEY"):
        print("Error: ALPACA_API_KEY or ALPACA_SECRET_KEY environment variables not set.")
        print("Please set them in your .env file or environment variables.")
        return
    
    print("=== AI Broker Functionality Test ===")
    print("Testing the updated broker implementation...")
    print()
    
    # Initialize broker
    broker = AIBroker()
    
    # Test 1: Get account info
    print("Test 1: Get account information")
    account_info = broker.get_account_info()
    print(f"Account info: {json.dumps(account_info, indent=2, cls=UUIDEncoder)}")
    print()
    
    # Test 2: Get stock price for a popular symbol
    symbol = "AAPL"
    print(f"Test 2: Get stock price for {symbol}")
    price_info = broker.get_stock_price(symbol)
    print(f"Price info: {json.dumps(price_info, indent=2, cls=UUIDEncoder)}")
    print()
    
    # Test 3: Try market data retrieval
    symbols = ["AAPL", "MSFT", "AMZN"]
    print(f"Test 3: Get market data for {', '.join(symbols)}")
    market_data = broker.get_market_data(symbols)
    print(f"Market data available for: {list(market_data.keys())}")
    for symbol in symbols:
        if symbol in market_data:
            if "error" in market_data[symbol]:
                print(f"  - {symbol}: Error - {market_data[symbol]['error']}")
            else:
                print(f"  - {symbol}: Price = {market_data[symbol].get('price')}")
    print()
    
    # Test 4: Test buy stock functionality
    print("Test 4: Test buy stock functionality")
    print("Would you like to test buying stock? This will use paper trading. (y/n)")
    response = input("> ")
    
    if response.lower() == "y":
        symbol = input("Enter stock symbol to buy (e.g., AAPL): ").strip().upper()
        try:
            quantity = int(input("Enter quantity to buy (e.g., 1): ").strip())
            
            print(f"Attempting to buy {quantity} shares of {symbol}...")
            result = broker.buy_stock(symbol, quantity)
            
            print("Result:")
            print(json.dumps(result, indent=2, cls=UUIDEncoder))
        except ValueError:
            print("Invalid quantity. Must be a number.")
    else:
        print("Skipping buy stock test.")
    
    print("\nTests completed.")

if __name__ == "__main__":
    test_broker_functionality() 