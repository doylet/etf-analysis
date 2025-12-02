# Configuration settings for the ETF Analysis Dashboard

# Database
DATABASE_URL = 'sqlite:///./data/etf_analysis.db'

# API Keys
ALPHAVANTAGE_API_KEY = "F4M0NKO6QMBZJFKP"  # Set via environment variable

# GCP Settings
GCP_PROJECT_ID = "conda-portfolio-dashboard"
GCP_BUCKET_NAME = None

# Application Settings
APP_TITLE = "ETF Analysis Dashboard"
DEFAULT_FETCH_PERIOD = "all"
MAX_INSTRUMENTS_TO_COMPARE = 10
