import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const benchmarkSymbol = searchParams.get('benchmark_symbol') || 'SPY';
    const timePeriod = searchParams.get('time_period') || '1Y';
    
    const backendUrl = `${API_BASE_URL}/api/widgets/benchmark-comparison?portfolio_id=${portfolioId || 'default'}&benchmark=${benchmarkSymbol}&time_period=${timePeriod}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return NextResponse.json({
        widget_name: 'benchmark_comparison',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: { portfolio_id: portfolioId || 'default', benchmark_symbol: benchmarkSymbol, time_period: timePeriod },
          widget_description: 'Benchmark Comparison Widget'
        },
        error: { code: `HTTP_${response.status}`, message: `Backend API error: ${response.status}` }
      }, { status: 200 });
    }

    const data = await response.json();
    
    return NextResponse.json({
      widget_name: 'benchmark_comparison',
      success: true,
      data: data.data || data,
      metadata: {
        execution_time: data.metadata?.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default', benchmark_symbol: benchmarkSymbol, time_period: timePeriod },
        widget_description: 'Benchmark Comparison Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching benchmark comparison:', error);
    return NextResponse.json({
      widget_name: 'benchmark_comparison',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: {}, widget_description: 'Benchmark Comparison Widget' },
      error: { code: 'INTERNAL_ERROR', message: error instanceof Error ? error.message : 'Unknown error' }
    }, { status: 200 });
  }
}
