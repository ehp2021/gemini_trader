# AI Trading System - Complete Setup Guide 🚀

## 🎯 What You're Building

An **AI-powered trading system** that:
- Analyzes stocks using Google Gemini AI (FREE)
- Executes trades via Alpaca Markets (FREE, no commissions)
- Manages a $100K portfolio automatically
- Makes data-driven decisions based on fundamentals, technicals, and news
- Provides detailed reasoning for every trade
- Tracks performance vs S&P 500

## 📦 What's Included

```
ai-trader/
├── main.py              # Main trading orchestrator
├── gemini_trader.py     # AI analysis engine
├── alpaca_trader.py     # Trading execution
├── market_data.py       # Data collection
├── risk_manager.py      # Risk management
├── database.py          # Data storage
├── test_setup.py        # Setup verification
├── requirements.txt     # Dependencies
├── .env.example         # Config template
├── README.md            # Full documentation
├── QUICKSTART.md        # Fast setup guide
└── PROJECT_STRUCTURE.md # Architecture details
```

## 🚀 Installation (10 Minutes)

### Step 1: Prerequisites

**Required:**
- Python 3.10 or higher
- Internet connection
- Terminal/Command prompt

**Check Python version:**
```bash
python --version
# Should show Python 3.10.x or higher
```

### Step 2: Extract Files

```bash
# Navigate to your desired location
cd ~/Documents  # or wherever you want

# Extract the ai-trader folder
# (if you downloaded as zip, unzip it first)

cd ai-trader
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Gemini AI
- `alpaca-py` - Trading API
- `yfinance` - Market data
- `pandas` - Data processing
- `schedule` - Automation
- And more...

### Step 4: Get API Keys

#### A) Google Gemini API (100% FREE)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

**Cost:** $0/month (free tier includes 2 requests/min)

#### B) Alpaca Trading API (100% FREE)

1. Go to: https://alpaca.markets
2. Sign up for free account
3. Go to "Paper Trading" section
4. Click "View" under API Keys
5. Click "Generate New Key"
6. Copy both:
   - API Key (starts with `PK...`)
   - Secret Key

**Cost:** $0/month (no commissions, free paper trading)

### Step 5: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit with your keys
nano .env
# or use any text editor
```

**Update .env file:**
```bash
GOOGLE_API_KEY=AIza...paste_your_gemini_key_here
ALPACA_API_KEY=PK...paste_your_alpaca_key_here
ALPACA_SECRET_KEY=paste_your_alpaca_secret_here

# Keep these as-is for now
ALPACA_ENV=paper
INITIAL_CAPITAL=100000
MAX_POSITION_SIZE=0.15
DAILY_LOSS_LIMIT=0.02
MIN_CONFIDENCE=6
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

### Step 6: Test Setup

```bash
python test_setup.py
```

**Expected output:**
```
✓ Package Imports - PASS
✓ Environment Variables - PASS
✓ Database - PASS
✓ Market Data - PASS
✓ Alpaca Connection - PASS
✓ Gemini AI Connection - PASS

✓ ALL TESTS PASSED - System is ready!
```

If any test fails, check the error message and fix accordingly.

## 🎮 Usage

### Option 1: Manual Trading Cycle

Best for testing and learning.

```bash
python main.py
# Select: 1 (Run single trading cycle)
```

**What happens:**
1. Fetches your portfolio state
2. Collects market data for 12 stocks
3. Analyzes market conditions (SPY, VIX)
4. Runs AI analysis (takes 30-60 seconds)
5. Makes BUY/SELL/HOLD decision
6. Validates and executes trade
7. Saves everything to database

**Duration:** 1-2 minutes per cycle

### Option 2: Automated Trading

Runs automatically during market hours.

```bash
python main.py
# Select: 2 (Start scheduled automated trading)
```

**Schedule:**
- **9:35 AM EST**: Morning analysis
- **3:55 PM EST**: End-of-day analysis
- **4:05 PM EST**: Daily report

The script will keep running. Press Ctrl+C to stop.

### Option 3: Generate Report Only

```bash
python main.py
# Select: 3 (Generate report only)
```

Shows current portfolio state and recent activity.

## 📊 Understanding the Output

### Example Trading Cycle

```
TRADING CYCLE STARTED - 2024-01-31 09:35:00
================================================

