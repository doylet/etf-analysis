# ETF Analysis Dashboard 📊

A comprehensive ETF and stock analysis dashboard with a modern Next.js interface, featuring persistent data storage and Google Cloud Platform integration for production deployment.

## Features

✨ **Instrument Management**
- Add, search, and manage ETFs, stocks, and indices
- Automatic metadata fetching from Yahoo Finance
- Soft delete with tracking history

📈 **Price Analysis**
- Persistent historical price data storage
- Interactive price charts with Plotly
- Volume analysis and trading metrics
- Customizable time periods (1M to 5Y)

📊 **Comparative Analysis**
- Compare multiple instruments side-by-side
- Normalized performance comparison
- Performance metrics table
- Visual trend analysis

💾 **Data Persistence**
- SQLite for local development
- BigQuery for production deployment
- Automatic price data caching
- Incremental updates

🔍 **Symbol Search**
- Live symbol search via Alpha Vantage API
- Search across global exchanges
- View company details before adding

☁️ **Cloud Ready**
- Dockerized for easy deployment
- Google Cloud Run configuration
- BigQuery integration for scalable storage
- Cloud Storage and Secret Manager support
- CI/CD with Cloud Build

## Quick Start (Local Development)

### Next.js Dashboard

The Next.js dashboard is the primary interface:

1. **Navigate to frontend:**
```bash
cd frontend/v1
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
cp .env.example .env.local
```

4. **Run the development server:**
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### API Server (Backend)

The FastAPI backend provides data services:

The Streamlit interface is still available but will be removed soon:

### Prerequisites

- Python 3.11 or higher
- Conda (Anaconda or Miniconda)
1. **Start API server:**
```bash
python start_api_server.py
```

Or with docker-compose:
```bash
docker-compose up api
```

The API will be available at `http://localhost:8000`

## Project Structure

```
etf-analysis/
├── frontend/v1/                # Next.js dashboard
├── src/                        # Source code
│   ├── api/                    # FastAPI backend
│   ├── models/                 # Data models
│   ├── services/               # Business logic
│   ├── widgets/                # Widget business logic
│   └── utils/                  # Utilities
├── requirements.txt            # Python dependencies
├── Dockerfile.api              # API container configuration
├── docker-compose.yml          # Multi-service setup
├── cloudbuild.yaml             # Cloud Build CI/CD config
├── .env.example                # Environment variables template
├── tests/                      # Test suites
└── docs/                       # Documentation
```
│       └── gcp_utils.py       # GCP integration
│
├── config/                    # Configuration
│   ├── __init__.py
│   └── settings.py            # App settings
│
├── scripts/                   # Deployment scripts
│   ├── deploy.sh              # Cloud Run deployment
│   └── setup-cloud-build.sh   # CI/CD setup
│
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_database.py       # Database tests
│
├── .streamlit/                # Streamlit config
│   └── config.toml
│
└── data/                      # Local database (created automatically)
    └── etf_analysis.db
```

## Google Cloud Deployment

### Prerequisites

- Google Cloud Platform account
- gcloud CLI installed and configured
- Docker installed (for local testing)

### Option 1: Manual Deployment

1. **Update scripts/deploy.sh with your project details:**
```bash
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="etf-analysis-dashboard"
REGION="us-central1"
```

2. **Deploy to Cloud Run:**
```bash
./scripts/deploy.sh
```

The script will:
- Enable required GCP APIs
- Build the container image
- Deploy to Cloud Run
- Provide the public URL

### Option 2: Automatic Deployment (CI/CD)

Set up Cloud Build to automatically deploy on every push to master:

1. **Update scripts/setup-cloud-build.sh with your project ID:**
```bash
PROJECT_ID="your-gcp-project-id"
```

2. **Run the setup script:**
```bash
./scripts/setup-cloud-build.sh
```

3. **Follow the prompts to connect your GitHub repository**

Once configured, every push to the master branch will:
- Trigger Cloud Build automatically
- Build the Docker image
- Deploy to Cloud Run
- Tag with commit SHA and 'latest'

Monitor builds at: https://console.cloud.google.com/cloud-build/builds

### Cloud SQL Setup (Optional)

For production with PostgreSQL:

1. **Create a Cloud SQL instance:**
```bash
gcloud sql instances create etf-analysis-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1
```

2. **Create the database:**
```bash
gcloud sql databases create etf_analysis \
    --instance=etf-analysis-db
```

3. **Set environment variables in Cloud Run:**
```bash
gcloud run services update etf-analysis-dashboard \
    --add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME \
    --set-env-vars=CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME \
    --set-env-vars=DB_USER=postgres \
    --set-env-vars=DB_NAME=etf_analysis
