# AI Trading System - Project Structure

```
ai-trader/
│
├── main.py                  # Main orchestrator - run this to start trading
├── database.py              # SQLite database management
├── market_data.py           # Market data collection (Yahoo Finance)
├── alpaca_trader.py         # Alpaca API integration for trading
├── gemini_trader.py         # Gemini AI analysis and decision making
├── risk_manager.py          # Risk management and trade validation
├── test_setup.py            # Setup verification script
│
├── requirements.txt         # Python package dependencies
├── .env.example            # Environment variable template
├── .env                    # Your actual API keys (create this!)
│
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick start guide
└── PROJECT_STRUCTURE.md    # This file
│
└── trading_data.db         # SQLite database (created automatically)
```

## File Descriptions

### Core Trading Files

**main.py** (400 lines)
- Main entry point for the trading system
- Coordinates all components
- Handles scheduling and automation
- Generates daily reports
- Usage: `python main.py`

**gemini_trader.py** (350 lines)
- Integrates with Google Gemini 1.5 Pro
- Builds comprehensive analysis prompts
- Parses AI decisions
- Generates trading narratives
- Core intelligence of the system

**alpaca_trader.py** (300 lines)
- Connects to Alpaca Markets API
- Executes buy/sell orders
- Fetches account and position data
- Validates trades
- Handles market hours

**market_data.py** (250 lines)
- Fetches stock prices and fundamentals
- Gets news and sentiment
- Retrieves earnings calendar
- Monitors market conditions (SPY, VIX)
- Uses Yahoo Finance API

**risk_manager.py** (200 lines)
- Validates every trade
- Enforces position limits (15% max)
- Enforces daily loss limits (2% max)
- Checks portfolio concentration
- Monitors portfolio health

**database.py** (150 lines)
- SQLite database management
- Stores all trades and decisions
- Tracks portfolio snapshots
- Maintains performance history
- Provides query methods

### Configuration Files

**.env.example**
- Template for environment variables
- Shows required API keys
- Includes default parameters
- Copy to `.env` and fill in

**requirements.txt**
- Lists all Python dependencies
- Install with: `pip install -r requirements.txt`
- Includes: Gemini, Alpaca, yfinance, pandas, etc.

### Documentation

**README.md**
- Comprehensive system documentation
- Setup instructions
- Usage examples
- Architecture overview
- Troubleshooting guide

**QUICKSTART.md**
- Fast 10-minute setup guide
- Step-by-step instructions
- Common questions
- Example output

**PROJECT_STRUCTURE.md**
- This file
- Explains each component
- Shows data flow
- Integration points

### Testing

**test_setup.py**
- Verifies all components work
- Tests API connections
- Validates environment setup
- Run before trading: `python test_setup.py`

## Data Flow

```
1. SCHEDULE
   └─> main.py (TradingOrchestrator)
   
2. DATA COLLECTION
   ├─> market_data.py (fetch stock data)
   ├─> alpaca_trader.py (get portfolio state)
   └─> market_data.py (get market overview)
   
3. AI ANALYSIS
   └─> gemini_trader.py (analyze & decide)
   
4. RISK VALIDATION
   └─> risk_manager.py (validate trade)
   
5. EXECUTION
   └─> alpaca_trader.py (execute order)
   
6. STORAGE
   └─> database.py (log everything)
```

## Database Schema

**trades**
- Trade history (executed orders)
- Columns: timestamp, symbol, action, quantity, price, reasoning

**ai_decisions**
- All AI analysis (including HOLD decisions)
- Columns: timestamp, action, reasoning, confidence, market_data

**portfolio_snapshots**
- Historical portfolio values
- Columns: timestamp, total_value, cash, positions, returns

**performance_metrics**
- Daily performance tracking
- Columns: date, portfolio_value, daily_return, sharpe_ratio

## Integration Points

### External APIs
1. **Google Gemini** (gemini_trader.py)
   - Endpoint: Google AI API
   - Rate limit: 2 requests/min (free tier)
   - Purpose: AI analysis and decisions

