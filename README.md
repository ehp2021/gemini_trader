# AI Trading System 🤖📈

An automated trading system powered by **Google Gemini AI** and **Alpaca Markets** for intelligent portfolio management.

## Features

- ✅ **AI-Powered Analysis**: Uses Google Gemini 1.5 Pro for market analysis
- ✅ **Real Market Data**: Fetches live stock prices, fundamentals, and news
- ✅ **Automated Trading**: Executes trades via Alpaca API
- ✅ **Risk Management**: Built-in position sizing and loss limits
- ✅ **Performance Tracking**: Complete audit trail of all decisions and trades
- ✅ **Paper Trading**: Test strategies risk-free before going live

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Trading Orchestrator                  │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Market Data  │  │  Gemini AI  │  │   Alpaca    │
│   Collector   │  │   Trader    │  │   Trading   │
└───────────────┘  └─────────────┘  └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                  ┌───────▼────────┐
                  │ Risk Manager   │
                  └────────────────┘
                          │
                  ┌───────▼────────┐
                  │   Database     │
                  └────────────────┘
```

## Installation

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd ai-trader

# Install dependencies
pip install -r requirements.txt
```

### 2. Get API Keys

#### Google Gemini API (FREE)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key

#### Alpaca Trading API (FREE)
1. Sign up at https://alpaca.markets
2. Go to Paper Trading dashboard
3. Generate API keys
4. Copy both API Key and Secret Key

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Update `.env` with your actual keys:
```bash
GOOGLE_API_KEY=your_google_gemini_api_key_here
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_ENV=paper  # Use 'paper' for testing
```

## Usage

### Quick Start (Manual Trading)

```bash
python main.py
# Select option 1: Run single trading cycle
```

This will:
1. Fetch current market data
2. Analyze your portfolio
3. Generate AI trading decision
4. Execute trade (if not HOLD)
5. Save results to database

### Automated Trading

```bash
python main.py
# Select option 2: Start scheduled automated trading
```

This runs trading cycles automatically:
- **9:35 AM EST**: Morning analysis and trade
- **3:55 PM EST**: End-of-day analysis and trade
- **4:05 PM EST**: Daily report generation

### Generate Report Only

```bash
python main.py
# Select option 3: Generate report only
```

## How It Works

### 1. Data Collection
The system collects comprehensive market data:
- **Real-time prices** (current, high, low, volume)
- **Fundamentals** (P/E ratio, earnings growth, margins, ROE)
- **News & sentiment** (recent articles, analyst ratings)
- **Technical indicators** (momentum, volatility)
- **Earnings calendar** (upcoming catalysts)

### 2. AI Analysis
Gemini AI receives all data and analyzes:
- Portfolio positioning and concentration
- Individual stock fundamentals and technicals
- Market conditions (VIX, SPY trends)
- Upcoming catalysts (earnings, Fed meetings)
- Risk/reward of each position

### 3. Decision Making
The AI decides one of three actions:
- **BUY**: Purchase shares with specific reasoning
- **SELL**: Exit position with specific reasoning
- **HOLD**: Maintain current positions with detailed explanation

### 4. Risk Management
Every trade is validated:
- ✅ Confidence threshold (min 6/10)
- ✅ Position size limit (max 15% per stock)
- ✅ Daily loss limit (max 2% down)
- ✅ Cash availability
- ✅ Market open hours

### 5. Execution
Valid trades are executed via Alpaca:
- Market orders at real-time prices
- Full audit trail in database
- Automatic position tracking

## Example AI Output

```
Decision: HOLD
Symbol: N/A
Quantity: N/A
Confidence: 8

Analysis:
Holding all 6 positions steady ahead of critical earnings week. 
Portfolio at $107,880 (+7.9%) with strong momentum across tech 
holdings. MSFT reports tomorrow after close with Azure expected 
at 37% growth - this is a key catalyst for my 11.6% position. 
AMD and GOOGL both report next week (Feb 3-4), representing 
another 45% of portfolio.

With 88% deployed and three major binary events in the next 8 
days, the disciplined move is letting these quality positions 
run through their earnings catalysts rather than making changes 
for activity's sake. Market conditions are supportive with Fed 
on pause and AI infrastructure spend accelerating.

Key Catalysts:
- MSFT earnings (tomorrow AH) - Azure growth is key metric
- AMD earnings (Feb 3) - MI300 datacenter ramp crucial
- GOOGL earnings (Feb 4) - Cloud margin expansion expected
- Fed commentary - Powell speaks Friday
- Semiconductor sector rotation trends

Risk Factors:
- Earnings disappointment risk with 60% reporting next week
- Tech sector concentration - need diversification
- Market overbought short-term - watching for pullback
- Rising yields could pressure growth multiples
- Geopolitical tensions affecting chip stocks
```

