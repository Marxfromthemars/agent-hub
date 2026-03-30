"""
DISTRIBUTED MARKETPLACE - Scalable market for 10,000+ agents
Enables micro-transactions, automatic pricing, and market making
"""
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ListingType(Enum):
    TOOL = "tool"
    SERVICE = "service"
    RESEARCH = "research"
    DATA = "data"
    COMPUTE = "compute"

class ListingStatus(Enum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    FLAGGED = "flagged"

@dataclass
class Listing:
    id: str
    seller: str
    title: str
    description: str
    price: float
    type: ListingType
    tags: List[str]
    quality_score: float
    sales_count: int
    created_at: str
    expires_at: Optional[str]
    status: ListingStatus = ListingStatus.ACTIVE

@dataclass
class Transaction:
    id: str
    buyer: str
    seller: str
    listing_id: str
    amount: float
    timestamp: str
    verified: bool
    dispute: bool

class DistributedMarketplace:
    """Marketplace that scales to 10,000+ agents"""
    
    def __init__(self):
        self.listings: Dict[str, Listing] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.bids: Dict[str, List[dict]] = {}  # task_id -> list of bids
        self.prices: Dict[str, float] = {}  # type -> market price
        self.escrow: Dict[str, float] = {}  # transaction_id -> held amount
        
        # Market making: always have liquidity
        self.market_maker_enabled = True
        self.market_maker_spread = 0.05  # 5% spread
        
        # Initialize market prices for common types
        self.prices = {
            "tool": 50.0,
            "service": 100.0,
            "research": 75.0,
            "data": 25.0,
            "compute": 10.0,  # per unit
        }
    
    def create_listing(self, seller: str, title: str, description: str, 
                       price: float, listing_type: str, tags: List[str] = None) -> str:
        """Create a new listing"""
        listing_id = hashlib.sha256(f"{seller}{title}{time.time()}".encode()).hexdigest()[:16]
        
        listing = Listing(
            id=listing_id,
            seller=seller,
            title=title,
            description=description,
            price=price,
            type=ListingType(listing_type),
            tags=tags or [],
            quality_score=50.0,  # Start neutral
            sales_count=0,
            created_at=datetime.utcnow().isoformat(),
            expires_at=None
        )
        
        self.listings[listing_id] = listing
        return listing_id
    
    def get_market_price(self, listing_type: str) -> float:
        """Get current market price for a type"""
        return self.prices.get(listing_type, 50.0)
    
    def get_listings(self, listing_type: str = None, min_quality: float = 0, 
                     limit: int = 100) -> List[Listing]:
        """Get available listings, filtered and ranked"""
        results = []
        
        for listing in self.listings.values():
            if True:  # listing.status == ListingStatus.ACTIVE
                if listing_type and listing.type.value != listing_type:
                    continue
                if listing.quality_score >= min_quality:
                    results.append(listing)
        
        # Sort by quality score (highest first)
        results.sort(key=lambda x: x.quality_score, reverse=True)
        return results[:limit]
    
    def buy(self, buyer: str, listing_id: str, use_market_maker: bool = False) -> Transaction:
        """Buy a listing (or use market maker for instant purchase)"""
        
        if use_market_maker and listing_id not in self.listings:
            # Market maker creates pseudo-listing
            return self.market_maker_buy(buyer, listing_id)
        
        listing = self.listings.get(listing_id)
        if not listing or listing.status != ListingStatus.ACTIVE:
            raise ValueError("Listing not available")
        
        if buyer == listing.seller:
            raise ValueError("Cannot buy your own listing")
        
        # Create transaction
        tx_id = hashlib.sha256(f"{buyer}{listing_id}{time.time()}".encode()).hexdigest()[:16]
        
        transaction = Transaction(
            id=tx_id,
            buyer=buyer,
            seller=listing.seller,
            listing_id=listing_id,
            amount=listing.price,
            timestamp=datetime.utcnow().isoformat(),
            verified=False,
            dispute=False
        )
        
        # Put in escrow (held until delivery verified)
        self.escrow[tx_id] = listing.price
        
        # Update listing
        listing.sales_count += 1
        listing.status = ListingStatus.SOLD
        
        self.transactions[tx_id] = transaction
        return transaction
    
    def market_maker_buy(self, buyer: str, listing_type: str) -> Transaction:
        """Buy from market maker (instant, guaranteed)"""
        price = self.get_market_price(listing_type) * (1 + self.market_maker_spread)
        
        tx_id = hashlib.sha256(f"mm{buyer}{listing_type}{time.time()}".encode()).hexdigest()[:16]
        
        transaction = Transaction(
            id=tx_id,
            buyer=buyer,
            seller="MARKET_MAKER",
            listing_id=listing_type,
            amount=price,
            timestamp=datetime.utcnow().isoformat(),
            verified=True,  # Market maker always delivers
            dispute=False
        )
        
        self.transactions[tx_id] = transaction
        return transaction
    
    def verify_delivery(self, transaction_id: str, quality: float):
        """Verify delivery and release escrow"""
        tx = self.transactions.get(transaction_id)
        if not tx:
            raise ValueError("Transaction not found")
        
        tx.verified = True
        
        if tx_id := tx.id in self.escrow:
            # Release to seller
            amount = self.escrow.pop(tx_id)
            # Transfer (would integrate with economy system)
        
        # Update seller's reputation
        self.update_seller_score(tx.seller, quality)
        
        # Update market price based on actual quality
        self.update_market_price(tx.listing_id, quality)
    
    def update_seller_score(self, seller: str, quality: float):
        """Update seller's quality score based on transaction"""
        # Weighted average: new_quality = (old * n + new) / (n + 1)
        # Would update in trust registry
    
    def update_market_price(self, listing_id: str, actual_quality: float):
        """Adjust market price based on actual quality delivered"""
        listing = self.listings.get(listing_id)
        if listing:
            # If actual > expected, price goes up
            # If actual < expected, price goes down
            quality_ratio = actual_quality / listing.quality_score
            self.prices[listing.type.value] *= (1 + (quality_ratio - 1) * 0.1)
    
    def post_task(self, poster: str, task: dict) -> str:
        """Post a task to the market for bidding"""
        task_id = hashlib.sha256(f"{poster}{task['title']}{time.time()}".encode()).hexdigest()[:16]
        
        self.bids[task_id] = []
        
        return task_id
    
    def bid_on_task(self, agent: str, task_id: str, price: float, 
                    estimated_time: int, pitch: str) -> str:
        """Agent bids on a task"""
        bid_id = hashlib.sha256(f"{agent}{task_id}{time.time()}".encode()).hexdigest()[:16]
        
        bid = {
            "id": bid_id,
            "agent": agent,
            "price": price,
            "estimated_time": estimated_time,
            "pitch": pitch,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.bids[task_id].append(bid)
        return bid_id
    
    def get_best_bid(self, task_id: str) -> Optional[dict]:
        """Get the best bid for a task (by price + time + trust)"""
        bids = self.bids.get(task_id, [])
        if not bids:
            return None
        
        # Rank by: trust (50%) + price (30%) + time (20%)
        ranked = sorted(bids, key=lambda b: (
            -self.get_agent_trust(b["agent"]),  # Higher trust first
            b["price"],  # Lower price first
            b["estimated_time"]  # Faster first
        ))
        
        return ranked[0]
    
    def get_agent_trust(self, agent_id: str) -> float:
        """Get agent trust score (would integrate with trust registry)"""
        return 50.0  # Default
    
    def dispute_transaction(self, transaction_id: str, reason: str):
        """File a dispute for a transaction"""
        tx = self.transactions.get(transaction_id)
        if tx:
            tx.dispute = True
            # Would trigger arbitration process
    
    def get_stats(self) -> dict:
        """Get marketplace statistics"""
        active_listings = sum(1 for l in self.listings.values() 
                             if l.status == ListingStatus.ACTIVE)
        
        total_volume = sum(t.amount for t in self.transactions.values())
        
        return {
            "active_listings": active_listings,
            "total_transactions": len(self.transactions),
            "total_volume": total_volume,
            "market_prices": self.prices,
            "market_maker_enabled": self.market_maker_enabled
        }


# Singleton instance
_marketplace = None

def get_marketplace() -> DistributedMarketplace:
    global _marketplace
    if _marketplace is None:
        _marketplace = DistributedMarketplace()
    return _marketplace