"""
Symbol search component for manage instruments
"""

import streamlit as st


class SymbolSearchComponent:
    """Component for searching and selecting symbols via Alpha Vantage"""
    
    def __init__(self, av_client):
        self.av_client = av_client
    
    def render(self):
        """Render the symbol search interface"""
        if not self.av_client or not self.av_client.is_available():
            st.info("💡 Enter symbols directly in the order form below. Add ALPHAVANTAGE_API_KEY to .env for optional search feature.")
            return
        
        st.info("💡 **Optional search** - You can skip this and enter symbols directly in the order form below. Alpha Vantage free tier has 25 requests/day and may not include all international securities.")
        
        with st.container(border=False):
            self._render_search_header()
            self._render_search_results()
    
    def _render_search_header(self):
        col_search, col_clear = st.columns([4, 1])
        
        with col_search:
            self._render_search_input()
        with col_clear:
            st.space("small")  # Spacing
            if st.button("Clear", type="secondary", key="clear_search"):
                # Clear all search-related session state
                for key in ['search_query', 'search_results', 'av_search_input', 
                           'selected_symbol', 'selected_name', 'selected_type', 'selected_sector']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    def _render_search_input(self):
        # Initialize search state if needed
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ''
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        
        # Auto-search on text input
        search_query = st.text_input(
            "Search for symbol or company", 
            value=st.session_state.search_query,
            key="av_search_input",
            placeholder="e.g., Apple, AAPL, QQQ",
        )
        
        # Only search if query changed and is long enough
        if search_query != st.session_state.search_query and len(search_query) >= 1:
            st.session_state.search_query = search_query
            with st.spinner("Searching..."):
                results = self.av_client.search_symbols(search_query)
                st.session_state.search_results = results
                if not results and len(search_query) >= 2:
                    st.warning(f"No results found for '{search_query}'. Check your Alpha Vantage API key or try a different search term.")
    
    def _render_search_results(self):
        """Display search results with select buttons"""
        if not st.session_state.search_results:
            if len(st.session_state.search_query) >= 2:
                st.info("No results found")
            return
        
        st.markdown("**Search Results:**")
        for idx, result in enumerate(st.session_state.search_results[:10]):
            col_a, col_b, col_c, col_d = st.columns([1.5, 3, 1, 1])
            
            with col_a:
                st.code(result['symbol'])
            with col_b:
                st.write(f"{result['name']} ({result['type']})")
            with col_c:
                st.caption(result['region'])
            with col_d:
                if st.button("Select", key=f"add_search_{idx}", type="secondary", width='stretch'):
                    self._handle_select(result)
    
    def _handle_select(self, result):
        """Handle selection of a search result"""
        # Determine instrument type from search result
        result_type = result['type'].upper()
        if 'ETF' in result_type:
            instrument_type = 'ETF'
        elif 'INDEX' in result_type:
            instrument_type = 'Index'
        else:
            instrument_type = 'Stock'
        
        # Populate form fields via session state
        st.session_state.selected_symbol = result['symbol']
        st.session_state.selected_name = result['name']
        st.session_state.selected_type = instrument_type
        st.session_state.selected_sector = result.get('sector', '')
        
        # Clear search state completely
        st.session_state.search_query = ''
        st.session_state.search_results = []
        if 'av_search_input' in st.session_state:
            del st.session_state.av_search_input
        
        st.rerun()
