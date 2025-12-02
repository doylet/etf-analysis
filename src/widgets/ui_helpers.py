"""
UI helper functions for Streamlit widgets.

Provides reusable UI components and helper functions for building
consistent widget interfaces.
"""

import streamlit as st
from typing import List, Dict, Callable, Any


def render_bulk_selection_buttons(
    select_all_key: str,
    deselect_all_key: str,
    on_select_all: Callable,
    on_deselect_all: Callable,
    column_ratios: List[int] = None
):
    """
    Render Select All / Deselect All buttons.
    
    Parameters:
        select_all_key: Unique key for Select All button
        deselect_all_key: Unique key for Deselect All button
        on_select_all: Callback when Select All is clicked
        on_deselect_all: Callback when Deselect All is clicked
        column_ratios: Column width ratios (default: [1, 1, 4])
    """
    if column_ratios is None:
        column_ratios = [1, 1, 4]
    
    col1, col2, *rest = st.columns(column_ratios)
    
    with col1:
        if st.button("Select All", key=select_all_key, width="stretch"):
            on_select_all()
            st.rerun()
    
    with col2:
        if st.button("Deselect All", key=deselect_all_key, width="stretch"):
            on_deselect_all()
            st.rerun()


def render_checkbox_grid(
    items: List[Dict[str, Any]],
    key_prefix: str,
    label_formatter: Callable[[Dict], str],
    is_selected: Callable[[Dict], bool],
    num_columns: int = 4
) -> List[Any]:
    """
    Render a grid of checkboxes.
    
    Parameters:
        items: List of items to display as checkboxes
        key_prefix: Prefix for checkbox keys
        label_formatter: Function to format item label
        is_selected: Function to check if item is selected
        num_columns: Number of columns in grid
        
    Returns:
        List of selected items
    """
    cols = st.columns(num_columns)
    selected_items = []
    
    for idx, item in enumerate(items):
        col_idx = idx % num_columns
        with cols[col_idx]:
            label = label_formatter(item)
            selected = st.checkbox(
                label,
                value=is_selected(item),
                key=f"{key_prefix}_{idx}"
            )
            if selected:
                selected_items.append(item)
    
    return selected_items


def render_removable_list(
    items: List[str],
    key_prefix: str,
    on_remove: Callable[[str], None],
    empty_message: str = "No items",
    title: str = None
):
    """
    Render a list of items with remove buttons.
    
    Parameters:
        items: List of items to display
        key_prefix: Prefix for button keys
        on_remove: Callback when item is removed
        empty_message: Message to show when list is empty
        title: Optional title to display
    """
    if title:
        st.caption(title)
    
    if items:
        for item in items:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.text(item)
            with col2:
                if st.button("×", key=f"{key_prefix}_remove_{item}", help=f"Remove {item}"):
                    on_remove(item)
                    st.rerun()
    else:
        st.caption(empty_message)


def render_add_item_input(
    label: str,
    button_label: str,
    input_key: str,
    button_key: str,
    on_add: Callable[[str], None],
    placeholder: str = None
):
    """
    Render input field with add button.
    
    Parameters:
        label: Label for input field
        button_label: Label for add button
        input_key: Key for input widget
        button_key: Key for button widget
        on_add: Callback when item is added
        placeholder: Placeholder text for input
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_input(
            label,
            key=input_key,
            placeholder=placeholder or ""
        )
    
    with col2:
        # st.markdown("&nbsp;")
        st.space("small")
        if st.button(button_label, key=button_key):
            on_add(st.session_state.get(input_key, ""))


def render_selection_summary(
    selected_count: int,
    total_count: int,
    item_type: str = "items"
) -> str:
    """
    Generate selection summary text.
    
    Parameters:
        selected_count: Number of selected items
        total_count: Total number of items
        item_type: Type of items (e.g., "items", "holdings", "symbols")
        
    Returns:
        Formatted summary string
        
    Examples:
        >>> render_selection_summary(5, 10, "holdings")
        "5/10 holdings selected"
    """
    return f"{selected_count}/{total_count} {item_type} selected"


def render_holdings_selection_grid(
    holdings: List[Dict],
    session_key: str,
    checkbox_key_prefix: str,
    num_columns: int = 3,
    label_formatter: Callable[[Dict], str] = None
) -> List[str]:
    """
    Render a checkbox grid for selecting holdings with automatic session state management.
    
    Parameters:
        holdings: List of holding dictionaries (must have 'symbol' key)
        session_key: Session state key for storing selections
        checkbox_key_prefix: Prefix for individual checkbox keys
        num_columns: Number of columns in grid layout
        label_formatter: Optional function to format checkbox labels (default: symbol)
        
    Returns:
        List of selected holding symbols
        
    Example:
        >>> selected = render_holdings_selection_grid(
        ...     holdings,
        ...     "my_widget_selected_holdings",
        ...     "my_widget_holding",
        ...     num_columns=4,
        ...     label_formatter=lambda h: f"{h['symbol']} ({h.get('name', '')})"
        ... )
    """
    # Default label formatter
    if label_formatter is None:
        label_formatter = lambda h: h['symbol']
    
    # Create column grid
    cols = st.columns(num_columns)
    selected_symbols = []
    
    # Render checkboxes
    for idx, holding in enumerate(holdings):
        col_idx = idx % num_columns
        with cols[col_idx]:
            is_selected = st.checkbox(
                label_formatter(holding),
                value=holding['symbol'] in st.session_state.get(session_key, []),
                key=f"{checkbox_key_prefix}_{holding['symbol']}"
            )
            if is_selected:
                selected_symbols.append(holding['symbol'])
    
    # Update session state
    st.session_state[session_key] = selected_symbols
    
    return selected_symbols
