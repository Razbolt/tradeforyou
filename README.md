# Alpaca Paper Trading

A Python application for paper trading using the Alpaca API.

## Overview

This project provides a simple and functional way to interact with Alpaca's paper trading API. It allows you to:

- Manage Alpaca API credentials
- Execute different types of orders (market, limit, stop, stop-limit)
- Track your paper trading activities

The project includes two implementations:
1. **Custom Implementation**: A custom client built from scratch using the Alpaca REST API
2. **Official SDK**: Implementation using the official Alpaca Python SDK (alpaca-py)

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

- `alpaca_trader/` - Main package
  - `core/` - Custom implementation (built from scratch)
    - `account.py` - Account management
    - `client.py` - Alpaca API client
    - `orders.py` - Order functionality
  - `official/` - Official SDK implementation
    - `account.py` - Account management using official SDK
    - `orders.py` - Order functionality using official SDK
    - `demo.py` - Demonstration comparing both implementations
    - `data.py` - Data retrieval and analysis
  - `utils/` - Utility functions
    - `config.py` - Configuration management
  - `main.py` - Main entry point for custom implementation

## Usage

### Custom Implementation
Run the custom implementation:
```
python -m alpaca_trader
```

### Official SDK Implementation
Run the official SDK implementation:
```
python -m alpaca_trader.official
```

### Comparison Demo
To compare both implementations side by side:
```
python -m alpaca_trader.official.demo
```

### Data Explorer
To explore historical data:
```bash
python -m alpaca_trader.official.data
# or 
python alpaca_trader/official/data_explorer.py
```

Follow the prompts to set up your Alpaca paper trading account and execute trades.

## Authentication

To use this application, you'll need to:
1. Create an Alpaca account at https://app.alpaca.markets/signup
2. Generate API keys from your dashboard
3. Configure the application with your API keys

## Key Differences Between Implementations

1. **API Interaction**:
   - Custom: Uses direct HTTP requests to the Alpaca REST API
   - Official: Uses the Alpaca Python SDK (alpaca-py)

2. **Data Structures**:
   - Custom: Works with dictionaries for all data
   - Official: Uses SDK's native objects and converts to dictionaries for compatibility

3. **Error Handling**:
   - Custom: Custom error handling and validation
   - Official: Leverages SDK's built-in validation and error handling

## Updated Features

### 1. Data Retrieval and Analysis
The official implementation now includes a powerful data retrieval and exploration tool:

- Get historical market data for both stocks and cryptocurrencies
- Explore data with different timeframes (1Min to 1Month)
- Save retrieved data to CSV files for further analysis
- Interactive command-line interface for data exploration

### 2. Dependency Fixing
A dependency fixing script has been added to resolve NumPy/Pandas compatibility issues:

```bash
python fix_dependencies.py
```

This script will:
1. Uninstall problematic packages
2. Reinstall them in the correct order with compatible versions
3. Ensure the application runs without binary compatibility errors

## Troubleshooting

### NumPy/Pandas Compatibility Issue
If you encounter this error:
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

Run the included fix script:
```bash
python fix_dependencies.py
```

### API Authentication Issues
If you encounter authentication errors:
1. Verify your API keys in the `.env` file
2. Check that your Alpaca account is active
3. Ensure you're using the correct API endpoint (paper vs live)

## License

MIT # tradeforyou
