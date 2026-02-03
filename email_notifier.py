import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

class EmailNotifier:
    """Sends email notifications for trades and portfolio updates"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, 
                 sender_password: str, recipient_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        
        print(f"✓ Email notifier initialized (sending to {recipient_email})")
    
    def send_trading_summary(self, decision: Dict, portfolio_before: Dict, 
                            portfolio_after: Dict, trades_executed: List[Dict]) -> bool:
        """
        Send email with AI decision, trades executed, and portfolio changes
        """
        
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_subject(decision, portfolio_after)
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create HTML email body
            html_body = self._create_html_email(
                decision, portfolio_before, portfolio_after, trades_executed
            )
            
            # Attach HTML
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✓ Email sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False
    
    def _create_subject(self, decision: Dict, portfolio: Dict) -> str:
        """Create email subject line"""
        action = decision.get('action', 'HOLD')
        symbol = decision.get('symbol', '')
        portfolio_value = portfolio.get('total_value', 0)
        total_return = portfolio.get('total_return', 0)
        
        if action == 'HOLD':
            return f"🤖 AI Trader: HOLD - Portfolio ${portfolio_value:,.0f} ({total_return:+.1f}%)"
        else:
            return f"🤖 AI Trader: {action} {symbol} - Portfolio ${portfolio_value:,.0f} ({total_return:+.1f}%)"
    
    def _create_html_email(self, decision: Dict, portfolio_before: Dict,
                          portfolio_after: Dict, trades: List[Dict]) -> str:
        """Create beautiful HTML email"""
        
        # Extract data
        action = decision.get('action', 'HOLD')
        symbol = decision.get('symbol', 'N/A')
        quantity = decision.get('quantity', 0)
        confidence = decision.get('confidence', 0)
        reasoning = decision.get('reasoning', 'No reasoning provided')
        
        value_before = portfolio_before.get('total_value', 0)
        value_after = portfolio_after.get('total_value', 0)
        return_pct = portfolio_after.get('total_return', 0)
        
        value_change = value_after - value_before
        change_color = 'green' if value_change >= 0 else 'red'
        
        # Action color
        action_color = {
            'BUY': '#10b981',
            'SELL': '#ef4444',
            'HOLD': '#6b7280'
        }.get(action, '#6b7280')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid {action_color};
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    color: {action_color};
                    font-size: 32px;
                }}
                .header .timestamp {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 10px;
                }}
                .decision-box {{
                    background: {action_color};
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .decision-box h2 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .decision-box .details {{
                    font-size: 18px;
                    opacity: 0.9;
                }}
                .confidence {{
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 5px 15px;
                    border-radius: 20px;
                    margin-top: 10px;
                }}
                .portfolio-comparison {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 30px 0;
                }}
                .portfolio-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                }}
                .portfolio-card h3 {{
                    margin: 0 0 15px 0;
                    color: #1f2937;
                    font-size: 16px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .portfolio-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #1f2937;
                    margin: 10px 0;
                }}
                .portfolio-detail {{
                    font-size: 14px;
                    color: #6b7280;
                    margin: 5px 0;
                }}
                .change {{
                    font-size: 20px;
                    font-weight: bold;
                    color: {change_color};
                    text-align: center;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .trades-section {{
                    margin: 30px 0;
                }}
                .trades-section h3 {{
                    color: #1f2937;
                    border-bottom: 2px solid #e5e7eb;
                    padding-bottom: 10px;
                }}
                .trade-item {{
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid {action_color};
                }}
                .reasoning-section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                    border-left: 4px solid #3b82f6;
                }}
                .reasoning-section h3 {{
                    margin-top: 0;
                    color: #1f2937;
                }}
                .reasoning-text {{
                    white-space: pre-wrap;
                    line-height: 1.8;
                    color: #374151;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 12px;
                }}
                .positions-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .position-card {{
                    background: white;
                    border: 1px solid #e5e7eb;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .position-symbol {{
                    font-weight: bold;
                    font-size: 18px;
                    color: #1f2937;
                }}
                .position-pl {{
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI Trading Report</h1>
                    <div class="timestamp">{datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}</div>
                </div>
                
                <div class="decision-box">
                    <h2>Decision: {action}</h2>
                    <div class="details">
                        {f'{symbol} - {quantity} shares' if action != 'HOLD' else 'No trades executed'}
                    </div>
                    <div class="confidence">Confidence: {confidence}/10</div>
                </div>
                
                <div class="portfolio-comparison">
                    <div class="portfolio-card">
                        <h3>📊 Before</h3>
                        <div class="portfolio-value">${value_before:,.2f}</div>
                        <div class="portfolio-detail">Cash: ${portfolio_before.get('cash', 0):,.2f}</div>
                        <div class="portfolio-detail">Positions: {portfolio_before.get('position_count', 0)}</div>
                    </div>
                    
                    <div class="portfolio-card">
                        <h3>📈 After</h3>
                        <div class="portfolio-value">${value_after:,.2f}</div>
                        <div class="portfolio-detail">Cash: ${portfolio_after.get('cash', 0):,.2f}</div>
                        <div class="portfolio-detail">Positions: {portfolio_after.get('position_count', 0)}</div>
                    </div>
                </div>
                
                <div class="change">
                    Change: ${value_change:+,.2f} | Total Return: {return_pct:+.2f}%
                </div>
        """
        
        # Add trades section if any trades were executed
        if trades:
            html += """
                <div class="trades-section">
                    <h3>💰 Trades Executed</h3>
            """
            for trade in trades:
                html += f"""
                    <div class="trade-item">
                        <strong>{trade.get('action', 'N/A')}</strong> {trade.get('quantity', 0)} shares of 
                        <strong>{trade.get('symbol', 'N/A')}</strong> @ ${trade.get('price', 0):.2f}
                        <br>
                        <small>Total: ${trade.get('total_value', 0):,.2f} | Order ID: {trade.get('order_id', 'N/A')}</small>
                    </div>
                """
            html += "</div>"
        
        # Add current positions
        if portfolio_after.get('positions'):
            html += """
                <div class="trades-section">
                    <h3>📍 Current Positions</h3>
                    <div class="positions-grid">
            """
            for pos in portfolio_after.get('positions', []):
                pl_class = 'positive' if pos.get('unrealized_plpc', 0) >= 0 else 'negative'
                html += f"""
                    <div class="position-card">
                        <div class="position-symbol">{pos.get('symbol', 'N/A')}</div>
                        <div>{pos.get('quantity', 0)} shares</div>
                        <div class="position-pl {pl_class}">
                            {pos.get('unrealized_plpc', 0):+.2f}%
                        </div>
                        <div style="font-size: 12px; color: #6b7280;">
                            ${pos.get('market_value', 0):,.2f}
                        </div>
                    </div>
                """
            html += """
                    </div>
                </div>
            """
        
        # Add AI reasoning
        html += f"""
                <div class="reasoning-section">
                    <h3>🧠 AI Analysis & Reasoning</h3>
                    <div class="reasoning-text">{reasoning}</div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from your AI Trading System</p>
                    <p>Powered by Gemini AI & Alpaca Markets | Paper Trading Mode</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_error_alert(self, error_message: str) -> bool:
        """Send email alert for errors"""
        try:
            msg = MIMEText(f"""
