import sqlite3
from datetime import datetime
import json

class Database:
    """Handles all database operations for the AI trader"""
    
    def __init__(self, db_path='trading_data.db'):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create all necessary tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                reasoning TEXT,
                confidence INTEGER,
                order_id TEXT
            )
        ''')
        
        # AI Decisions table (stores all analysis, even HOLD decisions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                symbol TEXT,
                quantity INTEGER,
                reasoning TEXT NOT NULL,
                confidence INTEGER,
                market_data TEXT,
                portfolio_state TEXT
            )
        ''')
        
        # Portfolio snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash REAL NOT NULL,
                positions TEXT NOT NULL,
                daily_return REAL,
                total_return REAL
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                portfolio_value REAL NOT NULL,
                daily_return REAL,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                spy_return REAL
            )
        ''')
        
        self.conn.commit()
        print("✓ Database initialized successfully")
    
    def log_trade(self, trade_data):
        """Log a trade execution"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades 
            (timestamp, symbol, action, quantity, price, total_value, reasoning, confidence, order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['timestamp'],
            trade_data['symbol'],
            trade_data['action'],
            trade_data['quantity'],
            trade_data['price'],
            trade_data['total_value'],
            trade_data['reasoning'],
            trade_data['confidence'],
            trade_data.get('order_id', '')
        ))
        self.conn.commit()
    
    def log_decision(self, decision, market_context, portfolio_state):
        """Log an AI decision (including HOLD decisions)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ai_decisions
            (timestamp, action, symbol, quantity, reasoning, confidence, market_data, portfolio_state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision['timestamp'],
            decision['action'],
            decision.get('symbol'),
            decision.get('quantity'),
            decision['reasoning'],
            decision.get('confidence'),
            json.dumps(market_context),
            json.dumps(portfolio_state)
        ))
        self.conn.commit()
    
    def save_portfolio_snapshot(self, snapshot):
        """Save current portfolio state"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO portfolio_snapshots
            (timestamp, total_value, cash, positions, daily_return, total_return)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            snapshot['timestamp'],
            snapshot['total_value'],
            snapshot['cash'],
            json.dumps(snapshot['positions']),
            snapshot.get('daily_return'),
            snapshot.get('total_return')
        ))
        self.conn.commit()
    
    def get_recent_trades(self, limit=10):
        """Get recent trades"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trades 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        trades = []
        for row in cursor.fetchall():
            trades.append(dict(zip(columns, row)))
        return trades
    
    def get_latest_decision(self):
        """Get the most recent AI decision"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM ai_decisions 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_portfolio_history(self, days=30):
        """Get portfolio value history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, total_value, total_return 
            FROM portfolio_snapshots 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (days,))
        
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Test database creation
    db = Database()
    print("Database setup complete!")
