import { useState } from 'react';

interface Message {
  id: string;
  direction?: 'sent' | 'received';
  recipient_name?: string;
  sender_name?: string;
  contact_name?: string;
  content: string;
  delivery_status: 'pending' | 'sent' | 'delivered' | 'failed';
  total_latency_ms?: number | null;
  created_at: string;
}

interface Props {
  sentMessages: Message[];
  receivedMessages: Message[];
}

export default function ClientMessages({ sentMessages, receivedMessages }: Props) {
  const [tab, setTab] = useState<'sent' | 'received' | 'all'>('sent');

  const allMessages = [...sentMessages, ...receivedMessages].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const formatTime = (date: string) => new Date(date).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
      case 'delivered': return <span className="text-emerald-500">✓✓</span>;
      case 'sent': return <span className="text-amber-500">✓</span>;
      case 'failed': return <span className="text-red-500">✗</span>;
      default: return <span className="text-slate-400 animate-pulse">⏳</span>;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden flex-1 flex flex-col min-h-[300px]">
      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-800">
        <nav className="flex">
          {(['sent', 'received', 'all'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t
                  ? 'text-cyan-600 dark:text-cyan-400 border-cyan-500'
                  : 'text-slate-500 border-transparent hover:text-slate-700 dark:hover:text-slate-300'
              }`}>
              {t === 'sent' ? '↑ Gesendet' : t === 'received' ? '↓ Empfangen' : 'Alle'}
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
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Zeit</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Empfänger</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Nachricht</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                <th className="px-3 py-2 text-right text-xs font-medium text-slate-500 uppercase">Latenz</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {sentMessages.length === 0 ? (
                <tr><td colSpan={5} className="px-3 py-8 text-center text-slate-500">Keine gesendeten Nachrichten</td></tr>
              ) : sentMessages.map(msg => (
                <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">{formatTime(msg.created_at)}</td>
                  <td className="px-3 py-2 text-slate-900 dark:text-white">{msg.recipient_name}</td>
                  <td className="px-3 py-2 text-slate-600 dark:text-slate-300 max-w-xs truncate">{msg.content.slice(0, 30)}</td>
                  <td className="px-3 py-2"><StatusIcon status={msg.delivery_status} /></td>
                  <td className="px-3 py-2 text-right text-slate-500 text-xs">{msg.total_latency_ms ? `${msg.total_latency_ms}ms` : '-'}</td>
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
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Zeit</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Absender</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Nachricht</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {receivedMessages.length === 0 ? (
                <tr><td colSpan={3} className="px-3 py-8 text-center text-slate-500">Keine empfangenen Nachrichten</td></tr>
              ) : receivedMessages.map(msg => (
                <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">{formatTime(msg.created_at)}</td>
                  <td className="px-3 py-2 text-slate-900 dark:text-white">{msg.sender_name}</td>
                  <td className="px-3 py-2 text-slate-600 dark:text-slate-300">{msg.content.slice(0, 50)}</td>
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
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Zeit</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Typ</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Kontakt</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Nachricht</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                <th className="px-3 py-2 text-right text-xs font-medium text-slate-500 uppercase">Latenz</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {allMessages.length === 0 ? (
                <tr><td colSpan={6} className="px-3 py-8 text-center text-slate-500">Keine Nachrichten</td></tr>
              ) : allMessages.map(msg => (
                <tr key={msg.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-3 py-2 text-slate-500 text-sm whitespace-nowrap">{formatTime(msg.created_at)}</td>
                  <td className="px-3 py-2">{msg.direction === 'sent' ? <span className="text-emerald-500 text-xs">↑ OUT</span> : <span className="text-cyan-500 text-xs">↓ IN</span>}</td>
                  <td className="px-3 py-2 text-slate-900 dark:text-white">{msg.contact_name || msg.recipient_name || msg.sender_name}</td>
                  <td className="px-3 py-2 text-slate-600 dark:text-slate-300 max-w-xs truncate">{msg.content.slice(0, 30)}</td>
                  <td className="px-3 py-2"><StatusIcon status={msg.delivery_status} /></td>
                  <td className="px-3 py-2 text-right text-slate-500 text-xs">{msg.total_latency_ms ? `${msg.total_latency_ms}ms` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
