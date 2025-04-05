# Alpaca Paper Trading

A Python application for paper trading using the Alpaca API.

## Overview

This project provides a simple and functional way to interact with Alpaca's paper trading API. It allows you to:

- Manage Alpaca API credentials
- Execute different types of orders (market, limit, stop, stop-limit)
- Track your paper trading activities

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

- `alpaca_trader/` - Main package
  - `core/` - Core functionality
    - `account.py` - Account management
    - `client.py` - Alpaca API client
    - `orders.py` - Order functionality
  - `utils/` - Utility functions
    - `config.py` - Configuration management
  - `main.py` - Main entry point

## Usage

1. Run the main script:
   ```
   python -m alpaca_trader.main
   ```
2. Follow the prompts to set up your Alpaca paper trading account and execute trades.

## Authentication

To use this application, you'll need to:
1. Create an Alpaca account at https://app.alpaca.markets/signup
2. Generate API keys from your dashboard
3. Configure the application with your API keys

## License

MIT # tradeforyou
