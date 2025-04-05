"""
Account management using the official Alpaca SDK.
Provides functionality to manage account information.
"""

import os
from alpaca.trading.client import TradingClient
from ..utils.config import get_config_manager


class OfficialAccountManager:
    """Manages Alpaca trading accounts using the official SDK."""
    
    def __init__(self):
        """Initialize the account manager with configuration."""
        self.config_manager = get_config_manager()
        self.api_key, self.api_secret, self.base_url = self.config_manager.get_alpaca_credentials()
        self.trading_client = None
        
        # Initialize client if credentials are available
        if self.api_key and self.api_secret:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Alpaca trading client with API keys."""
        # Determine if paper trading from the base URL
        paper = 'paper' in self.base_url if self.base_url else True
        
        try:
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.api_secret,
                paper=paper
            )
            return True
        except Exception as e:
            print(f"Error initializing Alpaca client: {e}")
            self.trading_client = None
            return False
    
    def is_configured(self):
        """
        Check if the account is configured with API keys.
        
        Returns:
            bool: True if API keys are configured and client is initialized, False otherwise
        """
        return self.trading_client is not None
    
    def configure_account(self, api_key, api_secret, paper_trading=True):
        """
        Configure the account with API keys.
        
        Args:
            api_key (str): Alpaca API key
            api_secret (str): Alpaca API secret
            paper_trading (bool, optional): Use paper trading environment. Defaults to True.
            
        Returns:
            bool: True if configuration succeeded, False otherwise
        """
        # Save credentials
        self.config_manager.set_alpaca_credentials(api_key, api_secret, paper_trading)
        
        # Update instance variables
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Determine base URL based on paper_trading flag
        if paper_trading:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'
        
        # Initialize client
        if self._initialize_client():
            print("Account configured successfully.")
            return True
        else:
            print("Failed to initialize Alpaca client. Please check your credentials.")
            return False
    
    def get_account_info(self):
        """
        Get information about the Alpaca account.
        
        Returns:
            dict: Account information or None if unavailable
        """
        if not self.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        try:
            account = self.trading_client.get_account()
            # Convert account object to dictionary for compatibility with custom implementation
            account_dict = {
                'id': account.id,
                'status': account.status,
                'currency': account.currency,
                'cash': account.cash,
                'portfolio_value': account.portfolio_value,
                'buying_power': account.buying_power,
                'daytrade_count': account.daytrade_count,
                'pattern_day_trader': account.pattern_day_trader
            }
            return account_dict
        except Exception as e:
            print(f"Error getting account information: {e}")
            return None
    
    def print_account_summary(self):
        """Print a summary of the account information."""
        account_info = self.get_account_info()
        if not account_info:
            return
        
        print("\n=== Account Summary (Official SDK) ===")
        print(f"Account ID: {account_info.get('id')}")
        print(f"Status: {account_info.get('status')}")
        print(f"Currency: {account_info.get('currency')}")
        print(f"Cash: ${float(account_info.get('cash')):,.2f}")
        print(f"Portfolio Value: ${float(account_info.get('portfolio_value')):,.2f}")
        print(f"Buying Power: ${float(account_info.get('buying_power')):,.2f}")
        print(f"Daytrade Count: {account_info.get('daytrade_count')}")
        print(f"Pattern Day Trader: {'Yes' if account_info.get('pattern_day_trader') else 'No'}")
        print("========================\n")


# Singleton instance for global access
_official_account_manager = None

def get_official_account_manager():
    """
    Get or create the global OfficialAccountManager instance.
    
    Returns:
        OfficialAccountManager: The global account manager
    """
    global _official_account_manager
    if _official_account_manager is None:
        _official_account_manager = OfficialAccountManager()
    return _official_account_manager 