"""
Order functionality for Alpaca trading.
Implements different order types (market, limit, stop, stop limit).
"""

from enum import Enum
from .client import get_alpaca_client


class OrderSide(Enum):
    """Enum for order side (buy or sell)."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Enum for order type."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(Enum):
    """Enum for time in force."""
    DAY = "day"
    GTC = "gtc"  # Good Till Cancelled
    OPG = "opg"  # Market On Open
    CLS = "cls"  # Market On Close
    IOC = "ioc"  # Immediate Or Cancel
    FOK = "fok"  # Fill Or Kill


class OrderManager:
    """Manages order creation and submission to Alpaca."""
    
    def __init__(self):
        """Initialize order manager with Alpaca client."""
        self.client = get_alpaca_client()
    
    def validate_order_parameters(self, symbol, qty=None, notional=None):
        """
        Validate common order parameters.
        
        Args:
            symbol (str): The symbol to trade
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        if not symbol:
            print("Symbol is required.")
            return False
        
        # Either qty or notional must be provided, but not both
        if (qty is None and notional is None) or (qty is not None and notional is not None):
            print("Either 'qty' or 'notional' must be provided, but not both.")
            return False
        
        # Check qty is valid if provided
        if qty is not None and float(qty) <= 0:
            print("Quantity must be positive.")
            return False
        
        # Check notional is valid if provided
        if notional is not None and float(notional) <= 0:
            print("Notional value must be positive.")
            return False
        
        return True
    
    def _prepare_order_base(self, symbol, side, qty=None, notional=None, time_in_force=TimeInForce.DAY):
        """
        Prepare base order parameters.
        
        Args:
            symbol (str): The symbol to trade
            side (OrderSide): Buy or sell
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            
        Returns:
            dict: Base order parameters
        """
        # Validate parameters
        if not self.validate_order_parameters(symbol, qty, notional):
            return None
        
        # Create base order
        order = {
            'symbol': symbol.upper(),
            'side': side.value,
            'time_in_force': time_in_force.value
        }
        
        # Add either qty or notional
        if qty is not None:
            order['qty'] = str(qty)
        else:
            order['notional'] = str(notional)
        
        return order
    
    def market_order(self, symbol, side, qty=None, notional=None, time_in_force=TimeInForce.DAY, extended_hours=False):
        """
        Create and submit a market order.
        
        Args:
            symbol (str): The symbol to trade
            side (OrderSide): Buy or sell
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            extended_hours (bool, optional): Allow extended hours trading. Defaults to False.
            
        Returns:
            dict: Order information or None if creation failed
        """
        # Prepare base order
        order = self._prepare_order_base(symbol, side, qty, notional, time_in_force)
        if not order:
            return None
        
        # Add market order specific parameters
        order['type'] = OrderType.MARKET.value
        if extended_hours:
            order['extended_hours'] = True
        
        # Submit the order
        return self.client.submit_order(order)
    
    def limit_order(self, symbol, side, limit_price, qty=None, notional=None, time_in_force=TimeInForce.DAY, extended_hours=False):
        """
        Create and submit a limit order.
        
        Args:
            symbol (str): The symbol to trade
            side (OrderSide): Buy or sell
            limit_price (float): The limit price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            extended_hours (bool, optional): Allow extended hours trading. Defaults to False.
            
        Returns:
            dict: Order information or None if creation failed
        """
        # Prepare base order
        order = self._prepare_order_base(symbol, side, qty, notional, time_in_force)
        if not order:
            return None
        
        # Validate limit price
        if not limit_price or float(limit_price) <= 0:
            print("Limit price must be positive.")
            return None
        
        # Add limit order specific parameters
        order['type'] = OrderType.LIMIT.value
        order['limit_price'] = str(limit_price)
        if extended_hours:
            order['extended_hours'] = True
        
        # Submit the order
        return self.client.submit_order(order)
    
    def stop_order(self, symbol, side, stop_price, qty=None, notional=None, time_in_force=TimeInForce.DAY):
        """
        Create and submit a stop order.
        
        Args:
            symbol (str): The symbol to trade
            side (OrderSide): Buy or sell
            stop_price (float): The stop price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            
        Returns:
            dict: Order information or None if creation failed
        """
        # Prepare base order
        order = self._prepare_order_base(symbol, side, qty, notional, time_in_force)
        if not order:
            return None
        
        # Validate stop price
        if not stop_price or float(stop_price) <= 0:
            print("Stop price must be positive.")
            return None
        
        # Add stop order specific parameters
        order['type'] = OrderType.STOP.value
        order['stop_price'] = str(stop_price)
        
        # Submit the order
        return self.client.submit_order(order)
    
    def stop_limit_order(self, symbol, side, stop_price, limit_price, qty=None, notional=None, time_in_force=TimeInForce.DAY):
        """
        Create and submit a stop limit order.
        
        Args:
            symbol (str): The symbol to trade
            side (OrderSide): Buy or sell
            stop_price (float): The stop price
            limit_price (float): The limit price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            
        Returns:
            dict: Order information or None if creation failed
        """
        # Prepare base order
        order = self._prepare_order_base(symbol, side, qty, notional, time_in_force)
        if not order:
            return None
        
        # Validate prices
        if not stop_price or float(stop_price) <= 0:
            print("Stop price must be positive.")
            return None
        
        if not limit_price or float(limit_price) <= 0:
            print("Limit price must be positive.")
            return None
        
        # Add stop limit order specific parameters
        order['type'] = OrderType.STOP_LIMIT.value
        order['stop_price'] = str(stop_price)
        order['limit_price'] = str(limit_price)
        
        # Submit the order
        return self.client.submit_order(order)
    
    def cancel_order(self, order_id):
        """
        Cancel an order by ID.
        
        Args:
            order_id (str): The order ID to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.client.cancel_order(order_id)
    
    def cancel_all_orders(self):
        """
        Cancel all open orders.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.client.cancel_all_orders()
    
    def get_orders(self, status=None, limit=50):
        """
        Get orders with optional filtering.
        
        Args:
            status (str, optional): Filter by order status. Defaults to None.
            limit (int, optional): Maximum number of orders to return. Defaults to 50.
            
        Returns:
            list: List of orders or None if request fails
        """
        return self.client.get_orders(status, limit)
    
    def get_order(self, order_id):
        """
        Get a specific order by ID.
        
        Args:
            order_id (str): The order ID
            
        Returns:
            dict: Order information or None if request fails
        """
        return self.client.get_order(order_id)


# Singleton instance for global access
_order_manager = None

def get_order_manager():
    """
    Get or create the global OrderManager instance.
    
    Returns:
        OrderManager: The global order manager
    """
    global _order_manager
    if _order_manager is None:
        _order_manager = OrderManager()
    return _order_manager 