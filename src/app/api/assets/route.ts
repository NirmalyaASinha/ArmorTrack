import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    // Get token from headers
    const authHeader = request.headers.get('authorization');
    
    // Call FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/assets`, {
      headers: {
        'Authorization': authHeader || '',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to fetch assets' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({ assets: data });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch assets' },
      { status: 500 }
    );
  }
}
