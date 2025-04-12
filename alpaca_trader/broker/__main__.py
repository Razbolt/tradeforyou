"""
Entry point for the broker module when executed directly.
"""

import sys
from .ai_broker import AIBroker

def main():
    """Run the AI broker agent with command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python -m alpaca_trader.broker 'Buy 10 shares of AAPL'")
        return
    
    user_input = " ".join(sys.argv[1:])
    broker = AIBroker()
    response = broker.process_instruction(user_input)
    print(response)

if __name__ == "__main__":
    main() 