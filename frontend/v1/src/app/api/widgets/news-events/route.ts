import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const portfolioId = searchParams.get('portfolio_id');
    const timePeriod = searchParams.get('time_period') || '1M';
    
    // Backend doesn't have this endpoint yet
    return NextResponse.json({
      widget_name: 'news_event_analysis',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: { portfolio_id: portfolioId || 'default', time_period: timePeriod }, widget_description: 'News & Events Analysis Widget' },
      error: { code: 'NOT_IMPLEMENTED', message: 'News event analysis not yet implemented in backend' }
    });

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return NextResponse.json({
        widget_name: 'news_event_analysis',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: { portfolio_id: portfolioId || 'default', time_period: timePeriod },
          widget_description: 'News & Events Analysis Widget'
        },
        error: { code: `HTTP_${response.status}`, message: `Backend API error: ${response.status}` }
      }, { status: 200 });
    }

    const data = await response.json();
    
    return NextResponse.json({
      widget_name: 'news_event_analysis',
      success: true,
      data: data.data || data,
      metadata: {
        execution_time: data.metadata?.execution_time || '0ms',
        parameters: { portfolio_id: portfolioId || 'default', time_period: timePeriod },
        widget_description: 'News & Events Analysis Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching news event analysis:', error);
    return NextResponse.json({
      widget_name: 'news_event_analysis',
      success: false,
      data: null,
      metadata: { execution_time: '0ms', parameters: {}, widget_description: 'News & Events Analysis Widget' },
      error: { code: 'INTERNAL_ERROR', message: error instanceof Error ? error.message : 'Unknown error' }
    }, { status: 200 });
  }
}
