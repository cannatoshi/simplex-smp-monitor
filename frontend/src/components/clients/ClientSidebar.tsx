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
  onSendMessage?: (contactName: string, message: string) => Promise<void>;
}

export default function ClientSidebar({ client, connections, onSendMessage }: Props) {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const [selectedContact, setSelectedContact] = useState('');
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<{type: 'success' | 'error', text: string} | null>(null);

  // Neon Button Style
  const neonButtonStyle = {
    backgroundColor: 'rgb(30, 41, 59)',
    color: neonBlue,
    border: `1px solid ${neonBlue}`,
    boxShadow: neonGlow
  };

  const getContactOptions = () => {
    return connections.map(conn => {
      const isClientA = conn.client_a === client.id;
      return {
        contactName: isClientA ? conn.contact_name_on_a : conn.contact_name_on_b,
        recipientName: isClientA ? conn.client_b_name : conn.client_a_name,
      };
    });
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !selectedContact || !onSendMessage) return;
    setSending(true);
    setFeedback(null);
    try {
      await onSendMessage(selectedContact, message);
      setFeedback({ type: 'success', text: t('clients.messageSent') });
      setMessage('');
      setTimeout(() => setFeedback(null), 3000);
    } catch {
      setFeedback({ type: 'error', text: t('clients.sendError') });
    } finally {
      setSending(false);
    }
  };

  const contactOptions = getContactOptions();
  const showSendForm = client.status === 'running' && connections.length > 0;

  return (
    <div className="h-full flex flex-col space-y-6">
      {showSendForm ? (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 flex-shrink-0">
          <div className="p-4 border-b border-slate-200 dark:border-slate-800">
            <h2 className="text-lg font-semibold" style={{ color: neonBlue }}>{t('clients.sendMessage')}</h2>
          </div>
          <form onSubmit={handleSend} className="p-4 space-y-4">
            <div>
              <label className="block text-sm text-slate-500 mb-1">{t('clients.recipient')}</label>
              <select 
                value={selectedContact} 
                onChange={e => setSelectedContact(e.target.value)}
                className="w-full px-3 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
              >
                <option value="">{t('clients.selectRecipient')}</option>
                {contactOptions.map((opt, i) => (
                  <option key={i} value={opt.contactName}>{opt.recipientName} ({opt.contactName})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-500 mb-1">{t('messages.message')}</label>
              <textarea 
                value={message} 
                onChange={e => setMessage(e.target.value)} 
                rows={3}
                className="w-full px-3 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                placeholder={t('clients.messagePlaceholder')}
              />
            </div>
            <button 
              type="submit" 
              disabled={sending || !message.trim() || !selectedContact}
              className="w-full px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 hover:opacity-90 transition-opacity font-medium"
              style={neonButtonStyle}
            >
              {sending ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              ) : t('clients.send')}
            </button>
            {feedback && (
              <div 
                className="text-sm text-center py-2 rounded-lg"
                style={{ 
                  backgroundColor: feedback.type === 'success' ? 'rgba(136, 206, 208, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                  color: feedback.type === 'success' ? neonBlue : '#f87171'
                }}
              >
                {feedback.text}
              </div>
            )}
          </form>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 text-center flex-shrink-0">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
            <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
          <p className="text-slate-500 text-sm">{t('clients.createConnectionFirst')}</p>
        </div>
      )}

      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold" style={{ color: neonBlue }}>{t('clients.details')}</h2>
        </div>
        <div className="p-4 space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.containerId')}</span>
            <span className="text-slate-900 dark:text-white font-mono text-xs">{client.container_id?.slice(0, 12) || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.containerName')}</span>
            <span className="text-slate-900 dark:text-white">{client.container_name || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.dataVolume')}</span>
            <span className="text-slate-900 dark:text-white text-xs truncate max-w-[150px]">{client.data_volume || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.profileName')}</span>
            <span className="text-slate-900 dark:text-white">{client.profile_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.tor')}</span>
            <span style={{ color: client.use_tor ? neonBlue : undefined }} className={!client.use_tor ? 'text-slate-400' : ''}>
              {client.use_tor ? t('clients.torActive') : t('clients.torInactive')}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.websocket')}</span>
            <span className="font-mono text-xs" style={{ color: neonBlue }}>ws://localhost:{client.websocket_port}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">{t('clients.created')}</span>
            <span className="text-slate-900 dark:text-white">{client.created_at ? new Date(client.created_at).toLocaleDateString('de-DE') : '-'}</span>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 flex-1 flex flex-col min-h-[150px]">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex-shrink-0">
          <h2 className="text-lg font-semibold" style={{ color: neonBlue }}>{t('clients.smpServers')}</h2>
        </div>
        <div className="p-4 space-y-3 flex-1">
          {client.smp_server_ids && client.smp_server_ids.length > 0 ? (
            client.smp_server_ids.map((serverId: number, i: number) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
                    <span 
                      className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                      style={{ backgroundColor: cyan }}
                    ></span>
                    <span 
                      className="relative inline-flex rounded-full h-2.5 w-2.5"
                      style={{ backgroundColor: cyan }}
                    ></span>
                  </span>
                  <span className="text-slate-900 dark:text-white">Server #{serverId}</span>
                </div>
                <span className="text-slate-500 text-xs flex-shrink-0 ml-2">SMP</span>
              </div>
            ))
          ) : (
            <p className="text-slate-500 text-sm">{t('clients.noSmpServers')}</p>
          )}
        </div>
      </div>
    </div>
  );
}