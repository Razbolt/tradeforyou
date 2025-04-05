"""
Alpaca API client for trading functionality.
Handles API interactions with Alpaca.
"""

import requests
import json
from ..utils.config import get_config_manager
from .account import get_account_manager


class AlpacaClient:
    """Client for interacting with the Alpaca API."""
    
    def __init__(self):
        """Initialize the Alpaca client with account configuration."""
        self.account_manager = get_account_manager()
        self.api_key = self.account_manager.api_key
        self.api_secret = self.account_manager.api_secret
        self.base_url = self.account_manager.base_url
        
        # Define API endpoints
        if self.base_url:
            self.account_url = f"{self.base_url}/v2/account"
            self.orders_url = f"{self.base_url}/v2/orders"
            self.positions_url = f"{self.base_url}/v2/positions"
    
    def _headers(self):
        """
        Get the headers required for Alpaca API calls.
        
        Returns:
            dict: Headers with API keys
        """
        return {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret,
            'Content-Type': 'application/json'
        }
    
    def get_account(self):
        """
        Get account information.
        
        Returns:
            dict: Account information or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        try:
            response = requests.get(self.account_url, headers=self._headers())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get account information. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting account information: {e}")
            return None
    
    def get_positions(self):
        """
        Get current positions.
        
        Returns:
            list: List of positions or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        try:
            response = requests.get(self.positions_url, headers=self._headers())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get positions. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting positions: {e}")
            return None
    
    def get_position(self, symbol):
        """
        Get position for a specific symbol.
        
        Args:
            symbol (str): The symbol to get position for
            
        Returns:
            dict: Position information or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        url = f"{self.positions_url}/{symbol}"
        
        try:
            response = requests.get(url, headers=self._headers())
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"No position found for {symbol}")
                return None
            else:
                print(f"Failed to get position for {symbol}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting position for {symbol}: {e}")
            return None
    
    def get_orders(self, status=None, limit=50):
        """
        Get orders with optional filtering.
        
        Args:
            status (str, optional): Filter by order status. Defaults to None.
            limit (int, optional): Maximum number of orders to return. Defaults to 50.
            
        Returns:
            list: List of orders or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        params = {'limit': limit}
        if status:
            params['status'] = status
        
        try:
            response = requests.get(self.orders_url, headers=self._headers(), params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get orders. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting orders: {e}")
            return None
    
    def get_order(self, order_id):
        """
        Get a specific order by ID.
        
        Args:
            order_id (str): The order ID
            
        Returns:
            dict: Order information or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        url = f"{self.orders_url}/{order_id}"
        
        try:
            response = requests.get(url, headers=self._headers())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get order {order_id}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting order {order_id}: {e}")
            return None
    
    def submit_order(self, order_data):
        """
        Submit an order to Alpaca.
        
        Args:
            order_data (dict): Order parameters
            
        Returns:
            dict: Order information or None if request fails
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return None
        
        try:
            response = requests.post(
                self.orders_url,
                headers=self._headers(),
                data=json.dumps(order_data)
            )
            
            if response.status_code == 200 or response.status_code == 201:
                order_info = response.json()
                print(f"Order submitted successfully. Order ID: {order_info.get('id')}")
                return order_info
            else:
                print(f"Failed to submit order. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error submitting order: {e}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel an order by ID.
        
        Args:
            order_id (str): The order ID to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return False
        
        url = f"{self.orders_url}/{order_id}"
        
        try:
            response = requests.delete(url, headers=self._headers())
            if response.status_code == 204:
                print(f"Order {order_id} cancelled successfully.")
                return True
            else:
                print(f"Failed to cancel order {order_id}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self):
        """
        Cancel all open orders.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.account_manager.is_configured():
            print("Account not configured. Please configure the account first.")
            return False
        
        try:
            response = requests.delete(self.orders_url, headers=self._headers())
            if response.status_code == 207:
                result = response.json()
                print(f"Cancelled {len(result)} orders.")
                return True
            else:
                print(f"Failed to cancel all orders. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error cancelling all orders: {e}")
            return False


# Singleton instance for global access
_alpaca_client = None

def get_alpaca_client():
    """
    Get or create the global AlpacaClient instance.
    
    Returns:
        AlpacaClient: The global Alpaca client
    """
    global _alpaca_client
    if _alpaca_client is None:
        _alpaca_client = AlpacaClient()
    return _alpaca_client 