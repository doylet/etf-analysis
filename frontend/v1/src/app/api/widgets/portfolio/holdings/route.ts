import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

interface BackendHolding {
  symbol: string;
  name: string;
  type: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_pct: number;
  weight_pct: number;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const breakdownType = searchParams.get('breakdown_type') || 'sector';
    
    // Backend returns array directly, not an object
    const backendUrl = `${API_BASE_URL}/api/portfolio/holdings`;

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

    // Backend returns array of holdings directly
    const holdings = await response.json() as BackendHolding[];
    
    // Calculate total value
    const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
    
    // Transform backend response to widget response format
    return NextResponse.json({
      widget_name: 'holdings_breakdown',
      success: true,
      data: {
        holdings: holdings.map((holding) => ({
          symbol: holding.symbol,
          name: holding.name || holding.symbol,
          shares: holding.quantity || 0,
          current_price: holding.current_price || 0,
          current_value: holding.current_value || 0,
          weight_percent: holding.weight_pct || 0,
          day_change: 0, // Backend doesn't provide yet
          day_change_percent: 0, // Backend doesn't provide yet
          total_return: holding.unrealized_gain_loss || 0,
          total_return_percent: holding.unrealized_gain_loss_pct || 0
        })),
        breakdown: [], // Backend doesn't provide breakdown yet
        breakdown_type: breakdownType,
        total_value: totalValue,
        last_updated: new Date().toISOString()
      },
      metadata: {
        execution_time: '0ms',
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
