"""
Data fetching and persistence utilities
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import and_
from database import DatabaseManager, Instrument, PriceData


class DataFetcher:
    """Fetch and store financial data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_instrument(self, symbol: str, instrument_type: str = 'stock', 
                       sector: str = None, notes: str = None):
        """Add a new instrument to track"""
        session = self.db.get_session()
        try:
            # Check if already exists
            existing = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
            if existing:
                return {'success': False, 'message': f'{symbol} already exists'}
            
            # Fetch basic info from yfinance
            ticker = yf.Ticker(symbol)
            try:
                info = ticker.info
                name = info.get('longName', info.get('shortName', symbol))
                if sector is None:
                    sector = info.get('sector', 'Unknown')
            except:
                name = symbol
                sector = sector or 'Unknown'
            
            # Create new instrument
            instrument = Instrument(
                symbol=symbol.upper(),
                name=name,
                instrument_type=instrument_type,
                sector=sector,
                notes=notes,
                is_active=True
            )
            session.add(instrument)
            session.commit()
            
            return {'success': True, 'message': f'Added {symbol}', 'instrument': instrument}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def remove_instrument(self, symbol: str):
        """Deactivate an instrument (soft delete)"""
        session = self.db.get_session()
        try:
            instrument = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
            if not instrument:
                return {'success': False, 'message': f'{symbol} not found'}
            
            instrument.is_active = False
            session.commit()
            return {'success': True, 'message': f'Removed {symbol}'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_all_instruments(self, active_only=True):
        """Get all tracked instruments"""
        session = self.db.get_session()
        try:
            query = session.query(Instrument)
            if active_only:
                query = query.filter_by(is_active=True)
            instruments = query.all()
            return [
                {
                    'symbol': i.symbol,
                    'name': i.name,
                    'type': i.instrument_type,
                    'sector': i.sector,
                    'added_date': i.added_date,
                    'notes': i.notes
                }
                for i in instruments
            ]
        finally:
            session.close()
    
    def search_instruments(self, search_term: str):
        """Search instruments by symbol or name"""
        session = self.db.get_session()
        try:
            search = f"%{search_term.upper()}%"
            instruments = session.query(Instrument).filter(
                and_(
                    Instrument.is_active == True,
                    (Instrument.symbol.like(search) | Instrument.name.like(search))
                )
            ).all()
            return [
                {
                    'symbol': i.symbol,
                    'name': i.name,
                    'type': i.instrument_type,
                    'sector': i.sector
                }
                for i in instruments
            ]
        finally:
            session.close()
    
    def fetch_and_store_prices(self, symbol: str, period: str = '1y', force_refresh: bool = False):
        """Fetch historical prices and store in database"""
        session = self.db.get_session()
        try:
            # Check if instrument exists
            instrument = session.query(Instrument).filter_by(
                symbol=symbol.upper(), is_active=True
            ).first()
            if not instrument:
                return {'success': False, 'message': f'{symbol} not found in tracked instruments'}
            
            # Check if we need to fetch data
            if not force_refresh:
                latest = session.query(PriceData).filter_by(
                    symbol=symbol.upper()
                ).order_by(PriceData.date.desc()).first()
                
                if latest and (datetime.utcnow() - latest.date).days < 1:
                    return {'success': True, 'message': 'Data is up to date', 'cached': True}
            
            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {'success': False, 'message': f'No data available for {symbol}'}
            
            # Store in database
            records_added = 0
            for date, row in df.iterrows():
                # Check if record exists
                existing = session.query(PriceData).filter(
                    and_(
                        PriceData.symbol == symbol.upper(),
                        PriceData.date == date.to_pydatetime()
                    )
                ).first()
                
                if not existing:
                    price_record = PriceData(
                        symbol=symbol.upper(),
                        date=date.to_pydatetime(),
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=float(row['Volume'])
                    )
                    session.add(price_record)
                    records_added += 1
            
            # Update instrument last_updated
            instrument.last_updated = datetime.utcnow()
            session.commit()
            
            return {
                'success': True,
                'message': f'Fetched data for {symbol}',
                'records_added': records_added,
                'cached': False
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_price_data(self, symbol: str, start_date=None, end_date=None):
        """Retrieve price data from database"""
        session = self.db.get_session()
        try:
            query = session.query(PriceData).filter_by(symbol=symbol.upper())
            
            if start_date:
                query = query.filter(PriceData.date >= start_date)
            if end_date:
                query = query.filter(PriceData.date <= end_date)
            
            query = query.order_by(PriceData.date)
            
            prices = query.all()
            
            if not prices:
                return pd.DataFrame()
            
            df = pd.DataFrame([
                {
                    'date': p.date,
                    'open': p.open_price,
                    'high': p.high_price,
                    'low': p.low_price,
                    'close': p.close_price,
                    'volume': p.volume
                }
                for p in prices
            ])
            df.set_index('date', inplace=True)
            return df
        finally:
            session.close()
    
    def get_latest_prices(self, symbols: list):
        """Get latest close prices for multiple symbols"""
        session = self.db.get_session()
        try:
            results = {}
            for symbol in symbols:
                latest = session.query(PriceData).filter_by(
                    symbol=symbol.upper()
                ).order_by(PriceData.date.desc()).first()
                
                if latest:
                    results[symbol] = {
                        'close': latest.close_price,
                        'date': latest.date
                    }
            return results
        finally:
            session.close()
