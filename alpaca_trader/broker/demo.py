"""
Demo script for AI-powered broker agent.
This demonstrates how to use the AIBroker class to process user instructions.
"""

import os
import json
import re
import uuid
from dotenv import load_dotenv
from .ai_broker import AIBroker, UUIDEncoder

def main():
    """Run a demo of the AI broker agent."""
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Please set it in your .env file or environment variables.")
        return
    
    if not os.environ.get("ALPACA_API_KEY") or not os.environ.get("ALPACA_SECRET_KEY"):
        print("Error: ALPACA_API_KEY or ALPACA_SECRET_KEY environment variables not set.")
        print("Please set them in your .env file or environment variables.")
        return
    
    print("=== AI Broker Demo ===")
    print("This demo shows how the AI broker processes instructions and executes trades.")
    print("Note: This uses paper trading and does not use real money.")
    print("Note: Due to Alpaca API subscription limitations, some stock data may not be available.")
    print("      The broker will still attempt to execute orders with the available data.")
    print()
    
    # Initialize broker
    broker = AIBroker()
    
    # Example instructions to process
    examples = [
        "Buy 1 share of AAPL",
        "What's the current price of MSFT?",
        "Show me my account information",
        "Buy 1 share of AMZN and check my account balance"
    ]
    
    # Get user input or use examples
    print("Choose an option:")
    print("1. Run example instructions")
    print("2. Enter your own instruction")
    print("3. Run direct tests (without Claude)")
    choice = input("> ")
    
    if choice == "1":
        print("\nProcessing example instructions:")
        for i, example in enumerate(examples):
            print(f"\nExample {i+1}: {example}")
            process_and_print_response(broker, example)
    elif choice == "3":
        run_direct_tests(broker)
    else:
        while True:
            print("\nEnter your instruction (or 'exit' to quit):")
            user_input = input("> ")
            
            if user_input.lower() == "exit":
                break
                
            process_and_print_response(broker, user_input)
    
    print("\nDemo completed.")

def run_direct_tests(broker):
    """Run direct tests of the broker functionality without using Claude."""
    print("\n=== Direct Testing Mode ===")
    print("This mode tests the broker functions directly without using Claude.")
    
    while True:
        print("\nChoose a test to run:")
        print("1. Get account information")
        print("2. Get stock price")
        print("3. Buy stock")
        print("4. Return to main menu")
        
        choice = input("> ")
        
        if choice == "1":
            # Test account info
            print("\nGetting account information...")
            result = broker.get_account_info()
            print_formatted_result(result)
            
        elif choice == "2":
            # Test stock price
            symbol = input("\nEnter stock symbol: ").strip().upper()
            if not symbol:
                print("Symbol is required.")
                continue
                
            print(f"Getting price for {symbol}...")
            result = broker.get_stock_price(symbol)
            print_formatted_result(result)
            
        elif choice == "3":
            # Test buy stock
            symbol = input("\nEnter stock symbol: ").strip().upper()
            if not symbol:
                print("Symbol is required.")
                continue
                
            try:
                quantity = int(input("Enter quantity to buy: ").strip())
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
            except ValueError:
                print("Invalid quantity. Must be a number.")
                continue
                
            print(f"Attempting to buy {quantity} shares of {symbol}...")
            result = broker.buy_stock(symbol, quantity)
            print_formatted_result(result)
            
        elif choice == "4":
            # Exit
            return
            
        else:
            print("Invalid choice. Please try again.")

def print_formatted_result(result):
    """Print a result dictionary in a readable format."""
    print("\nResult:")
    print(json.dumps(result, indent=2, cls=UUIDEncoder))

def process_and_print_response(broker, instruction):
    """Process an instruction and print the response."""
    print("\nProcessing instruction:", instruction)
    print("\nAI broker thinking...")
    
    try:
        response = broker.process_instruction(instruction)
        
        # Print formatted response
        print("\nResponse:")
        print("=" * 80)
        
        # Extract and format the broker response section
        broker_response = re.search(r'<broker_response>(.*?)</broker_response>', response, re.DOTALL)
        if broker_response:
            print(broker_response.group(0))
        else:
            print(response)
            
        # Extract and format the actual results section if it exists
        actual_results = re.search(r'<actual_results>(.*?)</actual_results>', response, re.DOTALL)
        if actual_results:
            print("\nActual Results (Technical Details):")
            try:
                results_text = actual_results.group(1)
                results_dict = json.loads(results_text)
                print(json.dumps(results_dict, indent=2, cls=UUIDEncoder))
            except json.JSONDecodeError:
                print(actual_results.group(1))
                
        print("=" * 80)
    except Exception as e:
        print(f"Error processing instruction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 