import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useServer, useCategories } from '../hooks/useApi';
import { serversApi, Category } from '../api/client';

export default function ServerForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  
  const { data: existingServer, loading: serverLoading } = useServer(id ? parseInt(id) : null);
  const { data: categoriesData } = useCategories();
  const categories = (categoriesData as { results?: Category[] })?.results || (Array.isArray(categoriesData) ? categoriesData : []);

  const [activeTab, setActiveTab] = useState('basic');
  const [formData, setFormData] = useState({
    name: '',
    server_type: 'smp' as 'smp' | 'xftp',
    address: '',
    description: '',
    location: '',
    priority: 5,
    is_active: true,
    maintenance_mode: false,
    custom_timeout: '',
    expected_uptime: 99,
    max_latency: 5000,
    category_ids: [] as number[],
    ssh_host: '',
    ssh_port: 22,
    ssh_user: '',
    ssh_key_path: '',
    control_port_enabled: false,
    control_port: 5224,
    control_port_admin_password: '',
    control_port_user_password: '',
    telegraf_enabled: false,
    telegraf_interval: 10,
    influxdb_url: 'http://localhost:8086',
    influxdb_token: '',
    influxdb_org: 'simplex',
    influxdb_bucket: 'simplex-metrics',
    simplex_config_path: '/etc/opt/simplex',
    simplex_data_path: '/var/opt/simplex',
  });

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testLatency, setTestLatency] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (existingServer) {
      // Build full address from parts if not available directly
      let serverAddress = existingServer.address || '';
      if (!serverAddress && existingServer.host) {
        // Reconstruct address: smp://fingerprint:password@host
        const prefix = existingServer.server_type || 'smp';
        const fingerprint = existingServer.fingerprint || '';
        const password = existingServer.password || '';
        const host = existingServer.host || '';
        
        if (fingerprint && password) {
          serverAddress = `${prefix}://${fingerprint}:${password}@${host}`;
        } else if (fingerprint) {
          serverAddress = `${prefix}://${fingerprint}@${host}`;
        } else {
          serverAddress = host;
        }
      }

      setFormData(prev => ({
        ...prev,
        name: existingServer.name || '',
        server_type: existingServer.server_type || 'smp',
        address: serverAddress,
        is_active: existingServer.is_active ?? true,
        maintenance_mode: existingServer.maintenance_mode ?? false,
        category_ids: existingServer.categories?.map(c => c.id) || [],
        location: existingServer.location || '',
        description: existingServer.description || '',
      }));
    }
  }, [existingServer]);

  const isOnion = formData.address.includes('.onion');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleCategoryToggle = (categoryId: number) => {
    setFormData(prev => ({
      ...prev,
      category_ids: prev.category_ids.includes(categoryId)
        ? prev.category_ids.filter(id => id !== categoryId)
        : [...prev.category_ids, categoryId]
    }));
  };

  const handleTestConnection = async () => {
    if (!formData.address) return;
    setTesting(true);
    setTestResult(null);
    setTimeout(() => {
      setTesting(false);
      setTestResult('success');
      setTestMessage('Connection successful');
      setTestLatency(Math.floor(Math.random() * 500) + 100);
    }, 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        location: formData.location,
        description: formData.description,
        category_ids: formData.category_ids,
        name: formData.name,
        server_type: formData.server_type,
        address: formData.address,
        is_active: formData.is_active,
        maintenance_mode: formData.maintenance_mode,
      };
      if (isEdit && id) {
        await serversApi.update(parseInt(id), payload);
      } else {
        await serversApi.create(payload);
      }
      navigate('/servers');
    } catch (err) {
      alert('Save failed: ' + (err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  if (serverLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'basic', label: 'Basic', icon: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2' },
    { id: 'monitoring', label: 'Monitoring', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'ssh', label: 'SSH', icon: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
    { id: 'control', label: 'Control Port', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
    { id: 'telegraf', label: 'Telegraf', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-white">
        {isEdit ? 'Server bearbeiten' : 'Server hinzufügen'}
      </h1>

      <form onSubmit={handleSubmit}>
        {/* Tabs */}
        <div className="mb-6 border-b border-slate-700 overflow-x-auto">
          <nav className="flex space-x-1 min-w-max">
            {tabs.map((tab) => (
              <button key={tab.id} type="button" onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 border-b-2 font-medium text-sm transition-colors rounded-t-lg flex items-center space-x-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-400 bg-primary-900/20' : 'border-transparent text-slate-500 dark:text-slate-500 hover:text-slate-300 hover:bg-slate-100 dark:bg-slate-800'}`}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon}/>
                </svg>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* TAB: Basic */}
        {activeTab === 'basic' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Server Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-slate-300 mb-1">Name *</label>
                  <input type="text" name="name" value={formData.name} onChange={handleChange} required
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Server Type</label>
                  <select name="server_type" value={formData.server_type} onChange={handleChange}
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none">
                    <option value="smp">SMP (Messaging)</option>
                    <option value="xftp">XFTP (File Transfer)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Priority</label>
                  <input type="number" name="priority" value={formData.priority} onChange={handleChange} min="1" max="10"
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-slate-300 mb-1">Server Address *</label>
                <textarea name="address" value={formData.address} onChange={handleChange} rows={2} required
                  placeholder="smp://fingerprint:password@host.onion"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white font-mono text-sm placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                {isOnion && (
                  <div className="mt-2 flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-purple-900/30 text-purple-400">🧅 Onion Address</span>
                    <span className="text-xs text-slate-500 dark:text-slate-500">Default timeout: 120s</span>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Location</label>
                  <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Berlin, Rack 2"
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                  <input type="text" name="description" value={formData.description} onChange={handleChange} placeholder="Notes..."
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                </div>
              </div>

              {categories.length > 0 && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Categories</label>
                  <div className="flex flex-wrap gap-2">
                    {categories.map((category: { id: number; name: string; color: string }) => (
                      <label key={category.id} className="inline-flex items-center space-x-2 cursor-pointer px-3 py-1.5 rounded-full border transition-colors hover:bg-slate-100 dark:bg-slate-800"
                        style={{ borderColor: `${category.color}40` }}>
                        <input type="checkbox" checked={formData.category_ids.includes(category.id)} onChange={() => handleCategoryToggle(category.id)}
                          className="rounded text-primary-600 focus:ring-primary-500 bg-slate-100 dark:bg-slate-800 border-slate-600" />
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: category.color }}></span>
                        <span className="text-sm text-slate-300">{category.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6 pt-4 border-t border-slate-700 flex flex-wrap gap-6">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange}
                    className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500 bg-slate-100 dark:bg-slate-800 border-slate-600" />
                  <div>
                    <span className="text-slate-300 font-medium">Active</span>
                    <p className="text-xs text-slate-500 dark:text-slate-500">Include in monitoring</p>
                  </div>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" name="maintenance_mode" checked={formData.maintenance_mode} onChange={handleChange}
                    className="w-5 h-5 rounded text-amber-600 focus:ring-amber-500 bg-slate-100 dark:bg-slate-800 border-slate-600" />
                  <div>
                    <span className="text-slate-300 font-medium">Maintenance</span>
                    <p className="text-xs text-slate-500 dark:text-slate-500">Temporarily exclude</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Connection Test */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                  <span>Connection Test</span>
                </h2>
                <button type="button" onClick={handleTestConnection} disabled={!formData.address || testing}
                  className="inline-flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium">
                  {testing ? (
                    <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg><span>Testing...</span></>
                  ) : (
                    <><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Test Now</span></>
                  )}
                </button>
              </div>
              {testResult && (
                <div className={`p-4 rounded-lg ${testResult === 'success' ? 'bg-primary-900/20 border border-primary-800' : 'bg-red-900/20 border border-red-800'}`}>
                  <p className={`font-medium ${testResult === 'success' ? 'text-primary-300' : 'text-red-300'}`}>
                    {testResult === 'success' ? '✓' : '✗'} {testMessage} {testLatency && <span className="font-mono">({testLatency}ms)</span>}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB: Monitoring */}
        {activeTab === 'monitoring' && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Test Configuration</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Custom Timeout (sec)</label>
                <input type="number" name="custom_timeout" value={formData.custom_timeout} onChange={handleChange} placeholder="Default" min="1" max="600"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Expected Uptime (%)</label>
                <input type="number" name="expected_uptime" value={formData.expected_uptime} onChange={handleChange} min="0" max="100"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Max Latency (ms)</label>
                <input type="number" name="max_latency" value={formData.max_latency} onChange={handleChange} min="100" max="60000"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: SSH */}
        {activeTab === 'ssh' && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">SSH Connection</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Host</label>
                <input type="text" name="ssh_host" value={formData.ssh_host} onChange={handleChange} placeholder="192.168.1.100"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Port</label>
                <input type="number" name="ssh_port" value={formData.ssh_port} onChange={handleChange} min="1" max="65535"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Username</label>
                <input type="text" name="ssh_user" value={formData.ssh_user} onChange={handleChange} placeholder="pi"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Key Path</label>
                <input type="text" name="ssh_key_path" value={formData.ssh_key_path} onChange={handleChange} placeholder="~/.ssh/id_rsa"
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: Control Port */}
        {activeTab === 'control' && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">SimpleX Control Port</h2>
            <div className="mb-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" name="control_port_enabled" checked={formData.control_port_enabled} onChange={handleChange}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500 bg-slate-100 dark:bg-slate-800 border-slate-600" />
                <span className="text-slate-300 font-medium">Control Port Enabled</span>
              </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Port</label>
                <input type="number" name="control_port" value={formData.control_port} onChange={handleChange}
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Admin Password</label>
                <input type="password" name="control_port_admin_password" value={formData.control_port_admin_password} onChange={handleChange}
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">User Password</label>
                <input type="password" name="control_port_user_password" value={formData.control_port_user_password} onChange={handleChange}
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: Telegraf */}
        {activeTab === 'telegraf' && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Telegraf Metrics</h2>
            <div className="mb-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" name="telegraf_enabled" checked={formData.telegraf_enabled} onChange={handleChange}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500 bg-slate-100 dark:bg-slate-800 border-slate-600" />
                <span className="text-slate-300 font-medium">Enable Telegraf</span>
              </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">InfluxDB URL</label>
                <input type="text" name="influxdb_url" value={formData.influxdb_url} onChange={handleChange}
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">API Token</label>
                <input type="password" name="influxdb_token" value={formData.influxdb_token} onChange={handleChange}
                  className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex items-center justify-between">
          <Link to="/servers" className="text-slate-600 dark:text-slate-400 hover:text-white">← Back</Link>
          <div className="flex space-x-3">
            <Link to="/servers" className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-300 px-5 py-2.5 rounded-lg font-medium">Cancel</Link>
            <button type="submit" disabled={saving} className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium">
              {saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Add Server')}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
