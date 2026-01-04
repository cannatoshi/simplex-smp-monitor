/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * TestRunModal Component
 * 
 * Full-featured stress test modal with:
 * - Configuration form (messages, interval, size, mode)
 * - Live progress visualization with animated bars
 * - Real-time latency graph (Recharts)
 * - Message timeline with status indicators
 * - Detailed statistics (delivered, failed, latencies)
 * - Tor/Direct connection indicator
 * - Test history access
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import { SimplexClient } from '../../api/client';

// Brand colors - NO GREEN
const neonBlue = '#88CED0';
const cyan = '#22D3EE';
const purple = '#A855F7';
const red = '#EF4444';
const amber = '#F59E0B';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';

const neonButtonStyle = {
  backgroundColor: 'rgb(30, 41, 59)',
  color: neonBlue,
  border: `1px solid ${neonBlue}`,
  boxShadow: neonGlow
};

interface TestRunConfig {
  name: string;
  message_count: number;
  interval_ms: number;
  message_size: number;
  recipient_mode: 'all' | 'random' | 'round_robin' | 'selected';
  selected_recipients: string[];
}

interface LatencyPoint {
  index: number;
  timestamp: string;
  total: number | null;
  toServer: number | null;
  toClient: number | null;
  status: 'sending' | 'sent' | 'delivered' | 'failed';
  recipient: string;
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

interface TestMessage {
  id: string;
  tracking_id: string;
  recipient_name: string;
  delivery_status: string;
  sent_at: string;
  total_latency_ms: number | null;
  latency_to_server_ms: number | null;
  latency_to_client_ms: number | null;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  client: SimplexClient;
  connections: { client_a: string; client_b: string; contact_name_on_a: string; contact_name_on_b: string }[];
  allClients: SimplexClient[];
}

const getCsrfToken = (): string => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === 'csrftoken') return value;
  }
  return '';
};

