# Frontend

This directory contains the frontend implementation for the ETF Analysis Dashboard.

## Production Application
- **Technology**: Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- **UI Components**: shadcn/ui with Radix UI primitives
- **Status**: Production Ready
- **Features**: Server-side rendering, authentication context, protected routes, responsive design
- **Development**: `cd v1 && npm install && npm run dev`
- **Port**: http://localhost:3000

## API Integration

Both versions connect to the FastAPI backend at:
- **API Base URL**: http://localhost:8000/api
- **Authentication**: JWT tokens
- **Endpoints**: Portfolio, simulation, optimization, instruments

## Quick Start

```bash
cd frontend/v1
npm install
npm run dev
```

Access the dashboard at http://localhost:3000

## Architecture Migration Status

- ✅ Phase 6: REST API Infrastructure Complete
- ✅ Phase 7: Widget Integration Complete  
- 🚧 Phase 8: Frontend Development (Current)
  - ✅ T074: Frontend project initialization
  - 🔄 T075-T084: Component development and integration