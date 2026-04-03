"use client";

import { useState, useEffect } from 'react';
import { Plus, ChevronRight, CheckCircle, XCircle } from 'lucide-react';
import { Batch, BatchAsset } from '@/types/batch';
import { getToken } from '@/lib/auth';
import toast from 'react-hot-toast';

export default function BatchesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchBatches = async () => {
    try {
      const token = getToken();
      const response = await fetch('/api/batches', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setBatches(data.batches);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const handleBatchClick = (batch: Batch) => {
    // Mock batch details with assets
    const mockAssets: BatchAsset[] = [
      { assetId: 'AST-001', assetName: 'M4 Carbine Rifle', scanStatus: 'SCANNED' },
      { assetId: 'AST-002', assetName: 'Humvee H1', scanStatus: 'NOT_SCANNED' },
      { assetId: 'AST-003', assetName: 'Radio Set AN/PRC-152', scanStatus: 'SCANNED' },
    ];
    setSelectedBatch({ ...batch, assets: mockAssets });
    setDrawerOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const config = {
      PENDING: 'badge-ghost',
      IN_TRANSIT: 'badge-info',
      DELIVERED: 'badge-success',
    };
    return config[status as keyof typeof config] || 'badge-ghost';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <span className="loading loading-spinner loading-lg text-primary"></span>
          <p className="text-base-content/70 uppercase tracking-wider">Loading batches...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-base-content uppercase tracking-wider">
            Batch Management
          </h1>
          <p className="text-base-content/60 mt-1">
            Track and manage asset batches
          </p>
        </div>
        <button
          onClick={() => (document.getElementById('create_batch_modal') as HTMLDialogElement)?.showModal()}
          className="btn btn-primary military-button"
        >
          <Plus className="w-5 h-5" />
          Create Batch
        </button>
      </div>

      {/* Batches Table */}
      <div className="card bg-base-100 shadow-xl military-card">
        <div className="card-body p-0">
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr className="bg-base-200">
                  <th className="uppercase tracking-wider text-sm">Batch ID</th>
                  <th className="uppercase tracking-wider text-sm">Assets Count</th>
                  <th className="uppercase tracking-wider text-sm">Transporter</th>
                  <th className="uppercase tracking-wider text-sm">Status</th>
                  <th className="uppercase tracking-wider text-sm">Destination</th>
                  <th className="uppercase tracking-wider text-sm">Created At</th>
                  <th className="uppercase tracking-wider text-sm"></th>
                </tr>
              </thead>
              <tbody>
                {batches.map((batch) => (
                  <tr
                    key={batch.id}
                    className="hover:bg-base-200/50 cursor-pointer"
                    onClick={() => handleBatchClick(batch)}
                  >
                    <td className="font-mono font-bold text-primary">{batch.id}</td>
                    <td>{batch.assetsCount}</td>
                    <td>{batch.transporter}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(batch.status)} badge-sm font-semibold uppercase`}>
                        {batch.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>{batch.destination}</td>
                    <td className="text-base-content/70">
                      {new Date(batch.createdAt).toLocaleString()}
                    </td>
                    <td>
                      <ChevronRight className="w-5 h-5 text-base-content/40" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Batch Detail Drawer */}
      {selectedBatch && (
        <>
          <div className={`drawer ${drawerOpen ? 'drawer-open' : ''}`}>
            <input id="batch-drawer" type="checkbox" className="drawer-toggle" checked={drawerOpen} onChange={() => setDrawerOpen(!drawerOpen)} />
            <div className="drawer-content"></div>
            <div className="drawer-side z-50">
              <label htmlFor="batch-drawer" className="drawer-overlay" onClick={() => setDrawerOpen(false)}></label>
              <div className="bg-base-100 min-h-full w-80 md:w-96 p-6 overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold uppercase tracking-wider">Batch Details</h2>
                  <button onClick={() => setDrawerOpen(false)} className="btn btn-sm btn-circle btn-ghost">✕</button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-base-content/60 uppercase">Batch ID</p>
                    <p className="font-mono font-bold text-primary">{selectedBatch.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-base-content/60 uppercase">Transporter</p>
                    <p className="font-semibold">{selectedBatch.transporter}</p>
                  </div>
                  <div>
                    <p className="text-sm text-base-content/60 uppercase">Destination</p>
                    <p>{selectedBatch.destination}</p>
                  </div>
                  <div>
                    <p className="text-sm text-base-content/60 uppercase">Status</p>
                    <span className={`badge ${getStatusBadge(selectedBatch.status)} font-semibold uppercase`}>
                      {selectedBatch.status.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="divider"></div>

                  <h3 className="font-bold uppercase tracking-wider">Assets in Batch</h3>
                  <div className="space-y-2">
                    {selectedBatch.assets?.map((asset) => (
                      <div key={asset.assetId} className="card bg-base-200 p-3">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-mono text-sm text-primary">{asset.assetId}</p>
                            <p className="text-sm">{asset.assetName}</p>
                          </div>
                          {asset.scanStatus === 'SCANNED' ? (
                            <div className="flex items-center gap-1 text-success">
                              <CheckCircle className="w-4 h-4" />
                              <span className="text-xs font-semibold uppercase">Scanned</span>
                            </div>
                          ) : (
                            <div className="flex items-center gap-1 text-warning">
                              <XCircle className="w-4 h-4" />
                              <span className="text-xs font-semibold uppercase">Not Scanned</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Create Batch Modal */}
      <dialog id="create_batch_modal" className="modal">
        <div className="modal-box bg-base-100 military-card max-w-2xl">
          <button onClick={() => (document.getElementById('create_batch_modal') as HTMLDialogElement)?.close()} className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
          <h3 className="font-bold text-xl uppercase tracking-wider mb-6">Create New Batch</h3>
          <form onSubmit={async (e) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            const data = {
              assetIds: ['AST-001', 'AST-002'],
              transporterId: formData.get('transporter'),
              destination: formData.get('destination'),
              expectedDelivery: formData.get('expectedDelivery'),
            };
            
            try {
              const token = getToken();
              const response = await fetch('/api/batches/create', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(data),
              });
              const result = await response.json();
              if (response.ok) {
                toast.success(result.message);
                (e.target as HTMLFormElement).reset();
                const modal = document.getElementById('create_batch_modal') as HTMLDialogElement;
                if (modal) modal.close();
                fetchBatches();
              } else {
                toast.error(result.error);
              }
            } catch (error: any) {
              toast.error(error.message);
            }
          }} className="space-y-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text font-semibold uppercase text-sm">Transporter</span>
              </label>
              <select name="transporter" className="select select-bordered w-full military-input" required>
                <option value="" disabled>Select transporter</option>
                <option value="Transport Unit Alpha">Transport Unit Alpha</option>
                <option value="Transport Unit Bravo">Transport Unit Bravo</option>
                <option value="Transport Unit Charlie">Transport Unit Charlie</option>
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text font-semibold uppercase text-sm">Destination</span>
              </label>
              <input type="text" name="destination" placeholder="Enter destination" className="input input-bordered w-full military-input" required />
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text font-semibold uppercase text-sm">Expected Delivery</span>
              </label>
              <input type="datetime-local" name="expectedDelivery" className="input input-bordered w-full military-input" required />
            </div>

            <div className="modal-action">
              <button type="button" onClick={() => (document.getElementById('create_batch_modal') as HTMLDialogElement)?.close()} className="btn btn-ghost mr-2">Cancel</button>
              <button type="submit" className="btn btn-primary military-button">Create Batch</button>
            </div>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>
    </div>
  );
}
