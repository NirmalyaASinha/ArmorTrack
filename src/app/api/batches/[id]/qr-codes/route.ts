import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const authHeader = request.headers.get('authorization');

    const response = await fetch(`${BACKEND_URL}/api/batches/${params.id}/qr-codes`, {
      headers: { 'Authorization': authHeader || '' },
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      return NextResponse.json({ error: data.detail || 'QR codes not found' }, { status: response.status });
    }

    const buffer = await response.arrayBuffer();
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename=qr-codes-${params.id.substring(0, 8)}.zip`,
      },
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to download QR codes' }, { status: 500 });
  }
}
