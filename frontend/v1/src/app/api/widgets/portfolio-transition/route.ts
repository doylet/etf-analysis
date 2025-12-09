import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const targetAllocation = searchParams.get('target_allocation');
    
    // Backend doesn't have this endpoint yet
    return NextResponse.json({
      widget_name: 'portfolio_transition',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: { portfolio_id: portfolioId || 'default' }, widget_description: 'Portfolio Transition Widget' },
      error: { code: 'NOT_IMPLEMENTED', message: 'Portfolio transition not yet implemented in backend' }
    });

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return NextResponse.json({
        widget_name: 'portfolio_transition',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: { portfolio_id: portfolioId || 'default' },
          widget_description: 'Portfolio Transition Widget'
        },
        error: { code: `HTTP_${response.status}`, message: `Backend API error: ${response.status}` }
      }, { status: 200 });
    }

    const data = await response.json();
    
    return NextResponse.json({
      widget_name: 'portfolio_transition',
      success: true,
      data: data.data || data,
      metadata: {
        execution_time: data.metadata?.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default' },
        widget_description: 'Portfolio Transition Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching portfolio transition:', error);
    return NextResponse.json({
      widget_name: 'portfolio_transition',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: {}, widget_description: 'Portfolio Transition Widget' },
      error: { code: 'INTERNAL_ERROR', message: error instanceof Error ? error.message : 'Unknown error' }
    }, { status: 200 });
  }
}
