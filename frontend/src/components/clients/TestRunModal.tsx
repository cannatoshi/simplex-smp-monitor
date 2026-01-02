/**
 * TestRunModal - Modal for creating and monitoring test runs
 */

import { useState, useEffect } from 'react';
import { SimplexClient } from '../../api/client';

const neonBlue = '#88CED0';
const cyan = '#22D3EE';

interface TestRunConfig {
  name: string;
  message_count: number;
  interval_ms: number;
  message_size: number;
  recipient_mode: 'all' | 'random' | 'round_robin' | 'selected';
  selected_recipients: string[];
}

interface TestRun {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'cancelled' | 'failed';
  message_count: number;
  messages_sent: number;
  messages_delivered: number;
  messages_failed: number;
  avg_latency_ms: number | null;
  min_latency_ms: number | null;
  max_latency_ms: number | null;
  success_rate: number | null;
  progress_percent: number;
  started_at: string | null;
  completed_at: string | null;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  client: SimplexClient;
  connections: { client_a: string; client_b: string; contact_name_on_a: string; contact_name_on_b: string }[];
  allClients: SimplexClient[];
}

export default function TestRunModal({ isOpen, onClose, client, connections, allClients }: Props) {
  
  // Config state
  const [config, setConfig] = useState<TestRunConfig>({
    name: `Test ${new Date().toLocaleTimeString()}`,
    message_count: 10,
    interval_ms: 1000,
    message_size: 50,
    recipient_mode: 'round_robin',
    selected_recipients: [],
  });
  
  // Test run state
  const [activeTest, setActiveTest] = useState<TestRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Available recipients (connected clients)
  const availableRecipients = allClients.filter(c => {
    if (c.id === client.id) return false;
    return connections.some(conn => 
      (conn.client_a === client.id && conn.client_b === c.id) ||
      (conn.client_b === client.id && conn.client_a === c.id)
    );
  });

  // Get CSRF token
  const getCsrfToken = (): string => {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === 'csrftoken') return value;
    }
    return '';
  };

  // Start test
  const handleStartTest = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Create test run
      const createRes = await fetch('/api/v1/test-runs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          name: config.name,
          sender: client.id,
          message_count: config.message_count,
          interval_ms: config.interval_ms,
          message_size: config.message_size,
          recipient_mode: config.recipient_mode,
          selected_recipients: config.selected_recipients,
        }),
      });
      
      if (!createRes.ok) {
        throw new Error('Failed to create test run');
      }
      
      const testRun = await createRes.json();
      
      // Start test
      const startRes = await fetch(`/api/v1/test-runs/${testRun.id}/start/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
      });
      
      if (!startRes.ok) {
        throw new Error('Failed to start test');
      }
      
      const result = await startRes.json();
      setActiveTest(result.test_run);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Cancel test
  const handleCancelTest = async () => {
    if (!activeTest) return;
    
    try {
      await fetch(`/api/v1/test-runs/${activeTest.id}/cancel/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
      });
      
      setActiveTest(prev => prev ? { ...prev, status: 'cancelled' } : null);
    } catch (err) {
      console.error('Cancel error:', err);
    }
  };

  // Poll for updates when test is running
  useEffect(() => {
    if (!activeTest || activeTest.status !== 'running') return;
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/v1/test-runs/${activeTest.id}/`);
        if (res.ok) {
          const data = await res.json();
          setActiveTest(data);
          
          if (data.status !== 'running') {
            clearInterval(interval);
          }
        }
      } catch (err) {
        console.error('Poll error:', err);
      }
    }, 500);
    
    return () => clearInterval(interval);
  }, [activeTest?.id, activeTest?.status]);

  // Reset when modal closes
  useEffect(() => {
    if (!isOpen) {
      setActiveTest(null);
      setError(null);
      setConfig(prev => ({
        ...prev,
        name: `Test ${new Date().toLocaleTimeString()}`,
      }));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold" style={{ color: neonBlue }}>
              🧪 Test Run
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            {client.name} ({client.profile_name})
          </p>
        </div>
        
        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {!activeTest ? (
            // Configuration form
            <div className="space-y-6">
              {/* Test Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Test Name
                </label>
                <input
                  type="text"
                  value={config.name}
                  onChange={e => setConfig(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-[#88CED0]"
                />
              </div>
              
              {/* Message Count & Interval */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Messages
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={1000}
                    value={config.message_count}
                    onChange={e => setConfig(prev => ({ ...prev, message_count: parseInt(e.target.value) || 1 }))}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-[#88CED0]"
                  />
                  <p className="text-xs text-slate-500 mt-1">1 - 1000</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Interval (ms)
                  </label>
                  <input
                    type="number"
                    min={100}
                    max={60000}
                    step={100}
                    value={config.interval_ms}
                    onChange={e => setConfig(prev => ({ ...prev, interval_ms: parseInt(e.target.value) || 1000 }))}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-[#88CED0]"
                  />
                  <p className="text-xs text-slate-500 mt-1">100ms - 60s</p>
                </div>
              </div>
              
              {/* Message Size */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Message Size: {config.message_size} chars
                </label>
                <input
                  type="range"
                  min={10}
                  max={5000}
                  step={10}
                  value={config.message_size}
                  onChange={e => setConfig(prev => ({ ...prev, message_size: parseInt(e.target.value) }))}
                  className="w-full accent-[#88CED0]"
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>10</span>
                  <span>5000</span>
                </div>
              </div>
              
              {/* Recipient Mode */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Recipient Mode
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'round_robin', label: 'Round-Robin', desc: 'Fair rotation' },
                    { value: 'random', label: 'Random', desc: 'Random selection' },
                    { value: 'all', label: 'All', desc: 'Broadcast to all' },
                    { value: 'selected', label: 'Selected', desc: 'Choose recipients' },
                  ].map(mode => (
                    <button
                      key={mode.value}
                      onClick={() => setConfig(prev => ({ ...prev, recipient_mode: mode.value as any }))}
                      className={`p-3 rounded-lg border text-left transition-all ${
                        config.recipient_mode === mode.value
                          ? 'border-[#88CED0] bg-[#88CED0]/10'
                          : 'border-slate-600 hover:border-slate-500'
                      }`}
                    >
                      <div className="font-medium text-white">{mode.label}</div>
                      <div className="text-xs text-slate-400">{mode.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Selected Recipients (when mode = selected) */}
              {config.recipient_mode === 'selected' && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Select Recipients
                  </label>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {availableRecipients.map(r => (
                      <label key={r.id} className="flex items-center gap-2 p-2 hover:bg-slate-800 rounded cursor-pointer">
                        <input
                          type="checkbox"
                          checked={config.selected_recipients.includes(r.id)}
                          onChange={e => {
                            if (e.target.checked) {
                              setConfig(prev => ({
                                ...prev,
                                selected_recipients: [...prev.selected_recipients, r.id],
                              }));
                            } else {
                              setConfig(prev => ({
                                ...prev,
                                selected_recipients: prev.selected_recipients.filter(id => id !== r.id),
                              }));
                            }
                          }}
                          className="accent-[#88CED0]"
                        />
                        <span className="text-white">{r.name}</span>
                        <span className="text-slate-400 text-sm">({r.profile_name})</span>
                      </label>
                    ))}
                    {availableRecipients.length === 0 && (
                      <p className="text-slate-500 text-sm">No connected clients</p>
                    )}
                  </div>
                </div>
              )}
              
              {/* Estimated Duration */}
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-sm text-slate-400">Estimated Duration</div>
                <div className="text-2xl font-bold" style={{ color: neonBlue }}>
                  {((config.message_count * config.interval_ms) / 1000).toFixed(1)}s
                </div>
              </div>
              
              {/* Error */}
              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
                  {error}
                </div>
              )}
            </div>
          ) : (
            // Active test display
            <div className="space-y-6">
              {/* Status */}
              <div className="text-center">
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
                  activeTest.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                  activeTest.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                  activeTest.status === 'cancelled' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {activeTest.status === 'running' && (
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  )}
                  {activeTest.status.toUpperCase()}
                </div>
              </div>
              
              {/* Progress */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Progress</span>
                  <span style={{ color: neonBlue }}>
                    {activeTest.messages_sent} / {activeTest.message_count}
                  </span>
                </div>
                <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-300"
                    style={{
                      width: `${activeTest.progress_percent}%`,
                      backgroundColor: neonBlue,
                    }}
                  />
                </div>
              </div>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-slate-800 rounded-lg text-center">
                  <div className="text-2xl font-bold text-emerald-400">
                    {activeTest.messages_delivered}
                  </div>
                  <div className="text-xs text-slate-400">Delivered</div>
                </div>
                <div className="p-4 bg-slate-800 rounded-lg text-center">
                  <div className="text-2xl font-bold text-red-400">
                    {activeTest.messages_failed}
                  </div>
                  <div className="text-xs text-slate-400">Failed</div>
                </div>
                <div className="p-4 bg-slate-800 rounded-lg text-center">
                  <div className="text-2xl font-bold" style={{ color: neonBlue }}>
                    {activeTest.success_rate?.toFixed(1) || '-'}%
                  </div>
                  <div className="text-xs text-slate-400">Success Rate</div>
                </div>
              </div>
              
              {/* Latency Stats (when completed) */}
              {activeTest.status === 'completed' && activeTest.avg_latency_ms && (
                <div className="p-4 bg-slate-800 rounded-lg">
                  <div className="text-sm text-slate-400 mb-3">Latency Results</div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-xl font-bold" style={{ color: cyan }}>
                        {activeTest.min_latency_ms}ms
                      </div>
                      <div className="text-xs text-slate-400">Min</div>
                    </div>
                    <div>
                      <div className="text-xl font-bold" style={{ color: neonBlue }}>
                        {Math.round(activeTest.avg_latency_ms)}ms
                      </div>
                      <div className="text-xs text-slate-400">Avg</div>
                    </div>
                    <div>
                      <div className="text-xl font-bold text-red-400">
                        {activeTest.max_latency_ms}ms
                      </div>
                      <div className="text-xs text-slate-400">Max</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t border-slate-700 flex justify-end gap-3">
          {!activeTest ? (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleStartTest}
                disabled={loading || availableRecipients.length === 0}
                className="px-6 py-2 rounded-lg font-medium disabled:opacity-50 transition-all"
                style={{
                  backgroundColor: neonBlue,
                  color: '#0f172a',
                }}
              >
                {loading ? 'Starting...' : 'Start Test'}
              </button>
            </>
          ) : activeTest.status === 'running' ? (
            <button
              onClick={handleCancelTest}
              className="px-6 py-2 bg-red-500/20 text-red-400 rounded-lg font-medium hover:bg-red-500/30 transition-colors"
            >
              Cancel Test
            </button>
          ) : (
            <button
              onClick={() => setActiveTest(null)}
              className="px-6 py-2 rounded-lg font-medium transition-all"
              style={{
                backgroundColor: neonBlue,
                color: '#0f172a',
              }}
            >
              New Test
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
