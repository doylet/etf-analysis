# Configuration settings for the ETF Analysis Dashboard

# Database
DATABASE_URL = 'sqlite:///./data/etf_analysis.db'

# API Keys
ALPHAVANTAGE_API_KEY = None  # Set via environment variable

# GCP Settings
GCP_PROJECT_ID = None
GCP_BUCKET_NAME = None

# Application Settings
APP_TITLE = "ETF Analysis Dashboard"
APP_ICON = "📊"
DEFAULT_FETCH_PERIOD = "1y"
MAX_INSTRUMENTS_TO_COMPARE = 5
