import { NextRequest, NextResponse } from 'next/server';
import { Batch } from '@/types/batch';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { assetIds, transporterId, destination, expectedDelivery } = body;

    if (!assetIds || !transporterId || !destination || !expectedDelivery) {
      return NextResponse.json(
        { error: 'All fields are required' },
        { status: 400 }
      );
    }

    const newBatch: Batch = {
      id: `BATCH-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      assetsCount: assetIds.length,
      transporter: transporterId,
      status: 'PENDING',
      destination,
      createdAt: new Date().toISOString(),
    };

    return NextResponse.json({
      batch: newBatch,
      message: 'Batch created successfully'
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create batch' },
      { status: 500 }
    );
  }
}
