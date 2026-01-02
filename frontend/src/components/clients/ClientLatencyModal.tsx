/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * ClientLatencyModal Component
 * 
 * Full-featured latency history modal with:
 * - Interactive line chart (Recharts)
 * - Statistics summary (avg, min, max, counts)
 * - Sortable, paginated table
 * - Time range filter (24h, 7d, 30d, all)
 * - Status filter (delivered, sent, failed)
 * - Single entry deletion
 * - Clear all history
 * - CSV export
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, ReferenceLine 
} from 'recharts';

// Brand colors
const neonBlue = '#88CED0';
const cyan = '#22D3EE';

// =============================================================================
// TYPES
// =============================================================================

interface LatencyEntry {
  id: string;
  tracking_id: string;
  sender_name: string;
  recipient_name: string;
  sender_profile: string;
  recipient_profile: string;
  content_preview: string;
  delivery_status: string;
  status_display?: string;
  total_latency_ms: number | null;
  latency_to_server_ms: number | null;
  latency_to_client_ms: number | null;
  sent_at: string;
  client_received_at: string;
  latency_indicator: 'green' | 'yellow' | 'red' | 'gray';
  created_at: string;
}

interface LatencyTimeSeriesPoint {
  timestamp: string;
  latency: number;
  message_id: string;
  sender_profile: string;
  recipient_profile: string;
}

interface LatencyStats {
  avg_latency: number;
  min_latency: number | null;
  max_latency: number | null;
  total_messages: number;
  delivered_count: number;
  failed_count: number;
  pending_count: number;
  time_series: LatencyTimeSeriesPoint[];
  time_range: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: LatencyEntry[];
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  clientId: string;
  clientName: string;
  clientProfile: string;
}

type SortField = 'created_at' | 'total_latency_ms' | 'sender__name' | 'recipient__name' | 'delivery_status';
type SortOrder = 'asc' | 'desc';
type TimeRange = '24h' | '7d' | '30d' | 'all';

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

const getCsrfToken = (): string => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === 'csrftoken') return value;
  }
  return '';
};

const formatTime = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const formatLatency = (ms: number | null): string => {
  if (ms === null) return '-';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'delivered': 
      return <span className="text-lg font-bold" style={{ color: cyan }}>✓✓</span>;
    case 'sent': 
      return <span className="text-lg font-bold" style={{ color: cyan }}>✓</span>;
    case 'failed': 
      return <span className="text-lg font-bold text-red-500">✗</span>;
    default: 
      return <span className="text-lg text-slate-400 animate-pulse">⏳</span>;
  }
};

const LatencyDot = ({ indicator }: { indicator: string }) => {
  const colors: Record<string, string> = {
    green: '#22C55E',
    yellow: '#EAB308',
    red: '#EF4444',
    gray: '#6B7280',
  };
  return (
    <span 
      className="inline-block w-2.5 h-2.5 rounded-full ml-2"
      style={{ backgroundColor: colors[indicator] || colors.gray }}
    />
  );
};

