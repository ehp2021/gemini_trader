from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from datetime import datetime
import os
from typing import Dict, List, Optional

class AlpacaTrader:
    """Handles all Alpaca API interactions for trading execution"""
    
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        
        # Initialize trading client
        self.trading_client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
            paper=paper
        )
        
        # Initialize data client
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        
        print(f"✓ Alpaca connected ({'PAPER' if paper else 'LIVE'} trading)")
    
    def get_account(self) -> Dict:
        """Get account information"""
        try:
            account = self.trading_client.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'initial_capital': float(account.last_equity) if hasattr(account, 'last_equity') else 100000,
                'status': account.status,
                'pattern_day_trader': account.pattern_day_trader
            }
        except Exception as e:
            print(f"Error getting account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            positions = self.trading_client.get_all_positions()
            position_list = []
            
            for pos in positions:
                position_list.append({
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc),
                    'side': pos.side
                })
            
            return position_list
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def get_portfolio_state(self) -> Dict:
        """Get complete portfolio state"""
        account = self.get_account()
        positions = self.get_positions()
        
        total_value = account.get('portfolio_value', 0)
        initial_capital = account.get('initial_capital', 100000)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_value': total_value,
            'cash': account.get('cash', 0),
            'equity': account.get('equity', 0),
            'buying_power': account.get('buying_power', 0),
            'positions': positions,
            'position_count': len(positions),
            'cash_percentage': (account.get('cash', 0) / total_value * 100) if total_value > 0 else 100,
            'total_return': ((total_value - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0,
            'total_pl': total_value - initial_capital
        }
    
    def execute_order(self, symbol: str, quantity: int, side: str) -> Dict:
        """Execute a market order"""
        try:
            # Validate inputs
            if quantity <= 0:
                return {'status': 'error', 'message': 'Invalid quantity'}
            
            # Determine order side
            order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
            
            # Create market order
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data)
            
            return {
                'status': 'success',
                'order_id': order.id,
                'symbol': order.symbol,
                'quantity': int(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None
            }
            
        except Exception as e:
            print(f"Error executing order: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_latest_price(self, symbol: str) -> float:
        """Get latest price for a symbol"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(request)
            
            if symbol in quote:
                return float(quote[symbol].ask_price)
            return 0.0
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def calculate_position_size(self, symbol: str, confidence: int, max_position_pct: float = 0.15) -> int:
        """Calculate position size based on confidence and portfolio value"""
        portfolio_value = self.get_account().get('portfolio_value', 100000)
        
        # Adjust position size by confidence (1-10 scale)
        confidence_factor = min(confidence / 10.0, 1.0)
        position_pct = max_position_pct * confidence_factor
        
        # Calculate dollar amount
        dollar_amount = portfolio_value * position_pct
        
        # Get current price
        price = self.get_latest_price(symbol)
        
        if price <= 0:
            return 0
        
        # Calculate shares (round down)
        shares = int(dollar_amount / price)
        
        return shares
    
    def validate_trade(self, symbol: str, quantity: int, side: str) -> tuple[bool, str]:
        """Validate if trade can be executed"""
        try:
            account = self.get_account()
            
            # Check if market is open
            clock = self.trading_client.get_clock()
            if not clock.is_open:
                return False, "Market is closed"
            
            # For buys, check if we have enough buying power
            if side.upper() == 'BUY':
                price = self.get_latest_price(symbol)
                required_cash = price * quantity
                
                if required_cash > account.get('buying_power', 0):
                    return False, f"Insufficient buying power. Need ${required_cash:.2f}, have ${account.get('buying_power', 0):.2f}"
            
            # For sells, check if we have the position
            if side.upper() == 'SELL':
                positions = self.get_positions()
                position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if not position:
                    return False, f"No position in {symbol} to sell"
                
                if quantity > position['quantity']:
                    return False, f"Cannot sell {quantity} shares, only own {position['quantity']}"
            
            return True, "Trade validated"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_order_history(self, limit: int = 10) -> List[Dict]:
        """Get recent order history"""
        try:
            orders = self.trading_client.get_orders(
                limit=limit,
                status='all'
            )
            
            order_list = []
            for order in orders:
                order_list.append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'quantity': int(order.qty),
                    'side': order.side.value,
                    'type': order.type.value,
                    'status': order.status.value,
                    'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                    'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None
                })
            
            return order_list
        except Exception as e:
            print(f"Error getting order history: {e}")
            return []
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except:
            return False

if __name__ == "__main__":
    # Test Alpaca connection
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('ALPACA_API_KEY', '')
    secret_key = os.getenv('ALPACA_SECRET_KEY', '')
    
    if api_key and secret_key:
        trader = AlpacaTrader(api_key, secret_key, paper=True)
        
        account = trader.get_account()
        print(f"✓ Account value: ${account.get('portfolio_value', 0):,.2f}")
        
        positions = trader.get_positions()
        print(f"✓ Current positions: {len(positions)}")
    else:
        print("⚠ Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
