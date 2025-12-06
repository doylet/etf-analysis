import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/portfolio/summary`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Transform the backend data to match the frontend interface
    const transformedData = {
      total_value: data.total_value,
      total_return: data.total_unrealized_gain_loss,
      total_return_percent: data.total_unrealized_gain_loss_pct,
      day_change: 0, // Backend doesn't provide day change yet
      day_change_percent: 0, // Backend doesn't provide day change yet
      positions: data.num_holdings,
      cash: 0, // Backend doesn't provide cash separately yet
    };

    return NextResponse.json(transformedData);
  } catch (error) {
    console.error('Error fetching portfolio summary:', error);
    return NextResponse.json(
      { error: 'Failed to fetch portfolio summary' },
      { status: 500 }
    );
  }
}