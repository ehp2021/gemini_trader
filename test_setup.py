#!/usr/bin/env python3
"""
Test script to verify all components are working correctly
Run this before starting live trading
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test that all required packages are installed"""
    print("\n" + "="*60)
    print("TESTING PACKAGE IMPORTS")
    print("="*60)
    
    required_packages = [
        ('google.generativeai', 'Google Generative AI'),
        ('alpaca.trading.client', 'Alpaca Trading'),
        ('yfinance', 'Yahoo Finance'),
        ('pandas', 'Pandas'),
        ('schedule', 'Schedule'),
        ('sqlite3', 'SQLite3')
    ]
    
    all_passed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name} - FAILED")
            print(f"  Error: {e}")
            all_passed = False
    
    return all_passed

def test_env_vars():
    """Test that all environment variables are set"""
    print("\n" + "="*60)
    print("TESTING ENVIRONMENT VARIABLES")
    print("="*60)
    
    load_dotenv()
    
    required_vars = [
        'GOOGLE_API_KEY',
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var, '')
        if value and value != f'your_{var.lower()}_here':
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is NOT set or still has default value")
            all_set = False
    
    return all_set

def test_database():
    """Test database initialization"""
    print("\n" + "="*60)
    print("TESTING DATABASE")
    print("="*60)
    
    try:
        from database import Database
        db = Database('test_trading.db')
        print("✓ Database initialized successfully")
        
        # Test logging a decision
        test_decision = {
            'timestamp': '2024-01-01T12:00:00',
            'action': 'HOLD',
            'reasoning': 'Test decision',
            'confidence': 8
        }
        db.log_decision(test_decision, {}, {})
        print("✓ Can log decisions")
        
        # Test retrieving decision
        latest = db.get_latest_decision()
        if latest:
            print("✓ Can retrieve decisions")
        
        db.close()
        
        # Clean up test database
        if os.path.exists('test_trading.db'):
            os.remove('test_trading.db')
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_market_data():
    """Test market data collection"""
    print("\n" + "="*60)
    print("TESTING MARKET DATA COLLECTION")
    print("="*60)
    
    try:
        from market_data import MarketDataCollector
        collector = MarketDataCollector()
        
        # Test getting stock data
        print("  Fetching AAPL data...")
        data = collector.get_stock_data(['AAPL'])
        
        if 'AAPL' in data and 'current_price' in data['AAPL']:
            price = data['AAPL']['current_price']
            print(f"✓ Successfully fetched AAPL data: ${price:.2f}")
        else:
            print("✗ Failed to fetch valid stock data")
            return False
        
        # Test market overview
        print("  Fetching market overview...")
        overview = collector.get_market_overview()
        
        if 'spy_price' in overview:
            print(f"✓ Successfully fetched market overview: SPY at ${overview['spy_price']:.2f}")
        else:
            print("✗ Failed to fetch market overview")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Market data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alpaca_connection():
    """Test Alpaca API connection"""
    print("\n" + "="*60)
    print("TESTING ALPACA CONNECTION")
    print("="*60)
    
    load_dotenv()
    
    api_key = os.getenv('ALPACA_API_KEY', '')
    secret_key = os.getenv('ALPACA_SECRET_KEY', '')
    
    if not api_key or not secret_key:
        print("✗ Alpaca API keys not set in .env")
        return False
    
    try:
        from alpaca_trader import AlpacaTrader
        trader = AlpacaTrader(api_key, secret_key, paper=True)
        
        # Get account info
        account = trader.get_account()
        if account and 'portfolio_value' in account:
            print(f"✓ Connected to Alpaca (Paper Trading)")
            print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"  Buying Power: ${account['buying_power']:,.2f}")
        else:
            print("✗ Failed to get account information")
            return False
        
        # Check if market is open
        is_open = trader.is_market_open()
        print(f"  Market Status: {'OPEN' if is_open else 'CLOSED'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Alpaca connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n" + "="*60)
    print("TESTING GEMINI AI CONNECTION")
    print("="*60)
    
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY', '')
    
    if not api_key or api_key == 'your_google_gemini_api_key_here':
        print("✗ Google API key not set in .env")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test simple generation
        print("  Testing API call (this may take a few seconds)...")
        response = model.generate_content("Say 'API test successful' if you can read this.")
        
        if response and response.text:
            print(f"✓ Gemini API connected successfully")
            print(f"  Response: {response.text[:100]}")
        else:
            print("✗ Failed to get response from Gemini")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Gemini connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║            AI TRADING SYSTEM - SETUP TEST                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'Package Imports': test_imports(),
        'Environment Variables': test_env_vars(),
        'Database': test_database(),
        'Market Data': test_market_data(),
        'Alpaca Connection': test_alpaca_connection(),
        'Gemini AI Connection': test_gemini_connection()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - System is ready!")
        print("\nYou can now run: python main.py")
    else:
        print("✗ SOME TESTS FAILED - Please fix issues above")
        print("\nCommon fixes:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Set up .env file with your API keys")
        print("3. Verify API keys are correct")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)