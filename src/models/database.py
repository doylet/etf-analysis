"""
Database models for ETF Analysis Dashboard
Supports both SQLite (local) and PostgreSQL (Cloud SQL)
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class Instrument(Base):
    """Model for tracked stocks/ETFs"""
    __tablename__ = 'instruments'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200))
    instrument_type = Column(String(20))  # 'stock', 'etf', 'index'
    sector = Column(String(100))
    currency = Column(String(3), default='USD')  # ISO currency code: USD, AUD, etc.
    is_active = Column(Boolean, default=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String(500))
    
    # Relationship to orders
    orders = relationship("Order", back_populates="instrument", cascade="all, delete-orphan")


class Order(Base):
    """Model for buy/sell orders"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)  # Denormalized for easier queries
    order_type = Column(String(10), nullable=False)  # 'Buy' or 'Sell'
    volume = Column(Float, nullable=False)  # Quantity traded (always positive)
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    notes = Column(String(500))
    is_active = Column(Integer, default=1)  # Soft delete flag: 1=active, 0=deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to instrument
    instrument = relationship("Instrument", back_populates="orders")


class PriceData(Base):
    """Model for historical price data"""
    __tablename__ = 'price_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    adj_close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint on symbol + date
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class Dividend(Base):
    """Model for dividend payments"""
    __tablename__ = 'dividends'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    ex_date = Column(DateTime, nullable=False, index=True)  # Ex-dividend date
    payment_date = Column(DateTime)  # Actual payment date
    amount = Column(Float, nullable=False)  # Dividend amount per share
    dividend_type = Column(String(20))  # 'cash', 'stock', 'special'
    currency = Column(String(10), default='USD')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class DividendCashFlow(Base):
    """Model for actual dividend cash flows received"""
    __tablename__ = 'dividend_cash_flows'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    payment_date = Column(DateTime, nullable=False, index=True)
    shares_held = Column(Float, nullable=False)  # Number of shares held on ex-date
    dividend_per_share = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # shares_held * dividend_per_share
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class AppSetting(Base):
    """Model for application settings and user preferences"""
    __tablename__ = 'app_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(String(5000))  # JSON blob or simple string value
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class FXRate(Base):
    """Model for foreign exchange rates (daily close prices)"""
    __tablename__ = 'fx_rates'
    
    id = Column(Integer, primary_key=True)
    currency_pair = Column(String(7), nullable=False, index=True)  # e.g., 'AUDUSD'
    date = Column(DateTime, nullable=False, index=True)
    rate = Column(Float, nullable=False)  # Exchange rate
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/etf_analysis.db')
        
        # Create data directory for SQLite if needed
        if database_url.startswith('sqlite'):
            os.makedirs('data', exist_ok=True)
        
        self.engine = create_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False} if database_url.startswith('sqlite') else {}
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
