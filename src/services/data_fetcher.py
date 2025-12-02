"""
Data fetching and persistence utilities
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from src.models.database import DatabaseManager, Instrument, PriceData, Order, Dividend, DividendCashFlow, AppSetting, FXRate


class DataFetcher:
    """Fetch and store financial data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_instrument(self, symbol: str, name: str = None, instrument_type: str = 'stock', 
                       sector: str = None, notes: str = None, is_active: bool = True, currency: str = 'USD'):
        """Add a new instrument to track"""
        session = self.db.get_session()
        try:
            # Check if already exists
            existing = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
            if existing:
                if existing.is_active:
                    return {'success': False, 'message': f'{symbol} already exists'}
                else:
                    # Update existing inactive instrument
                    existing.is_active = is_active
                    if name:
                        existing.name = name
                    existing.instrument_type = instrument_type
                    if sector:
                        existing.sector = sector
                    if notes:
                        existing.notes = notes
                    existing.last_updated = datetime.utcnow()
                    session.commit()
                    return {'success': True, 'message': f'Updated {symbol}', 'instrument': existing}
            
            # Fetch basic info from yfinance if name not provided
            if not name:
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
    
    def create_order(self, symbol: str, order_type: str, volume: float, 
                     order_date: datetime = None, notes: str = None):
        """Create a buy/sell order"""
        session = self.db.get_session()
        try:
            instrument = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
            if not instrument:
                return {'success': False, 'message': f'{symbol} not found'}
            
            if order_type not in ['Buy', 'Sell']:
                return {'success': False, 'message': 'Order type must be Buy or Sell'}
            
            if volume <= 0:
                return {'success': False, 'message': 'Volume must be positive'}
            
            # Check for duplicate order created in last 5 seconds
            recent_cutoff = datetime.utcnow() - timedelta(seconds=5)
            duplicate = session.query(Order).filter(
                and_(
                    Order.symbol == symbol.upper(),
                    Order.order_type == order_type,
                    Order.volume == volume,
                    Order.created_at >= recent_cutoff
                )
            ).first()
            
            if duplicate:
                return {'success': False, 'message': 'Duplicate order detected - order already created'}
            
            order = Order(
                instrument_id=instrument.id,
                symbol=symbol.upper(),
                order_type=order_type,
                volume=volume,
                order_date=order_date or datetime.utcnow(),
                notes=notes
            )
            session.add(order)
            session.commit()
            return {'success': True, 'message': f'Created {order_type} order for {volume} units of {symbol}'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_net_quantity(self, symbol: str):
        """Calculate net quantity from all orders (Buys - Sells)"""
        session = self.db.get_session()
        try:
            # Sum all Buy orders
            buys = session.query(func.sum(Order.volume)).filter(
                and_(Order.symbol == symbol.upper(), Order.order_type == 'Buy', Order.is_active == 1)
            ).scalar() or 0.0
            
            # Sum all Sell orders
            sells = session.query(func.sum(Order.volume)).filter(
                and_(Order.symbol == symbol.upper(), Order.order_type == 'Sell', Order.is_active == 1)
            ).scalar() or 0.0
            
            return buys - sells
        finally:
            session.close()
    
    def get_orders(self, symbol: str = None, include_deleted: bool = False):
        """Get orders for a symbol or all orders"""
        session = self.db.get_session()
        try:
            query = session.query(Order)
            if not include_deleted:
                query = query.filter_by(is_active=1)
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            
            orders = query.order_by(Order.order_date.desc()).all()
            return [
                {
                    'id': o.id,
                    'symbol': o.symbol,
                    'order_type': o.order_type,
                    'volume': o.volume,
                    'order_date': o.order_date,
                    'notes': o.notes,
                    'is_active': o.is_active,
                    'created_at': o.created_at
                }
                for o in orders
            ]
        finally:
            session.close()
    
    def get_all_instruments(self, active_only=True):
        """Get all tracked instruments with calculated quantities from orders"""
        session = self.db.get_session()
        try:
            query = session.query(Instrument)
            if active_only:
                query = query.filter_by(is_active=True)
            instruments = query.all()
            
            result = []
            for i in instruments:
                # Calculate net quantity from orders
                quantity = self.get_net_quantity(i.symbol)
                result.append({
                    'symbol': i.symbol,
                    'name': i.name,
                    'type': i.instrument_type,
                    'sector': i.sector,
                    'currency': getattr(i, 'currency', 'USD'),
                    'quantity': quantity,
                    'added_date': i.added_date,
                    'last_updated': i.last_updated,
                    'notes': i.notes
                })
            return result
        finally:
            session.close()
    
    def get_instrument(self, symbol):
        """Get a single instrument by symbol"""
        session = self.db.get_session()
        try:
            instrument = session.query(Instrument).filter_by(symbol=symbol.upper()).first()
            if instrument:
                quantity = self.get_net_quantity(instrument.symbol)
                return {
                    'symbol': instrument.symbol,
                    'name': instrument.name,
                    'type': instrument.instrument_type,
                    'sector': instrument.sector,
                    'currency': getattr(instrument, 'currency', 'USD'),
                    'quantity': quantity,
                    'added_date': instrument.added_date,
                    'last_updated': instrument.last_updated,
                    'notes': instrument.notes
                }
            return None
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
    
    def fetch_and_store_dividends(self, symbol: str, period: str = 'max'):
        """Fetch dividend history from yfinance and store in database"""
        session = self.db.get_session()
        try:
            ticker = yf.Ticker(symbol.upper())
            
            # Get dividend history
            dividends = ticker.dividends
            
            if dividends.empty:
                return {'success': True, 'message': f'No dividends found for {symbol}', 'records_added': 0}
            
            records_added = 0
            
            for date, amount in dividends.items():
                # Check if dividend already exists
                existing = session.query(Dividend).filter(
                    and_(
                        Dividend.symbol == symbol.upper(),
                        Dividend.ex_date == date
                    )
                ).first()
                
                if not existing:
                    dividend = Dividend(
                        symbol=symbol.upper(),
                        ex_date=date,
                        amount=float(amount),
                        dividend_type='cash',
                        currency='USD'
                    )
                    session.add(dividend)
                    records_added += 1
            
            session.commit()
            return {
                'success': True,
                'message': f'Fetched {records_added} dividend records for {symbol}',
                'records_added': records_added
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e), 'records_added': 0}
        finally:
            session.close()
    
    def get_dividends(self, symbol: str = None, start_date: datetime = None, end_date: datetime = None):
        """Get dividend history for a symbol or all symbols"""
        session = self.db.get_session()
        try:
            query = session.query(Dividend)
            
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            
            if start_date:
                query = query.filter(Dividend.ex_date >= start_date)
            
            if end_date:
                query = query.filter(Dividend.ex_date <= end_date)
            
            query = query.order_by(Dividend.ex_date.desc())
            
            dividends = query.all()
            
            return [
                {
                    'id': d.id,
                    'symbol': d.symbol,
                    'ex_date': d.ex_date,
                    'payment_date': d.payment_date,
                    'amount': d.amount,
                    'dividend_type': d.dividend_type,
                    'currency': d.currency
                }
                for d in dividends
            ]
        finally:
            session.close()
    
    def record_dividend_cash_flow(self, symbol: str, payment_date: datetime, 
                                  shares_held: float, dividend_per_share: float, notes: str = None):
        """Record actual dividend cash flow received"""
        session = self.db.get_session()
        try:
            total_amount = shares_held * dividend_per_share
            
            cash_flow = DividendCashFlow(
                symbol=symbol.upper(),
                payment_date=payment_date,
                shares_held=shares_held,
                dividend_per_share=dividend_per_share,
                total_amount=total_amount,
                notes=notes
            )
            
            session.add(cash_flow)
            session.commit()
            
            return {
                'success': True,
                'message': f'Recorded dividend cash flow: ${total_amount:.2f}',
                'amount': total_amount
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_dividend_cash_flows(self, symbol: str = None, start_date: datetime = None, end_date: datetime = None):
        """Get dividend cash flow history"""
        session = self.db.get_session()
        try:
            query = session.query(DividendCashFlow)
            
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            
            if start_date:
                query = query.filter(DividendCashFlow.payment_date >= start_date)
            
            if end_date:
                query = query.filter(DividendCashFlow.payment_date <= end_date)
            
            query = query.order_by(DividendCashFlow.payment_date.desc())
            
            cash_flows = query.all()
            
            return [
                {
                    'id': cf.id,
                    'symbol': cf.symbol,
                    'payment_date': cf.payment_date,
                    'shares_held': cf.shares_held,
                    'dividend_per_share': cf.dividend_per_share,
                    'total_amount': cf.total_amount,
                    'notes': cf.notes
                }
                for cf in cash_flows
            ]
        finally:
            session.close()
    
    def calculate_total_dividends_received(self, symbol: str = None, start_date: datetime = None, end_date: datetime = None):
        """Calculate total dividends received for a symbol or portfolio"""
        session = self.db.get_session()
        try:
            query = session.query(func.sum(DividendCashFlow.total_amount))
            
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            
            if start_date:
                query = query.filter(DividendCashFlow.payment_date >= start_date)
            
            if end_date:
                query = query.filter(DividendCashFlow.payment_date <= end_date)
            
            total = query.scalar() or 0.0
            
            return total
        finally:
            session.close()
    
    def calculate_dividends_from_holdings(self, symbol: str):
        """
        Automatically calculate dividends received based on holdings history
        
        For each dividend ex-date, determine how many shares were held and calculate payout.
        This looks at order history to determine position size at each ex-date.
        """
        session = self.db.get_session()
        try:
            # Get all dividends for symbol
            dividends = session.query(Dividend).filter_by(
                symbol=symbol.upper()
            ).order_by(Dividend.ex_date).all()
            
            if not dividends:
                return []
            
            # Get all orders for symbol
            orders = session.query(Order).filter(
                and_(Order.symbol == symbol.upper(), Order.is_active == 1)
            ).order_by(Order.order_date).all()
            
            results = []
            
            for dividend in dividends:
                ex_date = dividend.ex_date
                
                # Calculate shares held at ex-date
                shares_held = 0.0
                for order in orders:
                    if order.order_date <= ex_date:
                        if order.order_type == 'Buy':
                            shares_held += order.volume
                        elif order.order_type == 'Sell':
                            shares_held -= order.volume
                
                # Only record if shares were held
                if shares_held > 0:
                    total_amount = shares_held * dividend.amount
                    results.append({
                        'symbol': symbol.upper(),
                        'ex_date': ex_date,
                        'payment_date': dividend.payment_date,
                        'shares_held': shares_held,
                        'dividend_per_share': dividend.amount,
                        'total_amount': total_amount
                    })
            
            return results
        
        finally:
            session.close()
    
    def auto_populate_dividend_cash_flows(self, symbol: str = None):
        """
        Automatically populate dividend_cash_flows table based on holdings and dividend history
        
        Args:
            symbol: Specific symbol to process, or None for all holdings
        
        Returns:
            Dict with success status and number of records created
        """
        session = self.db.get_session()
        try:
            # Determine which symbols to process
            if symbol:
                symbols = [symbol.upper()]
            else:
                # Get all symbols with active positions
                holdings = session.query(Order.symbol).distinct().all()
                symbols = [h[0] for h in holdings]
            
            total_created = 0
            
            for sym in symbols:
                # Calculate dividends from holdings
                calculated_divs = self.calculate_dividends_from_holdings(sym)
                
                for div_data in calculated_divs:
                    # Check if already exists
                    existing = session.query(DividendCashFlow).filter(
                        and_(
                            DividendCashFlow.symbol == div_data['symbol'],
                            DividendCashFlow.payment_date == div_data['ex_date']
                        )
                    ).first()
                    
                    if not existing:
                        cash_flow = DividendCashFlow(
                            symbol=div_data['symbol'],
                            payment_date=div_data['payment_date'] or div_data['ex_date'],
                            shares_held=div_data['shares_held'],
                            dividend_per_share=div_data['dividend_per_share'],
                            total_amount=div_data['total_amount'],
                            notes='Auto-calculated from holdings'
                        )
                        session.add(cash_flow)
                        total_created += 1
            
            session.commit()
            
            return {
                'success': True,
                'message': f'Created {total_created} dividend cash flow records',
                'records_created': total_created
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e), 'records_created': 0}
        finally:
            session.close()
    
    def get_setting(self, key: str, default=None):
        """Get a setting value by key"""
        session = self.db.get_session()
        try:
            setting = session.query(AppSetting).filter_by(setting_key=key).first()
            if setting:
                return setting.setting_value
            return default
        finally:
            session.close()
    
    def set_setting(self, key: str, value: str, description: str = None):
        """Set or update a setting value"""
        session = self.db.get_session()
        try:
            setting = session.query(AppSetting).filter_by(setting_key=key).first()
            
            if setting:
                setting.setting_value = value
                setting.updated_at = datetime.utcnow()
                if description:
                    setting.description = description
            else:
                setting = AppSetting(
                    setting_key=key,
                    setting_value=value,
                    description=description
                )
                session.add(setting)
            
            session.commit()
            return {'success': True, 'message': f'Setting {key} updated'}
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_all_settings(self):
        """Get all settings"""
        session = self.db.get_session()
        try:
            settings = session.query(AppSetting).all()
            return {s.setting_key: s.setting_value for s in settings}
        finally:
            session.close()
    
    def fetch_and_store_fx_rates(self, currency_pair: str = 'AUDUSD', period: str = '5y', 
                                  force_refresh: bool = False):
        """Fetch FX rates and store in database
        
        Args:
            currency_pair: Currency pair (e.g., 'AUDUSD')
            period: Period to fetch ('1y', '5y', 'max')
            force_refresh: Force fetching even if data exists
        """
        session = self.db.get_session()
        try:
            # Check if we need to fetch data
            if not force_refresh:
                latest = session.query(FXRate).filter_by(
                    currency_pair=currency_pair
                ).order_by(FXRate.date.desc()).first()
                
                if latest and (datetime.utcnow() - latest.date).days < 1:
                    return {'success': True, 'message': 'FX data is up to date', 'cached': True}
            
            # Fetch from yfinance using =X suffix for forex
            # AUDUSD=X is the ticker for AUD/USD exchange rate
            ticker = yf.Ticker(f"{currency_pair}=X")
            df = ticker.history(period=period)
            
            if df.empty:
                return {'success': False, 'message': f'No FX data available for {currency_pair}'}
            
            # Store in database
            records_added = 0
            for date, row in df.iterrows():
                # Check if record exists
                existing = session.query(FXRate).filter(
                    and_(
                        FXRate.currency_pair == currency_pair,
                        FXRate.date == date.to_pydatetime()
                    )
                ).first()
                
                if not existing:
                    fx_record = FXRate(
                        currency_pair=currency_pair,
                        date=date.to_pydatetime(),
                        rate=float(row['Close'])
                    )
                    session.add(fx_record)
                    records_added += 1
            
            session.commit()
            return {
                'success': True,
                'message': f'Fetched {records_added} FX records for {currency_pair}',
                'records_added': records_added
            }
        
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            session.close()
    
    def get_fx_rate(self, currency_pair: str, date: datetime = None) -> float:
        """Get FX rate for a specific date
        
        Args:
            currency_pair: Currency pair (e.g., 'AUDUSD')
            date: Date to get rate for (defaults to latest)
            
        Returns:
            Exchange rate, or 1.0 if not found
        """
        session = self.db.get_session()
        try:
            query = session.query(FXRate).filter_by(currency_pair=currency_pair)
            
            if date:
                # Get rate for specific date or closest before it
                query = query.filter(FXRate.date <= date)
            
            rate = query.order_by(FXRate.date.desc()).first()
            
            if rate:
                return rate.rate
            return 1.0  # Default to 1.0 if no rate found
        finally:
            session.close()
    
    def get_fx_rates(self, currency_pair: str, start_date: datetime = None, 
                    end_date: datetime = None) -> pd.DataFrame:
        """Get FX rates for a date range
        
        Args:
            currency_pair: Currency pair (e.g., 'AUDUSD')
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            DataFrame with columns: date, rate
        """
        session = self.db.get_session()
        try:
            query = session.query(FXRate).filter_by(currency_pair=currency_pair)
            
            if start_date:
                query = query.filter(FXRate.date >= start_date)
            if end_date:
                query = query.filter(FXRate.date <= end_date)
            
            rates = query.order_by(FXRate.date).all()
            
            if not rates:
                return pd.DataFrame(columns=['date', 'rate'])
            
            return pd.DataFrame([
                {'date': r.date, 'rate': r.rate}
                for r in rates
            ])
        finally:
            session.close()
