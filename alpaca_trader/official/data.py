"""
Data retrieval utilities using the official Alpaca SDK.
"""

import datetime
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import StockDataStream
from .account import get_official_account_manager


class DataManager:
    """Manages data retrieval using the official Alpaca SDK."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.account_manager = get_official_account_manager()
        self.api_key = self.account_manager.api_key
        self.api_secret = self.account_manager.api_secret
        self.crypto_client = None
        self.stock_client = None
        
        # Initialize clients if credentials are available
        if self.api_key and self.api_secret:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize the data clients with API keys."""
        try:
            self.crypto_client = CryptoHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.api_secret
            )
            
            self.stock_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.api_secret
            )
            return True
        except Exception as e:
            print(f"Error initializing data clients: {e}")
            return False
    
    def is_ready(self):
        """
        Check if the data manager is ready to use.
        
        Returns:
            bool: True if clients are initialized, False otherwise
        """
        return self.crypto_client is not None and self.stock_client is not None
    
    def get_crypto_bars(self, symbol, timeframe=TimeFrame.Day, start=None, end=None, limit=50):
        """
        Get historical bars for a crypto symbol.
        
        Args:
            symbol (str): The symbol to get bars for (e.g., 'BTC/USD')
            timeframe (TimeFrame, optional): The timeframe. Defaults to TimeFrame.DAY.
            start (datetime, optional): Start time. Defaults to 50 bars back from end.
            end (datetime, optional): End time. Defaults to now.
            limit (int, optional): Maximum number of bars. Defaults to 50.
            
        Returns:
            dict: Bar data or None if request fails
        """
        if not self.is_ready():
            print("Data manager is not ready. Please configure the account first.")
            return None
        
        try:
            # Set default end time to now if not provided
            if end is None:
                end = datetime.datetime.now()
            
            # Set default start time to 50 bars back if not provided
            if start is None:
                # Calculate start time based on timeframe
                if timeframe == TimeFrame.Day:
                    start = end - datetime.timedelta(days=limit)
                elif timeframe == TimeFrame.Hour:
                    start = end - datetime.timedelta(hours=limit)
                elif timeframe == TimeFrame.Minute:
                    start = end - datetime.timedelta(minutes=limit)
                else:
                    start = end - datetime.timedelta(days=limit)
            
            # Prepare request
            request_params = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            # Get bars
            bars = self.crypto_client.get_crypto_bars(request_params,feed='us')
            
            return bars.dict() if hasattr(bars, 'dict') else bars
            
        except Exception as e:
            print(f"Error getting crypto bars: {e}")
            return None
    
    def get_stock_bars(self, symbol, timeframe=TimeFrame.Day, start=None, end=None, limit=50):
        """
        Get historical bars for a stock symbol.
        
        Args:
            symbol (str): The symbol to get bars for (e.g., 'AAPL')
            timeframe (TimeFrame, optional): The timeframe. Defaults to TimeFrame.DAY.
            start (datetime, optional): Start time. Defaults to 50 bars back from end.
            end (datetime, optional): End time. Defaults to now.
            limit (int, optional): Maximum number of bars. Defaults to 50.
            
        Returns:
            dict: Bar data or None if request fails
        """
        if not self.is_ready():
            print("Data manager is not ready. Please configure the account first.")
            return None
        
        try:
            # Set default end time to now if not provided
            if end is None:
                end = datetime.datetime.now()
            
            # Set default start time to 50 bars back if not provided
            if start is None:
                # Calculate start time based on timeframe
                if timeframe == TimeFrame.Day:
                    start = end - datetime.timedelta(days=limit)
                elif timeframe == TimeFrame.Hour:
                    start = end - datetime.timedelta(hours=limit)
                elif timeframe == TimeFrame.Minute:
                    start = end - datetime.timedelta(minutes=limit)
                else:
                    start = end - datetime.timedelta(days=limit)
            
            # Prepare request
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                #end=end,
                limit=limit
            )
            
            # Get bars
            bars = self.stock_client.get_stock_bars(request_params)
            
            return bars.dict() if hasattr(bars, 'dict') else bars
            
        except Exception as e:
            print(f"Error getting stock bars: {e}")
            return None
    
    def print_bars(self, bars, symbol=None):
        """
        Print bar data in a readable format.
        
        Args:
            bars (dict): Bar data from get_crypto_bars or get_stock_bars
            symbol (str, optional): Symbol to display. If None, print all symbols.
        """
        if not bars:
            print("No bar data available.")
            return
        
        # Handle both single symbol and multi-symbol responses
        if isinstance(bars, dict) and 'bars' in bars:
            # Multi-symbol format from newer SDK versions
            if symbol is None:
                # Print all symbols
                for sym, sym_data in bars['bars'].items():
                    print(f"\n=== {sym} Bars ===")
                    for bar in sym_data:
                        self._print_bar(bar)
            elif symbol in bars['bars']:
                # Print specific symbol
                print(f"\n=== {symbol} Bars ===")
                for bar in bars['bars'][symbol]:
                    self._print_bar(bar)
            else:
                print(f"Symbol {symbol} not found in bar data.")
        elif isinstance(bars, dict) and symbol in bars:
            # Single symbol request format from newer SDK versions
            print(f"\n=== {symbol} Bars ===")
            for bar in bars[symbol]:
                self._print_bar(bar)
        else:
            # Handle older SDK versions or unexpected formats
            try:
                print("\n=== Bars ===")
                if isinstance(bars, dict):
                    for symbol, symbol_bars in bars.items():
                        print(f"\n=== {symbol} ===")
                        for bar in symbol_bars:
                            self._print_bar(bar)
                elif isinstance(bars, list):
                    for bar in bars:
                        self._print_bar(bar)
                else:
                    print("Unrecognized bar data format")
            except Exception as e:
                print(f"Error printing bars: {e}")
    
    def _print_bar(self, bar):
        """
        Print a single bar in a readable format.
        
        Args:
            bar (dict): Bar data
        """
        if isinstance(bar, dict):
            # Convert datetime objects to strings if needed
            timestamp = bar.get('timestamp')
            if isinstance(timestamp, datetime.datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"Time: {timestamp} | "
                  f"Open: {bar.get('open'):.2f} | "
                  f"High: {bar.get('high'):.2f} | "
                  f"Low: {bar.get('low'):.2f} | "
                  f"Close: {bar.get('close'):.2f} | "
                  f"Volume: {bar.get('volume'):.2f}")
        else:
            # Try to access attributes for object representations
            try:
                timestamp = bar.timestamp
                if isinstance(timestamp, datetime.datetime):
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"Time: {timestamp} | "
                      f"Open: {bar.open:.2f} | "
                      f"High: {bar.high:.2f} | "
                      f"Low: {bar.low:.2f} | "
                      f"Close: {bar.close:.2f} | "
                      f"Volume: {bar.volume:.2f}")
            except Exception as e:
                print(f"Unable to print bar: {e}")
    
    
