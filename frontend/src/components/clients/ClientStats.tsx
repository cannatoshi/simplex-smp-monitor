import { useTranslation } from 'react-i18next';
import { SimplexClient } from '../../api/client';

// Neon Blue
const neonBlue = '#88CED0';
// Cyan für Status-Punkte
const cyan = '#22D3EE';

interface Props {
  client: SimplexClient;
  connectionCount: number;
}

export default function ClientStats({ client, connectionCount }: Props) {
  const { t } = useTranslation();

  return (
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

      {/* NACHRICHTEN Card */}
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

      {/* ERFOLGSRATE Card */}
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

      {/* LATENZ Card */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
        <div className="flex justify-between text-xs mb-auto">
          <span style={{ color: neonBlue }}>↓ {client.min_latency_ms || '-'}{client.min_latency_ms && 'ms'}</span>
          <span className="text-red-400">↑ {client.max_latency_ms || '-'}{client.max_latency_ms && 'ms'}</span>
        </div>
        <div className="flex flex-col items-center justify-center my-auto">
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {client.avg_latency_ms ? <>{Math.round(client.avg_latency_ms)}<span className="text-lg text-slate-400">ms</span></> : '-'}
          </p>
          <p className="text-xs text-slate-500">{t('clientStats.avgLatency')}</p>
        </div>
        <div className="mt-auto">
          <div className="h-6 flex items-end gap-0.5">
            {Array.from({length: 15}).map((_, i) => (
              <div key={i} className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-t" style={{height: '20%'}}></div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>{t('clientStats.last15')}</span>
            <span>--</span>
          </div>
        </div>
      </div>
    </div>
  );
}