import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');

    // Mock audit logs
    const mockLogs = Array.from({ length: 20 }, (_, i) => ({
      id: `AUD-${String(1000 + i).padStart(4, '0')}`,
      eventType: ['ASSET_REGISTERED', 'BATCH_CREATED', 'CUSTODY_TRANSFER', 'MAINTENANCE'][i % 4],
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      entryHash: `0x${Math.random().toString(16).substring(2, 34)}`,
      prevHash: `0x${Math.random().toString(16).substring(2, 34)}`,
    }));

    return NextResponse.json({ logs: mockLogs });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch audit logs' },
      { status: 500 }
    );
  }
}
