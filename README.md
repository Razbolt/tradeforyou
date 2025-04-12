# Alpaca-Trade

A comprehensive trading platform using Alpaca API with AI-powered capabilities.

## 🚀 Overview

Alpaca-Trade is a Python-based trading platform that connects to the Alpaca API for stock trading. It features both traditional API implementations and an advanced AI-powered broker that can interpret natural language instructions using Claude AI.

## 📂 Project Structure

The project is organized into several modules:

### 📌 `/alpaca_trader/broker`
An AI-powered broker that uses Claude (Anthropic's AI) to interpret user instructions and execute trades:
- `ai_broker.py`: Core AI broker implementation with Claude integration
- `demo.py`: Interactive demo for testing the AI broker
- `test_broker.py`: Test utilities for the broker functionality

### 📌 `/alpaca_trader/official`
Official Alpaca API integration with traditional programmatic methods:
- `account.py`: Account management functionality
- `data.py`: Market data retrieval
- `orders.py`: Order creation and management
- `demo.py`: Demonstration of the official API functionality

### 📌 `/alpaca_trader/utils`
Utility functions and helpers:
- `config.py`: Configuration management
- Other general-purpose utilities

### 📌 `/alpaca_trader/core`
Core trading functionality and shared components.

## 🔧 Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/Razbolt/tradeforyou.git
cd tradeforyou
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # Only needed for AI broker
```

## 🧠 AI-Powered Trading

The AI broker can interpret natural language instructions like:
- "Buy 10 shares of Apple"
- "What's the current price of Microsoft?"
- "Check my account balance"

### Using the AI Broker:

```python
from alpaca_trader.broker import AIBroker

broker = AIBroker()
response = broker.process_instruction("Buy 5 shares of TSLA")
print(response)
```

Or run the interactive demo:
```bash
python -m alpaca_trader.broker.demo
```

## 📊 Traditional API Usage

For programmatic trading using the official API:

```python
from alpaca_trader.official import get_official_order_manager

# Initialize order manager
order_manager = get_official_order_manager()

# Place a market order
result = order_manager.market_order(
    symbol="AAPL",
    side="buy",
    qty=10
)
```

## 🔒 Security

- All API trading is done through Alpaca's paper trading by default
- API keys are stored in environment variables, not in code
- The `.env` file is excluded from Git to prevent accidental key exposure

## 📚 Advanced Features

- **Company Name Recognition**: Query stocks by company name (e.g., "Analog Devices" instead of "ADI")
- **Multi-timeframe Data**: Fall back to different timeframes if data is unavailable
- **Robust Error Handling**: Graceful fallbacks for API limitations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
