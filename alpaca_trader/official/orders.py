"""
Order management using the official Alpaca SDK.
Implements different order types (market, limit, stop, stop limit).
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    StopLimitOrderRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce
from .account import get_official_account_manager


class OfficialOrderManager:
    """Manages order creation and submission using the official Alpaca SDK."""
    
    def __init__(self):
        """Initialize order manager with Alpaca client."""
        self.account_manager = get_official_account_manager()
        self.trading_client = self.account_manager.trading_client
    
    def is_ready(self):
        """
        Check if the order manager is ready to use.
        
        Returns:
            bool: True if manager is ready, False otherwise
        """
        return self.trading_client is not None
    
    def _validate_basic_params(self, symbol, side, qty, notional):
        """
        Validate basic order parameters.
        
        Args:
            symbol (str): The symbol to trade
            side (str or OrderSide): Buy or sell
            qty (float, optional): Quantity in shares
            notional (float, optional): Notional value in dollars
            
        Returns:
            OrderSide or None: The validated OrderSide or None if validation fails
        """
        if not symbol:
            print("Symbol is required.")
            return None
        
        # Either qty or notional must be provided, but not both
        if (qty is None and notional is None) or (qty is not None and notional is not None):
            print("Either 'qty' or 'notional' must be provided, but not both.")
            return None
        
        # Convert side to OrderSide enum if it's a string
        if isinstance(side, str):
            if side.lower() == "buy":
                side = OrderSide.BUY
            elif side.lower() == "sell":
                side = OrderSide.SELL
            else:
                print(f"Invalid order side: {side}. Must be 'buy' or 'sell'.")
                return None
        
        return side
    
    def _order_to_dict(self, order):
        """
        Convert Alpaca SDK order object to dictionary.
        
        Args:
            order: Alpaca SDK order object
            
        Returns:
            dict: Order information as dictionary
        """
        order_dict = {
            'id': order.id,
            'client_order_id': order.client_order_id,
            'symbol': order.symbol,
            'side': order.side.value if hasattr(order.side, 'value') else order.side,
            'type': order.type.value if hasattr(order.type, 'value') else order.type,
            'time_in_force': order.time_in_force.value if hasattr(order.time_in_force, 'value') else order.time_in_force,
            'status': order.status.value if hasattr(order.status, 'value') else order.status,
            'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
            'filled_at': order.filled_at.isoformat() if order.filled_at else None,
            'filled_qty': order.filled_qty,
            'filled_avg_price': order.filled_avg_price,
            'extended_hours': order.extended_hours
        }
        
        if hasattr(order, 'qty') and order.qty:
            order_dict['qty'] = order.qty
        if hasattr(order, 'notional') and order.notional:
            order_dict['notional'] = order.notional
        if hasattr(order, 'limit_price') and order.limit_price:
            order_dict['limit_price'] = order.limit_price
        if hasattr(order, 'stop_price') and order.stop_price:
            order_dict['stop_price'] = order.stop_price
        
        return order_dict
    
    def market_order(self, symbol, side, qty=None, notional=None, time_in_force=TimeInForce.DAY, extended_hours=False):
        """
        Create and submit a market order using the official SDK.
        
        Args:
            symbol (str): The symbol to trade
            side (str or OrderSide): Buy or sell
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            extended_hours (bool, optional): Allow extended hours trading. Defaults to False.
            
        Returns:
            dict: Order information or None if creation failed
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        # Validate inputs
        validated_side = self._validate_basic_params(symbol, side, qty, notional)
        if validated_side is None:
            return None
        
        try:
            # Prepare market order request
            order_data = {
                'symbol': symbol.upper(),
                'side': validated_side,
                'time_in_force': time_in_force,
                'extended_hours': extended_hours
            }
            
            # Add either qty or notional
            if qty is not None:
                order_data['qty'] = qty
            else:
                order_data['notional'] = notional
            
            # Create order request
            market_order = MarketOrderRequest(**order_data)
            
            # Submit the order
            order = self.trading_client.submit_order(market_order)
            
            # Convert to dictionary for compatibility with custom implementation
            order_info = self._order_to_dict(order)
                
            print(f"Market order submitted successfully. Order ID: {order_info['id']}")
            return order_info
            
        except Exception as e:
            print(f"Error creating market order: {e}")
            return None
    
    def limit_order(self, symbol, side, limit_price, qty=None, notional=None, time_in_force=TimeInForce.DAY, extended_hours=False):
        """
        Create and submit a limit order using the official SDK.
        
        Args:
            symbol (str): The symbol to trade
            side (str or OrderSide): Buy or sell
            limit_price (float): The limit price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            extended_hours (bool, optional): Allow extended hours trading. Defaults to False.
            
        Returns:
            dict: Order information or None if creation failed
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        # Validate inputs
        validated_side = self._validate_basic_params(symbol, side, qty, notional)
        if validated_side is None:
            return None
        
        # Validate limit price
        if not limit_price or float(limit_price) <= 0:
            print("Limit price must be positive.")
            return None
        
        try:
            # Prepare limit order request
            order_data = {
                'symbol': symbol.upper(),
                'side': validated_side,
                'limit_price': float(limit_price),
                'time_in_force': time_in_force,
                'extended_hours': extended_hours
            }
            
            # Add either qty or notional
            if qty is not None:
                order_data['qty'] = qty
            else:
                order_data['notional'] = notional
            
            # Create order request
            limit_order = LimitOrderRequest(**order_data)
            
            # Submit the order
            order = self.trading_client.submit_order(limit_order)
            
            # Convert to dictionary for compatibility with custom implementation
            order_info = self._order_to_dict(order)
                
            print(f"Limit order submitted successfully. Order ID: {order_info['id']}")
            return order_info
            
        except Exception as e:
            print(f"Error creating limit order: {e}")
            return None
    
    def stop_order(self, symbol, side, stop_price, qty=None, notional=None, time_in_force=TimeInForce.DAY):
        """
        Create and submit a stop order using the official SDK.
        
        Args:
            symbol (str): The symbol to trade
            side (str or OrderSide): Buy or sell
            stop_price (float): The stop price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            
        Returns:
            dict: Order information or None if creation failed
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        # Validate inputs
        validated_side = self._validate_basic_params(symbol, side, qty, notional)
        if validated_side is None:
            return None
        
        # Validate stop price
        if not stop_price or float(stop_price) <= 0:
            print("Stop price must be positive.")
            return None
        
        try:
            # Prepare stop order request
            order_data = {
                'symbol': symbol.upper(),
                'side': validated_side,
                'stop_price': float(stop_price),
                'time_in_force': time_in_force
            }
            
            # Add either qty or notional
            if qty is not None:
                order_data['qty'] = qty
            else:
                order_data['notional'] = notional
            
            # Create order request
            stop_order = StopOrderRequest(**order_data)
            
            # Submit the order
            order = self.trading_client.submit_order(stop_order)
            
            # Convert to dictionary for compatibility with custom implementation
            order_info = self._order_to_dict(order)
                
            print(f"Stop order submitted successfully. Order ID: {order_info['id']}")
            return order_info
            
        except Exception as e:
            print(f"Error creating stop order: {e}")
            return None
    
    def stop_limit_order(self, symbol, side, stop_price, limit_price, qty=None, notional=None, time_in_force=TimeInForce.DAY):
        """
        Create and submit a stop limit order using the official SDK.
        
        Args:
            symbol (str): The symbol to trade
            side (str or OrderSide): Buy or sell
            stop_price (float): The stop price
            limit_price (float): The limit price
            qty (float, optional): Quantity in shares. Defaults to None.
            notional (float, optional): Notional value in dollars. Defaults to None.
            time_in_force (TimeInForce, optional): Time in force. Defaults to TimeInForce.DAY.
            
        Returns:
            dict: Order information or None if creation failed
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        # Validate inputs
        validated_side = self._validate_basic_params(symbol, side, qty, notional)
        if validated_side is None:
            return None
        
        # Validate prices
        if not stop_price or float(stop_price) <= 0:
            print("Stop price must be positive.")
            return None
        
        if not limit_price or float(limit_price) <= 0:
            print("Limit price must be positive.")
            return None
        
        try:
            # Prepare stop limit order request
            order_data = {
                'symbol': symbol.upper(),
                'side': validated_side,
                'stop_price': float(stop_price),
                'limit_price': float(limit_price),
                'time_in_force': time_in_force
            }
            
            # Add either qty or notional
            if qty is not None:
                order_data['qty'] = qty
            else:
                order_data['notional'] = notional
            
            # Create order request
            stop_limit_order = StopLimitOrderRequest(**order_data)
            
            # Submit the order
            order = self.trading_client.submit_order(stop_limit_order)
            
            # Convert to dictionary for compatibility with custom implementation
            order_info = self._order_to_dict(order)
                
            print(f"Stop-limit order submitted successfully. Order ID: {order_info['id']}")
            return order_info
            
        except Exception as e:
            print(f"Error creating stop-limit order: {e}")
            return None
    
    def get_orders(self, status=None, limit=None):
        """
        Get orders with optional filtering.
        
        Args:
            status (str, optional): Filter by order status. Defaults to None.
            limit (int, optional): Maximum number of orders to return. Defaults to 50.
            
        Returns:
            list: List of orders or None if request fails
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        try:
            # Prepare parameters
            params = {}
            if status:
                params['status'] = status
            if limit:
                params['limit'] = limit
            
            # Get orders
            orders = self.trading_client.get_orders(**params)
            
            # Convert to dictionary list for compatibility with custom implementation
            order_list = []
            for order in orders:
                order_dict = self._order_to_dict(order)
                order_list.append(order_dict)
            
            return order_list
            
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
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return None
        
        try:
            order = self.trading_client.get_order(order_id)
            return self._order_to_dict(order)
            
        except Exception as e:
            print(f"Error getting order {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel an order by ID.
        
        Args:
            order_id (str): The order ID to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return False
        
        try:
            self.trading_client.cancel_order_by_id(order_id)
            print(f"Order {order_id} cancelled successfully.")
            return True
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self):
        """
        Cancel all open orders.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_ready():
            print("Order manager is not ready. Please configure the account first.")
            return False
        
        try:
            # Get all open orders
            open_orders = self.trading_client.get_orders()
            
            if not open_orders:
                print("No open orders to cancel.")
                return True
            
            # Cancel each order
            cancelled_count = 0
            for order in open_orders:
                try:
                    self.trading_client.cancel_order_by_id(order.id)
                    cancelled_count += 1
                except Exception as e:
                    print(f"Error cancelling order {order.id}: {e}")
            
            print(f"Cancelled {cancelled_count} of {len(open_orders)} orders.")
            return cancelled_count == len(open_orders)
            
        except Exception as e:
            print(f"Error cancelling all orders: {e}")
            return False


# Singleton instance for global access
_official_order_manager = None

def get_official_order_manager():
    """
    Get or create the global OfficialOrderManager instance.
    
    Returns:
        OfficialOrderManager: The global order manager
    """
    global _official_order_manager
    if _official_order_manager is None:
        _official_order_manager = OfficialOrderManager()
    return _official_order_manager 