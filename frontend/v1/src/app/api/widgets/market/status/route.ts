import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Provide basic market status without backend dependency
    return NextResponse.json({
      widget_name: 'market_status',
      success: true,
      data: {
        isOpen: true,
        marketHours: {
          open: '09:30',
          close: '16:00',
          timezone: 'America/New_York'
        },
        nextOpen: null,
        nextClose: null,
        currentTime: new Date().toISOString()
      },
      metadata: {
        execution_time: '1ms',
        parameters: {},
        widget_description: 'Market Status Widget',
        cache_hit: false
      },
      error: null
    });
  } catch (error) {
    console.error('Error fetching market status:', error);
    return NextResponse.json(
      {
        widget_name: 'market_status',
        success: false,
        data: null,
        metadata: {
          execution_time: '0ms',
          parameters: {},
          widget_description: 'Market Status Widget'
        },
        error: {
          code: 'INTERNAL_ERROR',
          message: error instanceof Error ? error.message : 'Failed to fetch market status',
          details: {}
        }
      },
      { status: 500 }
    );
  }
}
