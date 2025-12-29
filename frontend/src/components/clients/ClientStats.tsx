import { SimplexClient } from '../../api/client';

interface Props {
  client: SimplexClient;
  connectionCount: number;
}

export default function ClientStats({ client, connectionCount }: Props) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {/* STATUS Card */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
        <div className="flex justify-between text-xs text-slate-400 mb-auto">
          <span>Port <span className="text-slate-600 dark:text-slate-200">{client.websocket_port}</span></span>
          <span className={`px-1.5 py-0.5 rounded ${client.status === 'running' ? 'bg-cyan-900/30 text-cyan-400' : 'bg-slate-200 dark:bg-slate-800 text-slate-500'}`}>
            {client.status === 'running' ? client.uptime_display || '0s' : '--'}
          </span>
        </div>
        <div className="flex items-center justify-center gap-2 my-auto">
          {client.status === 'running' ? (
            <>
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-2xl font-bold text-emerald-400">Läuft</span>
            </>
          ) : client.status === 'error' ? (
            <>
              <span className="h-3 w-3 rounded-full bg-red-500"></span>
              <span className="text-2xl font-bold text-red-500">Fehler</span>
            </>
          ) : (
            <>
              <span className="h-3 w-3 rounded-full bg-slate-500"></span>
              <span className="text-2xl font-bold text-slate-500">Gestoppt</span>
            </>
          )}
        </div>
        <p className="text-xs text-slate-500 text-center -mt-1">Status</p>
        <div className="flex justify-between text-xs text-slate-400 mt-auto">
          <span><span className="text-slate-600 dark:text-slate-200">{connectionCount}</span> Verb.</span>
          <span>{client.profile_name}</span>
        </div>
      </div>

      {/* NACHRICHTEN Card */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 h-36 flex flex-col relative">
        <div className="flex justify-between text-xs text-slate-400 mb-auto">
          <span>✓ <span className="text-emerald-400">{client.messages_delivered || 0}</span></span>
          <span>✗ <span className="text-red-400">{client.messages_failed || 0}</span></span>
        </div>
        <div className="flex items-center justify-center gap-6 my-auto">
          <div className="text-center">
            <p className="text-2xl font-bold text-emerald-400">{client.messages_sent}</p>
            <p className="text-xs text-slate-500">↑ Gesendet</p>
          </div>
          <div className="w-px h-8 bg-slate-300 dark:bg-slate-700"></div>
          <div className="text-center">
            <p className="text-2xl font-bold text-cyan-400">{client.messages_received}</p>
            <p className="text-xs text-slate-500">↓ Empfangen</p>
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
          <span>Heute: <span className="text-slate-600 dark:text-slate-200">{client.messages_sent}</span></span>
          <span>Gesamt: <span className="text-slate-600 dark:text-slate-200">{client.messages_sent}</span></span>
        </div>
        <div className="flex flex-col items-center justify-center my-auto">
          <p className={`text-3xl font-bold ${client.delivery_success_rate >= 90 ? 'text-emerald-400' : client.delivery_success_rate >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
            {client.delivery_success_rate.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-500">Erfolgsrate</p>
        </div>
        <div className="mt-auto">
          <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${client.delivery_success_rate >= 90 ? 'bg-emerald-500' : client.delivery_success_rate >= 70 ? 'bg-amber-500' : 'bg-red-500'}`}
              style={{ width: `${client.delivery_success_rate}%` }}></div>
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
          <span className="text-emerald-400">↓ {client.min_latency_ms || '-'}{client.min_latency_ms && 'ms'}</span>
          <span className="text-red-400">↑ {client.max_latency_ms || '-'}{client.max_latency_ms && 'ms'}</span>
        </div>
        <div className="flex flex-col items-center justify-center my-auto">
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {client.avg_latency_ms ? <>{Math.round(client.avg_latency_ms)}<span className="text-lg text-slate-400">ms</span></> : '-'}
          </p>
          <p className="text-xs text-slate-500">Ø Latenz</p>
        </div>
        <div className="mt-auto">
          <div className="h-6 flex items-end gap-0.5">
            {Array.from({length: 15}).map((_, i) => (
              <div key={i} className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-t" style={{height: '20%'}}></div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>Letzte 15</span>
            <span>--</span>
          </div>
        </div>
      </div>
    </div>
  );
}
