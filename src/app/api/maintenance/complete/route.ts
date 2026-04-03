import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { asset_id } = body;

    if (!asset_id) {
      return NextResponse.json(
        { error: 'Asset ID is required' },
        { status: 400 }
      );
    }

    return NextResponse.json({
      message: 'Maintenance marked complete',
      asset_id
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update maintenance' },
      { status: 500 }
    );
  }
}
