from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import os

class MarketDataCollector:
    """Collects market data using Alpaca API (more reliable than Yahoo Finance)"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.cache = {}
        
        # Use provided keys or get from environment
        if not api_key or not secret_key:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        print("✓ Market data collector initialized (using Alpaca)")
    
    def get_stock_data(self, symbols: List[str]) -> Dict:
        """Get comprehensive data for a list of stocks using Alpaca"""
        data = {}
        
        for symbol in symbols:
            try:
                # Get latest quote
                request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
                quote = self.data_client.get_stock_latest_quote(request)
                
                if symbol not in quote:
                    data[symbol] = {'error': 'No data available'}
                    continue
                
                latest_quote = quote[symbol]
                
                # Get recent bars for performance calculation
                end = datetime.now()
                start = end - timedelta(days=30)
                
                bars_request = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame.Day,
                    start=start,
                    end=end
                )
                
                bars = self.data_client.get_stock_bars(bars_request)
                
                # Calculate performance metrics
                performance = {}
                if symbol in bars.data and len(bars.data[symbol]) > 0:
                    prices = [bar.close for bar in bars.data[symbol]]
                    current = prices[-1] if prices else latest_quote.ask_price
                    
                    performance = {
                        '1_day': ((current / prices[-2] - 1) * 100) if len(prices) > 1 else 0,
                        '5_day': ((current / prices[-6] - 1) * 100) if len(prices) > 5 else 0,
                        '1_month': ((current / prices[0] - 1) * 100) if len(prices) > 0 else 0,
                        'volatility': pd.Series(prices).pct_change().std() * 100 if len(prices) > 1 else 0
                    }
                
                data[symbol] = {
                    'current_price': float(latest_quote.ask_price),
                    'bid_price': float(latest_quote.bid_price),
                    'ask_price': float(latest_quote.ask_price),
                    'previous_close': float(prices[-2]) if len(prices) > 1 else float(latest_quote.ask_price),
                    'day_high': float(latest_quote.ask_price),  # Approximation
                    'day_low': float(latest_quote.bid_price),   # Approximation
                    'volume': int(latest_quote.ask_size + latest_quote.bid_size),
                    'avg_volume': 1000000,  # Placeholder
                    'market_cap': 0,  # Not available from Alpaca quotes
                    'pe_ratio': 0,  # Not available from Alpaca quotes
                    'forward_pe': 0,
                    'dividend_yield': 0,
                    '52_week_high': float(max(prices)) if prices else float(latest_quote.ask_price),
                    '52_week_low': float(min(prices)) if prices else float(latest_quote.bid_price),
                    'beta': 1.0,  # Placeholder
                    'sector': 'Unknown',  # Not available from Alpaca
                    'industry': 'Unknown',
                    'recommendation': 'none',
                    'target_price': 0,
                    'analyst_rating': 0,
                    'earnings_date': None,
                    'recent_performance': performance,
                    'news': [],  # Alpaca doesn't provide news in free tier
                    'fundamentals': {
                        'revenue': 0,
                        'revenue_growth': 0,
                        'earnings_growth': 0,
                        'profit_margins': 0,
                        'operating_margins': 0,
                        'roe': 0,
                        'roa': 0,
                        'debt_to_equity': 0,
                        'current_ratio': 0,
                        'free_cashflow': 0,
                        'eps': 0,
                        'forward_eps': 0
                    }
                }
                
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                data[symbol] = {'error': str(e)}
        
        return data
    
    def get_market_overview(self) -> Dict:
        """Get overall market conditions using SPY"""
        try:
            # Get SPY data
            request = StockLatestQuoteRequest(symbol_or_symbols='SPY')
            quote = self.data_client.get_stock_latest_quote(request)
            
            if 'SPY' not in quote:
                return {}
            
            spy_quote = quote['SPY']
            
            # Get recent SPY bars for performance
            end = datetime.now()
            start = end - timedelta(days=30)
            
            bars_request = StockBarsRequest(
                symbol_or_symbols='SPY',
                timeframe=TimeFrame.Day,
                start=start,
                end=end
            )
            
            bars = self.data_client.get_stock_bars(bars_request)
            
            spy_prices = [bar.close for bar in bars.data['SPY']] if 'SPY' in bars.data else []
            current_price = float(spy_quote.ask_price)
            
            # Calculate returns
            spy_1m_return = 0
            if len(spy_prices) > 0:
                spy_1m_return = ((current_price / spy_prices[0] - 1) * 100)
            
            # Estimate VIX from volatility (rough approximation)
            vix_estimate = 15.0  # Default neutral
            if len(spy_prices) > 1:
                volatility = pd.Series(spy_prices).pct_change().std() * 100
                vix_estimate = min(max(volatility * 15, 10), 40)  # Scale to VIX-like range
            
            return {
                'spy_price': current_price,
                'spy_change': ((current_price / spy_prices[-2] - 1) * 100) if len(spy_prices) > 1 else 0,
                'spy_1m_return': spy_1m_return,
                'vix': vix_estimate,
                'market_sentiment': 'Fearful' if vix_estimate > 20 else 'Neutral' if vix_estimate > 15 else 'Greedy',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching market overview: {e}")
            return {
                'spy_price': 0,
                'spy_change': 0,
                'spy_1m_return': 0,
                'vix': 15,
                'market_sentiment': 'Unknown',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_earnings_calendar(self, symbols: List[str]) -> List[Dict]:
        """Get upcoming earnings dates - placeholder for Alpaca (not available in free tier)"""
        # Alpaca free tier doesn't have earnings calendar
        # Return empty list for now
        return []
    
    def search_stock(self, query: str) -> List[str]:
        """Search for stock symbols"""
        # Simple validation - just return the query if it looks like a ticker
        if len(query) <= 5 and query.isupper():
            return [query]
        return []

if __name__ == "__main__":
    # Test the data collector
    from dotenv import load_dotenv
    load_dotenv()
    
    collector = MarketDataCollector()
    
    print("Testing market data collection...")
    data = collector.get_stock_data(['AAPL', 'MSFT'])
    print(f"✓ Fetched data for {len(data)} stocks")
    
    if 'AAPL' in data and 'current_price' in data['AAPL']:
        print(f"  AAPL: ${data['AAPL']['current_price']:.2f}")
    
    market = collector.get_market_overview()
    print(f"✓ Market overview: SPY at ${market.get('spy_price', 0):.2f}")