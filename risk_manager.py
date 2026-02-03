from typing import Dict, Tuple, List
from datetime import datetime

class RiskManager:
    """Manages trading risk and validates trades before execution"""
    
    def __init__(self, max_position_size: float = 0.15, daily_loss_limit: float = 0.02,
                 min_confidence: int = 6, max_positions: int = 12):
        self.max_position_size = max_position_size  # Max 15% per position
        self.daily_loss_limit = daily_loss_limit    # Max 2% daily loss
        self.min_confidence = min_confidence        # Min confidence to trade
        self.max_positions = max_positions          # Max number of positions
        self.daily_start_value = None
        self.trades_today = 0
        
        print(f"✓ Risk Manager initialized (Max pos: {max_position_size*100}%, Daily loss limit: {daily_loss_limit*100}%)")
    
    def validate_trade(self, decision: Dict, portfolio_state: Dict, 
                       price: float) -> Tuple[bool, str]:
        """
        Validate if a trade should be executed
        Returns: (is_valid, reason)
        """
        
        # Check 1: Confidence threshold
        if decision.get('confidence', 0) < self.min_confidence:
            return False, f"Confidence {decision.get('confidence')} below minimum {self.min_confidence}"
        
        # Check 2: HOLD decisions are always valid
        if decision['action'] == 'HOLD':
            return True, "HOLD decision - no validation needed"
        
        # Check 3: Valid action
        if decision['action'] not in ['BUY', 'SELL']:
            return False, f"Invalid action: {decision['action']}"
        
        # Check 4: Symbol provided
        if not decision.get('symbol'):
            return False, "No symbol specified for trade"
        
        # Check 5: Quantity provided
        if not decision.get('quantity') or decision['quantity'] <= 0:
            return False, "Invalid or missing quantity"
        
        # Check 6: Daily loss limit
        if self.daily_start_value:
            current_value = portfolio_state.get('total_value', 0)
            daily_loss = (current_value - self.daily_start_value) / self.daily_start_value
            
            if daily_loss < -self.daily_loss_limit:
                return False, f"Daily loss limit exceeded: {daily_loss*100:.2f}% (limit: {self.daily_loss_limit*100}%)"
        
        # Check 7: Position size limit (for BUY orders)
        if decision['action'] == 'BUY':
            trade_value = price * decision['quantity']
            portfolio_value = portfolio_state.get('total_value', 100000)
            position_pct = trade_value / portfolio_value
            
            if position_pct > self.max_position_size:
                return False, f"Position size {position_pct*100:.1f}% exceeds max {self.max_position_size*100}%"
            
            # Check cash available
            cash = portfolio_state.get('cash', 0)
            if trade_value > cash:
                return False, f"Insufficient cash: need ${trade_value:,.2f}, have ${cash:,.2f}"
            
            # Check max positions
            current_positions = len(portfolio_state.get('positions', []))
            if current_positions >= self.max_positions:
                return False, f"Max positions ({self.max_positions}) reached"
        
        # Check 8: Position exists (for SELL orders)
        if decision['action'] == 'SELL':
            positions = portfolio_state.get('positions', [])
            position = next((p for p in positions if p['symbol'] == decision['symbol']), None)
            
            if not position:
                return False, f"No position in {decision['symbol']} to sell"
            
            if decision['quantity'] > position['quantity']:
                return False, f"Cannot sell {decision['quantity']} shares, only own {position['quantity']}"
        
        # All checks passed
        return True, "All risk checks passed"
    
    def check_portfolio_health(self, portfolio_state: Dict) -> Dict:
        """
        Analyze overall portfolio health
        Returns risk metrics and warnings
        """
        
        positions = portfolio_state.get('positions', [])
        total_value = portfolio_state.get('total_value', 100000)
        
        health = {
            'status': 'healthy',
            'warnings': [],
            'metrics': {}
        }
        
        # Check concentration
        if positions:
            largest_position = max(positions, key=lambda p: p['market_value'])
            largest_pct = largest_position['market_value'] / total_value
            
            health['metrics']['largest_position_pct'] = largest_pct
            
            if largest_pct > 0.20:
                health['warnings'].append(f"High concentration: {largest_position['symbol']} is {largest_pct*100:.1f}% of portfolio")
                health['status'] = 'warning'
        
        # Check diversification
        num_positions = len(positions)
        health['metrics']['num_positions'] = num_positions
        
        if num_positions < 5:
            health['warnings'].append(f"Low diversification: only {num_positions} positions")
            health['status'] = 'warning'
        
        # Check cash level
        cash_pct = portfolio_state.get('cash_percentage', 0)
        health['metrics']['cash_pct'] = cash_pct
        
        if cash_pct < 5:
            health['warnings'].append(f"Low cash reserves: {cash_pct:.1f}%")
        elif cash_pct > 30:
            health['warnings'].append(f"High cash drag: {cash_pct:.1f}% not invested")
        
        # Check unrealized losses
        losing_positions = [p for p in positions if p['unrealized_plpc'] < -10]
        if losing_positions:
            health['warnings'].append(f"{len(losing_positions)} positions down >10%")
            health['status'] = 'warning'
        
        # Check daily performance
        if self.daily_start_value:
            current_value = portfolio_state.get('total_value', 0)
            daily_return = (current_value - self.daily_start_value) / self.daily_start_value
            health['metrics']['daily_return'] = daily_return
            
            if daily_return < -0.03:
                health['warnings'].append(f"Large daily loss: {daily_return*100:.2f}%")
                health['status'] = 'warning'
        
        return health
    
    def set_daily_start_value(self, value: float):
        """Set the starting portfolio value for the day"""
        self.daily_start_value = value
        self.trades_today = 0
    
    def record_trade(self):
        """Record that a trade was executed"""
        self.trades_today += 1
    
    def get_position_limits(self, portfolio_value: float) -> Dict:
        """Calculate position sizing limits"""
        return {
            'max_position_value': portfolio_value * self.max_position_size,
            'max_position_pct': self.max_position_size * 100,
            'recommended_position_value': portfolio_value * (self.max_position_size * 0.75),  # 75% of max
            'daily_loss_limit_value': portfolio_value * self.daily_loss_limit
        }
    
    def should_reduce_exposure(self, portfolio_state: Dict) -> Tuple[bool, str]:
        """Check if we should reduce overall market exposure"""
        
        # Check if we're heavily losing
        if self.daily_start_value:
            current_value = portfolio_state.get('total_value', 0)
            daily_loss = (current_value - self.daily_start_value) / self.daily_start_value
            
            if daily_loss < -0.015:  # Down 1.5%
                return True, f"Significant daily loss: {daily_loss*100:.2f}%"
        
        # Check if we have too many losing positions
        positions = portfolio_state.get('positions', [])
        if positions:
            losing_positions = [p for p in positions if p['unrealized_plpc'] < -5]
            if len(losing_positions) / len(positions) > 0.5:
                return True, f"{len(losing_positions)}/{len(positions)} positions losing"
        
        return False, "Portfolio exposure acceptable"

if __name__ == "__main__":
    # Test risk manager
    risk_mgr = RiskManager()
    
    # Mock decision
    decision = {
        'action': 'BUY',
        'symbol': 'AAPL',
        'quantity': 10,
        'confidence': 8
    }
    
    # Mock portfolio
    portfolio = {
        'total_value': 100000,
        'cash': 20000,
        'positions': []
    }
    
    valid, reason = risk_mgr.validate_trade(decision, portfolio, 180.0)
    print(f"Trade validation: {valid} - {reason}")
    
    health = risk_mgr.check_portfolio_health(portfolio)
    print(f"Portfolio health: {health['status']}")
    print(f"Warnings: {health['warnings']}")