```

4. **Store database password in Secret Manager:**
```bash
echo -n "your-db-password" | gcloud secrets create db-password --data-file=-
```

### BigQuery Setup (Production Default)

The deployed dashboard uses BigQuery for data storage automatically. No manual setup required - tables are created on first run:

- **Dataset**: `etf_analysis`
- **Tables**:
  - `instruments` - Tracked stocks/ETFs
  - `price_data` - Historical OHLCV data

**Benefits:**
- Serverless and auto-scaling
- Pay per query (very cost-effective)
- No database maintenance
- Built-in analytics capabilities

The app automatically uses BigQuery when `USE_BIGQUERY=true` environment variable is set (configured in Dockerfile for Cloud Run).

### Cloud Storage Setup (Optional)

For storing backups or large datasets:

1. **Create a storage bucket:**
```bash
gcloud storage buckets create gs://your-bucket-name \
    --location=us-central1
```

2. **Set environment variable:**
```bash
gcloud run services update etf-analysis-dashboard \
    --set-env-vars=GCP_BUCKET_NAME=your-bucket-name
```

## Environment Variables

### Local Development (.env)
```bash
DATABASE_URL=sqlite:///./data/etf_analysis.db
```

### Production (Cloud Run)
```bash
# Cloud SQL
CLOUD_SQL_CONNECTION_NAME=project:region:instance
DB_USER=postgres
DB_NAME=etf_analysis

# Cloud Storage (optional)
GCP_BUCKET_NAME=your-bucket-name

# Project
GCP_PROJECT_ID=your-project-id
```

## Database Schema

### Instruments Table
- `id`: Primary key
- `symbol`: Unique ticker symbol
- `name`: Full name
- `instrument_type`: etf, stock, or index
- `sector`: Industry sector
- `is_active`: Soft delete flag
- `added_date`: When added
- `last_updated`: Last update timestamp
- `notes`: User notes

### PriceData Table
- `id`: Primary key
- `symbol`: Foreign key to instrument
- `date`: Trading date
- `open_price`: Opening price
- `high_price`: Daily high
- `low_price`: Daily low
- `close_price`: Closing price
- `volume`: Trading volume
- `created_at`: Record creation time

## Technology Stack

### Frontend
- **Primary**: Next.js 14 (React) with TypeScript
- **Charts**: Recharts, Plotly
- **UI Components**: shadcn/ui with Radix UI
- **Styling**: Tailwind CSS

### Backend
- **API**: FastAPI
- **Data**: pandas, NumPy
- **Database**: SQLAlchemy (SQLite/PostgreSQL/BigQuery)
- **Market Data**: yfinance, Alpha Vantage

### Cloud & Infrastructure
- **Hosting**: Google Cloud Run
- **Database**: Cloud SQL, BigQuery
- **Storage**: Cloud Storage
- **CI/CD**: Cloud Build
- **Container**: Docker

## Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Local Docker Build
```bash
# Build API image
docker build -f Dockerfile.api -t etf-analysis-api .

# Run container
docker run -p 8000:8000 etf-analysis-api
```

Access at `http://localhost:8000`

## Cost Optimization (Cloud Run)

Cloud Run is pay-per-use:
- **Free tier**: 2 million requests/month, 360,000 GB-seconds
- **Scaling**: Automatically scales to zero when not in use
- **Cost**: ~$0.10-1.00/month for light usage

To minimize costs:
- Set `--min-instances=0` (default)
- Use `--max-instances=10` to cap scaling
- Set `--concurrency=80` for efficiency

## Troubleshooting

### Local Issues

**Database errors:**
```bash
# Delete and recreate database
rm -rf data/
python -c "from database import DatabaseManager; DatabaseManager()"
```

**Module not found:**
```bash
pip install -r requirements.txt --upgrade
```

### Cloud Run Issues

**Check logs:**
```bash
gcloud run services logs read etf-analysis-dashboard --limit=50
```

**Test deployment:**
```bash
gcloud run services describe etf-analysis-dashboard --region=us-central1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - feel free to use this project for your own analysis!

## Support

For issues or questions:
- Check the troubleshooting section
- Review Cloud Run logs
- Open an issue on GitHub

## Roadmap

- [ ] Real-time price updates
- [ ] Custom alerts and notifications
- [ ] Portfolio tracking
- [ ] Advanced technical indicators
- [ ] Export to Excel/PDF
- [ ] Multi-user support with authentication
- [ ] Backtesting capabilities

---

Built with ❤️ using Streamlit and Google Cloud Platform
