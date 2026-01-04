/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * Client Quick Test History
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

// Brand colors
const neonBlue = '#88CED0';
const cyan = '#22D3EE';
const red = '#EF4444';
const amber = '#F59E0B';
const purple = '#A855F7';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';

// Neon Button Style - exakt wie in ClientDetail
const neonButtonStyle = {
  backgroundColor: 'rgb(30, 41, 59)',
  color: neonBlue,
  border: `1px solid ${neonBlue}`,
  boxShadow: neonGlow
};

interface TestRun {
  id: string;
  name: string;
  sender: string;
  sender_name: string;
  sender_profile: string;
  sender_use_tor: boolean;
  message_count: number;
  interval_ms: number;
  message_size: number;
  recipient_mode: string;
  status: 'pending' | 'running' | 'completed' | 'cancelled' | 'failed';
  messages_sent: number;
  messages_delivered: number;
  messages_failed: number;
  // Total latency
  avg_latency_ms: number | null;
  min_latency_ms: number | null;
  max_latency_ms: number | null;
  // To-server latency
  avg_latency_to_server_ms: number | null;
  min_latency_to_server_ms: number | null;
  max_latency_to_server_ms: number | null;
  // To-client latency
  avg_latency_to_client_ms: number | null;
  min_latency_to_client_ms: number | null;
  max_latency_to_client_ms: number | null;
  // Computed
  success_rate: number | null;
  progress_percent: number;
  duration_seconds: number | null;
  created_at: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TestRun[];
}

const getCsrfToken = (): string => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === 'csrftoken') return value;
  }
  return '';
};

