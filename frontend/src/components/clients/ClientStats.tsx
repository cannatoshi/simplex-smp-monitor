/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * ClientStats Component
 * 
 * Displays 4 stat cards for a client:
 * - Status (running/stopped/error)
 * - Messages (sent/received/delivered/failed)
 * - Success Rate (with progress bar)
 * - Latency (clickable, opens modal with detailed history)
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { SimplexClient } from '../../api/client';
import ClientLatencyModal from './ClientLatencyModal';

// Neon Blue - Primary brand color
const neonBlue = '#88CED0';
// Cyan - Accent color for status indicators
const cyan = '#22D3EE';

interface Props {
  client: SimplexClient;
  connectionCount: number;
}

interface RecentLatency {
  latency: number;
  timestamp: string;
}

export default function ClientStats({ client, connectionCount }: Props) {
  const { t } = useTranslation();
  
  // Modal state
  const [showLatencyModal, setShowLatencyModal] = useState(false);
  
  // Mini graph data
  const [recentLatencies, setRecentLatencies] = useState<RecentLatency[]>([]);
  const [loadingLatencies, setLoadingLatencies] = useState(true);

  // Fetch recent 15 latencies for mini graph
  const fetchRecentLatencies = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/clients/${client.id}/latency-recent/`);
      if (response.ok) {
        const data = await response.json();
        setRecentLatencies(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching recent latencies:', error);
    } finally {
      setLoadingLatencies(false);
    }
  }, [client.id]);

  // Initial load + periodic refresh
  useEffect(() => {
    fetchRecentLatencies();
    
    // Refresh every 10 seconds for live updates
    const interval = setInterval(fetchRecentLatencies, 10000);
    return () => clearInterval(interval);
  }, [fetchRecentLatencies]);

  // Calculate max latency for scaling the bars
  const maxLatency = Math.max(...recentLatencies.map(r => r.latency), 1);

  // Get bar color based on latency value - using brand colors
  const getLatencyColor = (latency: number, maxLatency: number): string => {
    const ratio = latency / maxLatency;
    if (ratio < 0.5) return neonBlue;   // Fast = Neon Blue (heller)
    return cyan;                         // Slower = Cyan (dunkler)
  };

  return (
    <>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* STATUS Card */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>{t('clientStats.port')} <span className="text-slate-600 dark:text-slate-200">{client.websocket_port}</span></span>
            <span 
              className="px-1.5 py-0.5 rounded"
              style={{ 
                backgroundColor: client.status === 'running' ? 'rgba(136, 206, 208, 0.2)' : undefined,
                color: client.status === 'running' ? neonBlue : undefined
              }}
            >
              {client.status === 'running' ? client.uptime_display || '0s' : '--'}
            </span>
          </div>
          <div className="flex items-center justify-center gap-2 my-auto">
            {client.status === 'running' ? (
              <>
                <span className="relative flex h-3 w-3">
                  <span 
                    className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    style={{ backgroundColor: cyan }}
                  ></span>
                  <span 
                    className="relative inline-flex rounded-full h-3 w-3"
                    style={{ backgroundColor: cyan }}
                  ></span>
                </span>
                <span className="text-2xl font-bold" style={{ color: neonBlue }}>{t('status.running')}</span>
              </>
            ) : client.status === 'error' ? (
              <>
                <span className="h-3 w-3 rounded-full bg-red-500"></span>
                <span className="text-2xl font-bold text-red-500">{t('status.error')}</span>
              </>
            ) : (
              <>
                <span className="h-3 w-3 rounded-full bg-slate-500"></span>
                <span className="text-2xl font-bold text-slate-500">{t('status.stopped')}</span>
              </>
            )}
          </div>
          <p className="text-xs text-slate-500 text-center -mt-1">{t('clientStats.status')}</p>
          <div className="flex justify-between text-xs text-slate-400 mt-auto">
            <span><span className="text-slate-600 dark:text-slate-200">{connectionCount}</span> {t('clientStats.connections')}</span>
            <span>{client.profile_name}</span>
          </div>
        </div>

        {/* MESSAGES Card */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>✓ <span style={{ color: neonBlue }}>{client.messages_delivered || 0}</span></span>
            <span>✗ <span className="text-red-400">{client.messages_failed || 0}</span></span>
          </div>
          <div className="flex items-center justify-center gap-6 my-auto">
            <div className="text-center">
              <p className="text-2xl font-bold" style={{ color: neonBlue }}>{client.messages_sent}</p>
              <p className="text-xs text-slate-500">↑ {t('clientStats.sent')}</p>
            </div>
            <div className="w-px h-8 bg-slate-300 dark:bg-slate-700"></div>
            <div className="text-center">
              <p className="text-2xl font-bold" style={{ color: neonBlue }}>{client.messages_received}</p>
              <p className="text-xs text-slate-500">↓ {t('clientStats.received')}</p>
            </div>
          </div>
          <div className="flex justify-between text-xs text-slate-400 mt-auto">
            <span>⏳ <span className="text-amber-400">0</span></span>
            <span>--</span>
          </div>
        </div>

        {/* SUCCESS RATE Card */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
          <div className="flex justify-between text-xs text-slate-400 mb-auto">
            <span>{t('clientStats.today')}: <span className="text-slate-600 dark:text-slate-200">{client.messages_sent}</span></span>
            <span>{t('clientStats.total')}: <span className="text-slate-600 dark:text-slate-200">{client.messages_sent}</span></span>
          </div>
          <div className="flex flex-col items-center justify-center my-auto">
            <p className="text-3xl font-bold" style={{ color: neonBlue }}>
              {client.delivery_success_rate.toFixed(1)}%
            </p>
            <p className="text-xs text-slate-500">{t('clientStats.successRate')}</p>
          </div>
          <div className="mt-auto">
            <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all"
                style={{ 
                  width: `${client.delivery_success_rate}%`,
                  backgroundColor: cyan
                }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        {/* LATENCY Card - CLICKABLE */}
        <div 
          className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative cursor-pointer transition-all duration-200 hover:border-[#88CED0] hover:shadow-lg hover:shadow-[#88CED0]/10 group"
          onClick={() => setShowLatencyModal(true)}
          title={t('clientStats.clickForDetails')}
        >
          {/* Click indicator - shows on hover */}
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <svg className="w-4 h-4" style={{ color: neonBlue }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </div>
          
          <div className="flex justify-between text-xs mb-auto">
            <span style={{ color: neonBlue }}>↓ {client.min_latency_ms || '-'}{client.min_latency_ms && 'ms'}</span>
            <span className="text-red-400">↑ {client.max_latency_ms || '-'}{client.max_latency_ms && 'ms'}</span>
          </div>
          <div className="flex flex-col items-center justify-center my-auto">
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {client.avg_latency_ms ? (
                <>
                  {Math.round(client.avg_latency_ms)}
                  <span className="text-lg text-slate-400">ms</span>
                </>
              ) : '-'}
            </p>
            <p className="text-xs text-slate-500">{t('clientStats.avgLatency')}</p>
          </div>
          
          {/* Mini Graph - Real Data */}
          <div className="mt-auto pt-2">
            <div className="h-5 flex items-end gap-0.5">
              {loadingLatencies ? (
                // Loading placeholder with animation
                Array.from({ length: 15 }).map((_, i) => (
                  <div 
                    key={i} 
                    className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-t animate-pulse" 
                    style={{ height: '20%' }}
                  />
                ))
              ) : recentLatencies.length > 0 ? (
                // Real data bars with brand colors
                recentLatencies.map((data, i) => {
                  const height = Math.max(10, (data.latency / maxLatency) * 100);
                  return (
                    <div 
                      key={i} 
                      className="flex-1 rounded-t transition-all duration-300 group-hover:opacity-90"
                      style={{
                        height: `${height}%`,
                        backgroundColor: getLatencyColor(data.latency, maxLatency),
                        opacity: 0.8
                      }}
                      title={`${data.latency}ms`}
                    />
                  );
                })
              ) : (
                // Empty state placeholder
                Array.from({ length: 15 }).map((_, i) => (
                  <div 
                    key={i} 
                    className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-t" 
                    style={{ height: '20%' }}
                  />
                ))
              )}
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>{t('clientStats.last15')}</span>
              <span 
                className="group-hover:underline transition-all"
                style={{ color: neonBlue }}
              >
                {t('clientStats.details')} →
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Latency History Modal */}
      <ClientLatencyModal
        isOpen={showLatencyModal}
        onClose={() => setShowLatencyModal(false)}
        clientId={client.id}
        clientName={client.name}
        clientProfile={client.profile_name}
      />
    </>
  );
}