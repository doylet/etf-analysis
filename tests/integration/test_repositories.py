"""
Integration tests for repository layer with real SQLite database.

Tests T040-T042: InstrumentRepository, OrderRepository, PriceDataRepository
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import sqlite3

from src.repositories.instrument_repository import InstrumentRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.price_data_repository import PriceDataRepository
from src.services.storage_adapter import DataStorageAdapter
from src.domain.portfolio import InstrumentType, OrderType


@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    db_path = temp_file.name
    temp_file.close()
    
    # Create tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Instruments table
    cursor.execute("""
        CREATE TABLE instruments (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            sector TEXT,
            currency TEXT DEFAULT 'USD',
            active INTEGER DEFAULT 1
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            order_type TEXT NOT NULL,
            volume REAL NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            notes TEXT,
            deleted INTEGER DEFAULT 0
        )
    """)
    
    # Price data table
    cursor.execute("""
        CREATE TABLE price_data (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            PRIMARY KEY (symbol, date)
        )
    """)
    
    # Dividends table
    cursor.execute("""
        CREATE TABLE dividends (
            symbol TEXT NOT NULL,
            ex_date TEXT NOT NULL,
            amount REAL NOT NULL,
            PRIMARY KEY (symbol, ex_date)
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def storage_adapter(temp_db):
    """Create storage adapter with test database."""
    return DataStorageAdapter(db_path=temp_db)


@pytest.fixture
def instrument_repo(storage_adapter):
    """Create InstrumentRepository."""
    return InstrumentRepository(storage_adapter)


@pytest.fixture
def order_repo(storage_adapter):
    """Create OrderRepository."""
    return OrderRepository(storage_adapter)


@pytest.fixture
def price_repo(storage_adapter):
    """Create PriceDataRepository."""
    return PriceDataRepository(storage_adapter)


@pytest.fixture
def sample_instruments(storage_adapter):
    """Add sample instruments to database."""
    instruments = [
        {
            'symbol': 'VTI',
            'name': 'Vanguard Total Stock Market ETF',
            'type': 'ETF',
            'sector': 'Equity',
            'currency': 'USD',
            'active': True
        },
        {
            'symbol': 'BND',
            'name': 'Vanguard Total Bond Market ETF',
            'type': 'ETF',
            'sector': 'Fixed Income',
            'currency': 'USD',
            'active': True
        },
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'type': 'STOCK',
            'sector': 'Technology',
            'currency': 'USD',
            'active': True
        }
    ]
    
    for inst in instruments:
        storage_adapter.add_instrument(inst)
    
    return instruments


@pytest.fixture
def sample_orders(storage_adapter):
    """Add sample orders to database."""
    orders = [
        {
            'symbol': 'VTI',
            'order_type': 'BUY',
            'volume': 100,
            'date': '2023-01-15',
            'price': 200.0,
            'notes': 'Initial purchase'
        },
        {
            'symbol': 'VTI',
            'order_type': 'BUY',
            'volume': 50,
            'date': '2023-06-01',
            'price': 210.0,
            'notes': 'Additional shares'
        },
        {
            'symbol': 'BND',
            'order_type': 'BUY',
            'volume': 200,
            'date': '2023-01-15',
            'price': 75.0,
            'notes': 'Bond allocation'
        },
        {
            'symbol': 'AAPL',
            'order_type': 'BUY',
            'volume': 25,
            'date': '2023-03-01',
            'price': 150.0,
            'notes': 'Tech position'
        }
    ]
    
    for order in orders:
        storage_adapter.add_order(order)
    
    return orders