[1/7] Fetching portfolio state...
  Portfolio Value: $100,000.00
  Cash: $85,000.00 (85.0%)
  Positions: 2
  Total Return: +3.2%

[2/7] Collecting market data...
  Fetched data for 12 symbols

[3/7] Analyzing market conditions...
  SPY: $485.23 (+0.45%)
  VIX: 13.5 (Greedy)

[4/7] Checking earnings calendar...
  2 upcoming earnings

[5/7] Running AI analysis...

  AI Decision: BUY
  Symbol: NVDA
  Quantity: 15
  Confidence: 8/10

[6/7] Validating trade...
  ✓ Risk checks passed
  ✓ Alpaca validation passed
  
  Executing BUY 15 NVDA @ $875.30
  ✓ Trade executed successfully!
  Order ID: abc123...

[7/7] Saving portfolio snapshot...

TRADING CYCLE COMPLETED
================================================

AI REASONING:
------------------------------------------------------------
Initiating position in NVDA ahead of strong datacenter 
demand. The stock has consolidated well above $850 support 
and H100/H200 GPU demand remains robust. With Microsoft, 
Google, and Amazon all expanding AI infrastructure spend, 
NVDA is the clear beneficiary. Recent earnings guidance 
was conservative, setting up for a beat. Position sized 
at ~12% of portfolio given high conviction...
------------------------------------------------------------
```

### AI Decision Format

Every decision includes:

**Decision:** BUY/SELL/HOLD
**Symbol:** Stock ticker (if applicable)
**Quantity:** Number of shares (if applicable)
**Confidence:** 1-10 rating

**Analysis:** 250-400 word reasoning including:
- Current portfolio positioning
- Stock-specific catalysts
- Market conditions
- Risk considerations
- Upcoming events

**Key Catalysts:**
- List of upcoming events

**Risk Factors:**
- List of monitored risks

## 🛡️ Risk Management

The system has multiple safety layers:

### 1. Position Size Limits
- **Maximum:** 15% of portfolio per stock
- **Example:** With $100K, max $15K per position
- Prevents over-concentration

### 2. Daily Loss Limits
- **Maximum:** 2% daily loss
- **Example:** If down $2K in a day, stops trading
- Prevents catastrophic losses

### 3. Confidence Threshold
- **Minimum:** 6/10 confidence to trade
- AI won't trade unless reasonably confident
- Reduces impulsive decisions

### 4. Cash Reserves
- System warns if cash < 10%
- Maintains buying power for opportunities

### 5. Diversification
- Tracks number of positions
- Warns if too concentrated
- Monitors sector exposure

### 6. Market Hours
- Only trades when market is open
- No after-hours or pre-market trades
- Standard 9:30 AM - 4:00 PM EST

## 📈 Monitoring Performance

### View Database

```bash
# Open database
sqlite3 trading_data.db

# View recent trades
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;

# View AI decisions
SELECT timestamp, action, symbol, confidence 
FROM ai_decisions 
ORDER BY timestamp DESC 
LIMIT 10;

# View portfolio history
SELECT timestamp, total_value, total_return 
FROM portfolio_snapshots 
ORDER BY timestamp DESC 
LIMIT 30;

# Exit
.quit
```

### Alpaca Dashboard

1. Go to: https://app.alpaca.markets
2. Login to your account
3. Click "Paper Trading"
4. View:
   - Current positions
   - Order history
   - Portfolio chart
   - Activity feed

### Console Logs

All trading cycles print detailed logs:
- Portfolio state
- Market conditions
- AI reasoning
- Trade execution
- Risk validations

## 🎯 Customization

### Change Watchlist

Edit `main.py` around line 60:

```python
self.watchlist = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN',  # Mega-caps
    'NVDA', 'AMD', 'INTC',             # Semiconductors
    'META', 'NFLX', 'DIS',             # Consumer/Media
    'CRM', 'ADBE', 'ORCL'              # Enterprise software
]
```

Add any US stocks you want to track.

### Adjust Risk Parameters

Edit `.env` file:

```bash
MAX_POSITION_SIZE=0.15  # 15% max per position
DAILY_LOSS_LIMIT=0.02   # 2% max daily loss
MIN_CONFIDENCE=6        # Min confidence 6/10
```

### Change Trading Schedule

Edit `main.py` around line 300:

```python
schedule.every().day.at("09:35").do(self.trading_cycle)
schedule.every().day.at("13:00").do(self.trading_cycle)  # Add midday
schedule.every().day.at("15:55").do(self.trading_cycle)
```

### Modify AI Prompts

Edit `gemini_trader.py` around line 50-200:

The `_build_analysis_prompt()` function controls what the AI sees and how it thinks. You can:
- Add new data sources
- Emphasize certain factors
- Change strategy focus
- Include custom indicators

## 🔄 Workflow Recommendations

### Phase 1: Testing (Week 1-2)
```bash
# Run manual cycles daily
python main.py  # Option 1

