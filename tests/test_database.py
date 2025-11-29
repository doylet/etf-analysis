"""
Unit tests for database models
"""

import pytest
from src.models import DatabaseManager, Instrument, PriceData
from datetime import datetime


def test_database_initialization():
    """Test database can be initialized"""
    db = DatabaseManager('sqlite:///:memory:')
    assert db.engine is not None
    assert db.SessionLocal is not None


def test_instrument_creation():
    """Test creating an instrument"""
    db = DatabaseManager('sqlite:///:memory:')
    session = db.get_session()
    
    instrument = Instrument(
        symbol='TEST',
        name='Test Stock',
        instrument_type='stock',
        sector='Technology',
        is_active=True
    )
    
    session.add(instrument)
    session.commit()
    
    result = session.query(Instrument).filter_by(symbol='TEST').first()
    assert result is not None
    assert result.name == 'Test Stock'
    
    session.close()


def test_price_data_creation():
    """Test creating price data"""
    db = DatabaseManager('sqlite:///:memory:')
    session = db.get_session()
    
    price = PriceData(
        symbol='TEST',
        date=datetime.utcnow(),
        open_price=100.0,
        high_price=105.0,
        low_price=99.0,
        close_price=103.0,
        volume=1000000
    )
    
    session.add(price)
    session.commit()
    
    result = session.query(PriceData).filter_by(symbol='TEST').first()
    assert result is not None
    assert result.close_price == 103.0
    
    session.close()