// Custom Dropdown Component
function Dropdown({ 
  value, 
  options, 
  onChange, 
  icon 
}: { 
  value: string; 
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
  icon?: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentLabel = options.find(o => o.value === value)?.label || value;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1.5 rounded-lg text-sm font-medium inline-flex items-center gap-1.5 hover:opacity-90 transition-opacity"
        style={neonButtonStyle}
      >
        {icon}
        {currentLabel}
        <svg 
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 min-w-[140px] bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden">
          {options.map((opt) => (
            <button
              key={opt.value}
              onClick={() => { onChange(opt.value); setIsOpen(false); }}
              className={`w-full px-3 py-2 text-left text-sm hover:bg-slate-700/50 transition-colors ${
                opt.value === value ? 'text-white' : 'text-slate-400'
              }`}
              style={opt.value === value ? { color: neonBlue } : undefined}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function TestRunHistory() {
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('-created_at');
  const [selectedRuns, setSelectedRuns] = useState<Set<string>>(new Set());
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const pageSize = 25;

  const fetchTestRuns = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        ordering: sortBy,
      });
      if (filter !== 'all') params.append('status', filter);
      
      const res = await fetch(`/api/v1/test-runs/?${params}`);
      if (res.ok) {
        const data: PaginatedResponse = await res.json();
        setTestRuns(data.results || []);
        setTotalCount(data.count);
        setHasNext(!!data.next);
        setHasPrevious(!!data.previous);
      }
    } catch (err) {
      console.error('Error fetching test runs:', err);
    } finally {
      setLoading(false);
    }
  }, [page, filter, sortBy]);

  useEffect(() => { fetchTestRuns(); }, [fetchTestRuns]);

  useEffect(() => {
    const hasRunning = testRuns.some(t => t.status === 'running' || t.status === 'pending');
    if (!hasRunning) return;
    const interval = setInterval(fetchTestRuns, 2000);
    return () => clearInterval(interval);
  }, [testRuns, fetchTestRuns]);

  useEffect(() => { setPage(1); }, [filter, sortBy]);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this test run?')) return;
    setDeleteLoading(id);
    try {
      const res = await fetch(`/api/v1/test-runs/${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
      });
      if (res.ok) {
        setTestRuns(prev => prev.filter(t => t.id !== id));
        setTotalCount(prev => prev - 1);
      }
    } catch (err) {
      console.error('Delete error:', err);
    } finally {
      setDeleteLoading(null);
    }
  };

  const handleBulkDelete = async () => {
    setShowDeleteConfirm(false);
    for (const id of selectedRuns) {
      try {
        await fetch(`/api/v1/test-runs/${id}/`, {
          method: 'DELETE',
          headers: { 'X-CSRFToken': getCsrfToken() },
        });
      } catch (err) { console.error('Bulk delete error:', err); }
    }
    setSelectedRuns(new Set());
    fetchTestRuns();
  };

  // Stats
  const completedRuns = testRuns.filter(t => t.success_rate != null);
  const avgSuccessRate = completedRuns.length > 0
    ? completedRuns.reduce((sum, t) => sum + (t.success_rate || 0), 0) / completedRuns.length
    : 0;
  const latencyRuns = testRuns.filter(t => t.avg_latency_ms != null);
  const avgLatency = latencyRuns.length > 0
    ? latencyRuns.reduce((sum, t) => sum + (t.avg_latency_ms || 0), 0) / latencyRuns.length
    : 0;
  const runningCount = testRuns.filter(t => t.status === 'running').length;

  // Sparkline
  const getSparklineData = (test: TestRun) => {
    if (!test.avg_latency_ms) return [];
    const min = test.min_latency_ms || test.avg_latency_ms * 0.7;
    const max = test.max_latency_ms || test.avg_latency_ms * 1.3;
    return Array.from({ length: 12 }, () => ({
      v: Math.max(0, test.avg_latency_ms! + (Math.random() - 0.5) * (max - min))
    }));
  };

  // Status badge
  const renderStatus = (status: string) => {
    const styles: Record<string, { bg: string; color: string; glow?: boolean }> = {
      pending: { bg: 'rgba(100, 116, 139, 0.2)', color: '#94a3b8' },
      running: { bg: 'rgba(34, 211, 238, 0.2)', color: cyan, glow: true },
      completed: { bg: 'rgba(34, 211, 238, 0.2)', color: cyan },
      cancelled: { bg: 'rgba(245, 158, 11, 0.2)', color: amber },
      failed: { bg: 'rgba(239, 68, 68, 0.2)', color: red },
    };
    const s = styles[status] || styles.pending;
    return (
      <span 
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
        style={{ 
          backgroundColor: s.bg, 
          color: s.color,
          boxShadow: s.glow ? `0 0 8px ${cyan}` : undefined
        }}
      >
        {status === 'running' && (
          <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: cyan }} />
        )}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDuration = (s: number | null) => {
    if (!s) return '—';
    return s < 60 ? `${s.toFixed(1)}s` : `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - d.getTime()) / 60000);
    if (diff < 1) return 'now';
    if (diff < 60) return `${diff}m`;
    if (diff < 1440) return `${Math.floor(diff / 60)}h`;
    return `${Math.floor(diff / 1440)}d`;
  };

  // Latency cell renderer
  const renderLatency = (avg: number | null, min: number | null, max: number | null, color: string) => {
    if (avg == null) return <span className="text-slate-600">—</span>;
    return (
      <div className="text-xs">
        <div style={{ color }} className="font-medium">{Math.round(avg)}ms</div>
        {min != null && max != null && (
          <div className="text-slate-500">{min}–{max}</div>
        )}
      </div>
    );
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading && testRuns.length === 0) {
    return (
      <div className="flex justify-center items-center py-24">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: neonBlue }} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <Link 
            to="/clients" 
            className="text-sm flex items-center gap-1 mb-2 hover:opacity-80 transition-opacity"
            style={{ color: neonBlue }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
            </svg>
            All Clients
          </Link>
          <h1 className="text-2xl font-bold text-white">
            Test History
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Message delivery tests · Latency metrics · Tor comparison
          </p>
        </div>

        {/* Buttons - exakt wie ClientDetail */}
        <div className="flex flex-wrap gap-2">
          {/* Back to Clients Button */}
          <Link
            to="/clients"
            className="px-3 py-1.5 rounded-lg text-sm font-medium inline-flex items-center gap-1.5 hover:opacity-90 transition-opacity"
            style={neonButtonStyle}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            Clients
          </Link>

          {selectedRuns.size > 0 && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-3 py-1.5 rounded-lg text-sm font-medium inline-flex items-center gap-1.5 hover:opacity-90 transition-opacity"
              style={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: red, border: `1px solid ${red}`, boxShadow: '0 0 8px rgba(239, 68, 68, 0.3)' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              Delete ({selectedRuns.size})
            </button>
          )}

          <Dropdown
            value={filter}
            onChange={setFilter}
            options={[
              { value: 'all', label: 'All Status' },
              { value: 'completed', label: 'Completed' },
              { value: 'running', label: 'Running' },
              { value: 'failed', label: 'Failed' },
              { value: 'cancelled', label: 'Cancelled' },
            ]}
          />

          <Dropdown
            value={sortBy}
            onChange={setSortBy}
            options={[
              { value: '-created_at', label: 'Newest' },
              { value: 'created_at', label: 'Oldest' },
              { value: '-success_rate', label: 'Best Rate' },
              { value: 'avg_latency_ms', label: 'Low Latency' },
            ]}
          />

          <button
            onClick={() => fetchTestRuns()}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg text-sm font-medium inline-flex items-center gap-1.5 disabled:opacity-50 hover:opacity-90 transition-opacity"
            style={neonButtonStyle}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards - ClientStats Style */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* TOTAL TESTS Card */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>Completed: <span style={{ color: cyan }}>{testRuns.filter(t => t.status === 'completed').length}</span></span>
            <span>Failed: <span className="text-red-400">{testRuns.filter(t => t.status === 'failed').length}</span></span>
          </div>
          <div className="flex flex-col items-center justify-center my-auto">
            <p className="text-3xl font-bold" style={{ color: neonBlue }}>{totalCount}</p>
            <p className="text-xs text-slate-500">Total Tests</p>
          </div>
          <div className="flex justify-between text-xs text-slate-400 mt-auto">
            <span>Page {page}/{totalPages || 1}</span>
            <span>{pageSize}/page</span>
          </div>
        </div>

        {/* SUCCESS RATE Card */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>Best: <span style={{ color: cyan }}>{completedRuns.length > 0 ? Math.max(...completedRuns.map(t => t.success_rate || 0)).toFixed(0) : '-'}%</span></span>
            <span>Worst: <span className="text-amber-400">{completedRuns.length > 0 ? Math.min(...completedRuns.map(t => t.success_rate || 100)).toFixed(0) : '-'}%</span></span>
          </div>
          <div className="flex flex-col items-center justify-center my-auto">
            <p className="text-3xl font-bold" style={{ color: cyan }}>{avgSuccessRate.toFixed(1)}%</p>
            <p className="text-xs text-slate-500">Avg Success Rate</p>
          </div>
          <div className="mt-auto">
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all"
                style={{ width: `${avgSuccessRate}%`, backgroundColor: cyan }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        {/* AVG LATENCY Card */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs mb-auto">
            <span style={{ color: neonBlue }}>↓ {(() => {
              const mins = latencyRuns.map(t => t.min_latency_ms).filter(v => v != null && v !== Infinity) as number[];
              return mins.length > 0 ? Math.min(...mins) : '—';
            })()}ms</span>
            <span className="text-red-400">↑ {(() => {
              const maxs = latencyRuns.map(t => t.max_latency_ms).filter(v => v != null && v > 0) as number[];
              return maxs.length > 0 ? Math.max(...maxs) : '—';
            })()}ms</span>
          </div>
          <div className="flex flex-col items-center justify-center my-auto">
            <p className="text-3xl font-bold text-white">
              {avgLatency > 0 ? (
                <>{Math.round(avgLatency)}<span className="text-lg text-slate-400">ms</span></>
              ) : '—'}
            </p>
            <p className="text-xs text-slate-500">Avg Latency</p>
          </div>
          <div className="mt-auto pt-2">
            <div className="h-5 flex items-end gap-0.5">
              {latencyRuns.slice(0, 15).map((t, i) => {
                const maxLat = Math.max(...latencyRuns.slice(0, 15).map(r => r.avg_latency_ms || 0), 1);
                const height = Math.max(10, ((t.avg_latency_ms || 0) / maxLat) * 100);
                return (
                  <div 
                    key={i} 
                    className="flex-1 rounded-t"
                    style={{ height: `${height}%`, backgroundColor: cyan, opacity: 0.8 }}
                    title={`${Math.round(t.avg_latency_ms || 0)}ms`}
                  />
                );
              })}
              {latencyRuns.length < 15 && Array.from({ length: 15 - Math.min(latencyRuns.length, 15) }).map((_, i) => (
                <div key={`empty-${i}`} className="flex-1 bg-slate-700 rounded-t" style={{ height: '20%' }} />
              ))}
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Last {Math.min(15, latencyRuns.length)}</span>
              <span style={{ color: neonBlue }}>—</span>
            </div>
          </div>
        </div>

        {/* RUNNING NOW Card */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>Pending: <span className="text-amber-400">{testRuns.filter(t => t.status === 'pending').length}</span></span>
            <span>Cancelled: <span className="text-slate-200">{testRuns.filter(t => t.status === 'cancelled').length}</span></span>
          </div>
          <div className="flex items-center justify-center gap-2 my-auto">
            {runningCount > 0 ? (
              <>
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: cyan }} />
                  <span className="relative inline-flex rounded-full h-3 w-3" style={{ backgroundColor: cyan }} />
                </span>
                <span className="text-3xl font-bold" style={{ color: cyan }}>{runningCount}</span>
              </>
            ) : (
              <span className="text-3xl font-bold text-slate-500">0</span>
            )}
          </div>
          <p className="text-xs text-slate-500 text-center -mt-1">Running Now</p>
          <div className="flex justify-between text-xs text-slate-400 mt-auto">
            <span>Live</span>
            <span>—</span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="px-3 py-3 text-left w-10">
                  <input
                    type="checkbox"
                    checked={selectedRuns.size === testRuns.length && testRuns.length > 0}
                    onChange={(e) => setSelectedRuns(e.target.checked ? new Set(testRuns.map(t => t.id)) : new Set())}
                    className="accent-[#88CED0] w-4 h-4"
                  />
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Test</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Client</th>
                <th className="px-3 py-3 text-center text-xs font-medium text-slate-500 uppercase w-10">Tor</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-20">Status</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-16">Msgs</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-14">Rate</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-20">Total</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-20">→ Srv</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-20">→ Cli</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-16">Trend</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-14">Time</th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase w-12">Age</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase w-16"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {testRuns.length === 0 ? (
                <tr><td colSpan={14} className="px-3 py-8 text-center text-slate-500">No tests found</td></tr>
              ) : testRuns.map((t) => (
                <tr key={t.id} className="hover:bg-slate-800/30 transition-colors">
                  {/* Checkbox */}
                  <td className="px-3 py-2">
                    <input
                      type="checkbox"
                      checked={selectedRuns.has(t.id)}
                      onChange={(e) => {
                        const s = new Set(selectedRuns);
                        e.target.checked ? s.add(t.id) : s.delete(t.id);
                        setSelectedRuns(s);
                      }}
                      className="accent-[#88CED0] w-4 h-4"
                    />
                  </td>

                  {/* Test Name */}
                  <td className="px-3 py-2">
                    <span className="text-white text-sm font-medium">{t.name}</span>
                  </td>

                  {/* Client */}
                  <td className="px-3 py-2">
                    <div className="text-sm text-slate-300">{t.sender_name}</div>
                    <div className="text-xs text-slate-500">{t.sender_profile}</div>
                  </td>

                  {/* Tor - lila Haken */}
                  <td className="px-3 py-2 text-center">
                    {t.sender_use_tor ? (
                      <svg className="w-4 h-4 mx-auto" style={{ color: purple }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/>
                      </svg>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>

                  {/* Status */}
                  <td className="px-3 py-2">{renderStatus(t.status)}</td>

                  {/* Messages */}
                  <td className="px-3 py-2 text-sm">
                    <span className="text-white">{t.messages_delivered}</span>
                    <span className="text-slate-500">/{t.message_count}</span>
                  </td>

                  {/* Success Rate */}
                  <td className="px-3 py-2">
                    {t.success_rate != null ? (
                      <span 
                        className="text-sm font-medium"
                        style={{ color: t.success_rate >= 95 ? cyan : t.success_rate >= 80 ? amber : red }}
                      >
                        {t.success_rate.toFixed(0)}%
                      </span>
                    ) : <span className="text-slate-600">—</span>}
                  </td>

                  {/* Total Latency */}
                  <td className="px-3 py-2">
                    {renderLatency(t.avg_latency_ms, t.min_latency_ms, t.max_latency_ms, cyan)}
                  </td>

                  {/* To Server Latency */}
                  <td className="px-3 py-2">
                    {renderLatency(t.avg_latency_to_server_ms, t.min_latency_to_server_ms, t.max_latency_to_server_ms, neonBlue)}
                  </td>

                  {/* To Client Latency */}
                  <td className="px-3 py-2">
                    {renderLatency(t.avg_latency_to_client_ms, t.min_latency_to_client_ms, t.max_latency_to_client_ms, neonBlue)}
                  </td>

                  {/* Trend Sparkline */}
                  <td className="px-3 py-2">
                    {t.avg_latency_ms ? (
                      <div className="w-14 h-6">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={getSparklineData(t)}>
                            <defs>
                              <linearGradient id={`grad-${t.id}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={cyan} stopOpacity={0.4} />
                                <stop offset="100%" stopColor={cyan} stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="v" stroke={cyan} strokeWidth={1.5} fill={`url(#grad-${t.id})`} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    ) : <span className="text-slate-600">—</span>}
                  </td>

                  {/* Duration */}
                  <td className="px-3 py-2 text-xs text-slate-400">
                    {formatDuration(t.duration_seconds)}
                  </td>

                  {/* When */}
                  <td className="px-3 py-2 text-xs text-slate-500">
                    {formatDate(t.created_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-3 py-2 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Link
                        to={`/clients/${t.sender}`}
                        className="p-1.5 rounded-lg hover:opacity-80 transition-opacity"
                        style={{ backgroundColor: 'rgb(30, 41, 59)', border: `1px solid ${neonBlue}40` }}
                        title="View Client"
                      >
                        <svg className="w-3.5 h-3.5" style={{ color: neonBlue }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </Link>
                      <button
                        onClick={() => handleDelete(t.id)}
                        disabled={deleteLoading === t.id}
                        className="p-1.5 rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50"
                        style={{ backgroundColor: 'rgb(30, 41, 59)', border: `1px solid ${red}40` }}
                        title="Delete"
                      >
                        {deleteLoading === t.id ? (
                          <div className="w-3.5 h-3.5 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <svg className="w-3.5 h-3.5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-slate-800 flex items-center justify-between">
            <span className="text-sm text-slate-500">
              {((page-1)*pageSize)+1}–{Math.min(page*pageSize, totalCount)} of {totalCount}
            </span>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setPage(1)} 
                disabled={!hasPrevious} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium disabled:opacity-30 hover:opacity-90 transition-opacity"
                style={neonButtonStyle}
              >
                ««
              </button>
              <button 
                onClick={() => setPage(p => p-1)} 
                disabled={!hasPrevious} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium disabled:opacity-30 hover:opacity-90 transition-opacity"
                style={neonButtonStyle}
              >
                ‹
              </button>
              <span className="px-3 text-sm" style={{ color: neonBlue }}>
                {page} / {totalPages}
              </span>
              <button 
                onClick={() => setPage(p => p+1)} 
                disabled={!hasNext} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium disabled:opacity-30 hover:opacity-90 transition-opacity"
                style={neonButtonStyle}
              >
                ›
              </button>
              <button 
                onClick={() => setPage(totalPages)} 
                disabled={!hasNext} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium disabled:opacity-30 hover:opacity-90 transition-opacity"
                style={neonButtonStyle}
              >
                »»
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setShowDeleteConfirm(false)} />
          <div className="relative bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-white mb-2">Delete {selectedRuns.size} Tests?</h3>
            <p className="text-slate-400 mb-6">This action cannot be undone.</p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setShowDeleteConfirm(false)} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleBulkDelete} 
                className="px-3 py-1.5 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
                style={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: red, border: `1px solid ${red}` }}
              >
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}