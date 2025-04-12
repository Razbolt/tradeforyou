# AI-Powered Broker Agent

This module provides an AI-powered broker agent that uses Claude (Anthropic's AI model) to understand user instructions and Alpaca API to execute stock trades.

## Features

- Natural language understanding of trading instructions
- Execution of buy orders based on user requests
- Retrieval of stock prices and account information
- Interactive demo mode for testing

## Prerequisites

Before using this module, you need:

1. An Anthropic API key for Claude access
2. Alpaca API key and secret for trading functionality

## Setup

1. Create a `.env` file in the project root with the following variables:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_SECRET_KEY=your_alpaca_secret_key
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from alpaca_trader.broker import AIBroker

# Initialize the broker
broker = AIBroker()

# Process a user instruction
response = broker.process_instruction("Buy 10 shares of AAPL")
print(response)
```

### Running the Demo

You can run the interactive demo with:

```bash
python -m alpaca_trader.broker.demo
```

Or directly from the command line:

```bash
python -m alpaca_trader.broker "Buy 10 shares of AAPL"
```

## Module Structure

- `__init__.py` - Package initialization
- `__main__.py` - Command-line entry point
- `ai_broker.py` - Main AIBroker class implementation
- `demo.py` - Interactive demo script

## Available Actions

The broker currently supports the following actions:

1. `buy_stock(symbol, quantity)` - Buy a specified quantity of stock
2. `get_stock_price(symbol)` - Get the current price for a stock
3. `get_account_info()` - Get current account information

## Response Format

The broker returns responses in a structured format:

```
<broker_response>
<actions_taken>
[List of actions executed]
</actions_taken>

<results>
[Results of the actions and relevant market data]
</results>

<additional_info>
[Other pertinent information or context]
</additional_info>
</broker_response>
```

## Security Notes

- This implementation uses Alpaca's paper trading by default
- No real money is used or at risk
- API keys should be kept secure and never committed to version control

## Limitations

- Currently only supports buying stocks (not selling)
- Limited to basic stock information and account details
- No portfolio analysis or recommendations
- No support for advanced order types (limit orders, stop orders, etc.)

## Future Enhancements

- Support for selling stocks
- Advanced order types
- Portfolio analysis and visualization
- Support for other asset classes (options, crypto, etc.)
- Historical performance tracking 