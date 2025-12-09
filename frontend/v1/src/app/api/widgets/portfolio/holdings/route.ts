import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const breakdownType = searchParams.get('breakdown_type') || 'sector';
    
    const backendUrl = portfolioId 
      ? `${API_BASE_URL}/api/portfolio/holdings?portfolio_id=${portfolioId}&breakdown_type=${breakdownType}`
      : `${API_BASE_URL}/api/portfolio/holdings?breakdown_type=${breakdownType}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        {
          widget_name: 'holdings_breakdown',
          success: false,
          data: null,
          metadata: {
            execution_time: '0ms',
            parameters: { portfolio_id: portfolioId || 'default', breakdown_type: breakdownType },
            widget_description: 'Holdings Breakdown Widget'
          },
          error: {
            code: `HTTP_${response.status}`,
            message: error.detail || `Backend API error: ${response.status}`,
            details: error
          }
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Transform backend response to widget response format
    return NextResponse.json({
      widget_name: 'holdings_breakdown',
      success: true,
      data: {
        holdings: (data.holdings || []).map((holding: any) => ({
          symbol: holding.symbol,
          name: holding.instrument?.name || holding.symbol,
          shares: holding.quantity || 0,
          current_price: holding.current_price || 0,
          current_value: holding.market_value || 0,
          weight_percent: holding.weight || 0,
          day_change: 0, // Backend doesn't provide yet
          day_change_percent: 0, // Backend doesn't provide yet
          total_return: holding.unrealized_gain_loss || 0,
          total_return_percent: holding.unrealized_gain_loss_pct || 0
        })),
        breakdown: data.breakdown || [],
        breakdown_type: breakdownType,
        total_value: data.total_value || 0,
        last_updated: new Date().toISOString()
      },
      metadata: {
        execution_time: data.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default', breakdown_type: breakdownType },
        widget_description: 'Holdings Breakdown Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching holdings breakdown:', error);
    return NextResponse.json(
      {
        widget_name: 'holdings_breakdown',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: {},
          widget_description: 'Holdings Breakdown Widget'
        },
        error: {
          code: 'INTERNAL_ERROR',
          message: error instanceof Error ? error.message : 'Failed to fetch holdings breakdown',
          details: {}
        }
      },
      { status: 500 }
    );
  }
}
