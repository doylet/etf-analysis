# Deployment Configuration Updates for Streamlit Removal

**Date**: December 8, 2025  
**Purpose**: Document required changes to deployment configurations after Streamlit removal

---

## Overview

After removing Streamlit, the following deployment configurations need to be updated to reflect the new architecture with only Next.js frontend and FastAPI backend.

---

## Files Requiring Updates

### 1. Dockerfile (Streamlit Container)

**Current**: `Dockerfile` builds Streamlit application
**Action**: **DELETE** - No longer needed after Streamlit removal

**Current Content**:
```dockerfile
FROM python:3.11-slim
# ... Streamlit-specific configuration
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

**Replacement**: None - Streamlit container not needed

---

### 2. Dockerfile.api (FastAPI Container)

**Current**: `Dockerfile.api` builds FastAPI backend
**Action**: **KEEP** - This is the main backend container

**Status**: ✅ No changes needed - already correct

---

### 3. docker-compose.yml

**Current**: Includes 5 services (api, celery, redis, postgres, **streamlit**)

**Action**: **UPDATE** - Remove streamlit service

**Before**:
```yaml
services:
  api:
    # ... FastAPI config
  
  celery:
    # ... Celery config
  
  redis:
    # ... Redis config
  
  postgres:
    # ... PostgreSQL config
  
  streamlit:  # ← REMOVE THIS ENTIRE SERVICE
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/etf_analysis
      - USE_NEW_SERVICE_LAYER=false
    volumes:
      - ./src:/app/src
      - ./pages:/app/pages
      - ./config:/app/config
      - ./data:/app/data
      - ./.env:/app/.env
    depends_on:
      - postgres
    command: streamlit run app.py
    networks:
      - etf-network
```

**After**:
```yaml
services:
  api:
    # ... FastAPI config (unchanged)
  
  celery:
    # ... Celery config (unchanged)
  
  redis:
    # ... Redis config (unchanged)
  
  postgres:
    # ... PostgreSQL config (unchanged)
  
  # Optional: Add Next.js frontend service for local development
  frontend:
    build:
      context: ./frontend/v1
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    volumes:
      - ./frontend/v1/src:/app/src
      - ./frontend/v1/public:/app/public
    depends_on:
      - api
    networks:
      - etf-network
```

---

### 4. requirements.txt

**Current**: Includes Streamlit dependencies

**Action**: **UPDATE** - Remove Streamlit packages

**Before**:
```txt
streamlit==1.29.0
# ... other packages
```

**After**:
```txt
# Remove:
# - streamlit==1.29.0
# - streamlit-aggrid (if present)
# - streamlit-option-menu (if present)

# Keep all other packages:
fastapi
uvicorn
pydantic
pandas
# ... etc
```

---

### 5. README.md

**Current**: Features Streamlit as main interface

**Action**: **UPDATE** - Replace with Next.js documentation

**Before**:
```markdown
# ETF Analysis Dashboard 📊

A comprehensive ETF and stock analysis dashboard built with Streamlit...

## Features

✨ **Instrument Management**
- Add, search, and manage ETFs, stocks, and indices
- Automatic metadata fetching from Yahoo Finance

📈 **Price Analysis**
- Persistent historical price data storage
- Interactive price charts with Plotly
```

**After**:
```markdown
# ETF Analysis Platform 📊

A comprehensive ETF and stock analysis platform with a modern Next.js frontend and FastAPI backend.

## Architecture

- **Frontend**: Next.js 16 with React 19 and shadcn/ui
- **Backend**: FastAPI with Python 3.11+
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis

## Features

✨ **Modern Dashboard**
- Drag-and-drop widget management
- Responsive design for all devices
- Real-time data updates

📈 **Portfolio Analysis**
- Interactive charts and visualizations
- Monte Carlo simulations
- Portfolio optimization
- Risk analysis

📊 **Comparative Analysis**
- Compare multiple instruments
- Benchmark tracking
- Performance metrics

## Quick Start

### Development