2. **Alpaca Markets** (alpaca_trader.py)
   - Endpoint: Alpaca Trading API
   - Rate limit: Generous
   - Purpose: Trade execution and account data

3. **Yahoo Finance** (market_data.py)
   - Endpoint: yfinance library
   - Rate limit: Reasonable
   - Purpose: Market data and fundamentals

### Internal Communication
- All modules import from each other
- Shared data structures (Dict/List)
- Centralized configuration (env vars)
- Common database (SQLite)

## Customization Points

### Easy to Modify

**Watchlist** (main.py line ~60)
```python
self.watchlist = ['AAPL', 'MSFT', ...]
```

**Risk Parameters** (.env)
```bash
MAX_POSITION_SIZE=0.15
DAILY_LOSS_LIMIT=0.02
MIN_CONFIDENCE=6
```

**Trading Schedule** (main.py line ~300)
```python
schedule.every().day.at("09:35").do(...)
```

**AI Prompt** (gemini_trader.py line ~50)
```python
def _build_analysis_prompt(...)
```

### Advanced Modifications

**Add New Data Sources**
- Edit market_data.py
- Add new collection methods
- Include in analysis prompt

**Change AI Model**
- Edit gemini_trader.py
- Switch to GPT-4, Claude, etc.
- Adjust prompt format

**Add New Risk Rules**
- Edit risk_manager.py
- Add validation checks
- Update health checks

**Custom Strategies**
- Edit gemini_trader.py prompt
- Add technical indicators
- Include custom signals

## Dependencies

### Required Python Packages
```
google-generativeai  # Gemini AI
alpaca-py           # Trading
yfinance            # Market data
pandas              # Data processing
schedule            # Automation
fastapi             # API (future)
sqlite3             # Database (built-in)
```

### System Requirements
- Python 3.10+
- Internet connection
- 100MB disk space
- Minimal CPU/RAM

## Security Notes

### Sensitive Files
- `.env` - Contains API keys (DO NOT COMMIT)
- `trading_data.db` - Contains your trading history

### Safe to Share
- All `.py` files
- `.env.example`
- Documentation files
- `requirements.txt`

### Best Practices
1. Never commit `.env` to git
2. Use paper trading first
3. Review AI decisions daily
4. Keep API keys secret
5. Regular database backups

## Deployment Options

### Local Machine
```bash
python main.py  # Run directly
```

### Cloud Server (AWS/GCP/DigitalOcean)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env
nano .env

# Run with screen/tmux
screen -S trading
python main.py
```

### Docker (Future)
```dockerfile
FROM python:3.10
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## Monitoring & Logs

### Real-time
- Console output during trading cycles
- Alpaca dashboard (web)

### Historical
- Database queries: `sqlite3 trading_data.db`
- Portfolio snapshots
- Trade history

### Performance
- Daily reports (generated automatically)
- Performance metrics table
- Comparison to S&P 500

## Scaling Considerations

### Current Setup (Good for $100K-$1M)
- 2-3 API calls per day
- 12-stock watchlist
- Single strategy

### To Scale to $1M+
- Add more watchlist symbols
- Multiple strategies
- Upgrade Gemini tier
- Add redundancy
- Professional data feeds

## Version History

**v1.0** (Current)
- Gemini 1.5 Pro integration
- Alpaca trading
- Basic risk management
- SQLite storage
- Paper trading ready

**Future Versions**
- v1.1: Web dashboard
- v1.2: Multiple strategies
- v1.3: Options trading
- v2.0: Full automation platform

## Getting Help

### Check These First
1. Run `python test_setup.py`
2. Review console output
3. Check database logs
4. Read README.md

### Common Issues
- See README.md "Common Issues" section
- Most problems are API key related
- Verify .env file is correct

---

**Built with Python 🐍 | Powered by AI 🤖 | Trade Smarter 📈**