export default function TestRunModal({ isOpen, onClose, client, connections, allClients }: Props) {
  const navigate = useNavigate();
  
  // === State ===
  const [config, setConfig] = useState<TestRunConfig>({
    name: `Test ${new Date().toLocaleTimeString()}`,
    message_count: 10,
    interval_ms: 1000,
    message_size: 100,
    recipient_mode: 'round_robin',
    selected_recipients: [],
  });
  
  const [activeTest, setActiveTest] = useState<TestRun | null>(null);
  const [latencyData, setLatencyData] = useState<LatencyPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  
  // === Derived State ===
  const connectedClients = connections.map(conn => {
    const otherId = conn.client_a === client.id ? conn.client_b : conn.client_a;
    const otherClient = allClients.find(c => c.id === otherId);
    const contactName = conn.client_a === client.id ? conn.contact_name_on_a : conn.contact_name_on_b;
    return { id: otherId, name: otherClient?.name || 'Unknown', contactName };
  });
  
  const usesTor = client.use_tor;
  const isRunning = activeTest?.status === 'running' || activeTest?.status === 'pending';
  const isCompleted = activeTest?.status === 'completed' || activeTest?.status === 'cancelled' || activeTest?.status === 'failed';
  
  // === Handlers ===
  const handleStartTest = async () => {
    if (connectedClients.length === 0) {
      setError('No connected clients to send to');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch('/api/v1/test-runs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          sender: client.id,
          name: config.name,
          message_count: config.message_count,
          interval_ms: config.interval_ms,
          message_size: config.message_size,
          recipient_mode: config.recipient_mode,
          selected_recipients: config.selected_recipients,
        }),
      });
      
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to start test');
      }
      
      const data = await res.json();
      const test = data.test_run || data;
      setActiveTest(test);
      setLatencyData([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancelTest = async () => {
    if (!activeTest) return;
    
    try {
      await fetch(`/api/v1/test-runs/${activeTest.id}/cancel/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
      });
      
      setActiveTest(prev => prev ? { ...prev, status: 'cancelled' } : null);
    } catch (err) {
      console.error('Cancel error:', err);
    }
  };
  
  const handleRunInBackground = () => {
    onClose();
    navigate('/test-runs');
  };
  
  const handleViewResults = () => {
    onClose();
    navigate('/test-runs');
  };
  
  const handleNewTest = () => {
    setActiveTest(null);
    setLatencyData([]);
    setError(null);
    setConfig(prev => ({ ...prev, name: `Test ${new Date().toLocaleTimeString()}` }));
  };
  
  const fetchTestMessages = useCallback(async (testId: string) => {
    try {
      const res = await fetch(`/api/v1/test-runs/${testId}/messages/`);
      if (res.ok) {
        const messages: TestMessage[] = await res.json();
        
        const points: LatencyPoint[] = messages.map((msg, idx) => ({
          index: idx + 1,
          timestamp: new Date(msg.sent_at).toLocaleTimeString(),
          total: msg.total_latency_ms,
          toServer: msg.latency_to_server_ms,
          toClient: msg.latency_to_client_ms,
          status: msg.delivery_status as any,
          recipient: msg.recipient_name,
        }));
        
        setLatencyData(points);
      }
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  }, []);
  
  // === Polling Effect ===
  useEffect(() => {
    if (!activeTest) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }
    
    if (isCompleted) {
      const finalFetch = async () => {
        try {
          const res = await fetch(`/api/v1/test-runs/${activeTest.id}/`);
          if (res.ok) {
            const data = await res.json();
            setActiveTest(data);
            await fetchTestMessages(activeTest.id);
          }
        } catch (err) {
          console.error('Final fetch error:', err);
        }
      };
      finalFetch();
      
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }
    
    const poll = async () => {
      try {
        const res = await fetch(`/api/v1/test-runs/${activeTest.id}/`);
        if (res.ok) {
          const data = await res.json();
          setActiveTest(data);
          await fetchTestMessages(activeTest.id);
        }
      } catch (err) {
        console.error('Poll error:', err);
      }
    };
    
    poll();
    pollIntervalRef.current = setInterval(poll, 400);
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [activeTest?.id, isCompleted, fetchTestMessages]);
  
  // === Reset on Close ===
  useEffect(() => {
    if (!isOpen) {
      if (!isRunning) {
        setActiveTest(null);
        setLatencyData([]);
      }
      setError(null);
      setConfig(prev => ({
        ...prev,
        name: `Test ${new Date().toLocaleTimeString()}`,
      }));
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  }, [isOpen, isRunning]);
  
  if (!isOpen) return null;
  
  // === Render Helpers ===
  const renderStatusBadge = (status: string) => {
    const configs: Record<string, { bg: string; color: string; pulse?: boolean }> = {
      pending: { bg: 'rgba(100, 116, 139, 0.2)', color: '#94a3b8' },
      running: { bg: `rgba(34, 211, 238, 0.2)`, color: cyan, pulse: true },
      completed: { bg: `rgba(34, 211, 238, 0.2)`, color: cyan },
      cancelled: { bg: 'rgba(245, 158, 11, 0.2)', color: amber },
      failed: { bg: 'rgba(239, 68, 68, 0.2)', color: red },
    };
    
    const cfg = configs[status] || configs.pending;
    
    return (
      <div 
        className="inline-flex items-center gap-2 px-4 py-2 rounded-full"
        style={{ backgroundColor: cfg.bg, color: cfg.color }}
      >
        {cfg.pulse && (
          <div 
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: cfg.color, boxShadow: `0 0 8px ${cfg.color}` }}
          />
        )}
        {status.toUpperCase()}
      </div>
    );
  };
  
  const renderLatencyGraph = () => {
    if (latencyData.length === 0) {
      return (
        <div className="h-48 flex items-center justify-center text-slate-500">
          <div className="text-center">
            <div className="text-4xl mb-2 animate-pulse">📊</div>
            <div>Latency data will appear here...</div>
          </div>
        </div>
      );
    }
    
    const avgLatency = activeTest?.avg_latency_ms || 0;
    const maxVal = Math.max(...latencyData.map(d => d.total || 0));
    
    return (
      <div className="h-56 relative" ref={chartRef}>
        {/* Animated grid background */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(${cyan}33 1px, transparent 1px),
              linear-gradient(90deg, ${cyan}33 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px',
          }}
        />
        
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={latencyData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="latencyGradientCyan" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={cyan} stopOpacity={0.4} />
                <stop offset="100%" stopColor={cyan} stopOpacity={0} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#334155" 
              vertical={false}
            />
            
            <XAxis 
              dataKey="index" 
              stroke="#475569" 
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            
            <YAxis 
              stroke="#475569" 
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              tickFormatter={(v) => `${v}ms`}
              domain={[0, maxVal * 1.1]}
            />
            
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                border: `1px solid ${cyan}`,
                borderRadius: '8px',
                boxShadow: `0 0 20px ${cyan}33`,
              }}
              labelStyle={{ color: cyan, fontWeight: 'bold' }}
              itemStyle={{ color: '#e2e8f0' }}
              labelFormatter={(label) => `Message #${label}`}
            />
            
            {/* Average reference line with glow */}
            {avgLatency > 0 && (
              <ReferenceLine 
                y={avgLatency} 
                stroke={amber}
                strokeWidth={1}
                strokeDasharray="8 4"
                label={{ 
                  value: `Avg: ${Math.round(avgLatency)}ms`, 
                  fill: amber, 
                  fontSize: 11,
                  fontWeight: 'bold',
                }}
              />
            )}
            
            {/* Area fill */}
            <Area
              type="monotone"
              dataKey="total"
              stroke="none"
              fill="url(#latencyGradientCyan)"
              animationDuration={300}
            />
            
            {/* Main latency line with glow effect */}
            <Line
              type="monotone"
              dataKey="total"
              stroke={cyan}
              strokeWidth={2}
              filter="url(#glow)"
              dot={(props) => {
                const { cx, cy, payload } = props;
                if (!cx || !cy) return null;
                
                let fill = cyan;
                let glowColor = cyan;
                if (payload.status === 'failed') {
                  fill = red;
                  glowColor = red;
                } else if (payload.status === 'delivered') {
                  fill = cyan;
                  glowColor = cyan;
                } else if (payload.status === 'sent') {
                  fill = amber;
                  glowColor = amber;
                } else if (payload.status === 'sending') {
                  fill = neonBlue;
                  glowColor = neonBlue;
                }
                
                return (
                  <g>
                    <circle cx={cx} cy={cy} r={8} fill={glowColor} opacity={0.2} />
                    <circle cx={cx} cy={cy} r={4} fill={fill} stroke="#0f172a" strokeWidth={2} />
                  </g>
                );
              }}
              activeDot={{
                r: 8,
                fill: cyan,
                stroke: '#0f172a',
                strokeWidth: 2,
                style: { filter: `drop-shadow(0 0 6px ${cyan})` }
              }}
              animationDuration={300}
            />
          </ComposedChart>
        </ResponsiveContainer>
        
        {/* Live indicator */}
        {isRunning && (
          <div className="absolute top-2 right-2 flex items-center gap-2">
            <div 
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: cyan, boxShadow: `0 0 10px ${cyan}` }}
            />
            <span className="text-xs" style={{ color: cyan }}>LIVE</span>
          </div>
        )}
      </div>
    );
  };
  
  const renderProgressBar = () => {
    if (!activeTest) return null;
    
    const { messages_sent, messages_delivered, messages_failed, message_count } = activeTest;
    
    const deliveredPct = (messages_delivered / message_count) * 100;
    const failedPct = (messages_failed / message_count) * 100;
    const pendingPct = ((messages_sent - messages_delivered - messages_failed) / message_count) * 100;
    
    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Progress</span>
          <span style={{ color: neonBlue }}>
            {messages_sent} / {message_count}
          </span>
        </div>
        
        {/* Stacked progress bar */}
        <div className="h-4 bg-slate-700 rounded-full overflow-hidden flex">
          {/* Delivered */}
          <div
            className="h-full transition-all duration-300"
            style={{ width: `${deliveredPct}%`, backgroundColor: cyan }}
          />
          {/* Pending (animated) */}
          <div
            className="h-full transition-all duration-300 relative overflow-hidden"
            style={{ width: `${pendingPct}%`, backgroundColor: neonBlue }}
          >
            {isRunning && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
            )}
          </div>
          {/* Failed */}
          <div
            className="h-full transition-all duration-300"
            style={{ width: `${failedPct}%`, backgroundColor: red }}
          />
        </div>
        
        {/* Legend */}
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: cyan }} />
            <span className="text-slate-400">Delivered ({messages_delivered})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: neonBlue }} />
            <span className="text-slate-400">Pending ({messages_sent - messages_delivered - messages_failed})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: red }} />
            <span className="text-slate-400">Failed ({messages_failed})</span>
          </div>
        </div>
      </div>
    );
  };
  
  const renderMessageTimeline = () => {
    if (latencyData.length === 0) return null;
    
    const recentMessages = latencyData.slice(-5).reverse();
    
    return (
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-slate-400">Recent Messages</h4>
        <div className="space-y-1">
          {recentMessages.map((msg, i) => (
            <div 
              key={i}
              className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-lg text-xs"
              style={{
                animation: i === 0 && isRunning ? 'slideIn 0.3s ease-out' : undefined,
                borderLeft: `3px solid ${
                  msg.status === 'delivered' ? cyan :
                  msg.status === 'failed' ? red :
                  msg.status === 'sent' ? amber : neonBlue
                }`
              }}
            >
              <span className="text-slate-500">#{msg.index}</span>
              <span className="flex-1 text-slate-300 truncate">{msg.recipient}</span>
              <span 
                className="px-1.5 py-0.5 rounded text-xs"
                style={{
                  backgroundColor: msg.status === 'delivered' ? `${cyan}20` :
                                  msg.status === 'failed' ? `${red}20` : `${amber}20`,
                  color: msg.status === 'delivered' ? cyan :
                        msg.status === 'failed' ? red : amber
                }}
              >
                {msg.status}
              </span>
              {msg.total && (
                <span className="text-slate-500">{msg.total}ms</span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  const renderStatsGrid = () => {
    if (!activeTest) return null;
    
    const { avg_latency_ms, min_latency_ms, max_latency_ms, success_rate } = activeTest;
    
    return (
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold" style={{ color: cyan }}>
            {success_rate?.toFixed(1) || '0.0'}%
          </div>
          <div className="text-xs text-slate-500">Success Rate</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-white">
            {avg_latency_ms ? Math.round(avg_latency_ms) : '-'}
            <span className="text-sm text-slate-500">ms</span>
          </div>
          <div className="text-xs text-slate-500">Avg Latency</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold" style={{ color: neonBlue }}>
            {min_latency_ms || '-'}
            <span className="text-sm text-slate-500">ms</span>
          </div>
          <div className="text-xs text-slate-500">Min</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-400">
            {max_latency_ms || '-'}
            <span className="text-sm text-slate-500">ms</span>
          </div>
          <div className="text-xs text-slate-500">Max</div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Backdrop - NO onClick to prevent accidental close */}
      <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl pointer-events-auto">
          {/* Header */}
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold" style={{ color: neonBlue }}>
                  🧪 Test Run
                </h2>
                
                {/* Tor/Direct Badge */}
                <div 
                  className="px-2 py-0.5 rounded text-xs font-medium"
                  style={{
                    backgroundColor: usesTor ? `${purple}20` : `${cyan}20`,
                    color: usesTor ? purple : cyan
                  }}
                >
                  {usesTor ? '🧅 Tor' : '⚡ Direct'}
                </div>
                
                {activeTest && renderStatusBadge(activeTest.status)}
              </div>
              
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-white font-medium">{client.name}</div>
                  <div className="text-slate-500 text-sm">{client.profile_name}</div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {!activeTest ? (
              // === Configuration Form ===
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
                
                {/* Message Count & Interval & Size */}
                <div className="grid grid-cols-3 gap-4">
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
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Interval (ms)
                    </label>
                    <input
                      type="number"
                      min={50}
                      max={60000}
                      step={50}
                      value={config.interval_ms}
                      onChange={e => setConfig(prev => ({ ...prev, interval_ms: parseInt(e.target.value) || 1000 }))}
                      className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-[#88CED0]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Size (chars)
                    </label>
                    <input
                      type="number"
                      min={10}
                      max={5000}
                      value={config.message_size}
                      onChange={e => setConfig(prev => ({ ...prev, message_size: parseInt(e.target.value) || 100 }))}
                      className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-[#88CED0]"
                    />
                  </div>
                </div>
                
                {/* Recipient Mode */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Recipient Mode
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { value: 'round_robin', label: 'Round-Robin', icon: '🔄' },
                      { value: 'random', label: 'Random', icon: '🎲' },
                      { value: 'all', label: 'Broadcast', icon: '📡' },
                      { value: 'selected', label: 'Selected', icon: '✅' },
                    ].map(mode => (
                      <button
                        key={mode.value}
                        onClick={() => setConfig(prev => ({ ...prev, recipient_mode: mode.value as any }))}
                        className="p-3 rounded-lg border text-left transition-all"
                        style={{
                          borderColor: config.recipient_mode === mode.value ? neonBlue : '#475569',
                          backgroundColor: config.recipient_mode === mode.value ? `${neonBlue}15` : 'transparent',
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <span>{mode.icon}</span>
                          <span className={config.recipient_mode === mode.value ? 'text-white' : 'text-slate-400'}>
                            {mode.label}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Connected Clients */}
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-2">
                    Recipients ({connectedClients.length})
                  </div>
                  {connectedClients.length === 0 ? (
                    <p className="text-slate-500 text-sm">No connections available</p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {connectedClients.map(c => (
                        <span 
                          key={c.id} 
                          className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300"
                        >
                          {c.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
                    {error}
                  </div>
                )}
              </div>
            ) : (
              // === Active Test View ===
              <div className="space-y-6">
                {/* Progress Bar */}
                {renderProgressBar()}
                
                {/* Stats Grid */}
                {renderStatsGrid()}
                
                {/* Latency Graph */}
                <div>
                  <h4 className="text-sm font-medium text-slate-400 mb-2">Latency Timeline</h4>
                  {renderLatencyGraph()}
                </div>
                
                {/* Message Timeline */}
                {renderMessageTimeline()}
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="p-6 border-t border-slate-700">
            <div className="flex items-center justify-between">
              <div className="text-sm text-slate-500">
                {activeTest ? (
                  <>Test ID: {activeTest.id.slice(0, 8)}...</>
                ) : (
                  <>{connectedClients.length} recipient(s) available</>
                )}
              </div>
              
              <div className="flex items-center gap-3">
                {!activeTest ? (
                  // === Config Buttons ===
                  <>
                    <button
                      onClick={onClose}
                      className="px-4 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleStartTest}
                      disabled={loading || connectedClients.length === 0}
                      className="px-6 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 disabled:opacity-50 hover:opacity-90 transition-opacity"
                      style={neonButtonStyle}
                    >
                      {loading ? (
                        <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: neonBlue }} />
                      ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        </svg>
                      )}
                      Start Test
                    </button>
                  </>
                ) : isRunning ? (
                  // === Running Buttons ===
                  <>
                    <button
                      onClick={handleRunInBackground}
                      className="px-4 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
                      style={neonButtonStyle}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Background
                    </button>
                    <button
                      onClick={handleCancelTest}
                      className="px-4 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
                      style={{ ...neonButtonStyle, borderColor: red, color: red }}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Cancel
                    </button>
                  </>
                ) : (
                  // === Completed Buttons ===
                  <>
                    <button
                      onClick={handleNewTest}
                      className="px-4 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
                      style={neonButtonStyle}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      New Test
                    </button>
                    <button
                      onClick={handleViewResults}
                      className="px-6 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
                      style={neonButtonStyle}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      View Results
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Animations */}
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </>
  );
}