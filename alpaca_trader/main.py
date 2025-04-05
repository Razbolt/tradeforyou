"""
Main entry point for the Alpaca trader application.
Demonstrates account setup and order execution.
"""

import sys
import time
from getpass import getpass
from decimal import Decimal
from .core.account import get_account_manager
from .core.orders import get_order_manager, OrderSide, TimeInForce


def setup_account():
    """
    Set up the Alpaca account with API keys.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    account_manager = get_account_manager()
    
    if account_manager.is_configured():
        print("Account is already configured with API keys.")
        account_manager.print_account_summary()
        
        # Ask if user wants to reconfigure
        response = input("Do you want to reconfigure the account? (y/n): ").strip().lower()
        if response != 'y':
            return True
    
    print("\n=== Alpaca Account Setup ===")
    print("You will need to provide your Alpaca API keys.")
    print("You can generate these from the Alpaca dashboard: https://app.alpaca.markets/paper/dashboard/overview")
    print("Note: Keys entered will be stored securely with encryption.\n")
    
    # Get API key and secret
    api_key = input("API Key: ").strip()
    api_secret = getpass("API Secret: ").strip()
    
    # Default to paper trading
    response = input("Use paper trading? (y/n, default: y): ").strip().lower()
    paper_trading = response != 'n'
    
    # Configure the account
    if account_manager.configure_account(api_key, api_secret, paper_trading):
        print("Account configuration successful!")
        account_manager.print_account_summary()
        return True
    else:
        print("Account configuration failed. Please try again.")
        return False


def display_menu():
    """Display the main menu options."""
    print("\n=== Alpaca Trader Menu ===")
    print("1. View Account")
    print("2. Place Market Order")
    print("3. Place Limit Order")
    print("4. Place Stop Order")
    print("5. Place Stop Limit Order")
    print("6. View Orders")
    print("7. Cancel Order")
    print("8. Cancel All Orders")
    print("9. View Positions")
    print("0. Exit")
    print("========================")


def get_order_side():
    """
    Get the order side from user input.
    
    Returns:
        OrderSide: The selected order side
    """
    while True:
        response = input("Order side (buy/sell): ").strip().lower()
        if response == 'buy':
            return OrderSide.BUY
        elif response == 'sell':
            return OrderSide.SELL
        else:
            print("Invalid choice. Please enter 'buy' or 'sell'.")


def get_time_in_force():
    """
    Get the time in force from user input.
    
    Returns:
        TimeInForce: The selected time in force
    """
    print("\nTime in Force Options:")
    print("1. Day (valid for the day only)")
    print("2. GTC (good till cancelled)")
    print("3. IOC (immediate or cancel)")
    print("4. FOK (fill or kill)")
    
    while True:
        response = input("Choose time in force (1-4, default 1): ").strip()
        if not response or response == '1':
            return TimeInForce.DAY
        elif response == '2':
            return TimeInForce.GTC
        elif response == '3':
            return TimeInForce.IOC
        elif response == '4':
            return TimeInForce.FOK
        else:
            print("Invalid choice. Please enter a number from 1-4.")


def get_quantity_or_notional():
    """
    Get either quantity or notional value from user input.
    
    Returns:
        tuple: (qty, notional) one of which will be None
    """
    response = input("Use quantity in shares (q) or notional value in dollars (n)? (q/n): ").strip().lower()
    
    if response == 'q':
        while True:
            qty_str = input("Quantity (shares): ").strip()
            try:
                qty = float(qty_str)
                if qty <= 0:
                    print("Quantity must be positive.")
                    continue
                return qty, None
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
    else:
        while True:
            notional_str = input("Notional value (dollars): $").strip()
            try:
                notional = float(notional_str)
                if notional <= 0:
                    print("Notional value must be positive.")
                    continue
                return None, notional
            except ValueError:
                print("Invalid input. Please enter a numeric value.")


def place_market_order():
    """Place a market order based on user input."""
    order_manager = get_order_manager()
    
    print("\n=== Place Market Order ===")
    
    # Get symbol
    symbol = input("Symbol (e.g., AAPL): ").strip().upper()
    
    # Get order side
    side = get_order_side()
    
    # Get quantity or notional
    qty, notional = get_quantity_or_notional()
    
    # Get time in force
    time_in_force = get_time_in_force()
    
    # Get extended hours preference
    extended_hours_str = input("Allow extended hours trading? (y/n, default: n): ").strip().lower()
    extended_hours = extended_hours_str == 'y'
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side.value}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Market")
    print(f"Time in Force: {time_in_force.value}")
    print(f"Extended Hours: {'Yes' if extended_hours else 'No'}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order
    result = order_manager.market_order(
        symbol, side, qty, notional, time_in_force, extended_hours
    )
    
    if result:
        print(f"Market order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit market order.")


def place_limit_order():
    """Place a limit order based on user input."""
    order_manager = get_order_manager()
    
    print("\n=== Place Limit Order ===")
    
    # Get symbol
    symbol = input("Symbol (e.g., AAPL): ").strip().upper()
    
    # Get order side
    side = get_order_side()
    
    # Get limit price
    while True:
        limit_price_str = input("Limit Price: $").strip()
        try:
            limit_price = float(limit_price_str)
            if limit_price <= 0:
                print("Limit price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
    # Get quantity or notional
    qty, notional = get_quantity_or_notional()
    
    # Get time in force
    time_in_force = get_time_in_force()
    
    # Get extended hours preference
    extended_hours_str = input("Allow extended hours trading? (y/n, default: n): ").strip().lower()
    extended_hours = extended_hours_str == 'y'
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side.value}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Limit")
    print(f"Limit Price: ${limit_price}")
    print(f"Time in Force: {time_in_force.value}")
    print(f"Extended Hours: {'Yes' if extended_hours else 'No'}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order
    result = order_manager.limit_order(
        symbol, side, limit_price, qty, notional, time_in_force, extended_hours
    )
    
    if result:
        print(f"Limit order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit limit order.")


def place_stop_order():
    """Place a stop order based on user input."""
    order_manager = get_order_manager()
    
    print("\n=== Place Stop Order ===")
    
    # Get symbol
    symbol = input("Symbol (e.g., AAPL): ").strip().upper()
    
    # Get order side
    side = get_order_side()
    
    # Get stop price
    while True:
        stop_price_str = input("Stop Price: $").strip()
        try:
            stop_price = float(stop_price_str)
            if stop_price <= 0:
                print("Stop price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
    # Get quantity or notional
    qty, notional = get_quantity_or_notional()
    
    # Get time in force
    time_in_force = get_time_in_force()
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side.value}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Stop")
    print(f"Stop Price: ${stop_price}")
    print(f"Time in Force: {time_in_force.value}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order
    result = order_manager.stop_order(
        symbol, side, stop_price, qty, notional, time_in_force
    )
    
    if result:
        print(f"Stop order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit stop order.")


def place_stop_limit_order():
    """Place a stop limit order based on user input."""
    order_manager = get_order_manager()
    
    print("\n=== Place Stop Limit Order ===")
    
    # Get symbol
    symbol = input("Symbol (e.g., AAPL): ").strip().upper()
    
    # Get order side
    side = get_order_side()
    
    # Get stop price
    while True:
        stop_price_str = input("Stop Price: $").strip()
        try:
            stop_price = float(stop_price_str)
            if stop_price <= 0:
                print("Stop price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
    # Get limit price
    while True:
        limit_price_str = input("Limit Price: $").strip()
        try:
            limit_price = float(limit_price_str)
            if limit_price <= 0:
                print("Limit price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
    # Get quantity or notional
    qty, notional = get_quantity_or_notional()
    
    # Get time in force
    time_in_force = get_time_in_force()
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side.value}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Stop Limit")
    print(f"Stop Price: ${stop_price}")
    print(f"Limit Price: ${limit_price}")
    print(f"Time in Force: {time_in_force.value}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order
    result = order_manager.stop_limit_order(
        symbol, side, stop_price, limit_price, qty, notional, time_in_force
    )
    
    if result:
        print(f"Stop limit order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit stop limit order.")


def view_orders():
    """View and display orders."""
    order_manager = get_order_manager()
    
    print("\n=== View Orders ===")
    print("Filter options:")
    print("1. All orders")
    print("2. Open orders only")
    print("3. Closed orders only")
    
    choice = input("Choose an option (1-3, default 1): ").strip()
    
    status = None
    if choice == '2':
        status = 'open'
    elif choice == '3':
        status = 'closed'
    
    limit_str = input("Maximum number of orders to display (default 10): ").strip()
    limit = int(limit_str) if limit_str and limit_str.isdigit() else 10
    
    orders = order_manager.get_orders(status, limit)
    
    if not orders:
        print("No orders found or failed to retrieve orders.")
        return
    
    print(f"\nFound {len(orders)} orders:")
    for i, order in enumerate(orders):
        print(f"\n--- Order {i+1} ---")
        print(f"ID: {order.get('id')}")
        print(f"Symbol: {order.get('symbol')}")
        print(f"Side: {order.get('side')}")
        print(f"Type: {order.get('type')}")
        
        # Print quantity info
        if 'qty' in order:
            print(f"Quantity: {order.get('qty')} shares")
        elif 'notional' in order:
            print(f"Notional: ${order.get('notional')}")
        
        # Print price info based on order type
        if order.get('type') == 'limit' or order.get('type') == 'stop_limit':
            print(f"Limit Price: ${order.get('limit_price')}")
        if order.get('type') == 'stop' or order.get('type') == 'stop_limit':
            print(f"Stop Price: ${order.get('stop_price')}")
        
        print(f"Time in Force: {order.get('time_in_force')}")
        print(f"Status: {order.get('status')}")
        
        # Print filled quantity and price if available
        if order.get('filled_qty'):
            print(f"Filled Quantity: {order.get('filled_qty')}")
        if order.get('filled_avg_price'):
            print(f"Filled Average Price: ${order.get('filled_avg_price')}")
        
        # Print submission and update times
        if order.get('submitted_at'):
            print(f"Submitted At: {order.get('submitted_at')}")
        if order.get('updated_at'):
            print(f"Updated At: {order.get('updated_at')}")


def cancel_order():
    """Cancel a specific order by ID."""
    order_manager = get_order_manager()
    
    print("\n=== Cancel Order ===")
    
    # First, display open orders
    orders = order_manager.get_orders(status='open')
    
    if not orders:
        print("No open orders found or failed to retrieve orders.")
        return
    
    print("\nOpen Orders:")
    for i, order in enumerate(orders):
        print(f"{i+1}. ID: {order.get('id')} - {order.get('symbol')} {order.get('side')} {order.get('qty') or order.get('notional')} @ {order.get('type')}")
    
    # Get order to cancel
    while True:
        choice = input("\nEnter order number to cancel (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(orders):
                order_id = orders[index].get('id')
                break
            else:
                print("Invalid order number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Confirm cancellation
    confirm = input(f"Confirm cancellation of order {order_id}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        return
    
    # Cancel the order
    if order_manager.cancel_order(order_id):
        print(f"Order {order_id} cancelled successfully.")
    else:
        print(f"Failed to cancel order {order_id}.")


def cancel_all_orders():
    """Cancel all open orders."""
    order_manager = get_order_manager()
    
    print("\n=== Cancel All Orders ===")
    
    # Confirm cancellation
    confirm = input("Are you sure you want to cancel ALL open orders? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        return
    
    # Cancel all orders
    if order_manager.cancel_all_orders():
        print("All open orders cancelled successfully.")
    else:
        print("Failed to cancel all orders.")


def view_positions():
    """View and display current positions."""
    from .core.client import get_alpaca_client
    client = get_alpaca_client()
    
    print("\n=== View Positions ===")
    
    positions = client.get_positions()
    
    if not positions:
        print("No positions found or failed to retrieve positions.")
        return
    
    print(f"\nFound {len(positions)} positions:")
    for i, position in enumerate(positions):
        print(f"\n--- Position {i+1} ---")
        print(f"Symbol: {position.get('symbol')}")
        print(f"Quantity: {position.get('qty')}")
        print(f"Side: {position.get('side')}")
        print(f"Market Value: ${position.get('market_value')}")
        print(f"Cost Basis: ${position.get('cost_basis')}")
        print(f"Unrealized P/L: ${position.get('unrealized_pl')}")
        print(f"Unrealized P/L %: {position.get('unrealized_plpc')}")
        print(f"Current Price: ${position.get('current_price')}")
        print(f"Avg Entry Price: ${position.get('avg_entry_price')}")


def main():
    """Main function to run the application."""
    from .core.client import get_alpaca_client
    
    print("Welcome to Alpaca Paper Trading Application")
    
    # Setup account if not configured
    if not get_account_manager().is_configured():
        if not setup_account():
            print("Account setup failed. Exiting...")
            return
    
    # Main menu loop
    while True:
        display_menu()
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == '0':
            print("Exiting Alpaca Trader. Goodbye!")
            break
        elif choice == '1':
            get_account_manager().print_account_summary()
        elif choice == '2':
            place_market_order()
        elif choice == '3':
            place_limit_order()
        elif choice == '4':
            place_stop_order()
        elif choice == '5':
            place_stop_limit_order()
        elif choice == '6':
            view_orders()
        elif choice == '7':
            cancel_order()
        elif choice == '8':
            cancel_all_orders()
        elif choice == '9':
            view_positions()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1) 