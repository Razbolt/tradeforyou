"""
Demo of Alpaca trading using the official SDK implementation.
Provides a simple interface for using the Alpaca Python SDK.
"""

import sys
import datetime
from getpass import getpass

# Import official implementation
from .account import get_official_account_manager
from .orders import get_official_order_manager
from .data import get_data_manager, demo_stock_data, demo_crypto_data
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.timeframe import TimeFrame


def setup_account():
    """
    Set up the Alpaca account with API keys.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
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
    account_manager = get_official_account_manager()
    
    # Configure implementation
    if account_manager.configure_account(api_key, api_secret, paper_trading):
        print("\nAccount configured successfully!")
        return True
    else:
        print("Account configuration failed.")
        return False


def display_menu():
    """Display the main menu options."""
    print("\n=== Alpaca Trading SDK Demo ===")
    print("1. View Account")
    print("2. Place Market Order")
    print("3. Place Limit Order")
    print("4. Place Stop Order")
    print("5. Place Stop-Limit Order")
    print("6. View Orders")
    print("7. Cancel Order")
    print("8. Cancel All Orders")
    print("9. Get Stock Market Data")
    print("10. Get Crypto Market Data")
    print("11. Setup Account")
    print("0. Exit")
    print("==============================")


def get_order_details():
    """
    Get common order details from user input.
    
    Returns:
        tuple: (symbol, side_str, qty, notional, extended_hours)
    """
    # Get symbol
    symbol = input("Symbol (e.g., AAPL): ").strip().upper()
    
    # Get order side
    while True:
        side_str = input("Order side (buy/sell): ").strip().lower()
        if side_str in ('buy', 'sell'):
            break
        else:
            print("Invalid choice. Please enter 'buy' or 'sell'.")
    
    # Get quantity or notional
    use_qty = input("Use quantity (q) or notional value (n)? (q/n): ").strip().lower() == 'q'
    
    qty = None
    notional = None
    
    if use_qty:
        while True:
            try:
                qty_str = input("Quantity (shares): ").strip()
                qty = float(qty_str)
                if qty <= 0:
                    print("Quantity must be positive.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
    else:
        while True:
            try:
                notional_str = input("Notional value (dollars): $").strip()
                notional = float(notional_str)
                if notional <= 0:
                    print("Notional value must be positive.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
    
    # Get extended hours preference
    extended_hours = input("Allow extended hours trading? (y/n, default: n): ").strip().lower() == 'y'
    
    return symbol, side_str, qty, notional, extended_hours


def get_price_input(prompt):
    """
    Get a price input from the user.
    
    Args:
        prompt (str): The prompt to display
        
    Returns:
        float: The price entered by the user
    """
    while True:
        try:
            price_str = input(prompt).strip()
            price = float(price_str)
            if price <= 0:
                print("Price must be positive.")
                continue
            return price
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def place_market_order():
    """Place a market order using the official SDK implementation."""
    print("\n=== Place Market Order ===")
    
    # Get order details
    symbol, side_str, qty, notional, extended_hours = get_order_details()
    
    # Set time in force to DAY
    time_in_force = TimeInForce.DAY
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side_str}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Market")
    print(f"Time in Force: day")
    print(f"Extended Hours: {'Yes' if extended_hours else 'No'}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order using official SDK
    order_manager = get_official_order_manager()
    result = order_manager.market_order(
        symbol, side_str, qty, notional, time_in_force, extended_hours
    )
    
    if result:
        print(f"Market order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit market order.")


def place_limit_order():
    """Place a limit order using the official SDK implementation."""
    print("\n=== Place Limit Order ===")
    
    # Get order details
    symbol, side_str, qty, notional, extended_hours = get_order_details()
    
    # Get limit price
    limit_price = get_price_input("Limit price: $")
    
    # Set time in force to DAY
    time_in_force = TimeInForce.DAY
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side_str}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Limit")
    print(f"Limit Price: ${limit_price}")
    print(f"Time in Force: day")
    print(f"Extended Hours: {'Yes' if extended_hours else 'No'}")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order using official SDK
    order_manager = get_official_order_manager()
    result = order_manager.limit_order(
        symbol, side_str, limit_price, qty, notional, time_in_force, extended_hours
    )
    
    if result:
        print(f"Limit order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit limit order.")


def place_stop_order():
    """Place a stop order using the official SDK implementation."""
    print("\n=== Place Stop Order ===")
    
    # Get order details
    symbol, side_str, qty, notional, _ = get_order_details()  # Extended hours not applicable
    
    # Get stop price
    stop_price = get_price_input("Stop price: $")
    
    # Set time in force to DAY
    time_in_force = TimeInForce.DAY
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side_str}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Stop")
    print(f"Stop Price: ${stop_price}")
    print(f"Time in Force: day")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order using official SDK
    order_manager = get_official_order_manager()
    result = order_manager.stop_order(
        symbol, side_str, stop_price, qty, notional, time_in_force
    )
    
    if result:
        print(f"Stop order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit stop order.")


def place_stop_limit_order():
    """Place a stop-limit order using the official SDK implementation."""
    print("\n=== Place Stop-Limit Order ===")
    
    # Get order details
    symbol, side_str, qty, notional, _ = get_order_details()  # Extended hours not applicable
    
    # Get stop and limit prices
    stop_price = get_price_input("Stop price: $")
    limit_price = get_price_input("Limit price: $")
    
    # Set time in force to DAY
    time_in_force = TimeInForce.DAY
    
    # Confirm order
    print("\nOrder Summary:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side_str}")
    if qty:
        print(f"Quantity: {qty} shares")
    else:
        print(f"Notional: ${notional}")
    print(f"Type: Stop-Limit")
    print(f"Stop Price: ${stop_price}")
    print(f"Limit Price: ${limit_price}")
    print(f"Time in Force: day")
    
    confirm = input("\nConfirm order (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        return
    
    # Submit order using official SDK
    order_manager = get_official_order_manager()
    result = order_manager.stop_limit_order(
        symbol, side_str, stop_price, limit_price, qty, notional, time_in_force
    )
    
    if result:
        print(f"Stop-limit order submitted successfully. Order ID: {result.get('id')}")
    else:
        print("Failed to submit stop-limit order.")


def view_orders():
    """View orders using the official SDK implementation."""
    print("\n=== View Orders ===")
    
    order_manager = get_official_order_manager()
    orders = order_manager.get_orders()
    
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
        
        # Print price info
        if 'limit_price' in order:
            print(f"Limit Price: ${order.get('limit_price')}")
        if 'stop_price' in order:
            print(f"Stop Price: ${order.get('stop_price')}")
        
        print(f"Status: {order.get('status')}")


def cancel_order():
    """Cancel an order using the official SDK implementation."""
    print("\n=== Cancel Order ===")
    
    order_manager = get_official_order_manager()
    orders = order_manager.get_orders(status="open")
    
    if not orders:
        print("No open orders found to cancel.")
        return
    
    print("\nOpen Orders:")
    for i, order in enumerate(orders):
        print(f"{i+1}. {order.get('symbol')} - {order.get('side')} - {order.get('type')} - ID: {order.get('id')}")
    
    # Get order to cancel
    while True:
        try:
            choice = int(input("\nEnter order number to cancel (0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            if 1 <= choice <= len(orders):
                break
            print(f"Please enter a number between 1 and {len(orders)}.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get the order ID to cancel
    order_id = orders[choice-1].get('id')
    
    # Confirm cancellation
    confirm = input(f"\nAre you sure you want to cancel order {order_id}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        return
    
    # Cancel the order
    success = order_manager.cancel_order(order_id)
    
    if success:
        print(f"Order {order_id} cancelled successfully.")
    else:
        print(f"Failed to cancel order {order_id}.")


def cancel_all_orders():
    """Cancel all open orders using the official SDK implementation."""
    print("\n=== Cancel All Orders ===")
    
    order_manager = get_official_order_manager()
    orders = order_manager.get_orders(status="open")
    
    if not orders:
        print("No open orders found to cancel.")
        return
    
    # Confirm cancellation
    confirm = input(f"\nAre you sure you want to cancel all {len(orders)} open orders? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        return
    
    # Cancel all orders
    success = order_manager.cancel_all_orders()
    
    if success:
        print("All open orders cancelled successfully.")
    else:
        print("Failed to cancel all open orders.")


def main():
    """Main function for the demo application."""
    print("Welcome to Alpaca Trading SDK Demo")
    
    # Check if account is configured
    account_manager = get_official_account_manager()
    
    if not account_manager.is_configured():
        print("Account not configured. Please set up your account first.")
        if not setup_account():
            print("Account setup failed. Exiting...")
            return
    
    # Main menu loop
    while True:
        display_menu()
        choice = input("Enter your choice (0-11): ").strip()
        
        if choice == '0':
            print("Exiting demo. Goodbye!")
            break
        elif choice == '1':
            account_manager.print_account_summary()
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
            demo_stock_data()
        elif choice == '10':
            demo_crypto_data()
        elif choice == '11':
            setup_account()
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