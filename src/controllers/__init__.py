"""
Page controllers for the ETF Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


class ManageInstrumentsPage:
    """Controller for Manage Instruments page"""
    
    def __init__(self, storage, av_client):
        self.storage = storage
        self.av_client = av_client
    
    def render(self):
        st.title("🔧 Manage Instruments")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_add_form()
        
        with col2:
            self._render_search()
        
        st.divider()
        self._render_instruments_list()
    
    def _render_add_form(self):
        st.subheader("Add New Instrument")
        
        # Symbol search feature
        if self.av_client.is_available():
            self._render_symbol_search()
        else:
            st.info("💡 Add ALPHAVANTAGE_API_KEY to .env for symbol search")
        
        with st.form("add_instrument_form"):
            symbol = st.text_input("Symbol (e.g., SPY, AAPL, BHP.AX)", key="add_symbol").upper()
            instrument_type = st.selectbox("Type", ["etf", "stock", "index"], key="add_type")
            sector = st.text_input("Sector (optional)", key="add_sector")
            notes = st.text_area("Notes (optional)", key="add_notes")
            
            submitted = st.form_submit_button("Add Instrument")
            
            if submitted and symbol:
                self._handle_add_instrument(symbol, instrument_type, sector, notes)
    
    def _render_symbol_search(self):
        st.markdown("**Search for symbols:**")
        search_query = st.text_input("Search by company name or symbol", key="av_search")
        
        if search_query and len(search_query) >= 2:
            with st.spinner("Searching..."):
                results = self.av_client.search_symbols(search_query)
                
                if results:
                    st.markdown("**Search Results:**")
                    for result in results[:10]:
                        col_a, col_b, col_c = st.columns([2, 3, 1])
                        with col_a:
                            st.code(result['symbol'])
                        with col_b:
                            st.write(f"{result['name']} ({result['type']})")
                        with col_c:
                            st.caption(result['region'])
                    st.divider()
                else:
                    st.info("No results found")
    
    def _handle_add_instrument(self, symbol, instrument_type, sector, notes):
        with st.spinner(f"Adding {symbol}..."):
            result = self.storage.add_instrument(
                symbol=symbol,
                instrument_type=instrument_type,
                sector=sector if sector else None,
                notes=notes if notes else None
            )
            
            if result['success']:
                st.success(result['message'])
                with st.spinner(f"Fetching historical data for {symbol}..."):
                    price_result = self.storage.fetch_and_store_prices(symbol, period='1y')
                    if price_result['success']:
                        st.info(f"Loaded {price_result.get('records_added', 0)} price records")
                st.rerun()
            else:
                st.error(result['message'])
    
    def _render_search(self):
        st.subheader("Search Instruments")
        search_term = st.text_input("Search by symbol or name", key="search")
        
        if search_term:
            results = self.storage.search_instruments(search_term)
            if results:
                st.write(f"Found {len(results)} instrument(s):")
                for inst in results:
                    st.write(f"**{inst['symbol']}** - {inst['name']} ({inst['type']})")
            else:
                st.info("No instruments found")
    
    def _render_instruments_list(self):
        st.subheader("Tracked Instruments")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if instruments:
            df = pd.DataFrame(instruments)
            df['added_date'] = pd.to_datetime(df['added_date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df[['symbol', 'name', 'type', 'sector', 'added_date']],
                use_container_width=True,
                hide_index=True
            )
            
            self._render_remove_form(instruments)
        else:
            st.info("No instruments tracked yet. Add some above!")
    
    def _render_remove_form(self, instruments):
        st.subheader("Remove Instrument")
        col_remove1, col_remove2 = st.columns([3, 1])
        
        with col_remove1:
            remove_symbol = st.selectbox(
                "Select instrument to remove",
                options=[i['symbol'] for i in instruments],
                key="remove_select"
            )
        
        with col_remove2:
            st.write("")
            st.write("")
            if st.button("Remove", type="secondary"):
                result = self.storage.remove_instrument(remove_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])


class DashboardPage:
    """Controller for main Dashboard page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("📊 ETF Analysis Dashboard")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        latest_prices = self.storage.get_latest_prices(symbols)
        
        self._render_overview(instruments, latest_prices)
        st.divider()
        self._render_data_management(symbols)
        st.divider()
        self._render_instruments_table(instruments, latest_prices)
    
    def _render_overview(self, instruments, latest_prices):
        st.subheader("Portfolio Overview")
        
        cols = st.columns(min(4, len(instruments)))
        for idx, inst in enumerate(instruments[:4]):
            with cols[idx]:
                symbol = inst['symbol']
                if symbol in latest_prices:
                    price_info = latest_prices[symbol]
                    st.metric(
                        label=symbol,
                        value=f"${price_info['close']:.2f}",
                        delta=None
                    )
                    st.caption(inst['name'][:30])
    
    def _render_data_management(self, symbols):
        st.subheader("Data Management")
        col_refresh1, col_refresh2 = st.columns([3, 1])
        
        with col_refresh1:
            refresh_symbol = st.selectbox(
                "Update price data for:",
                options=['All'] + symbols,
                key="refresh_select"
            )
        
        with col_refresh2:
            st.write("")
            st.write("")
            if st.button("Fetch Latest Data"):
                self._handle_data_refresh(refresh_symbol, symbols)
    
    def _handle_data_refresh(self, refresh_symbol, symbols):
        symbols_to_refresh = symbols if refresh_symbol == 'All' else [refresh_symbol]
        
        progress_bar = st.progress(0)
        for idx, sym in enumerate(symbols_to_refresh):
            with st.spinner(f"Fetching {sym}..."):
                result = self.storage.fetch_and_store_prices(sym, period='1mo')
                if result['success']:
                    st.success(f"{sym}: {result['message']}")
            progress_bar.progress((idx + 1) / len(symbols_to_refresh))
        
        st.rerun()
    
    def _render_instruments_table(self, instruments, latest_prices):
        st.subheader("All Tracked Instruments")
        
        display_data = []
        for inst in instruments:
            symbol = inst['symbol']
            row = {
                'Symbol': symbol,
                'Name': inst['name'],
                'Type': inst['type'],
                'Sector': inst['sector']
            }
            if symbol in latest_prices:
                row['Last Price'] = f"${latest_prices[symbol]['close']:.2f}"
                row['Last Update'] = latest_prices[symbol]['date'].strftime('%Y-%m-%d')
            else:
                row['Last Price'] = 'N/A'
                row['Last Update'] = 'N/A'
            
            display_data.append(row)
        
        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True
        )


