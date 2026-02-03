# Quick Start Guide 🚀

Get your AI trading system up and running in 10 minutes!

## Step 1: Get API Keys (5 minutes)

### Gemini API (FREE)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with "AI...")

### Alpaca API (FREE)
1. Visit: https://alpaca.markets
2. Sign up for free account
3. Go to "Paper Trading" section
4. Click "Generate API Keys"
5. Copy both "API Key" and "Secret Key"

## Step 2: Install Dependencies (2 minutes)

```bash
# Make sure you're in the ai-trader directory
cd ai-trader

# Install all required packages
pip install -r requirements.txt
```

## Step 3: Configure Environment (1 minute)

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your favorite editor
nano .env
# or
vim .env
# or
code .env
```

Replace the placeholder values:
```bash
GOOGLE_API_KEY=AIza...your_actual_gemini_key_here
ALPACA_API_KEY=PK...your_actual_alpaca_key_here
ALPACA_SECRET_KEY=...your_actual_alpaca_secret_here
ALPACA_ENV=paper  # Keep as 'paper' for testing!
```

Save and exit.

## Step 4: Test Your Setup (2 minutes)

```bash
# Run the test script
python test_setup.py
```

You should see all tests pass:
```
✓ Package Imports - PASS
✓ Environment Variables - PASS
✓ Database - PASS
✓ Market Data - PASS
✓ Alpaca Connection - PASS
✓ Gemini AI Connection - PASS
```

If any test fails, check the error message and fix accordingly.

## Step 5: Run Your First Trading Cycle! 🎉

```bash
python main.py
```

Select option 1 for a manual test run.

You'll see:
1. Portfolio state fetched
2. Market data collected
3. AI analysis running
4. Trading decision made
5. Trade executed (or HOLD)
6. Results saved to database

## What Happens Next?

The AI will:
- Analyze current market conditions
- Review your portfolio (or start fresh)
- Consider fundamentals, technicals, and news
- Make a BUY, SELL, or HOLD decision
- Provide detailed reasoning
- Execute the trade if valid

## Example Output

```
TRADING CYCLE STARTED - 2024-01-31 09:35:00
================================================

[1/7] Fetching portfolio state...
  Portfolio Value: $100,000.00
  Cash: $100,000.00 (100.0%)
  Positions: 0
  
[2/7] Collecting market data...
  Fetched data for 12 symbols
  
[3/7] Analyzing market conditions...
  SPY: $485.23 (+0.45%)
  VIX: 13.5 (Greedy)
  
[4/7] Checking earnings calendar...
  3 upcoming earnings
  
[5/7] Running AI analysis...

  AI Decision: BUY
  Symbol: NVDA
  Quantity: 50
  Confidence: 9/10
  
[6/7] Validating trade...
  ✓ Risk checks passed
  ✓ Alpaca validation passed
  
  Executing BUY 50 NVDA @ $875.30
  ✓ Trade executed successfully!
  
[7/7] Saving portfolio snapshot...

TRADING CYCLE COMPLETED
```

## Next Steps

### Paper Trading (Recommended: 30-60 days)
```bash
# Run automated trading
python main.py
# Select option 2

# This will trade automatically at:
# - 9:35 AM EST (market open)
# - 3:55 PM EST (market close)
```

### Monitor Performance
- Check Alpaca dashboard daily
- Review AI reasoning in console
- Query database for trade history

### After Success
- If paper trading is profitable after 60 days
- Consider small real capital ($5K)
- Scale gradually based on results

## Common Questions

**Q: Will this lose all my money?**
A: You're using PAPER TRADING by default. It's 100% simulated with fake money!

**Q: How often does it trade?**
A: 1-2 times per day typically. The AI often chooses HOLD to let positions mature.

**Q: What if the AI makes a bad decision?**
A: Risk limits protect you (max 15% per position, 2% daily loss limit).

**Q: Can I change the stocks it trades?**
A: Yes! Edit the watchlist in `main.py`.

**Q: Is Gemini really free?**
A: Yes! The free tier allows 2 requests/minute, perfect for trading.

## Support

Issues? Check:
1. Test script output: `python test_setup.py`
2. Log files in console
3. Database: `sqlite3 trading_data.db`
4. README.md for detailed docs

## Ready to Trade!

You're all set! The system will:
- ✅ Analyze markets professionally
- ✅ Make data-driven decisions
- ✅ Manage risk automatically
- ✅ Track performance meticulously
- ✅ Learn and adapt over time

**Happy Trading! 📈🤖**

---

*Remember: Start with paper trading, test thoroughly, and only use real capital after proving success.*
