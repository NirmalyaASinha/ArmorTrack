"use client";

interface StatusBadgeProps {
  status: 'WAREHOUSE' | 'IN_TRANSIT' | 'DEPLOYED' | 'MAINTENANCE_DUE';
}

const statusConfig = {
  WAREHOUSE: { color: 'badge-ghost', label: 'Warehouse' },
  IN_TRANSIT: { color: 'badge-warning', label: 'In Transit' },
  DEPLOYED: { color: 'badge-info', label: 'Deployed' },
  MAINTENANCE_DUE: { color: 'badge-error', label: 'Maintenance Due' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  return (
    <span className={`badge ${config.color} badge-sm font-semibold uppercase tracking-wider`}>
      {config.label}
    </span>
  );
}
