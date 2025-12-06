# Frontend Versions

This directory contains different frontend implementations for the ETF Analysis Dashboard.

## V0 - React + Vite POC
- **Technology**: React 18 + TypeScript + Vite
- **Status**: Proof of Concept
- **Features**: Basic authentication, portfolio summary, dashboard
- **Development**: `cd v0 && npm install && npm run dev`
- **Port**: http://localhost:5173

## V1 - NextJS Production
- **Technology**: Next.js 14 + TypeScript + Tailwind CSS
- **Status**: Production Ready
- **Features**: Server-side rendering, authentication context, protected routes
- **Development**: `cd v1 && npm install && npm run dev`
- **Port**: http://localhost:3000

## API Integration

Both versions connect to the FastAPI backend at:
- **API Base URL**: http://localhost:8000/api
- **Authentication**: JWT tokens
- **Endpoints**: Portfolio, simulation, optimization, instruments

## Quick Start

### React POC (V0)
```bash
cd frontend/v0
npm install
npm run dev
```

### NextJS Production (V1)  
```bash
cd frontend/v1
npm install
npm run dev
```

## Architecture Migration Status

- ✅ Phase 6: REST API Infrastructure Complete
- ✅ Phase 7: Widget Integration Complete  
- 🚧 Phase 8: Frontend Development (Current)
  - ✅ T074: Frontend project initialization
  - 🔄 T075-T084: Component development and integration