@pytest.fixture
def sample_price_data(storage_adapter):
    """Add sample price data to database."""
    # Generate 30 days of price data for VTI
    base_date = datetime(2023, 1, 1)
    prices = []
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        prices.append({
            'symbol': 'VTI',
            'date': date.strftime('%Y-%m-%d'),
            'open': 200.0 + i * 0.5,
            'high': 205.0 + i * 0.5,
            'low': 198.0 + i * 0.5,
            'close': 202.0 + i * 0.5,
            'volume': 1000000 + i * 10000
        })
    
    # Store price data
    conn = sqlite3.connect(storage_adapter.db_path)
    cursor = conn.cursor()
    for price in prices:
        cursor.execute("""
            INSERT INTO price_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            price['symbol'],
            price['date'],
            price['open'],
            price['high'],
            price['low'],
            price['close'],
            price['volume']
        ))
    conn.commit()
    conn.close()
    
    return prices


# T040: InstrumentRepository Integration Tests

class TestInstrumentRepository:
    """Integration tests for InstrumentRepository."""
    
    def test_find_by_symbol(self, instrument_repo, sample_instruments):
        """Test finding instrument by symbol."""
        instrument = instrument_repo.find_by_symbol('VTI')
        
        assert instrument is not None
        assert instrument.symbol == 'VTI'
        assert instrument.name == 'Vanguard Total Stock Market ETF'
        assert instrument.type == InstrumentType.ETF
        assert instrument.sector == 'Equity'
        assert instrument.currency == 'USD'
    
    def test_find_by_symbol_not_found(self, instrument_repo):
        """Test finding non-existent instrument."""
        instrument = instrument_repo.find_by_symbol('NOTFOUND')
        assert instrument is None
    
    def test_find_all_active(self, instrument_repo, sample_instruments):
        """Test finding all active instruments."""
        instruments = instrument_repo.find_all_active()
        
        assert len(instruments) == 3
        symbols = [inst.symbol for inst in instruments]
        assert 'VTI' in symbols
        assert 'BND' in symbols
        assert 'AAPL' in symbols
    
    def test_search(self, instrument_repo, sample_instruments):
        """Test search functionality."""
        # Search by name
        results = instrument_repo.search('Vanguard')
        assert len(results) == 2
        
        # Search by symbol
        results = instrument_repo.search('VTI')
        assert len(results) == 1
        assert results[0].symbol == 'VTI'
        
        # Case insensitive
        results = instrument_repo.search('apple')
        assert len(results) == 1
        assert results[0].symbol == 'AAPL'
    
    def test_add_instrument(self, instrument_repo):
        """Test adding new instrument."""
        from src.domain.portfolio import InstrumentDomainModel
        
        new_inst = InstrumentDomainModel(
            symbol='GOOGL',
            name='Alphabet Inc.',
            type=InstrumentType.STOCK,
            sector='Technology',
            currency='USD',
            quantity=0,
            current_value=0,
            average_cost=0
        )
        
        result = instrument_repo.add(new_inst)
        assert result.symbol == 'GOOGL'
        
        # Verify it was added
        found = instrument_repo.find_by_symbol('GOOGL')
        assert found is not None
        assert found.name == 'Alphabet Inc.'
    
    def test_add_duplicate_instrument(self, instrument_repo, sample_instruments):
        """Test adding duplicate instrument raises error."""
        from src.domain.portfolio import InstrumentDomainModel
        
        dup = InstrumentDomainModel(
            symbol='VTI',
            name='Duplicate',
            type=InstrumentType.ETF,
            sector='Test',
            currency='USD',
            quantity=0,
            current_value=0,
            average_cost=0
        )
        
        with pytest.raises(ValueError, match="already exists"):
            instrument_repo.add(dup)
    
    def test_update_instrument(self, instrument_repo, sample_instruments):
        """Test updating instrument."""
        updates = {'sector': 'Updated Sector', 'name': 'Updated Name'}
        result = instrument_repo.update('VTI', updates)
        
        assert result.sector == 'Updated Sector'
        assert result.name == 'Updated Name'
        assert result.symbol == 'VTI'  # Symbol unchanged
    
    def test_remove_instrument(self, instrument_repo, sample_instruments):
        """Test removing (deactivating) instrument."""
        success = instrument_repo.remove('AAPL')
        assert success is True
        
        # Should not appear in active instruments
        active = instrument_repo.find_all_active()
        symbols = [inst.symbol for inst in active]
        assert 'AAPL' not in symbols


# T041: OrderRepository Integration Tests

class TestOrderRepository:
    """Integration tests for OrderRepository."""
    
    def test_create_order(self, order_repo):
        """Test creating new order."""
        from src.domain.portfolio import OrderRecord
        
        order = OrderRecord(
            symbol='TEST',
            order_type=OrderType.BUY,
            volume=100,
            date=datetime(2023, 1, 1),
            price=50.0,
            notes='Test order'
        )
        
        result = order_repo.create(order)
        assert result.symbol == 'TEST'
        assert result.order_type == OrderType.BUY
        assert result.volume == 100
    
    def test_find_by_symbol(self, order_repo, sample_orders):
        """Test finding orders by symbol."""
        orders = order_repo.find_by_symbol('VTI')
        
        assert len(orders) == 2
        assert all(o.symbol == 'VTI' for o in orders)
        
        # Check order types
        types = [o.order_type for o in orders]
        assert OrderType.BUY in types
    
    def test_find_in_date_range(self, order_repo, sample_orders):
        """Test finding orders in date range."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 3, 31)
        
        orders = order_repo.find_in_date_range(start, end)
        
        assert len(orders) >= 3  # VTI Jan, BND Jan, AAPL Mar
        
        # Verify all dates in range
        for order in orders:
            assert start <= order.date <= end
    
    def test_calculate_holdings_at_date(self, order_repo, sample_orders):
        """Test calculating holdings at specific date."""
        # After all purchases
        holdings = order_repo.calculate_holdings_at_date(datetime(2023, 12, 31))
        
        assert holdings['VTI'] == 150  # 100 + 50
        assert holdings['BND'] == 200
        assert holdings['AAPL'] == 25
    
    def test_calculate_holdings_partial_date(self, order_repo, sample_orders):
        """Test holdings calculation at intermediate date."""
        # After Jan 15 but before Jun 1
        holdings = order_repo.calculate_holdings_at_date(datetime(2023, 2, 1))
        
        assert holdings['VTI'] == 100  # Only first purchase
        assert holdings['BND'] == 200
        assert 'AAPL' not in holdings  # Not purchased yet
    
    def test_get_all_orders(self, order_repo, sample_orders):
        """Test getting all orders."""
        all_orders = order_repo.get_all_orders()
        
        assert len(all_orders) == 4
        
        # Check order attributes
        symbols = [o.symbol for o in all_orders]
        assert 'VTI' in symbols
        assert 'BND' in symbols
        assert 'AAPL' in symbols


# T042: PriceDataRepository Integration Tests

class TestPriceDataRepository:
    """Integration tests for PriceDataRepository."""
    
    def test_get_price_history(self, price_repo, sample_price_data):
        """Test getting price history."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 15)
        
        history = price_repo.get_price_history('VTI', start, end)
        
        assert history.symbol == 'VTI'
        assert history.start_date == start
        assert history.end_date == end
        assert 'close' in history.prices
        assert 'volume' in history.prices
        assert len(history.prices['close']) > 0
    
    def test_get_price_history_no_data(self, price_repo):
        """Test getting price history with no data."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 31)
        
        with pytest.raises(ValueError, match="No price data available"):
            price_repo.get_price_history('NOTFOUND', start, end)
    
    def test_get_latest_prices(self, price_repo, sample_price_data):
        """Test getting latest prices for multiple symbols."""
        prices = price_repo.get_latest_prices(['VTI'])
        
        assert 'VTI' in prices
        assert prices['VTI'] > 0
        
        # Latest price should be from most recent date
        assert prices['VTI'] > 200  # Base was 202 + growth
    
    def test_get_latest_prices_multiple_symbols(self, price_repo, sample_price_data):
        """Test getting latest prices for symbols without data."""
        prices = price_repo.get_latest_prices(['VTI', 'NOTFOUND'])
        
        assert 'VTI' in prices
        assert 'NOTFOUND' in prices
        assert prices['VTI'] > 0
        assert prices['NOTFOUND'] == 0.0  # No data returns 0
    
    def test_get_returns(self, price_repo, sample_price_data):
        """Test calculating returns."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 30)
        
        returns = price_repo.get_returns('VTI', start, end)
        
        assert isinstance(returns, pd.Series)
        assert len(returns) > 0
        
        # Returns should be calculated (pct_change)
        # First return should be NaN (no prior data)
        assert pd.isna(returns.iloc[0])
    
    def test_get_returns_no_data(self, price_repo):
        """Test returns calculation with no data."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 31)
        
        with pytest.raises(ValueError, match="No price data available"):
            price_repo.get_returns('NOTFOUND', start, end)


# Integration test for combined repository operations

class TestRepositoriesIntegration:
    """Test repositories working together."""
    
    def test_full_portfolio_workflow(
        self,
        instrument_repo,
        order_repo,
        price_repo,
        sample_instruments,
        sample_orders,
        sample_price_data
    ):
        """Test complete workflow using all repositories."""
        # 1. Get active instruments
        instruments = instrument_repo.find_all_active()
        assert len(instruments) == 3
        
        # 2. Get holdings for a date
        holdings = order_repo.calculate_holdings_at_date(datetime(2023, 12, 31))
        assert len(holdings) == 3
        
        # 3. Get latest prices
        symbols = list(holdings.keys())
        prices = price_repo.get_latest_prices(symbols)
        
        # 4. Calculate portfolio value
        total_value = sum(holdings[sym] * prices.get(sym, 0) for sym in symbols)
        assert total_value > 0
