"""
Order repository - manages portfolio transaction orders.

Wraps DataStorageAdapter to provide domain-focused API returning OrderRecord.
"""

from typing import List, Dict
from datetime import datetime

from domain.portfolio import OrderRecord, OrderType
from services.storage_adapter import DataStorageAdapter


class OrderRepository:
    """Repository for managing portfolio orders."""
    
    def __init__(self, storage: DataStorageAdapter):
        """
        Initialize repository with storage adapter.
        
        Args:
            storage: DataStorageAdapter instance for data access
        """
        self.storage = storage
    
    def create(self, order: OrderRecord) -> OrderRecord:
        """
        Create new order.
        
        Args:
            order: OrderRecord to create
            
        Returns:
            Created OrderRecord with any generated fields
        """
        # Convert to dict for storage
        order_dict = {
            'symbol': order.symbol,
            'order_type': order.order_type.value,
            'volume': order.volume,
            'order_date': order.order_date,
            'price': order.price,
            'notes': order.notes
        }
        
        # Add to storage
        self.storage.add_order(order_dict)
        
        return order
    
    def find_by_symbol(self, symbol: str) -> List[OrderRecord]:
        """
        Find all orders for a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            List of OrderRecord instances for the symbol
        """
        orders = self.storage.get_orders(symbol=symbol)
        return [self._to_domain_model(order_dict) for order_dict in orders]
    
    def find_in_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[OrderRecord]:
        """
        Find orders within date range.
        
        Args:
            start: Start date (inclusive)
            end: End date (inclusive)
            
        Returns:
            List of OrderRecord instances in range
        """
        all_orders = self.storage.get_orders()
        
        filtered = []
        for order_dict in all_orders:
            order_date = order_dict.get('order_date')
            if order_date and start <= order_date <= end:
                filtered.append(self._to_domain_model(order_dict))
        
        return filtered
    
    def calculate_holdings_at_date(self, date: datetime) -> Dict[str, float]:
        """
        Calculate holdings quantities at a specific date.
        
        Args:
            date: Date to calculate holdings
            
        Returns:
            Dictionary mapping symbol to quantity
        """
        all_orders = self.storage.get_orders()
        
        holdings = {}
        for order_dict in all_orders:
            order_date = order_dict.get('order_date')
            if order_date and order_date <= date:
                symbol = order_dict['symbol']
                volume = order_dict.get('volume', 0)
                
                if symbol not in holdings:
                    holdings[symbol] = 0.0
                
                holdings[symbol] += volume
        
        # Remove zero or negative holdings
        return {sym: qty for sym, qty in holdings.items() if qty > 0}
    
    def get_all_orders(self) -> List[OrderRecord]:
        """
        Get all orders.
        
        Returns:
            List of all OrderRecord instances
        """
        orders = self.storage.get_orders()
        return [self._to_domain_model(order_dict) for order_dict in orders]
    
    def _to_domain_model(self, order_dict: Dict) -> OrderRecord:
        """
        Convert storage dict to domain model.
        
        Args:
            order_dict: Order dictionary from storage
            
        Returns:
            OrderRecord instance
        """
        # Map type string to enum
        order_type_str = order_dict.get('order_type', 'buy').lower()
        try:
            order_type = OrderType(order_type_str)
        except ValueError:
            order_type = OrderType.BUY  # Default
        
        return OrderRecord(
            symbol=order_dict['symbol'],
            order_type=order_type,
            volume=float(order_dict.get('volume', 0)),
            order_date=order_dict.get('order_date', datetime.now()),
            price=float(order_dict['price']) if order_dict.get('price') else None,
            notes=order_dict.get('notes')
        )
