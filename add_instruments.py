#!/usr/bin/env python3
"""
Bulk add instruments to the database for portfolio analysis
"""

from src.services.storage_adapter import DataStorageAdapter

def add_instruments():
    storage = DataStorageAdapter()
    
    # Comprehensive list of popular ETFs and stocks across different categories
    instruments = [
        # US Equity ETFs
        ('SPY', 'SPDR S&P 500 ETF', 'etf', 'US Equity'),
        ('QQQ', 'Invesco QQQ Trust', 'etf', 'US Equity'),
        ('IWM', 'iShares Russell 2000 ETF', 'etf', 'US Equity'),
        ('VTI', 'Vanguard Total Stock Market ETF', 'etf', 'US Equity'),
        ('VOO', 'Vanguard S&P 500 ETF', 'etf', 'US Equity'),
        ('DIA', 'SPDR Dow Jones Industrial Average ETF', 'etf', 'US Equity'),
        
        # International Equity ETFs
        ('VEA', 'Vanguard FTSE Developed Markets ETF', 'etf', 'International Equity'),
        ('VWO', 'Vanguard FTSE Emerging Markets ETF', 'etf', 'International Equity'),
        ('EFA', 'iShares MSCI EAFE ETF', 'etf', 'International Equity'),
        ('EEM', 'iShares MSCI Emerging Markets ETF', 'etf', 'International Equity'),
        ('IEFA', 'iShares Core MSCI EAFE ETF', 'etf', 'International Equity'),
        ('IEMG', 'iShares Core MSCI Emerging Markets ETF', 'etf', 'International Equity'),
        
        # Bond ETFs
        ('AGG', 'iShares Core US Aggregate Bond ETF', 'etf', 'Fixed Income'),
        ('BND', 'Vanguard Total Bond Market ETF', 'etf', 'Fixed Income'),
        ('TLT', 'iShares 20+ Year Treasury Bond ETF', 'etf', 'Fixed Income'),
        ('IEF', 'iShares 7-10 Year Treasury Bond ETF', 'etf', 'Fixed Income'),
        ('SHY', 'iShares 1-3 Year Treasury Bond ETF', 'etf', 'Fixed Income'),
        ('LQD', 'iShares iBoxx Investment Grade Corporate Bond ETF', 'etf', 'Fixed Income'),
        ('HYG', 'iShares iBoxx High Yield Corporate Bond ETF', 'etf', 'Fixed Income'),
        ('TIP', 'iShares TIPS Bond ETF', 'etf', 'Fixed Income'),
        
        # Sector ETFs
        ('XLF', 'Financial Select Sector SPDR Fund', 'etf', 'Financials'),
        ('XLE', 'Energy Select Sector SPDR Fund', 'etf', 'Energy'),
        ('XLK', 'Technology Select Sector SPDR Fund', 'etf', 'Technology'),
        ('XLV', 'Health Care Select Sector SPDR Fund', 'etf', 'Healthcare'),
        ('XLI', 'Industrial Select Sector SPDR Fund', 'etf', 'Industrials'),
        ('XLY', 'Consumer Discretionary Select Sector SPDR Fund', 'etf', 'Consumer Discretionary'),
        ('XLP', 'Consumer Staples Select Sector SPDR Fund', 'etf', 'Consumer Staples'),
        ('XLU', 'Utilities Select Sector SPDR Fund', 'etf', 'Utilities'),
        ('XLRE', 'Real Estate Select Sector SPDR Fund', 'etf', 'Real Estate'),
        ('XLB', 'Materials Select Sector SPDR Fund', 'etf', 'Materials'),
        
        # Thematic/Growth ETFs
        ('ARK', 'ARK Innovation ETF', 'etf', 'Innovation'),
        ('ARKK', 'ARK Innovation ETF', 'etf', 'Innovation'),
        ('ARKW', 'ARK Next Generation Internet ETF', 'etf', 'Technology'),
        ('ARKG', 'ARK Genomic Revolution ETF', 'etf', 'Healthcare'),
        ('ARKQ', 'ARK Autonomous Technology & Robotics ETF', 'etf', 'Technology'),
        ('ICLN', 'iShares Global Clean Energy ETF', 'etf', 'Clean Energy'),
        ('TAN', 'Invesco Solar ETF', 'etf', 'Clean Energy'),
        ('LIT', 'Global X Lithium & Battery Tech ETF', 'etf', 'Materials'),
        
        # Commodity/Alternative ETFs
        ('GLD', 'SPDR Gold Shares', 'etf', 'Commodities'),
        ('SLV', 'iShares Silver Trust', 'etf', 'Commodities'),
        ('USO', 'United States Oil Fund', 'etf', 'Commodities'),
        ('DBC', 'Invesco DB Commodity Index Tracking Fund', 'etf', 'Commodities'),
        ('VNQ', 'Vanguard Real Estate ETF', 'etf', 'Real Estate'),
        
        # Dividend/Value ETFs
        ('VYM', 'Vanguard High Dividend Yield ETF', 'etf', 'Dividend'),
        ('SCHD', 'Schwab US Dividend Equity ETF', 'etf', 'Dividend'),
        ('DVY', 'iShares Select Dividend ETF', 'etf', 'Dividend'),
        ('VIG', 'Vanguard Dividend Appreciation ETF', 'etf', 'Dividend'),
        ('VTV', 'Vanguard Value ETF', 'etf', 'Value'),
        ('VUG', 'Vanguard Growth ETF', 'etf', 'Growth'),
        
        # Large Cap Stocks - Tech
        ('AAPL', 'Apple Inc.', 'stock', 'Technology'),
        ('MSFT', 'Microsoft Corporation', 'stock', 'Technology'),
        ('GOOGL', 'Alphabet Inc.', 'stock', 'Technology'),
        ('AMZN', 'Amazon.com Inc.', 'stock', 'Consumer Discretionary'),
        ('META', 'Meta Platforms Inc.', 'stock', 'Technology'),
        ('NVDA', 'NVIDIA Corporation', 'stock', 'Technology'),
        ('TSLA', 'Tesla Inc.', 'stock', 'Consumer Discretionary'),
        ('AMD', 'Advanced Micro Devices Inc.', 'stock', 'Technology'),
        ('NFLX', 'Netflix Inc.', 'stock', 'Communication Services'),
        
        # Large Cap Stocks - Other
        ('BRK.B', 'Berkshire Hathaway Inc.', 'stock', 'Financials'),
        ('JNJ', 'Johnson & Johnson', 'stock', 'Healthcare'),
        ('V', 'Visa Inc.', 'stock', 'Financials'),
        ('PG', 'Procter & Gamble Co.', 'stock', 'Consumer Staples'),
        ('JPM', 'JPMorgan Chase & Co.', 'stock', 'Financials'),
        ('UNH', 'UnitedHealth Group Inc.', 'stock', 'Healthcare'),
        ('HD', 'Home Depot Inc.', 'stock', 'Consumer Discretionary'),
        ('BAC', 'Bank of America Corp.', 'stock', 'Financials'),
        ('DIS', 'Walt Disney Co.', 'stock', 'Communication Services'),
        ('ADBE', 'Adobe Inc.', 'stock', 'Technology'),
        
        # Mid Cap Stocks
        ('SQ', 'Block Inc.', 'stock', 'Technology'),
        ('PYPL', 'PayPal Holdings Inc.', 'stock', 'Technology'),
        ('SHOP', 'Shopify Inc.', 'stock', 'Technology'),
        ('SNAP', 'Snap Inc.', 'stock', 'Technology'),
        ('UBER', 'Uber Technologies Inc.', 'stock', 'Technology'),
        ('LYFT', 'Lyft Inc.', 'stock', 'Technology'),
        ('COIN', 'Coinbase Global Inc.', 'stock', 'Financials'),
        ('PLTR', 'Palantir Technologies Inc.', 'stock', 'Technology'),
        
        # International Stocks
        ('BABA', 'Alibaba Group Holding Ltd.', 'stock', 'Consumer Discretionary'),
        ('TSM', 'Taiwan Semiconductor Manufacturing', 'stock', 'Technology'),
        ('NVO', 'Novo Nordisk A/S', 'stock', 'Healthcare'),
        ('ASML', 'ASML Holding N.V.', 'stock', 'Technology'),
        ('SAP', 'SAP SE', 'stock', 'Technology'),
        
        # Volatility/Inverse ETFs
        ('VXX', 'iPath Series B S&P 500 VIX Short-Term Futures ETN', 'etf', 'Volatility'),
        ('UVXY', 'ProShares Ultra VIX Short-Term Futures ETF', 'etf', 'Volatility'),
        ('SH', 'ProShares Short S&P500', 'etf', 'Inverse'),
        ('PSQ', 'ProShares Short QQQ', 'etf', 'Inverse'),
    ]
    
    added = 0
    skipped = 0
    failed = 0
    
    print(f"Adding {len(instruments)} instruments to database...")
    print("-" * 60)
    
    for symbol, name, inst_type, sector in instruments:
        try:
            result = storage.add_instrument(
                symbol=symbol,
                name=name,
                instrument_type=inst_type,
                sector=sector,
                is_active=True
            )
            
            if result.get('success'):
                print(f"✓ Added: {symbol:8s} - {name}")
                added += 1
            else:
                print(f"⊘ Skipped: {symbol:8s} - {result.get('message', 'Already exists')}")
                skipped += 1
        except Exception as e:
            print(f"✗ Failed: {symbol:8s} - {str(e)}")
            failed += 1
    
    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Added:   {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"  Total:   {len(instruments)}")
    
    # Show final count
    all_instruments = storage.get_all_instruments(active_only=False)
    print(f"\nTotal instruments in database: {len(all_instruments)}")

if __name__ == '__main__':
    add_instruments()