```bash
# Start all services
docker-compose up

# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production Deployment

See [docs/deployment.md](docs/deployment.md) for production setup.

## Migration from Streamlit

If you're migrating from the legacy Streamlit interface, see [docs/migration-guide.md](docs/migration-guide.md).
```

---

### 6. Cloud Deployment Configurations

#### 6.1 Google Cloud Platform (if used)

**Files to Update**:
- `cloudbuild.yaml` - Remove Streamlit build steps
- `trigger.yaml` - Update deployment triggers

**Current** (`cloudbuild.yaml`):
```yaml
steps:
  # Build Streamlit container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/etf-streamlit', '-f', 'Dockerfile', '.']
  
  # Push Streamlit container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/etf-streamlit']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args: ['gcloud', 'run', 'deploy', 'etf-dashboard', '--image', 'gcr.io/$PROJECT_ID/etf-streamlit']
```

**After** (remove Streamlit, focus on API + Frontend):
```yaml
steps:
  # Build FastAPI container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/etf-api', '-f', 'Dockerfile.api', '.']
  
  # Push FastAPI container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/etf-api']
  
  # Deploy API to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args: ['gcloud', 'run', 'deploy', 'etf-api', '--image', 'gcr.io/$PROJECT_ID/etf-api']
  
  # Build Next.js frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/etf-frontend', '-f', 'frontend/v1/Dockerfile', './frontend/v1']
  
  # Push frontend container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/etf-frontend']
  
  # Deploy frontend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args: ['gcloud', 'run', 'deploy', 'etf-frontend', '--image', 'gcr.io/$PROJECT_ID/etf-frontend']
```

---

#### 6.2 CI/CD Pipeline (GitHub Actions, etc.)

**Files**: `.github/workflows/*.yml`

**Action**: Update to remove Streamlit builds/tests

**Before**:
```yaml
- name: Test Streamlit
  run: |
    pytest tests/streamlit/
    streamlit run app.py --headless &
    # ... Streamlit-specific tests
```

**After**:
```yaml
- name: Test API
  run: |
    pytest tests/api/
    pytest tests/services/
    
- name: Test Frontend
  run: |
    cd frontend/v1
    npm run test
    npm run build
```

---

### 7. Environment Variables

**Files**: `.env`, `.env.example`, deployment configs

**Action**: Remove Streamlit-specific variables

**Before**:
```env
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_ENABLED=true
STREAMLIT_READ_ONLY=false

# API Configuration
API_PORT=8000
# ...
```

**After**:
```env
# Remove all STREAMLIT_* variables

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Frontend Configuration  
NEXT_PUBLIC_API_URL=http://localhost:8000
# ...
```

---

### 8. Documentation Files

**Files to Update**:

1. **README.md** - Main project documentation
   - Remove Streamlit references
   - Add Next.js setup instructions
   - Update architecture diagrams

2. **docs/deployment.md** (if exists)
   - Remove Streamlit deployment instructions
   - Add Next.js deployment instructions
   - Update port mappings

3. **docs/development.md** (if exists)
   - Remove Streamlit development setup
   - Add Next.js development setup
   - Update local testing instructions

4. **CONTRIBUTING.md** (if exists)
   - Remove Streamlit contribution guidelines
   - Add Next.js/React guidelines
   - Update code style guides

---

## Migration Checklist

### Pre-Removal Verification
- [ ] Verify all business logic extracted to services
- [ ] Verify all API endpoints working
- [ ] Verify Next.js has feature parity
- [ ] Verify users migrated (90%+)
- [ ] Create backup branch with Streamlit code

### File Removal
- [ ] Delete `Dockerfile` (Streamlit container)
- [ ] Delete `app.py` (Streamlit entry point)
- [ ] Delete `pages/` directory
- [ ] Delete `src/controllers/` directory
- [ ] Delete `src/widgets/` directory
- [ ] Delete `.streamlit/` directory

