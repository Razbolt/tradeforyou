"""
AIBroker class that processes user instructions using Claude and executes trades via Alpaca API.
"""

import os
import json
from typing import Dict, List, Any, Optional
import anthropic
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime
import re
import uuid

class UUIDEncoder(json.JSONEncoder):
    """JSON Encoder that can handle UUID objects."""
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # Convert UUID to string
            return str(obj)
        return json.JSONEncoder.default(self, obj)

class AIBroker:
    """
    AI-powered broker that interprets user instructions using Claude
    and executes trades using Alpaca.
    """
    
    def __init__(self):
        """Initialize the broker with Claude and Alpaca clients."""
        # Load environment variables if not already loaded
        self._load_env_vars()
        
        # Initialize Claude client
        self.claude_client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
        # Initialize Alpaca clients
        self.trading_client = TradingClient(
            api_key=os.environ.get("ALPACA_API_KEY"),
            secret_key=os.environ.get("ALPACA_SECRET_KEY"),
            paper=True  # Use paper trading for safety
        )
        
        self.data_client = StockHistoricalDataClient(
            api_key=os.environ.get("ALPACA_API_KEY"),
            secret_key=os.environ.get("ALPACA_SECRET_KEY")
        )
        
        # Define available actions for the Claude agent
        self.available_actions = [
            "buy_stock(symbol, quantity)",
            "get_stock_price(symbol)",
            "get_account_info()",
        ]
    
    def _load_env_vars(self):
        """Load environment variables from .env file if present."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("python-dotenv not installed. Using system environment variables.")
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get current market data for the specified symbols.
        
        Args:
            symbols: List of stock symbols to get data for
            
        Returns:
            Dictionary containing market data for the specified symbols
        """
        market_data = {}
        
        # Get latest stock bars
        for symbol in symbols:
            try:
                # Try to get the latest price using the same approach as get_stock_price
                end = datetime.datetime.now()
                start = end - datetime.timedelta(days=30)
                
                # Try different timeframes to get most recent data
                for timeframe in [TimeFrame.Day, TimeFrame.Hour, TimeFrame.Minute]:
                    try:
                        bars_request = StockBarsRequest(
                            symbol_or_symbols=symbol,
                            timeframe=timeframe,
                            start=start,
                            limit=1  # Just get the latest bar
                        )
                        
                        bars = self.data_client.get_stock_bars(bars_request)
                        
                        # Check the bars structure and extract data
                        if hasattr(bars, 'data') and symbol in bars.data:
                            # Newer SDK version with data attribute
                            bars_data = bars.data
                            if len(bars_data[symbol]) > 0:
                                latest_bar = bars_data[symbol][-1]
                                # Try both attribute and dict-style access
                                try:
                                    close = float(latest_bar.close)
                                    open_price = float(latest_bar.open)
                                    timestamp = str(latest_bar.timestamp)
                                    volume = float(latest_bar.volume)
                                except AttributeError:
                                    close = float(latest_bar['close'])
                                    open_price = float(latest_bar['open'])
                                    timestamp = str(latest_bar['timestamp'])
                                    volume = float(latest_bar['volume'])
                                
                                market_data[symbol] = {
                                    "price": close,
                                    "change": close - open_price,
                                    "volume": volume,
                                    "timestamp": timestamp
                                }
                                break  # Got the data, no need to try other timeframes
                        elif symbol in bars:
                            # Traditional direct dict structure
                            if len(bars[symbol]) > 0:
                                latest_bar = bars[symbol][-1]
                                # Try both attribute and dict-style access
                                try:
                                    close = float(latest_bar.close)
                                    open_price = float(latest_bar.open)
                                    timestamp = str(latest_bar.timestamp)
                                    volume = float(latest_bar.volume)
                                except AttributeError:
                                    close = float(latest_bar['close'])
                                    open_price = float(latest_bar['open'])
                                    timestamp = str(latest_bar['timestamp'])
                                    volume = float(latest_bar['volume'])
                                
                                market_data[symbol] = {
                                    "price": close,
                                    "change": close - open_price,
                                    "volume": volume,
                                    "timestamp": timestamp
                                }
                                break  # Got the data, no need to try other timeframes
                    except Exception:
                        # Try the next timeframe
                        continue
                
                # If no data was found after trying all timeframes
                if symbol not in market_data:
                    market_data[symbol] = {
                        "price": None,
                        "error": "No data found",
                        "note": "Stock symbol is valid and can be traded even without price data",
                        "tradeable": True
                    }
            except Exception as e:
                # Still provide placeholder data with a note for Claude
                market_data[symbol] = {
                    "price": None,
                    "error": str(e),
                    "note": "Stock symbol can still be traded even without price data",
                    "tradeable": True
                }
        
        # Get account information
        try:
            account = self.trading_client.get_account()
            market_data["account"] = {
                "equity": float(account.equity),
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "status": account.status
            }
        except Exception as e:
            market_data["account"] = {"error": str(e)}
            
        return market_data
    
    def _order_to_dict(self, order):
        """
        Convert Alpaca SDK order object to dictionary.
        Based on the pattern in official/orders.py
        
        Args:
            order: Alpaca SDK order object
            
        Returns:
            dict: Order information as dictionary
        """
        try:
            order_dict = {
                'id': str(order.id),  # Convert UUID to string
                'client_order_id': str(order.client_order_id),  # Convert UUID to string
                'symbol': order.symbol,
                'side': order.side.value if hasattr(order.side, 'value') else str(order.side),
                'type': order.type.value if hasattr(order.type, 'value') else str(order.type),
                'status': order.status.value if hasattr(order.status, 'value') else str(order.status),
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0
            }
            
            if hasattr(order, 'qty') and order.qty:
                order_dict['qty'] = float(order.qty)
            if hasattr(order, 'notional') and order.notional:
                order_dict['notional'] = float(order.notional)
            if hasattr(order, 'time_in_force'):
                order_dict['time_in_force'] = order.time_in_force.value if hasattr(order.time_in_force, 'value') else str(order.time_in_force)
            
            return order_dict
        except Exception as e:
            return {
                'error': f"Error converting order to dictionary: {str(e)}",
                'raw_order': str(order)
            }
    
    def buy_stock(self, symbol: str, quantity: int) -> Dict[str, Any]:
        """
        Buy a specified quantity of stock.
        Based on the pattern in official/orders.py
        
        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy
            
        Returns:
            Dictionary containing the order status and details
        """
        try:
            # Validate inputs
            if not symbol:
                return {
                    "status": "error",
                    "message": "Symbol is required"
                }
            
            if not quantity or quantity <= 0:
                return {
                    "status": "error",
                    "message": "Quantity must be positive"
                }
            
            # Create a market order - using pattern from official/orders.py
            order_data = MarketOrderRequest(
                symbol=symbol.upper(),
                qty=quantity,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY  # Using correct enum value
            )
            
            # Submit the order
            order = self.trading_client.submit_order(order_data)
            
            # Convert to dictionary for easier handling
            order_info = self._order_to_dict(order)
            
            return {
                "status": "success",
                "order_id": str(order.id),  # Convert UUID to string
                "symbol": order.symbol,
                "quantity": float(order.qty) if order.qty else 0,
                "order_status": str(order.status),  # Convert enum to string
                "details": order_info
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the current price for a stock.
        Based on the pattern in official/data.py
        
        Args:
            symbol: Stock symbol to get price for
            
        Returns:
            Dictionary containing the price information
        """
        # Normalize symbol
        symbol = symbol.strip().upper()
        
        # Try multiple approaches to get stock price
        # 1. First try with daily bars
        try:
            end = datetime.datetime.now()
            start = end - datetime.timedelta(days=30)  # Last 30 days
            
            # Try with different timeframes in case one fails
            for timeframe in [TimeFrame.Day, TimeFrame.Hour, TimeFrame.Minute]:
                try:
                    timeframe_str = str(timeframe).split('.')[-1]  # Extract name from TimeFrame enum
                    bars_request = StockBarsRequest(
                        symbol_or_symbols=symbol,
                        timeframe=timeframe,
                        start=start,
                        limit=1  # Just get the latest bar
                    )
                    
                    bars = self.data_client.get_stock_bars(bars_request)
                    
                    # Check the bars structure and extract data
                    if hasattr(bars, 'data') and symbol in bars.data:
                        # Newer SDK version with data attribute
                        bars_data = bars.data
                        if len(bars_data[symbol]) > 0:
                            latest_bar = bars_data[symbol][-1]
                            # Try both attribute and dict-style access
                            try:
                                price = float(latest_bar.close)
                                timestamp = str(latest_bar.timestamp)
                            except AttributeError:
                                price = float(latest_bar['close'])
                                timestamp = str(latest_bar['timestamp'])
                                
                            return {
                                "status": "success",
                                "symbol": symbol,
                                "price": price,
                                "timestamp": timestamp,
                                "note": f"Price from latest available {timeframe_str} bar"
                            }
                    elif symbol in bars:
                        # Traditional direct dict structure
                        if len(bars[symbol]) > 0:
                            latest_bar = bars[symbol][-1]
                            # Try both attribute and dict-style access
                            try:
                                price = float(latest_bar.close)
                                timestamp = str(latest_bar.timestamp)
                            except AttributeError:
                                price = float(latest_bar['close'])
                                timestamp = str(latest_bar['timestamp'])
                                
                            return {
                                "status": "success",
                                "symbol": symbol,
                                "price": price,
                                "timestamp": timestamp,
                                "note": f"Price from latest available {timeframe_str} bar"
                            }
                except Exception:
                    # Continue to next timeframe if this one fails
                    continue
            
            # 2. If all timeframes failed, try a broader date range
            try:
                # Try a longer time window
                start = end - datetime.timedelta(days=90)  # Last 90 days
                bars_request = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame.Day,
                    start=start,
                    limit=5  # Get more bars to increase chances of finding data
                )
                
                bars = self.data_client.get_stock_bars(bars_request)
                
                # Check the bars structure and extract data
                if hasattr(bars, 'data') and symbol in bars.data:
                    # Newer SDK version with data attribute
                    bars_data = bars.data
                    if len(bars_data[symbol]) > 0:
                        latest_bar = bars_data[symbol][-1]
                        # Try both attribute and dict-style access
                        try:
                            price = float(latest_bar.close)
                            timestamp = str(latest_bar.timestamp)
                        except AttributeError:
                            price = float(latest_bar['close'])
                            timestamp = str(latest_bar['timestamp'])
                            
                        return {
                            "status": "success",
                            "symbol": symbol,
                            "price": price,
                            "timestamp": timestamp,
                            "note": "Historical price data - may not be current"
                        }
                elif symbol in bars:
                    # Traditional direct dict structure
                    if len(bars[symbol]) > 0:
                        latest_bar = bars[symbol][-1]
                        # Try both attribute and dict-style access
                        try:
                            price = float(latest_bar.close)
                            timestamp = str(latest_bar.timestamp)
                        except AttributeError:
                            price = float(latest_bar['close'])
                            timestamp = str(latest_bar['timestamp'])
                            
                        return {
                            "status": "success",
                            "symbol": symbol,
                            "price": price,
                            "timestamp": timestamp,
                            "note": "Historical price data - may not be current"
                        }
            except Exception:
                # Continue to fallback if this fails
                pass
            
            # 3. Fallback - return missing price but mark as tradeable
            return {
                "status": "partial",
                "symbol": symbol,
                "price": None,
                "message": f"No price data available for {symbol}",
                "note": "Stock can still be traded without current price data",
                "tradeable": True
            }
        
        except Exception as e:
            # Global error handling
            return {
                "status": "error",
                "symbol": symbol,
                "message": str(e),
                "note": "Stock can still be traded without current price data",
                "tradeable": True
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get current account information.
        
        Returns:
            Dictionary containing account details
        """
        try:
            account = self.trading_client.get_account()
            return {
                "status": "success",
                "equity": float(account.equity),
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "day_trade_count": account.daytrade_count,
                "status": account.status
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def extract_action_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract action information from the Claude response.
        
        Args:
            response: Claude's response text
            
        Returns:
            List of action dictionaries with function name and parameters
        """
        actions = []
        
        # Look for actions_taken section
        actions_taken_match = re.search(r'<actions_taken>(.*?)</actions_taken>', response, re.DOTALL)
        if not actions_taken_match:
            return actions
        
        actions_text = actions_taken_match.group(1).strip()
        
        # Enhanced action pattern matching with more flexible patterns
        action_patterns = [
            # Buy stock patterns with variations
            r'buy_stock\(\s*(?:"|\')?(.*?)(?:"|\')?\s*,\s*(\d+)\s*\)',  # buy_stock("AAPL", 10) or buy_stock(AAPL, 10)
            r'buy_stock\(\s*(?:"|\')?(.*?)(?:"|\')?\s*,\s*quantity\s*=\s*(\d+)\s*\)',  # buy_stock("AAPL", quantity=10)
            r'buy_stock\(\s*symbol\s*=\s*(?:"|\')?(.*?)(?:"|\')?\s*,\s*quantity\s*=\s*(\d+)\s*\)',  # buy_stock(symbol="AAPL", quantity=10)
            r'buy\s+(\d+)\s+shares?\s+of\s+([A-Z]+)',  # Buy 10 shares of AAPL
            r'buy\s+([A-Z]+)\s+(\d+)\s+shares?',        # Buy AAPL 10 shares
            
            # Get stock price patterns
            r'get_stock_price\(\s*(?:"|\')?(.*?)(?:"|\')?\s*\)',  # get_stock_price("AAPL") or get_stock_price(AAPL)
            r'get_stock_price\(\s*symbol\s*=\s*(?:"|\')?(.*?)(?:"|\')?\s*\)',  # get_stock_price(symbol="AAPL")
            
            # Account info patterns
            r'get_account_info\(\s*\)',  # get_account_info()
        ]
        
        # Process each line in the actions_taken section
        for line in actions_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check for buy_stock patterns
            for pattern_index in [0, 1, 2, 3, 4]:
                match = re.search(action_patterns[pattern_index], line, re.IGNORECASE)
                if match:
                    try:
                        if pattern_index <= 2:  # Standard function call format
                            symbol = match.group(1).strip().strip('"\'').upper()
                            quantity = int(match.group(2))
                        elif pattern_index == 3:  # "Buy X shares of Y" format
                            quantity = int(match.group(1))
                            symbol = match.group(2).strip().upper()
                        elif pattern_index == 4:  # "Buy Y X shares" format
                            symbol = match.group(1).strip().upper()
                            quantity = int(match.group(2))
                        
                        # Validate symbol and quantity
                        if symbol and quantity > 0:
                            actions.append({
                                "action": "buy_stock",
                                "params": {"symbol": symbol, "quantity": quantity}
                            })
                    except (ValueError, IndexError):
                        # Skip if we can't parse the values properly
                        continue
                    break  # Found a match, no need to check other patterns
            
            # Check for get_stock_price patterns
            for pattern_index in [5, 6]:
                match = re.search(action_patterns[pattern_index], line, re.IGNORECASE)
                if match:
                    try:
                        symbol = match.group(1).strip().strip('"\'').upper()
                        if symbol:  # Only add if we have a valid symbol
                            actions.append({
                                "action": "get_stock_price",
                                "params": {"symbol": symbol}
                            })
                    except (ValueError, IndexError):
                        continue
                    break
            
            # Check for get_account_info pattern
            if re.search(action_patterns[7], line, re.IGNORECASE):
                actions.append({
                    "action": "get_account_info",
                    "params": {}
                })
        
        return actions
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the specified actions.
        
        Args:
            actions: List of action dictionaries with function and parameters
            
        Returns:
            Dictionary containing results of all actions
        """
        results = {}
        
        # Set up logging for actions
        print(f"Executing {len(actions)} actions:")
        for i, action in enumerate(actions):
            action_name = action["action"]
            params = action["params"]
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            print(f"  {i+1}. {action_name}({param_str})")
            
            try:
                if action_name == "buy_stock":
                    # Validate parameters
                    symbol = params.get("symbol", "").strip().upper()
                    quantity = int(params.get("quantity", 0))
                    
                    if not symbol:
                        results[f"{action_name}_{i}"] = {
                            "status": "error",
                            "message": "Missing or invalid symbol"
                        }
                        continue
                        
                    if quantity <= 0:
                        results[f"{action_name}_{i}"] = {
                            "status": "error",
                            "message": "Quantity must be positive"
                        }
                        continue
                    
                    # Execute the action
                    result = self.buy_stock(symbol, quantity)
                    results[f"{action_name}_{i}"] = result
                    
                elif action_name == "get_stock_price":
                    symbol = params.get("symbol", "").strip().upper()
                    if not symbol:
                        results[f"{action_name}_{i}"] = {
                            "status": "error",
                            "message": "Missing or invalid symbol"
                        }
                        continue
                    
                    result = self.get_stock_price(symbol)
                    results[f"{action_name}_{i}"] = result
                    
                elif action_name == "get_account_info":
                    result = self.get_account_info()
                    results[f"{action_name}_{i}"] = result
                    
                else:
                    results[f"unknown_action_{i}"] = {
                        "status": "error",
                        "message": f"Unknown action: {action_name}"
                    }
            except Exception as e:
                results[f"{action_name}_{i}_error"] = {
                    "status": "error",
                    "message": f"Error executing {action_name}: {str(e)}"
                }
                print(f"Error executing {action_name}: {str(e)}")
        
        return results
    
    def process_instruction(self, user_input: str) -> str:
        """
        Process a user instruction using Claude and execute necessary actions.
        
        Args:
            user_input: The user's text instruction
            
        Returns:
            String response to the user
        """
        try:
            # Common company name to symbol mappings
            company_to_symbol = {
                'APPLE': 'AAPL',
                'MICROSOFT': 'MSFT',
                'AMAZON': 'AMZN',
                'GOOGLE': 'GOOGL',
                'ALPHABET': 'GOOGL',
                'TESLA': 'TSLA',
                'NVIDIA': 'NVDA',
                'META': 'META',
                'FACEBOOK': 'META',
                'NETFLIX': 'NFLX',
                'ANALOG DEVICES': 'ADI',
                'INTEL': 'INTC',
                'AMD': 'AMD',
                'ADVANCED MICRO DEVICES': 'AMD',
                'COCA COLA': 'KO',
                'COCA-COLA': 'KO',
                'DISNEY': 'DIS',
                'WALT DISNEY': 'DIS',
                'JPMORGAN': 'JPM',
                'JP MORGAN': 'JPM',
                'BANK OF AMERICA': 'BAC',
                'GOLDMAN SACHS': 'GS',
                'JOHNSON & JOHNSON': 'JNJ',
                'JOHNSON AND JOHNSON': 'JNJ',
                'VISA': 'V',
                'MASTERCARD': 'MA',
                'WALMART': 'WMT',
                'TARGET': 'TGT',
                'COSTCO': 'COST',
                'HOME DEPOT': 'HD',
                'NIKE': 'NKE',
                'MCDONALDS': 'MCD',
                'MCDONALD\'S': 'MCD',
                'STARBUCKS': 'SBUX',
                'PFIZER': 'PFE',
                'MODERNA': 'MRNA',
                'EXXON': 'XOM',
                'EXXONMOBIL': 'XOM',
                'EXXON MOBIL': 'XOM',
                'CHEVRON': 'CVX',
                'BOEING': 'BA',
                'AMERICAN AIRLINES': 'AAL',
                'DELTA': 'DAL',
                'DELTA AIR LINES': 'DAL'
            }
            
            # Extract symbols from user input for market data
            # This regex looks for potential stock symbols (1-5 uppercase letters)
            symbols = re.findall(r'\b[A-Z]{1,5}\b', user_input.upper())
            symbols = list(set(symbols))  # Remove duplicates
            
            # Look for specific ticker mentions with $ prefix (e.g., $TSLA)
            dollar_symbols = re.findall(r'\$([A-Z]{1,5})\b', user_input.upper())
            symbols.extend(dollar_symbols)
            
            # Look for company names in the input
            user_input_upper = user_input.upper()
            for company, symbol in company_to_symbol.items():
                if company in user_input_upper and symbol not in symbols:
                    symbols.append(symbol)
            
            symbols = list(set(symbols))  # Remove duplicates again
            
            # Filter out common words that might be matched as symbols
            common_words = {'I', 'A', 'AN', 'THE', 'AND', 'OR', 'FOR', 'TO', 'IN', 'OF', 'AT', 'BY', 'AS', 
                           'IS', 'ARE', 'AM', 'BE', 'BEEN', 'BEING', 'WAS', 'WERE', 'HAS', 'HAVE', 'HAD',
                           'DO', 'DOES', 'DID', 'CAN', 'COULD', 'WILL', 'WOULD', 'SHALL', 'SHOULD', 'MAY',
                           'MIGHT', 'MUST', 'THAT', 'WHICH', 'WHO', 'WHOM', 'WHOSE', 'WHAT', 'PRICE'}
            symbols = [s for s in symbols if s not in common_words]
            
            # Print extracted symbols for debugging
            print(f"Extracted symbols from user input: {symbols}")
            
            # Get market data for relevant symbols
            market_data = self.get_market_data(symbols)
            
            # Create a mapping dictionary to help Claude understand company names
            company_mapping = {}
            for company, symbol in company_to_symbol.items():
                if symbol in symbols:
                    company_mapping[company] = symbol
            
            # Format message for Claude with clearer function calling examples
            prompt = f"""You are an AI-powered financial broker assistant. Your role is to interpret user input, execute financial actions based on that input, and provide relevant information to the user. Follow these instructions carefully:

1. Available Actions:
<available_actions>
{self.available_actions}
</available_actions>

Review the list of available actions above. These are the only actions you are authorized to execute.
IMPORTANT: When executing actions, use the exact function call format:
- buy_stock(symbol, quantity) - Example: buy_stock("AAPL", 10)
- get_stock_price(symbol) - Example: get_stock_price("AAPL")
- get_account_info() - Example: get_account_info()

2. Market Data:
<market_data>
{json.dumps(market_data, indent=2)}
</market_data>

3. Company Name to Symbol Mapping:
<company_mapping>
{json.dumps(company_mapping, indent=2)}
</company_mapping>

Use this mapping to understand when a user refers to a company by name rather than symbol.

4. Processing User Input:
When you receive user input, analyze it carefully to determine the user's intent. The user input will be provided in the following format:

<user_input>
{user_input}
</user_input>

5. IMPORTANT INSTRUCTION FOR BUY ORDERS:
If the user asks to buy a stock, you MUST execute the buy_stock() function call even if price data is unavailable. When the user asks to buy a stock:
- NEVER refuse to execute buy orders due to missing price data
- ALWAYS include buy_stock() in your actions_taken section exactly as shown
- Use the exact format: buy_stock("SYMBOL", QUANTITY)

6. Execution Logic:
- For any buy request like "Buy X shares of Y", you MUST execute buy_stock("Y", X)
- For requests to check stock prices, execute get_stock_price("SYMBOL")
- For requests about account information, execute get_account_info()
- Execute multiple actions when appropriate (e.g., checking price and then buying)

7. Output Format:
Present your response in the following format:

<broker_response>
<actions_taken>
[List the actions executed using the exact function call format]
</actions_taken>

<results>
[Provide the results of the actions and any relevant market data]
</results>

<additional_info>
[Include any other pertinent information or context]
</additional_info>
</broker_response>

Remember, our system allows trading stocks regardless of whether we have current price data. When a user wants to buy a stock, ALWAYS execute the buy_stock() function without hesitation or warning about missing price data.

When the user asks about a company by name (like "Analog Devices" instead of "ADI"), make sure to use the correct symbol in your response and acknowledge both the company name and symbol.

Always maintain a professional tone and be precise in your language.
"""

            # Call Claude API
            message = self.claude_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            claude_response = message.content[0].text
            
            # Extract actions from Claude's response with improved extraction
            actions = self.extract_action_from_response(claude_response)
            print(f"Extracted {len(actions)} actions from Claude's response")
            
            # Execute the actions
            if actions:
                results = self.execute_actions(actions)
                
                # Update Claude's response with actual results
                # Use custom encoder for UUID objects
                full_response = claude_response + "\n\n<actual_results>\n" + json.dumps(results, indent=2, cls=UUIDEncoder) + "\n</actual_results>"
                return full_response
            else:
                print("Warning: No actions were extracted from Claude's response")
                return claude_response
        
        except Exception as e:
            error_message = f"Error processing instruction: {str(e)}"
            print(error_message)
            import traceback
            traceback.print_exc()
            
            # Return a formatted error message
            return f"""<broker_response>
<error>
An error occurred while processing your request: {str(e)}
</error>
</broker_response>"""


# Simple demo usage
if __name__ == "__main__":
    broker = AIBroker()
    response = broker.process_instruction("Buy 10 shares of AAPL")
    print(response) 