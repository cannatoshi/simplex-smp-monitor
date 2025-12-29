import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useServer } from '../hooks/useApi';
import { serversApi } from '../api/client';

export default function ServerDetail() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: server, loading, error } = useServer(id ? parseInt(id) : null);

  const handleDelete = async () => {
    if (!server) return;
    if (!confirm(`Delete server '${server.name}'?`)) return;
    try {
      await serversApi.delete(server.id);
      navigate('/servers');
    } catch (err) {
      alert('Delete failed: ' + (err as Error).message);
    }
  };

  const handleToggle = async () => {
    if (!server) return;
    try {
      await serversApi.toggleActive(server.id);
      window.location.reload();
    } catch (err) {
      alert('Toggle failed: ' + (err as Error).message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error || !server) {
    return (
      <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-400">
        {error || 'Server not found'}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-white">{server.name}</h1>
          <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">{server.server_type.toUpperCase()} Server</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${server.is_active ? 'bg-primary-900/30 text-primary-400' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'}`}>
            {server.is_active ? t('common.active') : t('common.inactive')}
          </span>
          <button onClick={handleToggle} className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-300 px-4 py-1.5 rounded-lg text-sm font-medium">
            {server.is_active ? 'Deaktivieren' : 'Aktivieren'}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Server Details</h2>
        <dl className="space-y-5">
          <div>
            <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Host</dt>
            <dd className="text-white font-mono text-sm bg-slate-100 dark:bg-slate-800 p-3 rounded-lg break-all">{server.host}</dd>
          </div>
          <div>
            <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Fingerprint</dt>
            <dd className="text-white font-mono text-sm bg-slate-100 dark:bg-slate-800 p-3 rounded-lg break-all">{server.fingerprint || '-'}</dd>
          </div>
          <div className="grid grid-cols-2 gap-5">
            <div>
              <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Status</dt>
              <dd><span className={`px-2.5 py-1 rounded-full text-sm font-medium ${server.last_status === 'online' ? 'bg-primary-900/30 text-primary-400' : server.last_status === 'offline' ? 'bg-red-900/30 text-red-400' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'}`}>{server.last_status || 'Unknown'}</span></dd>
            </div>
            <div>
              <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Letzter Check</dt>
              <dd className="text-white">{server.last_check ? new Date(server.last_check).toLocaleString('de-DE') : '—'}</dd>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-5">
            <div>
              <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Latenz</dt>
              <dd className="text-white">{server.last_latency ? `${server.last_latency}ms` : '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Uptime</dt>
              <dd className="text-white">{server.uptime_percent ? `${server.uptime_percent.toFixed(1)}%` : '—'}</dd>
            </div>
          </div>
          {server.is_onion && (
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-purple-900/30 text-purple-400">🧅 Onion</span>
            </div>
          )}
        </dl>
      </div>

      <div className="flex space-x-3">
        <Link to="/servers" className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg font-medium">← Zurück</Link>
        <Link to={`/servers/${server.id}/edit`} className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium">Bearbeiten</Link>
        <button onClick={handleDelete} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium">Löschen</button>
      </div>
    </div>
  );
}
