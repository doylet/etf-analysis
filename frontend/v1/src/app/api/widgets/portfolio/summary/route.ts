import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

interface BackendSummaryResponse {
  total_value: number;
  total_unrealized_gain_loss: number;
  total_unrealized_gain_loss_pct: number;
  num_holdings: number;
  execution_time?: string;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    
    const backendUrl = portfolioId 
      ? `${API_BASE_URL}/api/portfolio/summary?portfolio_id=${portfolioId}`
      : `${API_BASE_URL}/api/portfolio/summary`;

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
          widget_name: 'portfolio_summary',
          success: false,
          data: null,
          metadata: {
            execution_time: '0ms',
            parameters: { portfolio_id: portfolioId || 'default' },
            widget_description: 'Portfolio Summary Widget'
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

    const data = await response.json() as BackendSummaryResponse;
    
    // Transform backend response to widget response format
    return NextResponse.json({
      widget_name: 'portfolio_summary',
      success: true,
      data: {
        total_value: data.total_value || 0,
        total_return: data.total_unrealized_gain_loss || 0,
        total_return_percent: data.total_unrealized_gain_loss_pct || 0,
        day_change: 0, // Backend doesn't provide yet
        day_change_percent: 0, // Backend doesn't provide yet
        positions: data.num_holdings || 0,
        allocated_cash: 0, // Backend doesn't provide yet
        last_updated: new Date().toISOString(),
        market_status: {
          isOpen: true,
          nextOpen: null,
          nextClose: null
        }
      },
      metadata: {
        execution_time: data.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default' },
        widget_description: 'Portfolio Summary Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching portfolio summary:', error);
    return NextResponse.json(
      {
        widget_name: 'portfolio_summary',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: {},
          widget_description: 'Portfolio Summary Widget'
        },
        error: {
          code: 'INTERNAL_ERROR',
          message: error instanceof Error ? error.message : 'Failed to fetch portfolio summary',
          details: {}
        }
      },
      { status: 500 }
    );
  }
}
