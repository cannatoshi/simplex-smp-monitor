/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * ClientMessages Component
 * 
 * Displays message history in tabs:
 * - Sent: Messages sent by this client
 * - Received: Messages received by this client
 * - All: Combined view with direction indicators
 * 
 * Features:
 * - Profile name display (maria, bob, etc.)
 * - Direction badges (↑ Outgoing, ↓ Incoming)
 * - Status icons with cyan color for delivered/sent
 * - Latency display with color coding
 * - Content without tracking ID prefix
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';

// Brand colors
const neonBlue = '#88CED0';
const cyan = '#22D3EE';

interface Message {
  id: string;
  direction?: 'sent' | 'received';
  recipient_name?: string;
  sender_name?: string;
  recipient_profile?: string;
  sender_profile?: string;
  contact_name?: string;
  content: string;
  content_clean?: string;
  delivery_status: 'sending' | 'sent' | 'delivered' | 'failed';
  total_latency_ms?: number | null;
  created_at: string;
}

interface Props {
  sentMessages: Message[];
  receivedMessages: Message[];
}

export default function ClientMessages({ sentMessages, receivedMessages }: Props) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<'sent' | 'received' | 'all'>('sent');

  // Combine and sort all messages
  const allMessages = [...sentMessages, ...receivedMessages].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const formatTime = (date: string) => 
    new Date(date).toLocaleTimeString('de-DE', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });

  // Get display content (prefer content_clean if available)
  const getContent = (msg: Message): string => {
    const content = msg.content_clean || msg.content;
    return content.slice(0, 40);
  };

  // Status Icon - CYAN for delivered/sent
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

  // Latency display with color coding
  const LatencyDisplay = ({ ms }: { ms: number | null | undefined }) => {
    if (!ms) return <span className="text-slate-500">-</span>;
    
    let color = '#22C55E'; // green
    if (ms >= 2000) color = '#EF4444'; // red
    else if (ms >= 500) color = '#EAB308'; // yellow
    
    return (
      <span style={{ color }}>
        {ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`}
      </span>
    );
  };

  const tabs = [
    { key: 'sent', label: `↑ ${t('messages.sent')}` },
    { key: 'received', label: `↓ ${t('messages.received')}` },
    { key: 'all', label: t('messages.all') },
  ] as const;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden flex-1 flex flex-col min-h-[300px]">
      {/* Tabs - NEON BLUE */}
      <div className="border-b border-slate-200 dark:border-slate-800">
        <nav className="flex">
          {tabs.map(tabItem => (
            <button 
              key={tabItem.key} 
              onClick={() => setTab(tabItem.key)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === tabItem.key
                  ? 'border-current'
                  : 'text-slate-500 border-transparent hover:text-slate-700 dark:hover:text-slate-300'
              }`}
              style={tab === tabItem.key ? { color: neonBlue, borderColor: neonBlue } : undefined}
            >
              {tabItem.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Sent Tab */}
      {tab === 'sent' && (
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead className="bg-slate-50 dark:bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.time')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.recipient')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.message')}</th>
                <th className="px-3 py-2 text-center text-xs font-medium text-slate-500 uppercase">{t('messages.status')}</th>
                <th className="px-3 py-2 text-right text-xs font-medium text-slate-500 uppercase">{t('messages.latency')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {sentMessages.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 py-8 text-center text-slate-500">
                    {t('messages.noSentMessages')}
                  </td>
                </tr>
              ) : sentMessages.map(msg => (
                <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">
                    {formatTime(msg.created_at)}
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-slate-900 dark:text-white">{msg.recipient_name}</span>
                    {msg.recipient_profile && (
                      <span className="text-slate-500 text-sm ml-1">({msg.recipient_profile})</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-slate-600 dark:text-slate-300 max-w-xs truncate">
                    {getContent(msg)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <StatusIcon status={msg.delivery_status} />
                  </td>
                  <td className="px-3 py-2 text-right text-xs">
                    <LatencyDisplay ms={msg.total_latency_ms} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Received Tab */}
      {tab === 'received' && (
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead className="bg-slate-50 dark:bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.time')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.sender')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.message')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {receivedMessages.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-3 py-8 text-center text-slate-500">
                    {t('messages.noReceivedMessages')}
                  </td>
                </tr>
              ) : receivedMessages.map(msg => (
                <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">
                    {formatTime(msg.created_at)}
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-slate-900 dark:text-white">{msg.sender_name}</span>
                    {msg.sender_profile && (
                      <span className="text-slate-500 text-sm ml-1">({msg.sender_profile})</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-slate-600 dark:text-slate-300">
                    {getContent(msg)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* All Tab */}
      {tab === 'all' && (
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead className="bg-slate-50 dark:bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.time')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.type')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.contact')}</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">{t('messages.message')}</th>
                <th className="px-3 py-2 text-center text-xs font-medium text-slate-500 uppercase">{t('messages.status')}</th>
                <th className="px-3 py-2 text-right text-xs font-medium text-slate-500 uppercase">{t('messages.latency')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {allMessages.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-3 py-8 text-center text-slate-500">
                    {t('messages.noMessages')}
                  </td>
                </tr>
              ) : allMessages.map(msg => {
                const isSent = msg.direction === 'sent';
                const contactName = msg.contact_name || (isSent ? msg.recipient_name : msg.sender_name);
                const contactProfile = isSent ? msg.recipient_profile : msg.sender_profile;
                
                return (
                  <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">
                      {formatTime(msg.created_at)}
                    </td>
                    <td className="px-3 py-2">
                      {isSent ? (
                        <span 
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                          style={{ backgroundColor: 'rgba(136, 206, 208, 0.2)', color: neonBlue }}
                        >
                          ↑ {t('messages.outgoing')}
                        </span>
                      ) : (
                        <span 
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                          style={{ backgroundColor: 'rgba(34, 211, 238, 0.2)', color: cyan }}
                        >
                          ↓ {t('messages.incoming')}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <span className="text-slate-900 dark:text-white">{contactName}</span>
                      {contactProfile && (
                        <span className="text-slate-500 text-sm ml-1">({contactProfile})</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-slate-600 dark:text-slate-300 max-w-xs truncate">
                      {getContent(msg)}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <StatusIcon status={msg.delivery_status} />
                    </td>
                    <td className="px-3 py-2 text-right text-xs">
                      <LatencyDisplay ms={msg.total_latency_ms} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}