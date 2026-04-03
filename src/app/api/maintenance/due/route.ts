import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const mockAssets = [
      {
        id: 'AST-005',
        name: 'Body Armor Plate Carrier',
        lastServiced: new Date(Date.now() - 2592000000).toISOString(),
        daysUntilDue: 5,
      },
      {
        id: 'AST-012',
        name: 'Night Vision Goggles',
        lastServiced: new Date(Date.now() - 5184000000).toISOString(),
        daysUntilDue: 18,
      },
      {
        id: 'AST-018',
        name: 'Communication Radio',
        lastServiced: new Date(Date.now() - 7776000000).toISOString(),
        daysUntilDue: 45,
      },
    ];

    return NextResponse.json({ assets: mockAssets });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch maintenance data' },
      { status: 500 }
    );
  }
}