# Singleton instance for global access
_data_manager = None

def get_data_manager():
    """
    Get or create the global DataManager instance.
    
    Returns:
        DataManager: The global data manager
    """
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


# Example usage
def demo_stock_data():
    """Demonstrate stock data retrieval."""
    data_manager = get_data_manager()
    
    if not data_manager.is_ready():
        print("Data manager is not ready. Please configure your account first.")
        return
    
    symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
    
    # Get daily bars for the last 10 days
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=10)
    
    print(f"\nGetting daily bars for {symbol} from {start.date()} to {end.date()}")
    bars = data_manager.get_stock_bars(
        symbol=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end
    )
    
    data_manager.print_bars(bars, symbol)


# Example usage
def demo_crypto_data():
    """Demonstrate crypto data retrieval."""
    data_manager = get_data_manager()
    
    if not data_manager.is_ready():
        print("Data manager is not ready. Please configure your account first.")
        return
    
    symbol = input("Enter crypto symbol (e.g., BTC/USD): ").strip().upper()
    
    # Get hourly bars for the last 24 hours
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=24)
    
    print(f"\nGetting hourly bars for {symbol} from {start} to {end}")
    bars = data_manager.get_crypto_bars(
        symbol=symbol,
        timeframe=TimeFrame.Hour,
        start=start,
        end=end
    )
    
    data_manager.print_bars(bars, symbol)


if __name__ == "__main__":
    # Example usage
    demo_choice = input("Demo stock (s) or crypto (c) data? (s/c): ").strip().lower()
    if demo_choice == 'c':
        demo_crypto_data()
    else:
        demo_stock_data() 