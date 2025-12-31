import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SimplexClient, ClientConnection } from '../../api/client';

// Neon Blue
const neonBlue = '#88CED0';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';
// Cyan für Status-Punkte
const cyan = '#22D3EE';

interface Props {
  client: SimplexClient;
  connections: ClientConnection[];
  otherClients?: SimplexClient[];
  onConnect?: (targetId: string) => void;
  onDelete?: (connectionId: string) => void;
}

export default function ClientConnections({ client, connections, otherClients = [], onConnect, onDelete }: Props) {
  const { t } = useTranslation();
  const [showConnectPanel, setShowConnectPanel] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const getContactName = (conn: ClientConnection) => {
    if (conn.client_a === client.id) return conn.contact_name_on_a || conn.client_b_name;
    return conn.contact_name_on_b || conn.client_a_name;
  };

  const getPartnerName = (conn: ClientConnection) => {
    if (conn.client_a === client.id) return conn.client_b_name;
    return conn.client_a_name;
  };

  // Neon Button Style
  const neonButtonStyle = {
    backgroundColor: 'rgb(30, 41, 59)',
    color: neonBlue,
    border: `1px solid ${neonBlue}`,
    boxShadow: neonGlow
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 relative min-h-[60px]">
        {!showConnectPanel ? (
          <div className="px-4 py-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold" style={{ color: neonBlue }}>{t('clients.connections')}</h2>
            {client.status === 'running' && otherClients.length > 0 && (
              <button 
                onClick={() => setShowConnectPanel(true)}
                className="text-sm flex items-center gap-1 hover:opacity-80 transition-opacity"
                style={{ color: neonBlue }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
                </svg>
                <span>{t('clients.newConnection')}</span>
              </button>
            )}
            {client.status === 'running' && otherClients.length === 0 && (
              <span className="text-xs text-slate-400">({t('clients.noOtherClients')})</span>
            )}
          </div>
        ) : (
          <div className="px-4 py-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 flex-1">
              <div 
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: cyan }}
              ></div>
              <select 
                value={selectedTarget} 
                onChange={e => setSelectedTarget(e.target.value)}
                className="flex-1 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
              >
                <option value="">{t('clients.selectClient')}</option>
                {otherClients.map(c => (
                  <option key={c.id} value={c.slug}>{c.name} ({c.profile_name})</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setShowConnectPanel(false)}
                className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white"
              >
                {t('common.cancel')}
              </button>
              <button 
                onClick={() => { onConnect?.(selectedTarget); setShowConnectPanel(false); }}
                disabled={!selectedTarget}
                className="px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50 hover:opacity-90 transition-opacity"
                style={neonButtonStyle}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                </svg>
                {t('clients.connect')}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Connection List */}
      <div className="divide-y divide-slate-200 dark:divide-slate-800">
        {connections.length === 0 ? (
          <div className="p-8 text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
              </svg>
            </div>
            <p className="text-slate-500">{t('clients.noConnections')}</p>
          </div>
        ) : connections.map(conn => (
          <div key={conn.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 group">
            {deleteConfirm === conn.id ? (
              <div className="flex items-center justify-between bg-red-500/10 rounded-lg p-3 -mx-1">
                <span className="text-red-500 text-sm">{t('clients.deleteConnection')}</span>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => setDeleteConfirm(null)} 
                    className="px-3 py-1 text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white"
                  >
                    {t('common.cancel')}
                  </button>
                  <button 
                    onClick={() => { onDelete?.(conn.id); setDeleteConfirm(null); }} 
                    className="px-3 py-1 text-sm bg-red-600 hover:bg-red-500 text-white rounded"
                  >
                    {t('common.delete')}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {conn.status === 'connected' ? (
                    <span className="relative flex h-2.5 w-2.5">
                      <span 
                        className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                        style={{ backgroundColor: cyan }}
                      ></span>
                      <span 
                        className="relative inline-flex rounded-full h-2.5 w-2.5"
                        style={{ backgroundColor: cyan }}
                      ></span>
                    </span>
                  ) : conn.status === 'pending' || conn.status === 'connecting' ? (
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-500 animate-pulse"></span>
                  ) : (
                    <span className="h-2.5 w-2.5 rounded-full bg-red-500"></span>
                  )}
                  <div>
                    <span className="text-slate-900 dark:text-white font-medium">{getPartnerName(conn)}</span>
                    <span className="text-slate-500 text-sm ml-1">({getContactName(conn)})</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500">{conn.status_display}</span>
                  <button 
                    onClick={() => setDeleteConfirm(conn.id)}
                    className="text-slate-400 hover:text-red-500 p-1.5 rounded-lg hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}