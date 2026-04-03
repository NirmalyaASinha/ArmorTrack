import { NextRequest, NextResponse } from 'next/server';
import { Asset } from '@/types/asset';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, type } = body;

    if (!name || !type) {
      return NextResponse.json(
        { error: 'Name and type are required' },
        { status: 400 }
      );
    }

    // Generate mock asset
    const newAsset: Asset = {
      id: `AST-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      name,
      type,
      status: 'WAREHOUSE',
      currentCustodian: 'Warehouse A',
      lastUpdated: new Date().toISOString(),
    };

    return NextResponse.json({
      asset: newAsset,
      message: 'Asset registered successfully'
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to register asset' },
      { status: 500 }
    );
  }
}
