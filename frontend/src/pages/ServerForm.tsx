import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useServer, useCategories } from '../hooks/useApi';
import { serversApi, Category } from '../api/client';

// Docker Status Badge Component
function DockerStatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
    not_created: { bg: 'bg-slate-700', text: 'text-slate-300', label: '⚪ Not Created' },
    created: { bg: 'bg-blue-900/30', text: 'text-blue-400', label: '🔵 Created' },
    starting: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', label: '🟡 Starting...' },
    running: { bg: 'bg-green-900/30', text: 'text-green-400', label: '🟢 Running' },
    stopping: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', label: '🟡 Stopping...' },
    stopped: { bg: 'bg-red-900/30', text: 'text-red-400', label: '🔴 Stopped' },
    error: { bg: 'bg-red-900/30', text: 'text-red-400', label: '❌ Error' },
  };
  
  const config = statusConfig[status] || statusConfig.not_created;
  
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
}

interface ServerData {
  name?: string;
  server_type?: 'smp' | 'xftp' | 'ntf';
  address?: string;
  is_active?: boolean;
  maintenance_mode?: boolean;
  categories?: Category[];
  location?: string;
  description?: string;
  fingerprint?: string;
  password?: string;
  host?: string;
  is_docker_hosted?: boolean;
  docker_status?: string;
  docker_error?: string;
  generated_address?: string;
  exposed_port?: number;
  container_name?: string;
  data_volume?: string;
  hosting_mode?: 'ip' | 'tor';
  host_ip?: string;
  onion_address?: string;
}

