# ETF Analysis Dashboard 📊

A comprehensive ETF and stock analysis dashboard built with Streamlit, featuring persistent data storage and Google Cloud Platform integration for production deployment.

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
- PostgreSQL/Cloud SQL support for production
- Automatic price data caching
- Incremental updates

☁️ **Cloud Ready**
- Dockerized for easy deployment
- Google Cloud Run configuration
- Cloud Storage integration
- Secret Manager support

## Quick Start (Local Development)

### Prerequisites

- Python 3.11 or higher
- Conda (Anaconda or Miniconda)

### Setup

1. **Activate your conda environment:**
```bash
conda activate etf-analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create environment file:**
```bash
cp .env.example .env
```

4. **Run the application:**
```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## Usage

### Adding Instruments

1. Navigate to **Manage Instruments**
2. Enter the ticker symbol (e.g., SPY, AAPL, QQQ)
3. Select the instrument type (ETF, stock, or index)
4. Add optional notes and sector information
5. Click **Add Instrument**

Historical price data (1 year) is automatically fetched and stored.

### Viewing Price History

1. Go to **Price History**
2. Select an instrument from the dropdown
3. Choose a time period (1M, 3M, 6M, 1Y, 2Y, 5Y, All)
4. View interactive charts and metrics

### Comparing Instruments

1. Navigate to **Comparative Analysis**
2. Select 2-5 instruments to compare
3. Choose a time period
4. View normalized performance and metrics

### Updating Data

From the **Dashboard** page:
1. Select an instrument or "All"
2. Click **Fetch Latest Data**
3. Data is updated and cached in the database

## Project Structure

```
etf-analysis/
├── app.py                  # Main Streamlit application
├── database.py             # Database models and connection
├── data_fetcher.py         # Price data fetching and storage
├── gcp_utils.py            # Google Cloud Platform utilities
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── deploy.sh               # Cloud Run deployment script
├── .env.example            # Environment variables template
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── data/                   # Local SQLite database (created automatically)
```

## Google Cloud Deployment

### Prerequisites

- Google Cloud Platform account
- gcloud CLI installed and configured
- Docker installed (for local testing)

### Option 1: Manual Deployment

1. **Update deploy.sh with your project details:**
```bash
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="etf-analysis-dashboard"
REGION="us-central1"
```

2. **Deploy to Cloud Run:**
```bash
./deploy.sh
```

The script will:
- Enable required GCP APIs
- Build the container image
- Deploy to Cloud Run
- Provide the public URL

### Option 2: Automatic Deployment (CI/CD)

Set up Cloud Build to automatically deploy on every push to master:

1. **Update setup-cloud-build.sh with your project ID:**
```bash
PROJECT_ID="your-gcp-project-id"
```

2. **Run the setup script:**
```bash
./setup-cloud-build.sh
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

- **Frontend**: Streamlit
- **Charts**: Plotly
- **Data**: pandas, NumPy
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Market Data**: yfinance
- **Cloud**: Google Cloud Run, Cloud SQL, Cloud Storage
- **Container**: Docker

## Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests (when test files are added)
pytest tests/
```

### Local Docker Build
```bash
# Build image
docker build -t etf-analysis-dashboard .

# Run container
docker run -p 8080:8080 etf-analysis-dashboard
```

Access at `http://localhost:8080`

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