# Review AI reasoning
# Check trade execution
# Monitor portfolio growth
```

### Phase 2: Paper Trading (Month 1-2)
```bash
# Run automated trading
python main.py  # Option 2

# Let it run for 30-60 days
# Track vs S&P 500
# Evaluate decision quality
```

### Phase 3: Analysis (End of Month 2)
- Review win rate
- Calculate Sharpe ratio
- Check maximum drawdown
- Compare to benchmark

### Phase 4: Live Trading (Month 3+)
**Only if paper trading successful:**
1. Change `.env`: `ALPACA_ENV=live`
2. Use Alpaca live API keys
3. Start with $5K-$10K
4. Scale gradually

## 🐛 Troubleshooting

### "Market is closed"
**Issue:** Trading attempted outside market hours  
**Solution:** Run during 9:30 AM - 4:00 PM EST or use scheduled mode

### "API rate limit exceeded"
**Issue:** Too many Gemini requests  
**Solution:** Free tier allows 2/min. Don't run cycles more than 2-3x per day

### "Insufficient buying power"
**Issue:** Trying to buy more than available cash  
**Solution:** Check Alpaca dashboard, verify position sizes

### "API key invalid"
**Issue:** Wrong API keys in .env  
**Solution:** Double-check keys from Gemini/Alpaca dashboards

### "No module named..."
**Issue:** Missing Python package  
**Solution:** Run `pip install -r requirements.txt`

### Tests failing
**Issue:** Setup not complete  
**Solution:** Run `python test_setup.py` and fix each failed test

## 💰 Cost Breakdown

### Current Setup: $0/month

- **Gemini API:** FREE (2 requests/min)
- **Alpaca Trading:** FREE (no commissions)
- **Yahoo Finance:** FREE
- **Hosting:** FREE (run on your computer)

**Total:** $0/month! 🎉

### If Scaling to Production

- **Gemini Pro (if needed):** ~$7/million tokens
- **Expected usage:** 2-3 calls/day = $5-10/month
- **Still FREE** with Alpaca (no commissions)

**Total:** Still very cheap!

## 📚 Additional Resources

### Documentation
- **README.md** - Comprehensive docs
- **QUICKSTART.md** - Fast setup guide
- **PROJECT_STRUCTURE.md** - Architecture details

### Code Files
- All Python files are well-commented
- Functions have docstrings
- Variable names are descriptive

### Support
- Alpaca Docs: https://docs.alpaca.markets
- Gemini Docs: https://ai.google.dev/docs
- yfinance: https://pypi.org/project/yfinance/

## ⚠️ Important Disclaimers

1. **Use Paper Trading First**
   - Test for at least 30-60 days
   - Prove profitability before real money
   
2. **Not Financial Advice**
   - This is educational software
   - Trading involves substantial risk
   - Consult a financial advisor

3. **No Guarantees**
   - Past performance ≠ future results
   - AI can make mistakes
   - Markets are unpredictable

4. **Your Responsibility**
   - You control when to go live
   - You manage risk parameters
   - You monitor performance

## ✅ Final Checklist

Before going live:

- [ ] Tested with paper trading for 60+ days
- [ ] Reviewed all AI decisions
- [ ] Profitable vs S&P 500
- [ ] Comfortable with strategy
- [ ] Understand all risk parameters
- [ ] Have emergency stop plan
- [ ] Using only risk capital

## 🎉 You're Ready!

You now have a complete AI trading system:

✅ Automated data collection  
✅ Intelligent analysis  
✅ Risk-managed execution  
✅ Performance tracking  
✅ Full audit trail  

**Start with paper trading and build confidence!**

Good luck and trade wisely! 📈🤖

---

*Built with Python | Powered by Gemini AI | Executed on Alpaca*