## Configuration

### Risk Parameters (`.env`)

```bash
MAX_POSITION_SIZE=0.15  # Max 15% per position
DAILY_LOSS_LIMIT=0.02   # Stop if down 2% in a day
MIN_CONFIDENCE=6        # Min AI confidence to trade
```

### Watchlist (`main.py`)

Edit the watchlist to track different stocks:
```python
self.watchlist = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META',
    'TSLA', 'AMD', 'NFLX', 'CRM', 'ADBE', 'ORCL'
]
```

## Database

All data is stored in `trading_data.db` (SQLite):

### Tables
- **trades**: All executed trades
- **ai_decisions**: All AI analysis (including HOLD)
- **portfolio_snapshots**: Historical portfolio values
- **performance_metrics**: Performance tracking

### Query Example
```sql
-- View all trades
SELECT * FROM trades ORDER BY timestamp DESC;

-- View AI decisions
SELECT timestamp, action, symbol, confidence 
FROM ai_decisions 
ORDER BY timestamp DESC 
LIMIT 10;

-- Portfolio history
SELECT timestamp, total_value, total_return 
FROM portfolio_snapshots 
ORDER BY timestamp DESC;
```

## Testing Strategy

### Phase 1: Paper Trading (1-2 months)
1. Start with Alpaca paper trading
2. Run daily for 30-60 days
3. Track performance vs S&P 500
4. Analyze AI decision quality

### Phase 2: Small Capital Test
1. If paper trading is successful
2. Start with $5,000 real capital
3. Run for 1 month
4. Evaluate real-world execution

### Phase 3: Full Deployment
1. Scale to $100K if successful
2. Continue monitoring daily
3. Adjust parameters as needed

## Cost Analysis

### API Costs
- **Gemini**: FREE (2 requests/min)
- **Alpaca**: FREE (no commissions)
- **Yahoo Finance**: FREE

### Expected Usage
- 2-3 AI calls per day
- Well within Gemini free tier
- Zero trading commissions

**Total Cost**: $0/month 🎉

## Monitoring & Maintenance

### Daily Review
1. Check AI reasoning quality
2. Verify trades were executed properly
3. Review portfolio health warnings
4. Compare to benchmark (S&P 500)

### Weekly Review
1. Analyze win rate
2. Check position concentration
3. Review risk metrics
4. Adjust watchlist if needed

### Monthly Review
1. Full performance analysis
2. Sharpe ratio calculation
3. Maximum drawdown review
4. Strategy refinement

## Common Issues

### "Market is closed"
- Trading only works during market hours (9:30 AM - 4:00 PM EST)
- Use scheduled mode to run automatically

### "Insufficient buying power"
- Check Alpaca account status
- Ensure you're using paper trading for testing
- Verify position size limits

### "API rate limit"
- Gemini free tier: 2 requests/min
- Don't run cycles more than 2-3 times per day
- Consider upgrading to paid tier if needed

### "No API key found"
- Ensure `.env` file exists
- Check API keys are correct
- Run `source .env` if needed

## Safety Features

- ✅ Paper trading by default
- ✅ Position size limits (15% max)
- ✅ Daily loss limits (2% max)
- ✅ Confidence thresholds
- ✅ Market hours validation
- ✅ Full audit trail

## Upgrading to Live Trading

**⚠️ ONLY after extensive paper trading success:**

1. Change `.env`:
   ```bash
   ALPACA_ENV=live
   ```

2. Use Alpaca live trading keys
3. Start with small capital ($5K-$10K)
4. Monitor closely for 1 month
5. Scale gradually

## Customization Ideas

### Add More Data Sources
- SEC filings (Edgar API)
- Social sentiment (Twitter/Reddit)
- Options flow (unusual activity)
- Insider trading data

### Enhance AI Prompts
- Add sector rotation analysis
- Include macro economic data
- Technical chart pattern recognition
- Correlation analysis

### Advanced Features
- Multi-timeframe analysis
- Pairs trading strategies
- Sector allocation optimization
- Options strategies

## Contributing

This is a personal trading system. Modify as needed for your strategy!

## Disclaimer

**⚠️ IMPORTANT DISCLAIMER ⚠️**

This software is for educational purposes only. Trading involves substantial risk of loss. 

- Not financial advice
- Past performance ≠ future results
- Test thoroughly before real capital
- Only invest what you can afford to lose
- Consult a financial advisor

The authors are not responsible for any trading losses.

## Support

For issues:
1. Check the logs in console output
2. Review database for decision history
3. Verify API keys are correct
4. Test with paper trading first

## License

MIT License - Use at your own risk

---

**Built with ❤️ using Gemini AI & Alpaca Markets**

Start your AI trading journey today! 🚀
