export interface Batch {
  id: string;
  assetsCount: number;
  transporter: string;
  status: 'PENDING' | 'IN_TRANSIT' | 'DELIVERED';
  destination: string;
  createdAt: string;
  assets?: BatchAsset[];
}

export interface BatchAsset {
  assetId: string;
  assetName: string;
  scanStatus: 'SCANNED' | 'NOT_SCANNED';
}

export interface CreateBatchInput {
  assetIds: string[];
  transporterId: string;
  destination: string;
  expectedDelivery: string;
}