AI Trading System Error Alert

An error occurred during the trading cycle:

{error_message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}

Please check the logs and system status.
            """)
            
            msg['Subject'] = '⚠️ AI Trader Error Alert'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send error alert: {e}")
            return False

if __name__ == "__main__":
    # Test email notifier
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Example usage
    notifier = EmailNotifier(
        smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(os.getenv('SMTP_PORT', 587)),
        sender_email=os.getenv('SENDER_EMAIL', ''),
        sender_password=os.getenv('SENDER_PASSWORD', ''),
        recipient_email=os.getenv('RECIPIENT_EMAIL', '')
    )
    
    # Test with dummy data
    decision = {
        'action': 'BUY',
        'symbol': 'AAPL',
        'quantity': 10,
        'confidence': 8,
        'reasoning': 'Strong fundamentals and positive momentum...'
    }
    
    portfolio_before = {'total_value': 100000, 'cash': 50000, 'position_count': 5}
    portfolio_after = {'total_value': 101500, 'cash': 48000, 'position_count': 6, 'total_return': 1.5}
    
    trades = [{'action': 'BUY', 'symbol': 'AAPL', 'quantity': 10, 'price': 180.50, 'total_value': 1805}]
    
    print("Sending test email...")
    notifier.send_trading_summary(decision, portfolio_before, portfolio_after, trades)