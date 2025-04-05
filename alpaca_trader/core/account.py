"""
Account management for Alpaca trading.
Handles API key generation and validation.
"""

import re
import json
import requests
from ..utils.config import get_config_manager


class AccountManager:
    """Manages Alpaca trading accounts and API keys."""
    
    def __init__(self):
        """Initialize the account manager with configuration."""
        self.config_manager = get_config_manager()
        self.api_key, self.api_secret, self.base_url = self.config_manager.get_alpaca_credentials()
    
    def is_configured(self):
        """
        Check if the account is configured with API keys.
        
        Returns:
            bool: True if API keys are configured, False otherwise
        """
        return bool(self.api_key and self.api_secret and self.base_url)
    
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
        # Validate keys format (basic validation)
        if not api_key or not re.match(r'^[A-Z0-9]{12,}$', api_key):
            print("Invalid API key format. Please check your API key.")
            return False
        
        if not api_secret or not re.match(r'^[a-zA-Z0-9]{32,}$', api_secret):
            print("Invalid API secret format. Please check your API secret.")
            return False
        
        # Test the API keys before saving
        if not self._test_api_keys(api_key, api_secret, paper_trading):
            print("Unable to validate API keys. Please check your credentials.")
            return False
        
        # Save credentials if they are valid
        self.config_manager.set_alpaca_credentials(api_key, api_secret, paper_trading)
        
        # Update instance variables
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Set base URL based on paper_trading flag
        if paper_trading:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'
        
        print("Account configured successfully.")
        return True
    
    def _test_api_keys(self, api_key, api_secret, paper_trading=True):
        """
        Test if the provided API keys are valid.
        
        Args:
            api_key (str): Alpaca API key
            api_secret (str): Alpaca API secret
            paper_trading (bool, optional): Use paper trading environment. Defaults to True.
            
        Returns:
            bool: True if keys are valid, False otherwise
        """
        # Determine which URL to use for testing
        base_url = 'https://paper-api.alpaca.markets' if paper_trading else 'https://api.alpaca.markets'
        url = f"{base_url}/v2/account"
        
        # Send a request to the Alpaca API
        headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': api_secret
        }
        
        try:
            response = requests.get(url, headers=headers)
            # Check if the request was successful
            if response.status_code == 200:
                # Parse account info
                account_info = response.json()
                print(f"Successfully connected to Alpaca account: {account_info.get('id')}")
                return True
            else:
                print(f"Failed to connect to Alpaca. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error testing API keys: {e}")
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
        
        url = f"{self.base_url}/v2/account"
        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get account information. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting account information: {e}")
            return None
    
    def print_account_summary(self):
        """Print a summary of the account information."""
        account_info = self.get_account_info()
        if not account_info:
            return
        
        print("\n=== Account Summary ===")
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
_account_manager = None

def get_account_manager():
    """
    Get or create the global AccountManager instance.
    
    Returns:
        AccountManager: The global account manager
    """
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager 