"""
Instrument repository - manages financial instruments in the portfolio.

Wraps DataStorageAdapter to provide domain-focused API returning InstrumentDomainModel.
"""

from typing import List, Optional, Dict
from datetime import datetime

from domain.portfolio import InstrumentDomainModel, InstrumentType
from services.storage_adapter import DataStorageAdapter


class InstrumentRepository:
    """Repository for managing financial instruments."""
    
    def __init__(self, storage: DataStorageAdapter):
        """
        Initialize repository with storage adapter.
        
        Args:
            storage: DataStorageAdapter instance for data access
        """
        self.storage = storage
    
    def find_by_symbol(self, symbol: str) -> Optional[InstrumentDomainModel]:
        """
        Find instrument by symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            InstrumentDomainModel if found, None otherwise
        """
        instruments = self.storage.get_all_instruments(active_only=False)
        
        for inst_dict in instruments:
            if inst_dict['symbol'].upper() == symbol.upper():
                return self._to_domain_model(inst_dict)
        
        return None
    
    def find_all_active(self) -> List[InstrumentDomainModel]:
        """
        Get all active instruments.
        
        Returns:
            List of active InstrumentDomainModel instances
        """
        instruments = self.storage.get_all_instruments(active_only=True)
        return [self._to_domain_model(inst) for inst in instruments]
    
    def search(self, query: str) -> List[InstrumentDomainModel]:
        """
        Search instruments by symbol or name.
        
        Args:
            query: Search string (case-insensitive)
            
        Returns:
            List of matching InstrumentDomainModel instances
        """
        instruments = self.storage.get_all_instruments(active_only=True)
        query_lower = query.lower()
        
        matches = []
        for inst_dict in instruments:
            if (query_lower in inst_dict['symbol'].lower() or 
                query_lower in inst_dict.get('name', '').lower()):
                matches.append(self._to_domain_model(inst_dict))
        
        return matches
    
    def add(self, instrument: InstrumentDomainModel) -> InstrumentDomainModel:
        """
        Add new instrument.
        
        Args:
            instrument: InstrumentDomainModel to add
            
        Returns:
            Created InstrumentDomainModel
            
        Raises:
            ValueError: If instrument already exists
        """
        # Check if already exists
        existing = self.find_by_symbol(instrument.symbol)
        if existing:
            raise ValueError(f"Instrument {instrument.symbol} already exists")
        
        # Convert to dict for storage
        inst_dict = {
            'symbol': instrument.symbol,
            'name': instrument.name,
            'type': instrument.instrument_type.value,
            'sector': instrument.sector,
            'currency': instrument.currency,
            'active': True
        }
        
        # Add to storage
        self.storage.add_instrument(inst_dict)
        
        return instrument
    
    def update(self, symbol: str, updates: Dict) -> InstrumentDomainModel:
        """
        Update instrument details.
        
        Args:
            symbol: Symbol of instrument to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated InstrumentDomainModel
            
        Raises:
            ValueError: If instrument not found
        """
        existing = self.find_by_symbol(symbol)
        if not existing:
            raise ValueError(f"Instrument {symbol} not found")
        
        # Update storage
        self.storage.update_instrument(symbol, updates)
        
        # Fetch updated version
        updated = self.find_by_symbol(symbol)
        if not updated:
            raise ValueError(f"Failed to retrieve updated instrument {symbol}")
        
        return updated
    
    def remove(self, symbol: str) -> bool:
        """
        Remove (deactivate) instrument.
        
        Args:
            symbol: Symbol of instrument to remove
            
        Returns:
            True if removed, False if not found
        """
        existing = self.find_by_symbol(symbol)
        if not existing:
            return False
        
        # Mark as inactive
        self.storage.update_instrument(symbol, {'active': False})
        return True
    
    def _to_domain_model(self, inst_dict: Dict) -> InstrumentDomainModel:
        """
        Convert storage dict to domain model.
        
        Args:
            inst_dict: Instrument dictionary from storage
            
        Returns:
            InstrumentDomainModel instance
        """
        # Map type string to enum
        inst_type_str = inst_dict.get('type', 'other').lower()
        try:
            inst_type = InstrumentType(inst_type_str)
        except ValueError:
            inst_type = InstrumentType.OTHER
        
        # Get current holdings to calculate quantity and value
        orders = self.storage.get_orders(symbol=inst_dict['symbol'])
        quantity = sum(order.get('volume', 0) for order in orders)
        
        # Get latest price
        price_data = self.storage.get_price_data(
            inst_dict['symbol'],
            start_date=datetime.now().replace(day=1),  # This month
            end_date=datetime.now()
        )
        
        current_price = 0.0
        if not price_data.empty and 'close' in price_data.columns:
            current_price = float(price_data['close'].iloc[-1])
        
        current_value = quantity * current_price
        
        return InstrumentDomainModel(
            symbol=inst_dict['symbol'],
            name=inst_dict.get('name', inst_dict['symbol']),
            instrument_type=inst_type,
            sector=inst_dict.get('sector'),
            currency=inst_dict.get('currency', 'USD'),
            quantity=float(quantity),
            current_value_local=current_value,
            current_value_base=current_value,  # Assume same currency for now
            weight_pct=0.0  # Will be calculated at portfolio level
        )
