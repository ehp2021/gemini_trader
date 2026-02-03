import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

from database import Database
from market_data import MarketDataCollector
from alpaca_trader import AlpacaTrader
from gemini_trader import GeminiTrader
from risk_manager import RiskManager
from email_notifier import EmailNotifier

class TradingOrchestrator:
    """
    Main orchestrator that coordinates all trading components
    """
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        print("="*60)
        print("AI TRADING SYSTEM - INITIALIZING")
        print("="*60)
        
        # Initialize components
        self.db = Database()
        self.market_data = MarketDataCollector()
        
        # Initialize Alpaca
        self.alpaca = AlpacaTrader(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY'),
            paper=os.getenv('ALPACA_ENV', 'paper') == 'paper'
        )
        
        # Initialize Gemini AI
        self.gemini = GeminiTrader(
            api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        # Initialize risk manager
        self.risk_mgr = RiskManager(
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', 0.15)),
            daily_loss_limit=float(os.getenv('DAILY_LOSS_LIMIT', 0.02)),
            min_confidence=int(os.getenv('MIN_CONFIDENCE', 6))
        )
        
        # Initialize email notifier (optional)
        self.email_enabled = os.getenv('ENABLE_EMAIL', 'false').lower() == 'true'
        self.email_notifier = None
        
        if self.email_enabled:
            try:
                self.email_notifier = EmailNotifier(
                    smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                    smtp_port=int(os.getenv('SMTP_PORT', 587)),
                    sender_email=os.getenv('SENDER_EMAIL'),
                    sender_password=os.getenv('SENDER_PASSWORD'),
                    recipient_email=os.getenv('RECIPIENT_EMAIL')
                )
            except Exception as e:
                print(f"⚠ Email notifications disabled: {e}")
                self.email_enabled = False
        
        # Watchlist - stocks to monitor
        self.watchlist = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META',
            'TSLA', 'AMD', 'NFLX', 'CRM', 'ADBE', 'ORCL'
        ]
        
        print("="*60)
        print("✓ ALL SYSTEMS INITIALIZED")
        print("="*60)
    
    def trading_cycle(self):
        """
        Main trading cycle - run this 1-2 times per day
        """
        
        print("\n" + "="*60)
        print(f"TRADING CYCLE STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Step 1: Check if market is open
            if not self.alpaca.is_market_open():
                print("⚠ Market is closed - skipping cycle")
                return
            
            # Step 2: Get current portfolio state
            print("\n[1/7] Fetching portfolio state...")
            portfolio_state = self.alpaca.get_portfolio_state()
            print(f"  Portfolio Value: ${portfolio_state['total_value']:,.2f}")
            print(f"  Cash: ${portfolio_state['cash']:,.2f} ({portfolio_state['cash_percentage']:.1f}%)")
            print(f"  Positions: {portfolio_state['position_count']}")
            print(f"  Total Return: {portfolio_state['total_return']:+.2f}%")
            
            # Set daily start value if not set
            if not self.risk_mgr.daily_start_value:
                self.risk_mgr.set_daily_start_value(portfolio_state['total_value'])
            
            # Step 3: Collect market data for watchlist
            print("\n[2/7] Collecting market data...")
            
            # Get data for current positions
            position_symbols = [p['symbol'] for p in portfolio_state['positions']]
            all_symbols = list(set(self.watchlist + position_symbols))
            
            market_data = self.market_data.get_stock_data(all_symbols)
            print(f"  Fetched data for {len(market_data)} symbols")
            
            # Step 4: Get market overview
            print("\n[3/7] Analyzing market conditions...")
            market_overview = self.market_data.get_market_overview()
            print(f"  SPY: ${market_overview.get('spy_price', 0):.2f} ({market_overview.get('spy_change', 0):+.2f}%)")
            print(f"  VIX: {market_overview.get('vix', 0):.2f} ({market_overview.get('market_sentiment', 'Unknown')})")
            
            # Step 5: Get earnings calendar
            print("\n[4/7] Checking earnings calendar...")
            earnings_calendar = self.market_data.get_earnings_calendar(all_symbols)
            print(f"  {len(earnings_calendar)} upcoming earnings")
            
            # Step 6: AI Analysis and Decision
            print("\n[5/7] Running AI analysis (this may take 30-60 seconds)...")
            decision = self.gemini.analyze_and_decide(
                portfolio_state=portfolio_state,
                market_data=market_data,
                market_overview=market_overview,
                earnings_calendar=earnings_calendar
            )
            
            print(f"\n  AI Decision: {decision['action']}")
            if decision.get('symbol'):
                print(f"  Symbol: {decision['symbol']}")
                print(f"  Quantity: {decision['quantity']}")
            print(f"  Confidence: {decision['confidence']}/10")
            
            # Step 7: Log decision
            self.db.log_decision(decision, market_data, portfolio_state)
            
            # Step 8: Execute trade if not HOLD
            if decision['action'] != 'HOLD':
                print("\n[6/7] Validating trade...")
                
                # Get current price
                price = self.alpaca.get_latest_price(decision['symbol'])
                
                # Validate with risk manager
                valid, reason = self.risk_mgr.validate_trade(decision, portfolio_state, price)
                
                if valid:
                    print(f"  ✓ Risk checks passed")
                    
                    # Validate with Alpaca
                    alpaca_valid, alpaca_reason = self.alpaca.validate_trade(
                        decision['symbol'],
                        decision['quantity'],
                        decision['action']
                    )
                    
                    if alpaca_valid:
                        print(f"  ✓ Alpaca validation passed")
                        print(f"\n  Executing {decision['action']} {decision['quantity']} {decision['symbol']} @ ${price:.2f}")
                        
                        # Execute the trade
                        result = self.alpaca.execute_order(
                            decision['symbol'],
                            decision['quantity'],
                            decision['action']
                        )
                        
                        if result['status'] == 'success':
                            print(f"  ✓ Trade executed successfully!")
                            print(f"  Order ID: {result.get('order_id', 'N/A')}")
                            
                            # Log the trade
                            self.db.log_trade({
                                'timestamp': datetime.now().isoformat(),
                                'symbol': decision['symbol'],
                                'action': decision['action'],
                                'quantity': decision['quantity'],
                                'price': price,
                                'total_value': price * decision['quantity'],
                                'reasoning': decision['reasoning'],
                                'confidence': decision['confidence'],
                                'order_id': result.get('order_id')
                            })
                            
                            self.risk_mgr.record_trade()
                        else:
                            print(f"  ✗ Trade failed: {result.get('message', 'Unknown error')}")
                    else:
                        print(f"  ✗ Alpaca validation failed: {alpaca_reason}")
                else:
                    print(f"  ✗ Risk validation failed: {reason}")
            else:
                print("\n[6/7] No trade to execute (HOLD decision)")
            
            # Step 9: Save portfolio snapshot
            print("\n[7/7] Saving portfolio snapshot...")
            self.db.save_portfolio_snapshot(portfolio_state)
            
            # Get updated portfolio state for email
            portfolio_state_after = self.alpaca.get_portfolio_state()
            
            # Step 10: Send email notification
            if self.email_enabled and self.email_notifier:
                print("\n[Email] Sending notification...")
                trades_for_email = []
                
                if decision['action'] != 'HOLD' and result and result.get('status') == 'success':
                    trades_for_email = [{
                        'action': decision['action'],
                        'symbol': decision['symbol'],
                        'quantity': decision['quantity'],
                        'price': price,
                        'total_value': price * decision['quantity'],
                        'order_id': result.get('order_id', 'N/A')
                    }]
                
                email_sent = self.email_notifier.send_trading_summary(
                    decision=decision,
                    portfolio_before=portfolio_state,
                    portfolio_after=portfolio_state_after,
                    trades_executed=trades_for_email
                )
                
                if email_sent:
                    print("  ✓ Email notification sent")
                else:
                    print("  ✗ Failed to send email")
            
            # Step 11: Check portfolio health
            print("\n[7/7] Checking portfolio health...")
            health = self.risk_mgr.check_portfolio_health(portfolio_state_after)
            if health['warnings']:
                print("\n⚠ Portfolio Health Warnings:")
                for warning in health['warnings']:
                    print(f"  - {warning}")
            
            print("\n" + "="*60)
            print("TRADING CYCLE COMPLETED")
            print("="*60)
            
            # Print AI reasoning summary
            print("\n" + "-"*60)
            print("AI REASONING:")
            print("-"*60)
            print(decision['reasoning'][:500] + "..." if len(decision['reasoning']) > 500 else decision['reasoning'])
            print("-"*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error in trading cycle: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_daily_report(self):
        """Generate end-of-day report"""
        
        print("\n" + "="*60)
        print("DAILY REPORT")
        print("="*60)
        
        portfolio_state = self.alpaca.get_portfolio_state()
        latest_decision = self.db.get_latest_decision()
        
        # Create list with latest decision (or empty if none)
        recent_decisions = [latest_decision] if latest_decision else []
        
        # Generate summary using AI
        try:
            summary = self.gemini.generate_daily_summary(portfolio_state, recent_decisions)
        except Exception as e:
            print(f"⚠ Could not generate AI summary: {e}")
            summary = f"Portfolio at ${portfolio_state['total_value']:,.2f} ({portfolio_state['total_return']:+.2f}%)"
        
        print(f"\nPortfolio Value: ${portfolio_state['total_value']:,.2f}")
        print(f"Total Return: {portfolio_state['total_return']:+.2f}%")
        print(f"Positions: {portfolio_state['position_count']}")
        print(f"\nStrategy Summary:\n{summary}")
        
        # Recent trades
        recent_trades = self.db.get_recent_trades(5)
        if recent_trades:
            print("\n\nRecent Trades:")
            for trade in recent_trades:
                print(f"  {trade['timestamp']}: {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
        else:
            print("\n\nRecent Trades: None yet")
        
        print("="*60 + "\n")
    
    def run_manual_cycle(self):
        """Run a single trading cycle manually"""
        self.trading_cycle()
        self.generate_daily_report()
    
    def start_scheduled_trading(self):
        """Start automated trading with scheduled runs"""
        
        print("\n" + "="*60)
        print("STARTING SCHEDULED TRADING")
        print("="*60)
        print(f"Market open analysis: {os.getenv('MARKET_OPEN_TIME', '09:35')} EST")
        print(f"Market close analysis: {os.getenv('MARKET_CLOSE_TIME', '15:55')} EST")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")
        
        # Schedule trades
        schedule.every().day.at(os.getenv('MARKET_OPEN_TIME', '09:35')).do(self.trading_cycle)
        schedule.every().day.at(os.getenv('MARKET_CLOSE_TIME', '15:55')).do(self.trading_cycle)
        schedule.every().day.at("16:05").do(self.generate_daily_report)
        
        # Run scheduling loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\nShutting down gracefully...")
            self.db.close()
            print("✓ Trading system stopped")

def main():
    """Main entry point"""
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              AI TRADING SYSTEM v1.0                      ║
    ║           Powered by Gemini & Alpaca                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize orchestrator
    orchestrator = TradingOrchestrator()
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Run single trading cycle (manual)")
    print("2. Start scheduled automated trading")
    print("3. Generate report only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        orchestrator.run_manual_cycle()
    elif choice == '2':
        orchestrator.start_scheduled_trading()
    elif choice == '3':
        orchestrator.generate_daily_report()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()