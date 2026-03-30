"""
Market Analyzer - Analyzes agent marketplace dynamics
"""
import json
from datetime import datetime
from collections import defaultdict

class MarketAnalyzer:
    def __init__(self):
        self.trades = []
        self.offers = []
        self.demands = []
    
    def record_trade(self, from_agent, to_agent, item, price):
        trade = {
            "from": from_agent,
            "to": to_agent,
            "item": item,
            "price": price,
            "time": datetime.now().isoformat()
        }
        self.trades.append(trade)
        return trade
    
    def record_offer(self, agent, item, price):
        offer = {"agent": agent, "item": item, "price": price, "time": datetime.now().isoformat()}
        self.offers.append(offer)
        return offer
    
    def record_demand(self, agent, item, max_price):
        demand = {"agent": agent, "item": item, "max_price": max_price, "time": datetime.now().isoformat()}
        self.demands.append(demand)
        return demand
    
    def get_market_stats(self):
        if not self.trades:
            return {"total_trades": 0, "volume": 0, "avg_price": 0}
        
        prices = [t["price"] for t in self.trades]
        return {
            "total_trades": len(self.trades),
            "volume": sum(prices),
            "avg_price": sum(prices) / len(prices),
            "max_price": max(prices),
            "min_price": min(prices)
        }
    
    def get_status(self):
        return {
            "trades": len(self.trades),
            "offers": len(self.offers),
            "demands": len(self.demands),
            "stats": self.get_market_stats()
        }

if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    analyzer.record_trade("alpha", "beta", "tool", 100)
    print("Market stats:", analyzer.get_market_stats())
