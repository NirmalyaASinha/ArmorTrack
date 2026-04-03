import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Mock validation
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      );
    }

    // Mock authentication (replace with real auth logic)
    if (password.length < 6) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Mock JWT token (in production, use proper JWT signing)
    const mockToken = `mock_jwt_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    
    // Determine role based on email (for demo purposes)
    let role = 'ADMIN';
    if (email.includes('auditor')) role = 'AUDITOR';
    else if (email.includes('warehouse')) role = 'WAREHOUSE';
    else if (email.includes('transporter')) role = 'TRANSPORTER';
    else if (email.includes('manufacturer')) role = 'MANUFACTURER';

    return NextResponse.json({
      token: mockToken,
      user: {
        email,
        name: email.split('@')[0],
        role
      }
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
