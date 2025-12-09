import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const constraints = searchParams.get('constraints');
    
    const backendUrl = `${API_BASE_URL}/api/v1/widgets/constrained-optimization?portfolio_id=${portfolioId || 'default'}${constraints ? `&constraints=${constraints}` : ''}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return NextResponse.json({
        widget_name: 'constrained_optimization',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: { portfolio_id: portfolioId || 'default' },
          widget_description: 'Constrained Optimization Widget'
        },
        error: { code: `HTTP_${response.status}`, message: `Backend API error: ${response.status}` }
      }, { status: 200 });
    }

    const data = await response.json();
    
    return NextResponse.json({
      widget_name: 'constrained_optimization',
      success: true,
      data: data.data || data,
      metadata: {
        execution_time: data.metadata?.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default' },
        widget_description: 'Constrained Optimization Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching constrained optimization:', error);
    return NextResponse.json({
      widget_name: 'constrained_optimization',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: {}, widget_description: 'Constrained Optimization Widget' },
      error: { code: 'INTERNAL_ERROR', message: error instanceof Error ? error.message : 'Unknown error' }
    }, { status: 200 });
  }
}
