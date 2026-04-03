import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const mockAssets = [
      { id: 'AST-001', name: 'M4 Carbine Rifle', daysUntilDue: 120 },
      { id: 'AST-002', name: 'Humvee H1', daysUntilDue: 45 },
      { id: 'AST-005', name: 'Body Armor Plate Carrier', daysUntilDue: 5 },
      { id: 'AST-012', name: 'Night Vision Goggles', daysUntilDue: 18 },
      { id: 'AST-018', name: 'Communication Radio', daysUntilDue: 45 },
    ];

    return NextResponse.json({ assets: mockAssets });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch assets' },
      { status: 500 }
    );
  }
}