class PriceHistoryPage:
    """Controller for Price History page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("📈 Price History")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        selected_symbol, period = self._render_controls(symbols)
        
        if selected_symbol:
            self._render_price_analysis(selected_symbol, period)
    
    def _render_controls(self, symbols):
        col1, col2 = st.columns([2, 2])
        
        with col1:
            selected_symbol = st.selectbox("Select Instrument", options=symbols)
        
        with col2:
            period = st.selectbox(
                "Time Period",
                options=['1M', '3M', '6M', '1Y', '2Y', '5Y', 'All'],
                index=3
            )
        
        return selected_symbol, period
    
    def _render_price_analysis(self, symbol, period):
        start_date = self._calculate_start_date(period)
        df = self.storage.get_price_data(symbol, start_date=start_date)
        
        if df.empty:
            st.warning(f"No price data available for {symbol}. Try fetching data from the Dashboard.")
            return
        
        self._render_metrics(df)
        self._render_price_chart(symbol, df)
        self._render_volume_chart(symbol, df)
        self._render_data_table(df)
    
    def _calculate_start_date(self, period):
        end_date = datetime.now()
        period_days = {
            '1M': 30, '3M': 90, '6M': 180,
            '1Y': 365, '2Y': 730, '5Y': 1825
        }
        
        if period in period_days:
            return end_date - timedelta(days=period_days[period])
        return None
    
    def _render_metrics(self, df):
        latest_price = df['close'].iloc[-1]
        first_price = df['close'].iloc[0]
        price_change = latest_price - first_price
        pct_change = (price_change / first_price) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"${latest_price:.2f}")
        with col2:
            st.metric("Change", f"${price_change:.2f}", f"{pct_change:+.2f}%")
        with col3:
            st.metric("High", f"${df['high'].max():.2f}")
        with col4:
            st.metric("Low", f"${df['low'].min():.2f}")
    
    def _render_price_chart(self, symbol, df):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} Price History",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_volume_chart(self, symbol, df):
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title=f"{symbol} Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_data_table(self, df):
        with st.expander("View Raw Data"):
            st.dataframe(
                df.reset_index().tail(50).sort_index(ascending=False),
                use_container_width=True
            )


class ComparativeAnalysisPage:
    """Controller for Comparative Analysis page"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def render(self):
        st.title("📊 Comparative Analysis")
        
        instruments = self.storage.get_all_instruments(active_only=True)
        
        if not instruments:
            st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
            return
        
        if len(instruments) < 2:
            st.warning("Add at least 2 instruments to compare.")
            return
        
        symbols = [i['symbol'] for i in instruments]
        selected_symbols, period = self._render_controls(symbols)
        
        if len(selected_symbols) >= 2:
            self._render_comparison(selected_symbols, period)
        else:
            st.info("Select at least 2 instruments to compare.")
    
    def _render_controls(self, symbols):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_symbols = st.multiselect(
                "Select Instruments to Compare (max 5)",
                options=symbols,
                default=symbols[:min(3, len(symbols))],
                max_selections=5
            )
        
        with col2:
            period = st.selectbox(
                "Period",
                options=['1M', '3M', '6M', '1Y', 'All'],
                index=3
            )
        
        return selected_symbols, period
    
    def _render_comparison(self, symbols, period):
        start_date = self._calculate_start_date(period)
        all_data = self._fetch_data(symbols, start_date)
        
        if not all_data:
            st.warning("No price data available for selected instruments. Fetch data from the Dashboard first.")
            return
        
        self._render_normalized_chart(all_data)
        self._render_metrics_table(all_data)
    
    def _calculate_start_date(self, period):
        end_date = datetime.now()
        period_days = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365}
        
        if period in period_days:
            return end_date - timedelta(days=period_days[period])
        return None
    
    def _fetch_data(self, symbols, start_date):
        all_data = {}
        for symbol in symbols:
            df = self.storage.get_price_data(symbol, start_date=start_date)
            if not df.empty:
                all_data[symbol] = df
        return all_data
    
    def _render_normalized_chart(self, all_data):
        st.subheader("Normalized Performance Comparison")
        
        fig = go.Figure()
        
        for symbol, df in all_data.items():
            normalized = ((df['close'] / df['close'].iloc[0]) - 1) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized,
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Return (%)",
            hovermode='x unified',
            height=500,
            yaxis=dict(ticksuffix="%")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_metrics_table(self, all_data):
        st.subheader("Performance Metrics")
        
        metrics_data = []
        for symbol, df in all_data.items():
            first_price = df['close'].iloc[0]
            last_price = df['close'].iloc[-1]
            pct_change = ((last_price / first_price) - 1) * 100
            
            metrics_data.append({
                'Symbol': symbol,
                'Start Price': f"${first_price:.2f}",
                'End Price': f"${last_price:.2f}",
                'Return': f"{pct_change:+.2f}%",
                'High': f"${df['high'].max():.2f}",
                'Low': f"${df['low'].min():.2f}",
                'Avg Volume': f"{df['volume'].mean():,.0f}"
            })
        
        st.dataframe(
            pd.DataFrame(metrics_data),
            use_container_width=True,
            hide_index=True
        )
