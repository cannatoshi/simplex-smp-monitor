import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { simplexClientsApi, serversApi, Server } from '../api/client';

interface FormData {
  websocket_port: number;
  use_tor: boolean;
  description: string;
  smp_server_ids: number[];
}

export default function ClientForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [availablePorts, setAvailablePorts] = useState<number[]>([]);
  const [servers, setServers] = useState<Server[]>([]);
  const [formData, setFormData] = useState<FormData>({
    websocket_port: 0,
    use_tor: true,
    description: '',
    smp_server_ids: []
  });

  useEffect(() => {
    loadInitialData();
  }, [id]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [statsData, serversData] = await Promise.all([
        simplexClientsApi.stats(),
        serversApi.list()
      ]);

      // Nur SMP Server (nicht XFTP)
      const smpServers = serversData.results.filter(s => s.server_type === 'smp');
      setServers(smpServers);

      const ports = statsData.available_ports || [];
      setAvailablePorts(ports);

      if (isEdit && id) {
        const client = await simplexClientsApi.get(id);
        setFormData({
          websocket_port: client.websocket_port,
          use_tor: client.use_tor,
          description: client.description || '',
          smp_server_ids: client.smp_server_ids || []
        });
        if (!ports.includes(client.websocket_port)) {
          setAvailablePorts([client.websocket_port, ...ports]);
        }
      } else {
        if (ports.length > 0) {
          setFormData(prev => ({ ...prev, websocket_port: ports[0] }));
        }
      }
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleServerToggle = (serverId: number) => {
    setFormData(prev => ({
      ...prev,
      smp_server_ids: prev.smp_server_ids.includes(serverId)
        ? prev.smp_server_ids.filter(id => id !== serverId)
        : [...prev.smp_server_ids, serverId]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (availablePorts.length === 0 && !isEdit) {
      alert('Keine Ports verfügbar.');
      return;
    }
    setSaving(true);
    try {
      if (isEdit) {
        await simplexClientsApi.update(id!, formData);
      } else {
        await simplexClientsApi.create(formData);
      }
      navigate('/clients');
    } catch (err) {
      console.error('Error saving client:', err);
      alert('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/clients" className="text-slate-500 hover:text-slate-700 dark:hover:text-white text-sm inline-flex items-center gap-1 mb-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
            </svg>
            Alle Clients
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            {isEdit ? 'Client bearbeiten' : 'Neuer Client'}
          </h1>
        </div>
        <div className="flex gap-2">
          <Link to="/clients" className="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium">
            Abbrechen
          </Link>
          <button
            onClick={handleSubmit}
            disabled={saving || (availablePorts.length === 0 && !isEdit)}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium flex items-center gap-2"
          >
            {saving && (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
            )}
            {isEdit ? 'Speichern' : 'Client erstellen'}
          </button>
        </div>
      </div>

      {/* Info Banner */}
      {!isEdit && (
        <div className="bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-800 rounded-xl p-4 flex items-start gap-3">
          <svg className="w-6 h-6 text-cyan-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          <div>
            <p className="font-medium text-cyan-900 dark:text-cyan-300">Automatische Generierung</p>
            <p className="text-sm text-cyan-700 dark:text-cyan-400 mt-1">
              Name, Slug und Profil werden automatisch generiert. Beispiel: "Client 004" / "client-004" / "dave"
            </p>
          </div>
        </div>
      )}

      {/* Port Warning */}
      {availablePorts.length === 0 && !isEdit && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
          <svg className="w-6 h-6 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <div>
            <p className="font-medium text-red-900 dark:text-red-300">Keine Ports verfügbar</p>
            <p className="text-sm text-red-700 dark:text-red-400 mt-1">Alle Ports (3031-3080) sind belegt. Lösche erst einen Client.</p>
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Main Settings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Docker Configuration */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Docker Konfiguration</h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">WebSocket Port *</label>
              <select
                value={formData.websocket_port}
                onChange={e => setFormData(prev => ({ ...prev, websocket_port: parseInt(e.target.value) }))}
                required
                disabled={availablePorts.length === 0 && !isEdit}
                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 disabled:opacity-50"
              >
                {availablePorts.length === 0 ? (
                  <option value="">Keine Ports verfügbar</option>
                ) : (
                  availablePorts.map(port => (
                    <option key={port} value={port}>Port {port}</option>
                  ))
                )}
              </select>
              <p className="text-xs text-slate-500 mt-1">{availablePorts.length} Port{availablePorts.length !== 1 ? 's' : ''} verfügbar (3031-3080)</p>
            </div>
          </div>

          {/* SimpleX Configuration */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">SimpleX Konfiguration</h2>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.use_tor}
                onChange={e => setFormData(prev => ({ ...prev, use_tor: e.target.checked }))}
                className="w-5 h-5 rounded bg-slate-50 dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-cyan-600 focus:ring-cyan-500"
              />
              <div>
                <span className="text-slate-700 dark:text-slate-300 font-medium">Tor verwenden</span>
                <p className="text-xs text-slate-500">Verbindung über SOCKS5 Proxy (localhost:9050)</p>
              </div>
            </label>
          </div>

          {/* Description */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Beschreibung</h2>
            <textarea
              value={formData.description}
              onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={4}
              placeholder="Optionale Notizen zu diesem Client..."
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </div>
        </div>

        {/* Right Column - Server Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 h-full flex flex-col">
            <div className="p-4 border-b border-slate-200 dark:border-slate-800">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                SMP Server
                {formData.smp_server_ids.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-cyan-500">
                    ({formData.smp_server_ids.length} ausgewählt)
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-500 mt-1">Client nutzt diese Server für Nachrichten</p>
            </div>
            
            <div className="p-4 flex-1 overflow-y-auto">
              {servers.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 mx-auto text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"/>
                  </svg>
                  <p className="text-slate-500 mb-2">Keine SMP Server</p>
                  <Link to="/servers/new" className="text-cyan-500 hover:text-cyan-400 text-sm">
                    + Server hinzufügen
                  </Link>
                </div>
              ) : (
                <div className="space-y-2">
                  {servers.map(server => (
                    <label
                      key={server.id}
                      className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all ${
                        formData.smp_server_ids.includes(server.id)
                          ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={formData.smp_server_ids.includes(server.id)}
                        onChange={() => handleServerToggle(server.id)}
                        className="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-cyan-600 focus:ring-cyan-500"
                      />
                      <div className="ml-3 flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                            server.is_active ? 'bg-emerald-500' : 'bg-slate-400'
                          }`}></span>
                          <span className="font-medium text-slate-900 dark:text-white text-sm truncate">
                            {server.name}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 truncate">{server.host}</p>
                      </div>
                      {server.is_onion && (
                        <span className="text-xs text-purple-500 bg-purple-100 dark:bg-purple-900/30 px-1.5 py-0.5 rounded flex-shrink-0">
                          TOR
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