### Configuration Updates
- [ ] Update `docker-compose.yml` - remove streamlit service
- [ ] Update `requirements.txt` - remove streamlit package
- [ ] Update `README.md` - remove Streamlit documentation
- [ ] Update `cloudbuild.yaml` - remove Streamlit builds (if used)
- [ ] Update `.env.example` - remove Streamlit variables
- [ ] Update CI/CD pipelines - remove Streamlit tests

### Deployment Updates
- [ ] Update production deployment scripts
- [ ] Remove Streamlit Cloud Run service (if used)
- [ ] Update load balancer / routing (if applicable)
- [ ] Update DNS records (if applicable)
- [ ] Update monitoring / alerts

### Documentation Updates
- [ ] Update README with new architecture
- [ ] Update deployment documentation
- [ ] Update development setup guide
- [ ] Add migration guide for future reference
- [ ] Update architecture diagrams

### Post-Removal Verification
- [ ] Test API deployments
- [ ] Test frontend deployments
- [ ] Verify database connections
- [ ] Verify task queue working
- [ ] Run full test suite
- [ ] Monitor production for 48 hours
- [ ] Collect user feedback

---

## Rollback Plan

If issues arise after removal:

### Quick Rollback (Re-enable Streamlit)
```bash
# 1. Restore from backup branch
git checkout archive/streamlit-backup

# 2. Cherry-pick deployment configs
git checkout main docker-compose.yml
git checkout archive/streamlit-backup -- Dockerfile app.py pages/ src/controllers/ src/widgets/

# 3. Re-add streamlit to requirements.txt
echo "streamlit==1.29.0" >> requirements.txt

# 4. Restore streamlit service in docker-compose.yml
# (manually edit to add back streamlit service)

# 5. Redeploy
docker-compose up --build
```

### Full Rollback (Production)
```bash
# 1. Restore previous container images
gcloud run deploy etf-dashboard \
  --image gcr.io/$PROJECT_ID/etf-streamlit:previous-tag

# 2. Update DNS / routing to point back to Streamlit

# 3. Monitor and stabilize

# 4. Investigate issues before attempting removal again
```

---

## Timeline for Configuration Updates

### During Deprecation Period (Weeks 1-7)
- Keep Streamlit configurations
- Add deprecation warnings
- Monitor both interfaces

### After Removal (Week 8)
- Remove Streamlit configurations
- Update all documentation
- Clean up deployment scripts

### Post-Removal (Week 9+)
- Monitor production stability
- Remove backup configurations
- Archive documentation

---

## Testing Strategy

### Before Removal
```bash
# Test API independently
curl http://localhost:8000/api/portfolio/summary
curl http://localhost:8000/api/widgets/

# Test Next.js independently
curl http://localhost:3000

# Test database connections
docker-compose exec postgres psql -U postgres -d etf_analysis -c "SELECT COUNT(*) FROM instruments;"

# Test task queue
docker-compose exec api python -c "from src.api.tasks import test_task; test_task.delay()"
```

### After Removal
```bash
# Verify no Streamlit references
grep -r "streamlit" . --exclude-dir=.git --exclude-dir=node_modules

# Verify containers build
docker-compose build

# Verify services start
docker-compose up

# Run test suite
pytest

# Check for broken imports
python -m py_compile src/**/*.py
```

---

## Monitoring Post-Removal

### Metrics to Watch
1. **API Response Times**: Should stay same or improve
2. **Error Rates**: Should not increase
3. **User Sessions**: Verify users accessing Next.js
4. **Database Load**: Should decrease (fewer connections)
5. **Memory Usage**: Should decrease (no Streamlit process)

### Alerts to Set
- API error rate > 1%
- Frontend build failures
- Database connection errors
- Task queue backlog

---

## Cost Impact

### Expected Savings
- **Compute**: -1 Cloud Run service (Streamlit)
- **Memory**: -500MB RAM (Streamlit process)
- **Container Registry**: -1 image to build/store
- **CI/CD**: Faster builds (skip Streamlit tests)

### Estimated Savings: **15-20% reduction** in cloud costs

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Next Review**: After Streamlit removal