const SortIndicator = ({ field, currentField, order }: { 
  field: SortField; 
  currentField: SortField; 
  order: SortOrder;
}) => {
  if (currentField !== field) {
    return <span className="text-slate-500 ml-1">↕</span>;
  }
  return (
    <span className="ml-1" style={{ color: neonBlue }}>
      {order === 'desc' ? '↓' : '↑'}
    </span>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ClientLatencyModal({ 
  isOpen, 
  onClose, 
  clientId, 
  clientName, 
  clientProfile 
}: Props) {
  const { t } = useTranslation();
  
  // Data state
  const [stats, setStats] = useState<LatencyStats | null>(null);
  const [entries, setEntries] = useState<LatencyEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 50;
  
  // Sorting state
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  
  // Filter state
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [statusFilter, setStatusFilter] = useState<string>('');
  
  // Action state
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [clearAllConfirm, setClearAllConfirm] = useState(false);

  // =========================================================================
  // DATA FETCHING
  // =========================================================================

  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const response = await fetch(
        `/api/v1/clients/${clientId}/latency-stats/?range=${timeRange}`
      );
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching latency stats:', error);
    } finally {
      setStatsLoading(false);
    }
  }, [clientId, timeRange]);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const sort = sortOrder === 'desc' ? `-${sortField}` : sortField;
      let url = `/api/v1/clients/${clientId}/latency-history/?page=${currentPage}&page_size=${pageSize}&sort=${sort}`;
      
      if (statusFilter) {
        url += `&status=${statusFilter}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data: PaginatedResponse = await response.json();
        setEntries(data.results);
        setTotalCount(data.count);
        setTotalPages(Math.ceil(data.count / pageSize));
      }
    } catch (error) {
      console.error('Error fetching latency history:', error);
    } finally {
      setLoading(false);
    }
  }, [clientId, currentPage, sortField, sortOrder, statusFilter]);

  // Initial load when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchStats();
      fetchHistory();
    }
  }, [isOpen, fetchStats, fetchHistory]);

  // =========================================================================
  // HANDLERS
  // =========================================================================

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
    setCurrentPage(1);
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`/api/v1/messages/${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
      });
      if (response.ok) {
        fetchHistory();
        fetchStats();
      }
    } catch (error) {
      console.error('Error deleting message:', error);
    }
    setDeleteConfirm(null);
  };

  const handleClearAll = async () => {
    try {
      const response = await fetch(`/api/v1/clients/${clientId}/reset-messages/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
      });
      if (response.ok) {
        fetchHistory();
        fetchStats();
      }
    } catch (error) {
      console.error('Error clearing history:', error);
    }
    setClearAllConfirm(false);
  };

  const handleExportCSV = () => {
    if (!entries.length) return;
    
    const headers = ['Time', 'From', 'To', 'Latency (ms)', 'Status', 'Content'];
    const rows = entries.map(e => [
      new Date(e.created_at).toLocaleString('de-DE'),
      `${e.sender_name} (${e.sender_profile})`,
      `${e.recipient_name} (${e.recipient_profile})`,
      e.total_latency_ms || '-',
      e.delivery_status,
      `"${e.content_preview.replace(/"/g, '""')}"`,
    ]);
    
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `latency-${clientName}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // =========================================================================
  // RENDER
  // =========================================================================

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 rounded-xl border border-slate-700 w-full max-w-6xl max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📈</span>
            <div>
              <h2 className="text-xl font-semibold" style={{ color: neonBlue }}>
                {t('latencyModal.title')}
              </h2>
              <p className="text-sm text-slate-400">
                {clientName} ({clientProfile})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-auto p-4 space-y-6">
          
          {/* Time Range Selector */}
          <div className="flex items-center gap-2">
            <span className="text-slate-400 text-sm">{t('latencyModal.timeRange')}:</span>
            {(['24h', '7d', '30d', 'all'] as TimeRange[]).map(range => (
              <button
                key={range}
                onClick={() => handleTimeRangeChange(range)}
                className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                  timeRange === range
                    ? 'border'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
                style={timeRange === range ? { borderColor: neonBlue, color: neonBlue } : {}}
              >
                {range === 'all' ? t('latencyModal.allTime') : range}
              </button>
            ))}
          </div>

          {/* Graph */}
          <div className="bg-slate-800/50 rounded-xl p-4">
            <h3 className="text-sm font-medium text-slate-400 mb-4">
              {t('latencyModal.graphTitle')}
            </h3>
            {statsLoading ? (
              <div className="h-48 flex items-center justify-center">
                <div 
                  className="animate-spin rounded-full h-8 w-8 border-b-2" 
                  style={{ borderColor: neonBlue }}
                />
              </div>
            ) : stats?.time_series && stats.time_series.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={stats.time_series}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    dataKey="timestamp" 
                    stroke="#64748B"
                    tick={{ fill: '#64748B', fontSize: 10 }}
                    tickFormatter={(value) => new Date(value).toLocaleTimeString('de-DE', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  />
                  <YAxis 
                    stroke="#64748B"
                    tick={{ fill: '#64748B', fontSize: 10 }}
                    tickFormatter={(value) => `${value}ms`}
                  />
                  <Tooltip
                    contentStyle={{ 
                      backgroundColor: '#1E293B', 
                      border: '1px solid #334155', 
                      borderRadius: '8px' 
                    }}
                    labelStyle={{ color: '#94A3B8' }}
                    formatter={(value, _name, props) => {
                      const payload = props?.payload as LatencyTimeSeriesPoint | undefined;
                      return [
                        `${value}ms`,
                        payload ? `${payload.sender_profile} → ${payload.recipient_profile}` : ''
                      ];
                    }}
                    labelFormatter={(value) => new Date(String(value)).toLocaleString('de-DE')}
                  />
                  {stats.avg_latency > 0 && (
                    <ReferenceLine 
                      y={stats.avg_latency} 
                      stroke="#EAB308" 
                      strokeDasharray="5 5" 
                      label={{ value: 'Avg', fill: '#EAB308', fontSize: 10 }} 
                    />
                  )}
                  <Line 
                    type="monotone" 
                    dataKey="latency" 
                    stroke={cyan}
                    strokeWidth={2}
                    dot={{ fill: cyan, r: 3 }}
                    activeDot={{ r: 5, fill: neonBlue }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-slate-500">
                {t('latencyModal.noData')}
              </div>
            )}
          </div>

          {/* Stats Summary */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold" style={{ color: neonBlue }}>
                  {stats.avg_latency ? `${Math.round(stats.avg_latency)}ms` : '-'}
                </p>
                <p className="text-xs text-slate-500">{t('latencyModal.avgLatency')}</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-green-400">
                  {stats.min_latency ? `${stats.min_latency}ms` : '-'}
                </p>
                <p className="text-xs text-slate-500">{t('latencyModal.minLatency')}</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-red-400">
                  {stats.max_latency ? formatLatency(stats.max_latency) : '-'}
                </p>
                <p className="text-xs text-slate-500">{t('latencyModal.maxLatency')}</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-white">{stats.total_messages}</p>
                <p className="text-xs text-slate-500">
                  <span className="text-green-400">{stats.delivered_count}</span> / 
                  <span className="text-red-400 ml-1">{stats.failed_count}</span> / 
                  <span className="text-amber-400 ml-1">{stats.pending_count}</span>
                </p>
              </div>
            </div>
          )}

          {/* Filters & Controls */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 text-sm">{t('latencyModal.status')}:</span>
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
                className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white"
              >
                <option value="">{t('latencyModal.all')}</option>
                <option value="delivered">✓✓ {t('latencyModal.delivered')}</option>
                <option value="sent">✓ {t('latencyModal.sent')}</option>
                <option value="failed">✗ {t('latencyModal.failed')}</option>
                <option value="sending">⏳ {t('latencyModal.sending')}</option>
              </select>
            </div>
            <div className="flex-1" />
            <span className="text-slate-500 text-sm">{totalCount} {t('latencyModal.entries')}</span>
          </div>

          {/* Table */}
          <div className="bg-slate-800/30 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-800">
                <tr>
                  <th 
                    className="px-3 py-2 text-left text-xs font-medium text-slate-400 uppercase cursor-pointer hover:text-white"
                    onClick={() => handleSort('created_at')}
                  >
                    {t('latencyModal.time')} 
                    <SortIndicator field="created_at" currentField={sortField} order={sortOrder} />
                  </th>
                  <th 
                    className="px-3 py-2 text-left text-xs font-medium text-slate-400 uppercase cursor-pointer hover:text-white"
                    onClick={() => handleSort('sender__name')}
                  >
                    {t('latencyModal.from')} 
                    <SortIndicator field="sender__name" currentField={sortField} order={sortOrder} />
                  </th>
                  <th 
                    className="px-3 py-2 text-left text-xs font-medium text-slate-400 uppercase cursor-pointer hover:text-white"
                    onClick={() => handleSort('recipient__name')}
                  >
                    {t('latencyModal.to')} 
                    <SortIndicator field="recipient__name" currentField={sortField} order={sortOrder} />
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-slate-400 uppercase">
                    {t('latencyModal.content')}
                  </th>
                  <th 
                    className="px-3 py-2 text-right text-xs font-medium text-slate-400 uppercase cursor-pointer hover:text-white"
                    onClick={() => handleSort('total_latency_ms')}
                  >
                    {t('latencyModal.latency')} 
                    <SortIndicator field="total_latency_ms" currentField={sortField} order={sortOrder} />
                  </th>
                  <th 
                    className="px-3 py-2 text-center text-xs font-medium text-slate-400 uppercase cursor-pointer hover:text-white"
                    onClick={() => handleSort('delivery_status')}
                  >
                    {t('latencyModal.statusColumn')} 
                    <SortIndicator field="delivery_status" currentField={sortField} order={sortOrder} />
                  </th>
                  <th className="px-3 py-2 text-center text-xs font-medium text-slate-400 uppercase">
                    {t('latencyModal.action')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center">
                      <div className="flex justify-center">
                        <div 
                          className="animate-spin rounded-full h-6 w-6 border-b-2" 
                          style={{ borderColor: neonBlue }}
                        />
                      </div>
                    </td>
                  </tr>
                ) : entries.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center text-slate-500">
                      {t('latencyModal.noMessages')}
                    </td>
                  </tr>
                ) : entries.map(entry => (
                  <tr key={entry.id} className="hover:bg-slate-800/50">
                    <td className="px-3 py-2 text-slate-400 text-sm whitespace-nowrap">
                      {formatTime(entry.created_at)}
                    </td>
                    <td className="px-3 py-2">
                      <span className="text-white">{entry.sender_name}</span>
                      <span className="text-slate-500 text-sm ml-1">({entry.sender_profile})</span>
                    </td>
                    <td className="px-3 py-2">
                      <span className="text-white">{entry.recipient_name}</span>
                      <span className="text-slate-500 text-sm ml-1">({entry.recipient_profile})</span>
                    </td>
                    <td className="px-3 py-2 text-slate-400 text-sm max-w-[150px] truncate">
                      {entry.content_preview}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <span className="text-white">{formatLatency(entry.total_latency_ms)}</span>
                      <LatencyDot indicator={entry.latency_indicator} />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <StatusIcon status={entry.delivery_status} />
                    </td>
                    <td className="px-3 py-2 text-center">
                      {deleteConfirm === entry.id ? (
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => handleDelete(entry.id)}
                            className="px-2 py-1 text-xs bg-red-600 hover:bg-red-500 text-white rounded"
                          >
                            {t('latencyModal.confirm')}
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="px-2 py-1 text-xs text-slate-400 hover:text-white"
                          >
                            {t('latencyModal.cancel')}
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(entry.id)}
                          className="p-1 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-slate-800 rounded-lg text-sm disabled:opacity-50 hover:bg-slate-700"
                style={{ color: neonBlue }}
              >
                ◀ {t('latencyModal.previous')}
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                  let page: number;
                  if (totalPages <= 7) {
                    page = i + 1;
                  } else if (currentPage <= 4) {
                    page = i + 1;
                  } else if (currentPage >= totalPages - 3) {
                    page = totalPages - 6 + i;
                  } else {
                    page = currentPage - 3 + i;
                  }
                  
                  return (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`w-8 h-8 rounded-lg text-sm ${
                        currentPage === page
                          ? 'border'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      }`}
                      style={currentPage === page ? { borderColor: neonBlue, color: neonBlue } : {}}
                    >
                      {page}
                    </button>
                  );
                })}
                {totalPages > 7 && currentPage < totalPages - 3 && (
                  <>
                    <span className="text-slate-500">...</span>
                    <button
                      onClick={() => setCurrentPage(totalPages)}
                      className="w-8 h-8 rounded-lg text-sm bg-slate-800 text-slate-400 hover:bg-slate-700"
                    >
                      {totalPages}
                    </button>
                  </>
                )}
              </div>
              
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 bg-slate-800 rounded-lg text-sm disabled:opacity-50 hover:bg-slate-700"
                style={{ color: neonBlue }}
              >
                {t('latencyModal.next')} ▶
              </button>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-700 flex items-center justify-between flex-shrink-0">
          <div>
            {clearAllConfirm ? (
              <div className="flex items-center gap-2">
                <span className="text-red-400 text-sm">{t('latencyModal.deleteAllConfirm')}</span>
                <button
                  onClick={handleClearAll}
                  className="px-3 py-1 text-sm bg-red-600 hover:bg-red-500 text-white rounded"
                >
                  {t('latencyModal.yesDeleteAll')}
                </button>
                <button
                  onClick={() => setClearAllConfirm(false)}
                  className="px-3 py-1 text-sm text-slate-400 hover:text-white"
                >
                  {t('latencyModal.cancel')}
                </button>
              </div>
            ) : (
              <button
                onClick={() => setClearAllConfirm(true)}
                className="px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                {t('latencyModal.clearAll')}
              </button>
            )}
          </div>
          
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 border"
            style={{ borderColor: neonBlue, color: neonBlue }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {t('latencyModal.exportCSV')}
          </button>
        </div>
      </div>
    </div>
  );
}