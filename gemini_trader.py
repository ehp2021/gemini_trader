import google.generativeai as genai
from datetime import datetime
import json
import re
from typing import Dict, List, Optional

class GeminiTrader:
    """AI trader powered by Google Gemini for market analysis and decision making"""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-pro'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        print(f"✓ Gemini AI initialized ({model_name})")
    
    def analyze_and_decide(self, portfolio_state: Dict, market_data: Dict, 
                          market_overview: Dict, earnings_calendar: List[Dict]) -> Dict:
        """
        Main analysis function - takes all market data and returns a trading decision
        """
        
        # Build comprehensive prompt
        prompt = self._build_analysis_prompt(
            portfolio_state=portfolio_state,
            market_data=market_data,
            market_overview=market_overview,
            earnings_calendar=earnings_calendar
        )
        
        try:
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the decision
            decision = self._parse_decision(response.text)
            decision['timestamp'] = datetime.now().isoformat()
            decision['model_used'] = self.model_name
            
            return decision
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {
                'action': 'HOLD',
                'reasoning': f'Error in analysis: {str(e)}',
                'confidence': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _build_analysis_prompt(self, portfolio_state: Dict, market_data: Dict,
                               market_overview: Dict, earnings_calendar: List[Dict]) -> str:
        """Build comprehensive prompt for Gemini"""
        
        # Format portfolio positions
        positions_text = self._format_positions(portfolio_state.get('positions', []))
        
        # Format market data for each stock
        market_analysis = self._format_market_data(market_data)
        
        # Format earnings calendar
        earnings_text = self._format_earnings_calendar(earnings_calendar)
        
        # Calculate days since start (estimate based on returns)
        days_active = 1  # TODO: Track this properly
        
        prompt = f"""You are an elite AI portfolio manager managing a ${portfolio_state.get('total_value', 100000):,.0f} portfolio.

====================
CURRENT PORTFOLIO STATE
====================
Total Value: ${portfolio_state.get('total_value', 0):,.2f}
Cash Available: ${portfolio_state.get('cash', 0):,.2f} ({portfolio_state.get('cash_percentage', 0):.1f}%)
Total Return: {portfolio_state.get('total_return', 0):+.2f}%
Total P&L: ${portfolio_state.get('total_pl', 0):+,.2f}
Number of Positions: {portfolio_state.get('position_count', 0)}
Days Active: {days_active}

CURRENT POSITIONS:
{positions_text}

====================
MARKET CONDITIONS
====================
S&P 500: ${market_overview.get('spy_price', 0):.2f} ({market_overview.get('spy_change', 0):+.2f}%)
1-Month SPY Return: {market_overview.get('spy_1m_return', 0):+.2f}%
VIX (Volatility): {market_overview.get('vix', 0):.2f}
Market Sentiment: {market_overview.get('market_sentiment', 'Unknown')}

====================
DETAILED STOCK ANALYSIS
====================
{market_analysis}

====================
UPCOMING EARNINGS
====================
{earnings_text}

====================
YOUR TASK
====================
Analyze all available data and make ONE of the following decisions:

1. **BUY** - Purchase shares of a specific stock
2. **SELL** - Sell shares of a current position
3. **HOLD** - Maintain current positions (no trades)

DECISION CRITERIA:
- Consider technical indicators (price momentum, volume, volatility)
- Evaluate fundamentals (PE ratios, growth rates, margins)
- Assess news sentiment and upcoming catalysts
- Manage risk through diversification and position sizing
- Time trades around earnings and major events
- Compare expected returns vs. current positions

RISK MANAGEMENT:
- Maximum position size: 15% of portfolio
- Target 6-10 positions for diversification
- Consider correlation between holdings
- Avoid over-concentration in single sector
- Maintain 10-20% cash for opportunities

====================
OUTPUT FORMAT (CRITICAL - FOLLOW EXACTLY)
====================
Decision: [BUY/SELL/HOLD]
Symbol: [TICKER if BUY/SELL, otherwise N/A]
Quantity: [Number of shares if BUY/SELL, otherwise N/A]
Confidence: [1-10, where 10 is highest confidence]

Analysis:
[Write 250-400 words explaining your reasoning. Be specific with data points. Reference actual numbers from the data provided. Explain your conviction and what you're watching for. Write in first person as the portfolio manager.]

Key Catalysts:
- [List 3-5 upcoming events or factors driving your decision]

Risk Factors:
- [List 3-5 risks you're monitoring]

====================
EXAMPLE OUTPUT (for reference only)
====================
Decision: HOLD
Symbol: N/A
Quantity: N/A
Confidence: 8

Analysis:
Holding all 6 positions steady ahead of critical earnings week. Portfolio at $107,880 (+7.9%) with strong momentum across tech holdings. MSFT reports tomorrow after close with Azure expected at 37% growth - this is a key catalyst for my 11.6% position. The stock has held $420 support well and analyst consensus is $465 (+8% upside). AMD and GOOGL both report next week (Feb 3-4), representing another 45% of my portfolio. AMD's MI300 AI chip ramp is the focus, with datacenter revenue expected up 25% QoQ. 

With 88% deployed and three major binary events in the next 8 days, the disciplined move is letting these quality positions run through their earnings catalysts rather than making changes for activity's sake. Market conditions are supportive with Fed on pause and AI infrastructure spend accelerating. VIX at 14 shows low volatility, and the S&P is holding above key 20-day MA support. 

My positions are relatively young (avg 28 days hold) and fundamentally sound. NVDA continues to benefit from H100/H200 demand. Will reassess after this earnings wave passes and look to add 1-2 new positions if cash builds above 20%. Watching for any GOOGL weakness pre-earnings as a potential add opportunity.

Key Catalysts:
- MSFT earnings (tomorrow AH) - Azure growth is key metric
- AMD earnings (Feb 3) - MI300 datacenter ramp crucial  
- GOOGL earnings (Feb 4) - Cloud margin expansion expected
- Fed commentary - Powell speaks Friday on economic outlook
- Semiconductor sector rotation - watching for broadening beyond NVDA

Risk Factors:
- Earnings disappointment risk with 60% of portfolio reporting next week
- Tech sector concentration - need to add diversification
- Market overbought on short-term - watching for 3-5% pullback
- Rising yields could pressure growth stock multiples
- Geopolitical tensions (China-Taiwan) affecting chip stocks

NOW PROVIDE YOUR ACTUAL ANALYSIS AND DECISION:
"""
        
        return prompt
    
    def _format_positions(self, positions: List[Dict]) -> str:
        """Format current positions for display"""
        if not positions:
            return "No current positions (100% cash)"
        
        text = ""
        for pos in positions:
            pct_of_portfolio = 0  # Calculate this if needed
            text += f"""
{pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_entry_price']:.2f}
  Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pl']:+,.2f} ({pos['unrealized_plpc']:+.2f}%)
  Market Value: ${pos['market_value']:,.2f}
"""
        return text.strip()
    
    def _format_market_data(self, market_data: Dict) -> str:
        """Format market data for all stocks in watchlist"""
        if not market_data:
            return "No market data available"
        
        text = ""
        for symbol, data in market_data.items():
            if 'error' in data:
                continue
            
            perf = data.get('recent_performance', {})
            fundamentals = data.get('fundamentals', {})
            news = data.get('news', [])
            
            text += f"""
--- {symbol} ({data.get('sector', 'Unknown')} / {data.get('industry', 'Unknown')}) ---
Price: ${data.get('current_price', 0):.2f} | Day Range: ${data.get('day_low', 0):.2f} - ${data.get('day_high', 0):.2f}
Performance: 1D {perf.get('1_day', 0):+.2f}% | 5D {perf.get('5_day', 0):+.2f}% | 1M {perf.get('1_month', 0):+.2f}%
Volume: {data.get('volume', 0):,} (Avg: {data.get('avg_volume', 0):,})
Volatility: {perf.get('volatility', 0):.2f}%

Valuation:
  P/E: {data.get('pe_ratio', 0):.1f} | Forward P/E: {data.get('forward_pe', 0):.1f}
  Market Cap: ${data.get('market_cap', 0)/1e9:.1f}B
  52-Week Range: ${data.get('52_week_low', 0):.2f} - ${data.get('52_week_high', 0):.2f}
  Beta: {data.get('beta', 0):.2f}

Fundamentals:
  Revenue Growth: {fundamentals.get('revenue_growth', 0)*100:.1f}%
  Earnings Growth: {fundamentals.get('earnings_growth', 0)*100:.1f}%
  Profit Margin: {fundamentals.get('profit_margins', 0)*100:.1f}%
  ROE: {fundamentals.get('roe', 0)*100:.1f}%
  EPS: ${fundamentals.get('eps', 0):.2f} (Fwd: ${fundamentals.get('forward_eps', 0):.2f})

Analyst Rating: {data.get('recommendation', 'N/A').upper()} | Target: ${data.get('target_price', 0):.2f}

Recent News:
"""
            # Add top 3 news items
            for i, item in enumerate(news[:3], 1):
                text += f"  {i}. {item.get('title', 'N/A')} ({item.get('publisher', 'Unknown')})\n"
            
            text += "\n"
        
        return text.strip()
    
    def _format_earnings_calendar(self, calendar: List[Dict]) -> str:
        """Format earnings calendar"""
        if not calendar:
            return "No upcoming earnings in current positions"
        
        text = "Upcoming Earnings:\n"
        for item in calendar:
            text += f"  - {item['symbol']} ({item.get('company', 'Unknown')}): {item.get('earnings_date', 'TBD')}\n"
        
        return text.strip()
    
    def _parse_decision(self, response_text: str) -> Dict:
        """Parse Gemini's response into structured decision"""
        
        decision = {
            'action': 'HOLD',
            'symbol': None,
            'quantity': None,
            'confidence': 5,
            'reasoning': response_text,
            'key_catalysts': [],
            'risk_factors': []
        }
        
        # Extract decision
        decision_match = re.search(r'Decision:\s*(BUY|SELL|HOLD)', response_text, re.IGNORECASE)
        if decision_match:
            decision['action'] = decision_match.group(1).upper()
        
        # Extract symbol
        symbol_match = re.search(r'Symbol:\s*([A-Z]{1,5})', response_text)
        if symbol_match:
            decision['symbol'] = symbol_match.group(1).upper()
        
        # Extract quantity
        quantity_match = re.search(r'Quantity:\s*(\d+)', response_text)
        if quantity_match:
            decision['quantity'] = int(quantity_match.group(1))
        
        # Extract confidence
        confidence_match = re.search(r'Confidence:\s*(\d+)', response_text)
        if confidence_match:
            decision['confidence'] = int(confidence_match.group(1))
        
        # Extract key catalysts
        catalysts_section = re.search(r'Key Catalysts:(.*?)(?:Risk Factors:|$)', response_text, re.DOTALL)
        if catalysts_section:
            catalysts = re.findall(r'-\s*(.+)', catalysts_section.group(1))
            decision['key_catalysts'] = [c.strip() for c in catalysts]
        
        # Extract risk factors
        risks_section = re.search(r'Risk Factors:(.*?)$', response_text, re.DOTALL)
        if risks_section:
            risks = re.findall(r'-\s*(.+)', risks_section.group(1))
            decision['risk_factors'] = [r.strip() for r in risks]
        
        return decision
    
    def generate_daily_summary(self, portfolio_state: Dict, recent_decisions: List[Dict]) -> str:
        """Generate a narrative summary of current strategy"""
        
        prompt = f"""Generate a concise 3-4 sentence trading plan summary for today.

Portfolio Status:
- Value: ${portfolio_state.get('total_value', 0):,.0f}
- Return: {portfolio_state.get('total_return', 0):+.2f}%
- Positions: {portfolio_state.get('position_count', 0)}
- Cash: ${portfolio_state.get('cash', 0):,.0f} ({portfolio_state.get('cash_percentage', 0):.1f}%)

Recent Activity:
{self._format_recent_activity(recent_decisions)}

Write a professional, concise summary similar to:
"Holding all positions steady ahead of earnings. Portfolio at $107,880 (+7.9%) with MSFT reporting tomorrow..."

Focus on: current strategy, upcoming catalysts, reasoning for holds/trades.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Portfolio update: ${portfolio_state.get('total_value', 0):,.0f} ({portfolio_state.get('total_return', 0):+.2f}%)"
    
    def _format_recent_activity(self, decisions: List[Dict]) -> str:
        """Format recent decisions"""
        if not decisions:
            return "No recent activity"
        
        # Filter out None values
        valid_decisions = [d for d in decisions if d is not None]
        
        if not valid_decisions:
            return "No recent activity"
        
        text = ""
        for decision in valid_decisions[-5:]:  # Last 5 decisions
            text += f"- {decision.get('timestamp', 'Unknown')}: {decision.get('action', 'HOLD')}"
            if decision.get('symbol'):
                text += f" {decision['symbol']}"
            text += "\n"
        
        return text.strip()

if __name__ == "__main__":
    # Test Gemini trader
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY', '')
    
    if api_key:
        trader = GeminiTrader(api_key)
        print("✓ Gemini trader ready for analysis")
    else:
        print("⚠ Please set GOOGLE_API_KEY in .env file")
