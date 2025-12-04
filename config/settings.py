# Configuration settings for the ETF Analysis Dashboard

import os

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

# Feature Flags
# Enable new service layer architecture (Phase 7 - Compatibility Layer)
# When True: Widgets use new service layer via StreamlitServiceBridge
# When False: Widgets use original implementation
# Override via environment variable: ETF_USE_NEW_SERVICES=true
USE_NEW_SERVICE_LAYER = os.environ.get('ETF_USE_NEW_SERVICES', 'false').lower() in ('true', '1', 'yes')
