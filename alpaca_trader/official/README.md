# Alpaca Official SDK Implementation

This directory contains the implementation of the Alpaca Trading application using the official `alpaca-py` Python SDK.

## Features

- **Account Management**: Access and manage your Alpaca paper trading account
- **Order Execution**: Place various types of orders (market, limit, stop, stop-limit)
- **Market Data Retrieval**: Get historical data for stocks and cryptocurrencies
- **Interactive Demo**: Test all functionality through a simple command-line interface

## Components

- `account.py`: Account management functionality
- `orders.py`: Order execution for various order types
- `data.py`: Market data retrieval for stocks and cryptocurrencies
- `demo.py`: Interactive demonstration of all features
- `__main__.py`: Entry point for running the official implementation
- `data_explorer.py`: Advanced tool for exploring market data

## Running the Application

```bash
# Run the interactive demo
python -m alpaca_trader.official

# Run only the data retrieval module
python -m alpaca_trader.official.data
```

## Menu Options

The official SDK demo provides a simplified interface with the following options:

1. View Account - Check account balance and status
2. Place Market Order - Execute immediate orders at market price
3. Place Limit Order - Set a maximum buy or minimum sell price
4. Place Stop Order - Create trigger-based market orders
5. Place Stop-Limit Order - Create trigger-based limit orders
6. View Orders - See all existing orders
7. Cancel Order - Cancel a specific open order
8. Cancel All Orders - Cancel all open orders
9. Get Stock Market Data - Retrieve historical stock data
10. Get Crypto Market Data - Retrieve historical cryptocurrency data
11. Setup Account - Configure API credentials

## Market Data Retrieval

The official SDK implementation provides access to historical market data for both stocks and cryptocurrencies through the `DataManager` class in `data.py`.

### Available Timeframes

- `1Min`, `5Min`, `15Min`, `30Min`, `1Hour`, `1Day`, `1Week`, `1Month`

### Sample Usage

```python
from alpaca_trader.official.data import get_data_manager

# Get stock data
data_mgr = get_data_manager()
bars = data_mgr.get_stock_bars(
    symbol="AAPL",
    timeframe="1Day",
    limit=5
)
data_mgr.print_bars(bars)

# Get crypto data
crypto_bars = data_mgr.get_crypto_bars(
    symbol="BTC/USD",
    timeframe="1Hour",
    limit=10
)
data_mgr.print_bars(crypto_bars)
```

## Common Issues and Solutions

### NumPy/Pandas Compatibility Issue

If you encounter this error:
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

Run the provided fix script:
```bash
python fix_dependencies.py
```

This will reinstall the dependencies in the correct order with compatible versions.

### API Key Issues

If you encounter authentication errors, make sure your Alpaca API keys are set correctly:

1. Check your `.env` file has the correct values
2. Verify the API key is active in your Alpaca dashboard
3. Ensure you're using the correct endpoint (paper vs live)

## Dependencies

The official implementation requires:
- `alpaca-py==0.8.2`
- `numpy==1.24.3`
- `pandas==2.0.3`

These specific versions are recommended to avoid compatibility issues. 