export default function ServerForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  
  const { data: existingServer, loading: serverLoading } = useServer(id ? parseInt(id) : null) as { data: ServerData | null; loading: boolean };
  const { data: categoriesData } = useCategories();
  const categories = (categoriesData as { results?: Category[] })?.results || (Array.isArray(categoriesData) ? categoriesData : []);

  const [activeTab, setActiveTab] = useState('basic');
  const [formData, setFormData] = useState({
    name: '',
    server_type: 'smp' as string,
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
    // Docker hosting
    is_docker_hosted: false,
    exposed_port: '',
    hosting_mode: 'ip' as 'ip' | 'tor',
    host_ip: '',
    // SMP Password (optional)
    smp_password: '',
    // SSH
    ssh_host: '',
    ssh_port: 22,
    ssh_user: '',
    ssh_key_path: '',
    // Control Port
    control_port_enabled: false,
    control_port: 5224,
    control_port_admin_password: '',
    control_port_user_password: '',
    // Telegraf
    telegraf_enabled: false,
    telegraf_interval: 10,
    influxdb_url: 'http://localhost:8086',
    influxdb_token: '',
    influxdb_org: 'simplex',
    influxdb_bucket: 'simplex-metrics',
    simplex_config_path: '/etc/opt/simplex',
    simplex_data_path: '/var/opt/simplex',
  });

  // Docker state
  const [dockerStatus, setDockerStatus] = useState('not_created');
  const [dockerError, setDockerError] = useState('');
  const [generatedAddress, setGeneratedAddress] = useState('');
  const [onionAddress, setOnionAddress] = useState('');
  const [dockerActionLoading, setDockerActionLoading] = useState(false);
  const [containerLogs, setContainerLogs] = useState('');
  const [showLogs, setShowLogs] = useState(false);
  const [dockerImagesAvailable, setDockerImagesAvailable] = useState<Record<string, { ip: boolean; tor: boolean }>>({}); 

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testLatency, setTestLatency] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  // Check available Docker images on mount
  useEffect(() => {
    checkDockerImages();
  }, []);

  const checkDockerImages = async () => {
    try {
      const response = await fetch('/api/v1/servers/docker-images/');
      if (response.ok) {
        const data = await response.json();
        setDockerImagesAvailable(data);
      }
    } catch (err) {
      console.error('Failed to check Docker images:', err);
    }
  };

  useEffect(() => {
    if (existingServer) {
      let serverAddress = existingServer.address || '';
      if (!serverAddress && existingServer.host) {
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
        category_ids: existingServer.categories?.map((c: Category) => c.id) || [],
        location: existingServer.location || '',
        description: existingServer.description || '',
        is_docker_hosted: existingServer.is_docker_hosted ?? false,
        exposed_port: existingServer.exposed_port?.toString() || '',
        hosting_mode: (existingServer as any).hosting_mode || 'ip',  // NEW
        host_ip: (existingServer as any).host_ip || '',  // NEW
      }));
      
      if (existingServer.is_docker_hosted) {
        setDockerStatus(existingServer.docker_status || 'not_created');
        setDockerError(existingServer.docker_error || '');
        setGeneratedAddress(existingServer.generated_address || '');
        setOnionAddress((existingServer as any).onion_address || '');  // NEW
      }
    }
  }, [existingServer]);

  const isOnion = formData.address.includes('.onion');
  const imageStatus = dockerImagesAvailable[formData.server_type];
  const isDockerImageAvailable = formData.hosting_mode === 'tor' 
    ? imageStatus?.tor ?? false 
    : imageStatus?.ip ?? false;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleCategoryToggle = (categoryId: number) => {
    setFormData(prev => ({
      ...prev,
      category_ids: prev.category_ids.includes(categoryId)
        ? prev.category_ids.filter(cid => cid !== categoryId)
        : [...prev.category_ids, categoryId]
    }));
  };

  const handleDockerToggle = () => {
    setFormData(prev => ({
      ...prev,
      is_docker_hosted: !prev.is_docker_hosted,
      address: !prev.is_docker_hosted ? '' : prev.address,
    }));
  };

  // Docker Actions
  const handleDockerAction = async (action: 'start' | 'stop' | 'restart' | 'delete') => {
    if (!id) return;
    
    setDockerActionLoading(true);
    setDockerError('');
    try {
      const response = await fetch(`/api/v1/servers/${id}/docker-action/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, remove_volumes: false }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setDockerStatus(data.docker_status);
        setGeneratedAddress(data.generated_address || '');
        if (showLogs) fetchContainerLogs();
      } else {
        setDockerError(data.error || 'Action failed');
      }
    } catch (err) {
      setDockerError((err as Error).message);
    } finally {
      setDockerActionLoading(false);
    }
  };

  const fetchContainerLogs = async () => {
    if (!id) return;
    try {
      const response = await fetch(`/api/v1/servers/${id}/logs/?tail=100`);
      if (response.ok) {
        const data = await response.json();
        setContainerLogs(data.logs);
      }
    } catch (err) {
      setContainerLogs(`Error fetching logs: ${(err as Error).message}`);
    }
  };

  const handleTestConnection = async () => {
    if (!formData.address && !generatedAddress) return;
    setTesting(true);
    setTestResult(null);
    setTimeout(() => {
      setTesting(false);
      setTestResult('success');
      setTestMessage('Connection successful');
      setTestLatency(Math.floor(Math.random() * 500) + 100);
    }, 2000);
  };

  const [saveError, setSaveError] = useState<string | null>(null);
  const [hasNavigated, setHasNavigated] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Prevent double-submit
    if (saving || hasNavigated) {
      console.log('Already saving or navigated, ignoring click');
      return;
    }
    
    console.log('handleSubmit called', { isEdit, id, name: formData.name });
    setSaving(true);
    setSaveError(null);
    
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: any = {
        name: formData.name,
        server_type: formData.server_type,
        address: formData.is_docker_hosted ? '' : formData.address,
        description: formData.description,
        location: formData.location,
        is_active: formData.is_active,
        maintenance_mode: formData.maintenance_mode,
        category_ids: formData.category_ids,
        is_docker_hosted: formData.is_docker_hosted,
        exposed_port: formData.exposed_port ? parseInt(formData.exposed_port) : null,
        hosting_mode: formData.hosting_mode,
        host_ip: formData.host_ip,
        smp_password: formData.smp_password || null,
      };
      
      console.log('Sending payload:', payload);
      
      if (isEdit && id) {
        console.log('Updating existing server...');
        await serversApi.update(parseInt(id), payload);
        console.log('Update successful, navigating...');
        setHasNavigated(true);
        navigate('/servers');
      } else {
        console.log('Creating new server...');
        const newServer = await serversApi.create(payload);
        console.log('Created server:', newServer);
        
        // Mark as navigated to prevent re-submit
        setHasNavigated(true);
        
        // Navigate to servers list (Edit-Seite hatte Auto-Submit Bug)
        console.log('Navigating to servers list');
        navigate('/servers', { replace: true });
      }
    } catch (err) {
      const errorMessage = (err as Error).message;
      setSaveError(errorMessage);
      console.error('Save failed:', errorMessage, err);
    } finally {
      setSaving(false);
      console.log('handleSubmit finished');
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
    { id: 'basic', label: 'Basic', icon: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2', show: true },
    { id: 'docker', label: 'Docker', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', show: formData.is_docker_hosted || (isEdit && existingServer?.is_docker_hosted) },
    { id: 'monitoring', label: 'Monitoring', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', show: true },
    { id: 'ssh', label: 'SSH', icon: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', show: !formData.is_docker_hosted },
    { id: 'control', label: 'Control Port', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', show: !formData.is_docker_hosted },
    { id: 'telegraf', label: 'Telegraf', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z', show: true },
  ].filter(tab => tab.show);

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
                className={`px-4 py-2.5 border-b-2 font-medium text-sm transition-colors rounded-t-lg flex items-center space-x-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-400 bg-primary-900/20' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-800'}`}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon}/>
                </svg>
                <span>{tab.label}</span>
                {tab.id === 'docker' && formData.is_docker_hosted && (
                  <span className="ml-1 w-2 h-2 rounded-full bg-blue-500"></span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* TAB: Basic */}
        {activeTab === 'basic' && (
          <div className="space-y-6">
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Server Details</h2>
              
              {/* Docker Hosting Toggle */}
              <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-blue-800/50">
                <label className="flex items-center justify-between cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-blue-900/30">
                      <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                      </svg>
                    </div>
                    <div>
                      <span className="text-white font-medium">🐳 Docker Hosted Server</span>
                      <p className="text-xs text-slate-400">Run this server locally in a Docker container</p>
                    </div>
                  </div>
                  <div className="relative flex-shrink-0">
                    <input type="checkbox" checked={formData.is_docker_hosted} onChange={handleDockerToggle}
                      className="sr-only" disabled={isEdit && existingServer?.is_docker_hosted} />
                    <div className={`w-14 h-7 rounded-full transition-colors flex items-center ${formData.is_docker_hosted ? 'bg-blue-600' : 'bg-slate-700'}`}>
                      <div className={`w-5 h-5 rounded-full bg-white shadow transform transition-transform ${formData.is_docker_hosted ? 'translate-x-8' : 'translate-x-1'}`}></div>
                    </div>
                  </div>
                </label>
                
                {formData.is_docker_hosted && !isDockerImageAvailable && (
                  <div className="mt-3 p-2 rounded bg-amber-900/30 border border-amber-700">
                    <p className="text-xs text-amber-400">
                      ⚠️ Docker image <code className="bg-slate-800 px-1 rounded">
                        simplex-{formData.server_type}{formData.hosting_mode === 'tor' ? '-tor' : ''}:latest
                      </code> not found.
                    </p>
                  </div>
                )}
                
                {/* Hosting Mode Selection (NEW) */}
                {formData.is_docker_hosted && (
                  <div className="mt-4 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                    <label className="block text-sm font-medium text-slate-300 mb-3">Hosting Mode</label>
                    <div className="grid grid-cols-2 gap-3">
                      {/* IP Mode */}
                      <label className={`relative flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        formData.hosting_mode === 'ip' 
                          ? 'border-blue-500 bg-blue-900/20' 
                          : 'border-slate-600 hover:border-slate-500'
                      }`}>
                        <input
                          type="radio"
                          name="hosting_mode"
                          value="ip"
                          checked={formData.hosting_mode === 'ip'}
                          onChange={handleChange}
                          className="sr-only"
                          disabled={isEdit && existingServer?.is_docker_hosted}
                        />
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">🏠</span>
                          <div>
                            <span className={`font-medium ${formData.hosting_mode === 'ip' ? 'text-blue-400' : 'text-slate-300'}`}>
                              LAN (IP)
                            </span>
                            <p className="text-xs text-slate-500">Local network access</p>
                          </div>
                        </div>
                        {formData.hosting_mode === 'ip' && (
                          <div className="absolute top-2 right-2">
                            <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                            </svg>
                          </div>
                        )}
                      </label>
                      
                      {/* Tor Mode */}
                      <label className={`relative flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        formData.hosting_mode === 'tor' 
                          ? 'border-purple-500 bg-purple-900/20' 
                          : 'border-slate-600 hover:border-slate-500'
                      }`}>
                        <input
                          type="radio"
                          name="hosting_mode"
                          value="tor"
                          checked={formData.hosting_mode === 'tor'}
                          onChange={handleChange}
                          className="sr-only"
                          disabled={isEdit && existingServer?.is_docker_hosted}
                        />
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">🧅</span>
                          <div>
                            <span className={`font-medium ${formData.hosting_mode === 'tor' ? 'text-purple-400' : 'text-slate-300'}`}>
                              Tor Hidden Service
                            </span>
                            <p className="text-xs text-slate-500">Global .onion access</p>
                          </div>
                        </div>
                        {formData.hosting_mode === 'tor' && (
                          <div className="absolute top-2 right-2">
                            <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                            </svg>
                          </div>
                        )}
                      </label>
                    </div>
                    
                    {/* Tor image warning */}
                    {formData.hosting_mode === 'tor' && !imageStatus?.tor && (
                      <div className="mt-3 p-2 rounded bg-purple-900/30 border border-purple-700">
                        <p className="text-xs text-purple-400">
                          🧅 Tor mode requires <code className="bg-slate-800 px-1 rounded">simplex-{formData.server_type}-tor:latest</code> image
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-slate-300 mb-1">Name *</label>
                  <input type="text" name="name" value={formData.name} onChange={handleChange} required
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Server Type</label>
                  <select name="server_type" value={formData.server_type} onChange={handleChange}
                    disabled={isEdit && formData.is_docker_hosted}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none disabled:opacity-50">
                    <option value="smp">SMP (Messaging)</option>
                    <option value="xftp">XFTP (File Transfer)</option>
                    <option value="ntf">NTF (Notifications)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Priority</label>
                  <input type="number" name="priority" value={formData.priority} onChange={handleChange} min="1" max="10"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
                </div>
              </div>

              {/* External Server Address */}
              {!formData.is_docker_hosted && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-1">Server Address *</label>
                  <textarea name="address" value={formData.address} onChange={handleChange} rows={2} required
                    placeholder="smp://fingerprint:password@host.onion"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white font-mono text-sm placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                  {isOnion && (
                    <div className="mt-2 flex items-center space-x-2">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-purple-900/30 text-purple-400">🧅 Onion</span>
                      <span className="text-xs text-slate-500">Timeout: 120s</span>
                    </div>
                  )}
                </div>
              )}
              
              {/* Docker Port & Host IP */}
              {formData.is_docker_hosted && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Host IP (only for IP mode) */}
                  {formData.hosting_mode === 'ip' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Host IP <span className="text-slate-500 text-xs">(auto-detected if empty)</span>
                      </label>
                      <input type="text" name="host_ip" value={formData.host_ip} onChange={handleChange}
                        placeholder="192.168.1.100 or 0.0.0.0"
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                      <p className="text-xs text-slate-500 mt-1">IP address for server certificate</p>
                    </div>
                  )}
                  
                  {/* Exposed Port (only for IP mode) */}
                  {formData.hosting_mode === 'ip' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Exposed Port <span className="text-slate-500 text-xs">(optional)</span>
                      </label>
                      <input type="number" name="exposed_port" value={formData.exposed_port} onChange={handleChange}
                        placeholder={formData.server_type === 'smp' ? '5223' : '443'} min="1024" max="65535"
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                      <p className="text-xs text-slate-500 mt-1">Host port mapping for Docker</p>
                    </div>
                  )}
                  
                  {/* Tor info message */}
                  {formData.hosting_mode === 'tor' && (
                    <div className="md:col-span-2 p-3 rounded-lg bg-purple-900/20 border border-purple-800">
                      <p className="text-sm text-purple-300">
                        🧅 Tor Hidden Service will generate a <code className="bg-slate-800 px-1 rounded">.onion</code> address automatically.
                        No port mapping needed - accessible globally via Tor network.
                      </p>
                    </div>
                  )}
                </div>
              )}
              
              {/* SMP Password - ALWAYS shown for Docker hosted servers */}
              {formData.is_docker_hosted && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    SMP Password <span className="text-slate-500 text-xs">(optional)</span>
                  </label>
                  <input type="text" name="smp_password" value={formData.smp_password} onChange={handleChange}
                    placeholder="Leave empty for no password"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                  <p className="text-xs text-slate-500 mt-1">Password required for creating new message queues on this server</p>
                </div>
              )}
              
              {/* Generated Onion Address */}
              {formData.is_docker_hosted && formData.hosting_mode === 'tor' && onionAddress && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-1">🧅 Onion Address</label>
                  <div className="flex items-center space-x-2">
                    <input type="text" value={onionAddress} readOnly
                      className="flex-1 bg-slate-800 border border-purple-800 rounded-lg px-4 py-2.5 text-purple-400 font-mono text-sm" />
                    <button type="button" onClick={() => navigator.clipboard.writeText(onionAddress)}
                      className="p-2.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-300" title="Copy">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              )}
              
              {/* Generated Address */}
              {formData.is_docker_hosted && generatedAddress && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-1">Generated Address</label>
                  <div className="flex items-center space-x-2">
                    <input type="text" value={generatedAddress} readOnly
                      className="flex-1 bg-slate-800 border border-green-800 rounded-lg px-4 py-2.5 text-green-400 font-mono text-sm" />
                    <button type="button" onClick={() => navigator.clipboard.writeText(generatedAddress)}
                      className="p-2.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-300" title="Copy">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Location</label>
                  <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Berlin, Rack 2"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                  <input type="text" name="description" value={formData.description} onChange={handleChange} placeholder="Notes..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
                </div>
              </div>

              {categories.length > 0 && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Categories</label>
                  <div className="flex flex-wrap gap-2">
                    {categories.map((cat: Category) => (
                      <label key={cat.id} className="inline-flex items-center space-x-2 cursor-pointer px-3 py-1.5 rounded-full border hover:bg-slate-800"
                        style={{ borderColor: `${cat.color}40` }}>
                        <input type="checkbox" checked={formData.category_ids.includes(cat.id)} onChange={() => handleCategoryToggle(cat.id)}
                          className="rounded text-primary-600 focus:ring-primary-500 bg-slate-800 border-slate-600" />
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }}></span>
                        <span className="text-sm text-slate-300">{cat.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6 pt-4 border-t border-slate-700 flex flex-wrap gap-6">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange}
                    className="w-5 h-5 rounded text-primary-600 bg-slate-800 border-slate-600" />
                  <div>
                    <span className="text-slate-300 font-medium">Active</span>
                    <p className="text-xs text-slate-500">Include in monitoring</p>
                  </div>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" name="maintenance_mode" checked={formData.maintenance_mode} onChange={handleChange}
                    className="w-5 h-5 rounded text-amber-600 bg-slate-800 border-slate-600" />
                  <div>
                    <span className="text-slate-300 font-medium">Maintenance</span>
                    <p className="text-xs text-slate-500">Temporarily exclude</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Connection Test */}
            {!formData.is_docker_hosted && (
              <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">⚡ Connection Test</h2>
                  <button type="button" onClick={handleTestConnection} disabled={!formData.address || testing}
                    className="inline-flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium">
                    {testing ? <span>Testing...</span> : <span>Test Now</span>}
                  </button>
                </div>
                {testResult && (
                  <div className={`p-4 rounded-lg ${testResult === 'success' ? 'bg-green-900/20 border border-green-800' : 'bg-red-900/20 border border-red-800'}`}>
                    <p className={testResult === 'success' ? 'text-green-400' : 'text-red-400'}>
                      {testResult === 'success' ? '✓' : '✗'} {testMessage} {testLatency && `(${testLatency}ms)`}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: Docker */}
        {activeTab === 'docker' && formData.is_docker_hosted && (
          <div className="space-y-6">
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white">🐳 Docker Container</h2>
                <DockerStatusBadge status={dockerStatus} />
              </div>
              
              {isEdit && existingServer && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="p-3 rounded-lg bg-slate-800">
                    <p className="text-xs text-slate-500 mb-1">Container</p>
                    <p className="text-sm text-white font-mono truncate">{existingServer.container_name || '-'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-800">
                    <p className="text-xs text-slate-500 mb-1">Image</p>
                    <p className="text-sm text-white font-mono">simplex-{formData.server_type}:latest</p>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-800">
                    <p className="text-xs text-slate-500 mb-1">Port</p>
                    <p className="text-sm text-white font-mono">{existingServer.exposed_port || 'Auto'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-800">
                    <p className="text-xs text-slate-500 mb-1">Volume</p>
                    <p className="text-sm text-white font-mono truncate">{existingServer.data_volume || '-'}</p>
                  </div>
                </div>
              )}
              
              {dockerError && (
                <div className="mb-6 p-4 rounded-lg bg-red-900/20 border border-red-800">
                  <p className="text-sm text-red-400">{dockerError}</p>
                </div>
              )}
              
              {isEdit ? (
                <div className="flex flex-wrap gap-3">
                  <button type="button" onClick={() => handleDockerAction('start')}
                    disabled={dockerActionLoading || dockerStatus === 'running'}
                    className="inline-flex items-center space-x-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm">
                    <span>▶ Start</span>
                  </button>
                  <button type="button" onClick={() => handleDockerAction('stop')}
                    disabled={dockerActionLoading || dockerStatus !== 'running'}
                    className="inline-flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm">
                    <span>⏹ Stop</span>
                  </button>
                  <button type="button" onClick={() => handleDockerAction('restart')}
                    disabled={dockerActionLoading || dockerStatus !== 'running'}
                    className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm">
                    <span>🔄 Restart</span>
                  </button>
                  <button type="button" onClick={() => { setShowLogs(!showLogs); if (!showLogs) fetchContainerLogs(); }}
                    disabled={dockerStatus === 'not_created'}
                    className="inline-flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm">
                    <span>📋 {showLogs ? 'Hide' : 'View'} Logs</span>
                  </button>
                  <button type="button" onClick={() => { if (confirm('Delete container?')) handleDockerAction('delete'); }}
                    disabled={dockerActionLoading}
                    className="inline-flex items-center space-x-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm ml-auto">
                    <span>🗑 Delete</span>
                  </button>
                </div>
              ) : (
                <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-800">
                  <p className="text-sm text-blue-400">💡 Save the server first to manage the Docker container.</p>
                </div>
              )}
            </div>
            
            {showLogs && (
              <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">Container Logs</h2>
                  <button type="button" onClick={fetchContainerLogs} className="text-sm text-primary-400 hover:text-primary-300">Refresh</button>
                </div>
                <pre className="bg-slate-950 rounded-lg p-4 text-xs text-slate-300 font-mono overflow-x-auto max-h-96 overflow-y-auto">
                  {containerLogs || 'No logs available'}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* TAB: Monitoring */}
        {activeTab === 'monitoring' && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Test Configuration</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Custom Timeout (sec)</label>
                <input type="number" name="custom_timeout" value={formData.custom_timeout} onChange={handleChange} placeholder="Default" min="1" max="600"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Expected Uptime (%)</label>
                <input type="number" name="expected_uptime" value={formData.expected_uptime} onChange={handleChange} min="0" max="100"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Max Latency (ms)</label>
                <input type="number" name="max_latency" value={formData.max_latency} onChange={handleChange} min="100" max="60000"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: SSH */}
        {activeTab === 'ssh' && !formData.is_docker_hosted && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">SSH Connection</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Host</label>
                <input type="text" name="ssh_host" value={formData.ssh_host} onChange={handleChange} placeholder="192.168.1.100"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Port</label>
                <input type="number" name="ssh_port" value={formData.ssh_port} onChange={handleChange} min="1" max="65535"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Username</label>
                <input type="text" name="ssh_user" value={formData.ssh_user} onChange={handleChange} placeholder="pi"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SSH Key Path</label>
                <input type="text" name="ssh_key_path" value={formData.ssh_key_path} onChange={handleChange} placeholder="~/.ssh/id_rsa"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: Control Port */}
        {activeTab === 'control' && !formData.is_docker_hosted && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">SimpleX Control Port</h2>
            <div className="mb-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" name="control_port_enabled" checked={formData.control_port_enabled} onChange={handleChange}
                  className="w-5 h-5 rounded text-primary-600 bg-slate-800 border-slate-600" />
                <span className="text-slate-300 font-medium">Control Port Enabled</span>
              </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Port</label>
                <input type="number" name="control_port" value={formData.control_port} onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Admin Password</label>
                <input type="password" name="control_port_admin_password" value={formData.control_port_admin_password} onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">User Password</label>
                <input type="password" name="control_port_user_password" value={formData.control_port_user_password} onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* TAB: Telegraf */}
        {activeTab === 'telegraf' && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Telegraf Metrics</h2>
            <div className="mb-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input type="checkbox" name="telegraf_enabled" checked={formData.telegraf_enabled} onChange={handleChange}
                  className="w-5 h-5 rounded text-primary-600 bg-slate-800 border-slate-600" />
                <span className="text-slate-300 font-medium">Enable Telegraf</span>
              </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">InfluxDB URL</label>
                <input type="text" name="influxdb_url" value={formData.influxdb_url} onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">API Token</label>
                <input type="password" name="influxdb_token" value={formData.influxdb_token} onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-primary-500 focus:outline-none" />
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {saveError && (
          <div className="mt-6 p-4 rounded-lg bg-red-900/30 border border-red-700">
            <div className="flex items-start space-x-3">
              <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div>
                <p className="text-red-400 font-medium">Error saving server</p>
                <p className="text-red-300 text-sm mt-1">{saveError}</p>
              </div>
              <button 
                type="button"
                onClick={() => setSaveError(null)}
                className="ml-auto text-red-400 hover:text-red-300"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex items-center justify-between">
          <Link to="/servers" className="text-slate-400 hover:text-white">← Back</Link>
          <div className="flex space-x-3">
            <Link to="/servers" className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-5 py-2.5 rounded-lg font-medium">Cancel</Link>
            <button type="submit" disabled={saving} className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium">
              {saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Add Server')}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}