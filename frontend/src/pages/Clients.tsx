import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { simplexClientsApi, SimplexClient, ClientStats, ClientListResponse } from '../api/client';
import { useClientsWebSocket } from '../hooks/useWebSocket';

export default function Clients() {
  const { t } = useTranslation();
  const { data: clientsData, loading, refetch } = useApi<ClientListResponse>(() => simplexClientsApi.list());
  const { data: stats } = useApi<ClientStats>(() => simplexClientsApi.stats());
  
  const [clients, setClients] = useState<SimplexClient[]>([]);
  
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Neon Blue
  const neonBlue = '#88CED0';

  // WebSocket für Live-Updates
  const { connectionState, bridgeClients } = useClientsWebSocket({
    onClientStats: (event) => {
      setClients(prev => prev.map(c => 
        c.slug === event.client_slug 
          ? { ...c, messages_sent: event.messages_sent, messages_received: event.messages_received }
          : c
      ));
    },
    onClientStatus: (event) => {
      setClients(prev => prev.map(c => 
        c.slug === event.client_slug 
          ? { ...c, status: event.status as SimplexClient['status'] } 
          : c
      ));
    },
  });

  // Clients aus API laden
  useEffect(() => {
    if (clientsData?.results) {
      setClients(clientsData.results);
    }
  }, [clientsData]);

  // Clients aus API laden
  useEffect(() => {
    if (clientsData?.results) {
      setClients(clientsData.results);
    }
  }, [clientsData]);

  const filteredClients = statusFilter === 'all' 
    ? clients 
    : clients.filter(c => c.status === statusFilter);

  const handleStart = async (client: SimplexClient) => {
    setActionLoading(client.id);
    try {
      await simplexClientsApi.start(client.id);
      refetch();
    } catch (err) {
      console.error('Start error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleStop = async (client: SimplexClient) => {
    setActionLoading(client.id);
    try {
      await simplexClientsApi.stop(client.id);
      refetch();
    } catch (err) {
      console.error('Stop error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRestart = async (client: SimplexClient) => {
    setActionLoading(client.id);
    try {
      await simplexClientsApi.restart(client.id);
      refetch();
    } catch (err) {
      console.error('Restart error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (client: SimplexClient) => {
    if (!confirm(t('common.confirm') + `: ${client.name}?`)) return;
    setActionLoading(client.id);
    try {
      await simplexClientsApi.delete(client.id);
      refetch();
    } catch (err) {
      console.error('Delete error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-cyan-500';
      case 'stopped': return 'bg-slate-500';
      case 'error': return 'bg-red-500';
      case 'starting':
      case 'stopping': return 'bg-amber-500';
      default: return 'bg-slate-500';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'running': return 'bg-cyan-500/20 text-cyan-400';
      case 'stopped': return 'bg-slate-500/20 text-slate-600 dark:text-slate-400';
      case 'error': return 'bg-red-500/20 text-red-400';
      case 'starting':
      case 'stopping': return 'bg-amber-500/20 text-amber-400';
      default: return 'bg-slate-500/20 text-slate-600 dark:text-slate-400';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: neonBlue }}>{t('clients.title')}</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">{t('clients.subtitle')}</p>
          <div className="flex items-center gap-2 mt-2">
            <div 
              className={`w-2 h-2 rounded-full ${connectionState === 'connecting' ? 'animate-pulse' : ''}`}
              style={{ backgroundColor: connectionState === 'connected' ? neonBlue : connectionState === 'connecting' ? neonBlue : '#64748b' }}
            />
            <span className="text-xs" style={{ color: connectionState === 'connected' ? neonBlue : '#94a3b8' }}>
              {connectionState === 'connected' ? `Live · ${bridgeClients} Bridge Clients` : connectionState}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Link
            to="/clients/new"
            className="px-4 py-2 bg-slate-800 border rounded-lg transition-colors flex items-center gap-2 hover:bg-slate-700"
            style={{ borderColor: neonBlue, color: neonBlue }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
            </svg>
            {t('clients.newClient')}
          </Link>
        </div>
      </div>

      {/* Stats Cards - ALLE ZAHLEN IN NEON BLUE */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
          <div className="text-slate-600 dark:text-slate-400 text-sm">{t('common.total')}</div>
          <div className="text-2xl font-bold" style={{ color: neonBlue }}>{stats?.total || 0}</div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
          <div className="text-slate-600 dark:text-slate-400 text-sm">{t('common.active')}</div>
          <div className="text-2xl font-bold" style={{ color: neonBlue }}>{stats?.running || 0}</div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
          <div className="text-slate-600 dark:text-slate-400 text-sm">{t('status.stopped')}</div>
          <div className="text-2xl font-bold" style={{ color: neonBlue }}>{stats?.stopped || 0}</div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
          <div className="text-slate-600 dark:text-slate-400 text-sm">{t('status.error')}</div>
          <div className="text-2xl font-bold" style={{ color: neonBlue }}>{stats?.error || 0}</div>
        </div>
      </div>

      {/* Message Stats - ZAHLEN IN NEON BLUE */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center justify-between">
          <div>
            <div className="text-slate-600 dark:text-slate-400 text-sm">{t('clients.messagesSent')}</div>
            <div className="text-xl font-bold" style={{ color: neonBlue }}>↑ {stats?.total_messages_sent || 0}</div>
          </div>
          <svg className="w-8 h-8 text-cyan-500/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center justify-between">
          <div>
            <div className="text-slate-600 dark:text-slate-400 text-sm">{t('clients.messagesReceived')}</div>
            <div className="text-xl font-bold" style={{ color: neonBlue }}>↓ {stats?.total_messages_received || 0}</div>
          </div>
          <svg className="w-8 h-8" style={{ color: `${neonBlue}30` }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
        </div>
      </div>

      {/* Filter - Neon Blue Style */}
      <div className="flex items-center gap-2">
        <span className="text-slate-600 dark:text-slate-400 text-sm">{t('common.filter')}:</span>
        {['all', 'running', 'stopped', 'error'].map(filter => (
          <button
            key={filter}
            onClick={() => setStatusFilter(filter)}
            className={`px-3 py-1 rounded-lg text-sm transition-colors border ${
              statusFilter === filter
                ? 'bg-slate-800 border-[#88CED0]'
                : 'bg-slate-100 dark:bg-slate-800 border-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
            style={statusFilter === filter ? { color: neonBlue, borderColor: neonBlue } : {}}
          >
            {filter === 'all' ? t('common.all') : filter === 'running' ? t('common.active') : filter === 'stopped' ? t('status.stopped') : t('status.error')}
          </button>
        ))}
      </div>

      {/* Client Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: neonBlue }}></div>
        </div>
      ) : filteredClients.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center">
          <svg className="w-16 h-16 text-slate-400 dark:text-slate-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">{t('clients.noClients')}</h3>
          <p className="text-slate-600 dark:text-slate-400 mb-6">{t('clients.createFirst')}</p>
          <Link
            to="/clients/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 border rounded-lg transition-colors hover:bg-slate-700"
            style={{ borderColor: neonBlue, color: neonBlue }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
            </svg>
            {t('clients.addClient')}
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredClients.map(client => (
            <div
              key={client.id}
              className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all overflow-hidden group"
            >
              {/* Header */}
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(client.status)}`}></div>
                    {client.status === 'running' && (
                      <div className={`absolute inset-0 w-3 h-3 rounded-full ${getStatusColor(client.status)} animate-ping opacity-75`}></div>
                    )}
                    {(client.status === 'starting' || client.status === 'stopping') && (
                      <div className="absolute inset-0 w-3 h-3 rounded-full bg-amber-500 animate-pulse"></div>
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold" style={{ color: neonBlue }}>{client.name}</h3>
                    <p className="text-xs text-slate-500">{client.slug}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded ${getStatusBadgeClass(client.status)}`}>
                  {t(`status.${client.status}`)}
                </span>
              </div>

              {/* Body */}
              <div className="p-4 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">{t('clients.profile')}</span>
                  <span className="text-slate-900 dark:text-white font-mono">{client.profile_name}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">{t('clients.port')}</span>
                  <span className="text-slate-900 dark:text-white font-mono">{client.websocket_port}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">{t('clients.connections')}</span>
                  <span className="text-slate-900 dark:text-white">{client.connection_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">{t('clients.messages')}</span>
                  <span className="text-slate-900 dark:text-white">
                    <span style={{ color: neonBlue }}>↑{client.messages_sent}</span>
                    <span className="text-slate-400 mx-1">/</span>
                    <span style={{ color: neonBlue }}>↓{client.messages_received}</span>
                  </span>
                </div>
                {client.uptime_display && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600 dark:text-slate-400">{t('servers.uptime')}</span>
                    <span style={{ color: neonBlue }}>{client.uptime_display}</span>
                  </div>
                )}
                {client.use_tor && (
                  <div className="flex items-center gap-2 text-sm">
                    <svg className="w-4 h-4 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                    </svg>
                    <span className="text-purple-400">Tor</span>
                  </div>
                )}
                {client.delivery_success_rate > 0 && (
                  <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
                    <div className="flex justify-between text-xs text-slate-500 mb-1">
                      <span>{t('clients.successRate')}</span>
                      <span style={{ color: neonBlue }}>
                        {client.delivery_success_rate.toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all"
                        style={{ 
                          width: `${client.delivery_success_rate}%`,
                          backgroundColor: '#22D3EE'
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex justify-between">
                <Link
                  to={`/clients/${client.id}`}
                  className="text-sm flex items-center gap-1 hover:opacity-80 transition-opacity"
                  style={{ color: neonBlue }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  {t('common.details')}
                </Link>
                <div className="flex gap-1">
                  {actionLoading === client.id ? (
                    <div className="p-1.5">
                      <svg className="w-4 h-4 animate-spin text-slate-400" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                  ) : (
                    <>
                      {client.status === 'running' ? (
                        <>
                          <button
                            onClick={() => handleRestart(client)}
                            className="p-1.5 text-amber-400 hover:bg-amber-500/20 rounded transition-colors"
                            title={t('clients.restart')}
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                            </svg>
                          </button>
                          <button
                            onClick={() => handleStop(client)}
                            className="p-1.5 text-red-400 hover:bg-red-500/20 rounded transition-colors"
                            title={t('clients.stop')}
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
                            </svg>
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => handleStart(client)}
                          className="p-1.5 hover:bg-cyan-500/20 rounded transition-colors"
                          style={{ color: neonBlue }}
                          title={t('clients.start')}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                          </svg>
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(client)}
                        className="p-1.5 text-slate-400 hover:bg-red-500/20 hover:text-red-400 rounded transition-colors"
                        title={t('common.delete')}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Port Info */}
      {stats?.available_ports && stats.available_ports.length > 0 && (
        <div className="text-sm text-slate-500">
          {t('clients.nextFreePorts')}:{' '}
          {stats.available_ports.map((port, i) => (
            <span key={port}>
              <span className="font-mono" style={{ color: neonBlue }}>{port}</span>
              {i < stats.available_ports.length - 1 && ', '}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}