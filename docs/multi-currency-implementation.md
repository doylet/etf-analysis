# Multi-Currency Support Implementation

## Quick Start

You have a multi-currency portfolio (USD and AUD holdings). The system now:
- ✅ Stores currency for each instrument
- ✅ Fetches AUDUSD FX rates daily
- ✅ Converts all values to AUD for accurate portfolio totals
- ✅ Shows both local currency and AUD values

**Migration complete! Your database now has:**
- 2 AUD securities (VEU.AX, XJO.AX)
- 14 USD securities  
- 1,302 AUDUSD FX rates (5 years of data)

**Just restart your Streamlit app to see the changes!**

---

## Overview
Added support for multi-currency portfolios with automatic conversion to base currency (AUD).

## Changes Made

### 1. Database Schema
- **Instrument table**: Added `currency` field (VARCHAR(3), default 'USD')
- **New FXRate table**: Stores daily FX rates for currency pairs
  - Fields: currency_pair, date, rate
  - Example: AUDUSD rates for converting USD holdings to AUD

### 2. Data Layer
**`src/models/database.py`**:
- Added `FXRate` model class
- Added `currency` field to `Instrument` model

**`src/services/data_fetcher.py`**:
- Added `currency` parameter to `add_instrument()`
- Updated `get_all_instruments()` to include currency field
- Updated `get_instrument()` to include currency field
- Added FX rate methods:
  - `fetch_and_store_fx_rates()`: Fetch from yfinance (e.g., AUDUSD=X)
  - `get_fx_rate()`: Get rate for specific date
  - `get_fx_rates()`: Get rates for date range

**`src/services/storage_adapter.py`**:
- Added FX rate method wrappers for both BigQuery and SQLite

### 3. Utilities
**`src/utils/currency_converter.py`** (NEW):
- `CurrencyConverter` class for converting values to base currency
- Supports USD ↔ AUD conversions using AUDUSD rates
- Caching for performance
- Methods:
  - `convert_to_base()`: Convert single amount
  - `convert_series()`: Convert pandas Series

### 4. Widgets
**`src/widgets/holdings_breakdown_widget.py`**:
- Updated to show both local currency and AUD values
- Uses `CurrencyConverter` for all valuations
- Portfolio total shown in AUD
- Individual holdings show:
  - Currency column
  - Value (Local) - in original currency
  - Value (AUD) - converted to AUD
  - Allocation % - based on AUD values

### 5. Setup Script
**`scripts/setup_currency_support.py`** (NEW):
- Fetches AUDUSD FX rates (5 years of data)
- Detects currency based on symbol suffix (.AX = AUD, others = USD)
- Provides SQL commands to update existing instruments

## Migration Steps

### Step 1: Backup Database
```bash
cp data/etf_analysis.db data/etf_analysis.db.backup
```

### Step 2: Run Database Migration
The `currency` column needs to be added to existing instruments table:

```bash
python3 scripts/migrate_add_currency.py
```

This will:
- Add `currency` column to instruments table
- Auto-detect and set currency based on symbol (.AX = AUD, others = USD)
- Show counts of AUD and USD securities

### Step 3: Fetch FX Rates
```bash
python3 scripts/setup_currency_support.py
```

This script will:
- Fetch ~5 years of AUDUSD FX rates
- Verify all currencies are correctly set
- Confirm setup is complete

### Step 4: Verify
Restart the app and check:
- Holdings Breakdown widget shows Currency column
- Values displayed in both local currency and AUD
- Portfolio total in AUD
- Sector/Type breakdowns use AUD values

## Currency Detection Rules

The system auto-detects currency based on symbol format:
- **Australian securities**: End with `.AX` → Currency = AUD
- **US securities**: No suffix → Currency = USD

Examples:
- `VAS.AX` → AUD (Vanguard Australian Shares)
- `AAPL` → USD (Apple Inc.)
- `SPY` → USD (S&P 500 ETF)

## FX Rate Data

- **Source**: Yahoo Finance (yfinance)
- **Ticker**: `AUDUSD=X` (AUD per USD)
- **Data**: Daily close prices
- **History**: 5 years (configurable)
- **Updates**: Can be refreshed by calling `fetch_and_store_fx_rates()`

## Adding New Currency Pairs

To support additional currencies (e.g., EUR, GBP):

1. Add FX rate fetching:
```python
storage.fetch_and_store_fx_rates('AUDEUR', period='5y')
storage.fetch_and_store_fx_rates('AUDGBP', period='5y')
```

2. Update `CurrencyConverter._get_currency_pair()` to handle new pairs

3. Set instrument currency when adding:
```python
storage.add_instrument(
    symbol='BMW.DE',
    name='BMW',
    instrument_type='stock',
    currency='EUR'
)
```

## Performance Considerations

- **FX Rate Caching**: Rates are cached per session in `CurrencyConverter`
- **Bulk Conversions**: Use `convert_series()` for DataFrame operations
- **Database Indexes**: `currency_pair` and `date` are indexed in FXRate table

## Future Enhancements

- [ ] Add update_instrument() method to change currency
- [ ] Auto-refresh FX rates daily
- [ ] Support more currency pairs (EUR, GBP, JPY, etc.)
- [ ] Add currency selector in UI to change base currency
- [ ] Show FX rate information in widgets
- [ ] Historical performance with FX conversion for accurate returns
- [ ] FX gain/loss tracking for multi-currency holdings

## Testing

After implementation, test:
1. Holdings widget shows correct conversions
2. Portfolio total matches manual calculation
3. Sector/Type breakdowns sum correctly
4. Different date ranges maintain correct FX rates
5. New instruments default to correct currency based on symbol
