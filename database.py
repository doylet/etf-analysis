"""
Database models for ETF Analysis Dashboard
Supports both SQLite (local) and PostgreSQL (Cloud SQL)
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    is_active = Column(Boolean, default=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String(500))


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
