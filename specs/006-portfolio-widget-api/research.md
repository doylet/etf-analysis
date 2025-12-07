# Research: Portfolio Widget API Integration

**Feature**: Portfolio Widget API Integration  
**Date**: 2025-12-07  
**Purpose**: Address technical decisions and approach for exposing portfolio analysis widgets via REST API

## Technical Decisions

### Decision: Widget-to-API Adapter Pattern
**Chosen**: Create adapter classes that wrap existing widget logic and return JSON-serializable data
**Rationale**: Preserves existing mathematical calculations and testing while enabling API access
**Alternatives considered**: 
- Direct widget modification: Rejected due to coupling with Streamlit UI
- Complete rewrite: Rejected due to risk of calculation errors and time investment

### Decision: Existing FastAPI Infrastructure
**Chosen**: Extend current FastAPI application with new widget-specific routers
**Rationale**: FastAPI infrastructure already exists with authentication, error handling, and OpenAPI docs
**Alternatives considered**:
- Separate microservice: Rejected due to added complexity for single-feature scope
- GraphQL API: Rejected due to team familiarity and REST being sufficient for current needs

### Decision: Progressive Widget Exposure
**Chosen**: Start with high-value widgets (Portfolio Summary, Holdings Breakdown) and expand incrementally
**Rationale**: Enables MVP delivery while managing complexity and testing scope
**Alternatives considered**:
- All widgets at once: Rejected due to increased implementation and testing scope
- Single widget: Rejected as insufficient for meaningful frontend integration

## API Design Patterns

### Request/Response Structure
- **Widget Configuration**: Accept parameters like time periods, benchmarks, analysis settings
- **Data Payload**: Return structured calculation results with metadata
- **Error Handling**: Distinguish between insufficient data vs calculation errors
- **Caching**: Leverage existing data layer caching for performance

### Authentication & Authorization
- **Current**: JWT-based authentication already implemented in FastAPI app
- **Widget Access**: All widgets require authentication but no additional authorization needed
- **Rate Limiting**: Consider for computationally expensive widgets (Monte Carlo, Optimization)

## Integration Approach

### Frontend Integration Points
- **Existing Components**: PortfolioSummary.tsx already demonstrates API consumption pattern
- **Data Visualization**: Leverage existing Recharts integration for chart data
- **State Management**: Use existing React hooks pattern for API calls
- **Error Boundaries**: Extend existing error handling for widget-specific errors

### Backend Architecture Alignment
- **Service Layer**: Widget adapters will use existing service layer where available
- **Repository Pattern**: Leverage existing data access patterns for consistency
- **Domain Models**: Map widget outputs to existing or new domain model structures

## Performance Considerations

### Computational Widgets
- **Monte Carlo Simulations**: Already have async task infrastructure via Celery
- **Optimization Calculations**: May require request timeouts and progress indicators  
- **Real-time Data**: Cache expensive calculations with appropriate TTL

### Data Loading
- **Bulk Price Data**: Leverage existing price data caching mechanisms
- **Portfolio State**: Use existing portfolio summary caching where applicable
- **Incremental Updates**: Design for partial data updates where possible

## Risk Mitigation

### Calculation Accuracy
- **Testing Strategy**: Compare API outputs with original widget outputs in tests
- **Validation**: Include data quality metadata in responses
- **Fallback**: Graceful degradation when insufficient data available

### Performance Impact
- **Resource Usage**: Monitor memory/CPU impact of concurrent widget calculations
- **Database Load**: Ensure efficient data access patterns for multiple simultaneous requests
- **Client Experience**: Implement proper loading states and error handling in frontend

## Implementation Phases

### Phase 1: Foundation (Core Widgets)
1. **Portfolio Summary API**: Expose basic performance metrics (builds on existing `/api/portfolio/summary`)
2. **Holdings Breakdown API**: Sector, geography, asset class allocation data
3. **Frontend Integration**: Update existing components to consume new endpoints

### Phase 2: Advanced Analytics
1. **Correlation Matrix API**: Holdings and benchmark correlation calculations
2. **Performance Analysis API**: Time-series performance with benchmark comparison
3. **Risk Metrics API**: Volatility, drawdown, and risk-adjusted returns

### Phase 3: Complex Calculations
1. **Monte Carlo API**: Portfolio simulation with various parameters
2. **Optimization API**: Efficient frontier and portfolio optimization
3. **Advanced Features**: News analysis, dividend tracking, transition planning

## Technology Validation

### Existing Infrastructure Suitability
- ✅ **FastAPI Framework**: Production-ready with authentication and docs
- ✅ **Widget Logic**: Proven calculation accuracy in existing Streamlit widgets  
- ✅ **Data Layer**: SQLAlchemy models support required portfolio data access
- ✅ **Frontend Framework**: NextJS app ready for API integration
- ✅ **Testing Infrastructure**: pytest with coverage requirements established

### Dependencies Assessment
- ✅ **No new major dependencies**: Feature uses existing technology stack
- ✅ **JSON Serialization**: Pydantic models handle complex data structures
- ✅ **Async Support**: FastAPI async capabilities available for expensive operations
- ⚠️  **Memory Usage**: Monitor impact of simultaneous complex calculations

## Success Metrics

### Technical Metrics
- API response times within performance goals (<3s basic, <30s complex)
- Widget calculation accuracy matches existing Streamlit outputs
- Frontend integration maintains existing UX patterns
- Test coverage maintains 80%+ requirement

### Business Value
- Reduced time to access portfolio analytics (target: 60% improvement)
- Increased user engagement with advanced analytics features
- Foundation for future mobile/external integrations