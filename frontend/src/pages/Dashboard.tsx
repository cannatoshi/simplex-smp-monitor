import { useTranslation } from 'react-i18next';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { useDashboardStats, useActivityData, useLatencyData, useRecentServers, useRecentTests, useRecentEvents } from '../hooks/useApi';

export default function Dashboard() {
  const { t } = useTranslation();
  
  // API Hooks
  const { data: stats, loading: statsLoading } = useDashboardStats();
  const { data: activityData, loading: activityLoading } = useActivityData(24);
  const { data: latencyData, loading: latencyLoading } = useLatencyData(24);
  const { data: servers, loading: serversLoading } = useRecentServers(5);
  const { data: tests, loading: testsLoading } = useRecentTests(3);
  const { data: events, loading: eventsLoading } = useRecentEvents(5);

  // Loading State
  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Format activity data for chart
  const chartData = activityData?.map(item => ({
    time: new Date(item.hour).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
    online: item.online,
    offline: item.offline,
    latency: item.avg_latency || 0,
  })) || [];

  // Format latency data for chart
  const latencyChartData = latencyData?.map(item => ({
    name: item.server_name.length > 15 ? item.server_name.substring(0, 15) + '...' : item.server_name,
    latency: item.last_latency || 0,
    avg: item.avg_latency || 0,
  })) || [];

  const avgLatency = stats?.avg_latency || 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{t('nav.dashboard')}</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">SimpleX Infrastructure Overview</p>
        </div>
        <div className="text-sm text-slate-600 dark:text-slate-400">
          {t('time.lastUpdate')}: {new Date().toLocaleTimeString('de-DE')}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Servers */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50 hover:border-primary-500/50 transition-all duration-300 hover:glow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{t('dashboard.totalServers')}</p>
              <p className="text-3xl font-bold text-white mt-1">{stats?.total_servers || 0}</p>
            </div>
            <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
              </svg>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-primary-400 text-sm">{stats?.online_servers || 0} online</span>
            <span className="text-slate-500 dark:text-slate-500">•</span>
            <span className="text-slate-600 dark:text-slate-400 text-sm">{stats?.onion_servers || 0} onion</span>
          </div>
        </div>

        {/* Active Servers */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50 hover:border-primary-500/50 transition-all duration-300 hover:glow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{t('dashboard.activeServers')}</p>
              <p className="text-3xl font-bold text-white mt-1">{stats?.active_servers || 0}</p>
            </div>
            <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-3">
            <span className={`text-sm ${stats?.overall_uptime && stats.overall_uptime >= 99 ? 'text-primary-400' : 'text-amber-400'}`}>
              {stats?.overall_uptime?.toFixed(1) || '—'}% uptime
            </span>
          </div>
        </div>

        {/* Running Tests */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50 hover:border-primary-500/50 transition-all duration-300 hover:glow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{t('dashboard.runningTests')}</p>
              <p className="text-3xl font-bold text-white mt-1">{stats?.running_tests || 0}</p>
            </div>
            <div className="w-12 h-12 bg-violet-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div className="mt-3">
            <span className="text-slate-600 dark:text-slate-400 text-sm">{stats?.active_tests || 0} {t('common.active')}</span>
            <span className="text-slate-500 dark:text-slate-500 mx-2">•</span>
            <span className="text-slate-600 dark:text-slate-400 text-sm">{stats?.total_tests || 0} total</span>
          </div>
        </div>

        {/* Avg Latency */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50 hover:border-primary-500/50 transition-all duration-300 hover:glow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{t('dashboard.avgLatency')}</p>
              <p className="text-3xl font-bold text-white mt-1">
                {stats?.avg_latency ? `${Math.round(stats.avg_latency)}ms` : '—'}
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-500/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-3">
            <span className="text-slate-600 dark:text-slate-400 text-sm">{stats?.running_clients || 0} clients running</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.serverActivity')}</h3>
          {activityLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="online" stackId="1" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.3} name="Online" />
                <Area type="monotone" dataKey="offline" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} name="Offline" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Latency Chart */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.latencyOverview')}</h3>
          {latencyLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={latencyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={12} unit="ms" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#f8fafc' }}
                />
                <ReferenceLine y={avgLatency} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: 'Avg', fill: '#f59e0b', fontSize: 12 }} />
                <Bar dataKey="latency" fill="#0ea5e9" radius={[4, 4, 0, 0]} name="Latency (ms)" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Server List */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">{t('dashboard.recentServers')}</h3>
            <a href="/servers" className="text-primary-400 hover:text-primary-300 text-sm">{t('common.viewAll')} →</a>
          </div>
          {serversLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-12 bg-slate-700/50 rounded-lg animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {servers?.map((server) => (
                <div key={server.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${server.last_status === 'online' ? 'bg-primary-400 animate-pulse' : 'bg-red-400'}`}></div>
                    <div>
                      <p className="text-white text-sm font-medium">{server.name}</p>
                      <p className="text-slate-600 dark:text-slate-400 text-xs">{server.server_type.toUpperCase()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-white text-sm">{server.last_latency ? `${server.last_latency}ms` : '—'}</p>
                    <p className="text-slate-600 dark:text-slate-400 text-xs">{server.uptime_percent?.toFixed(0) || '—'}%</p>
                  </div>
                </div>
              ))}
              {(!servers || servers.length === 0) && (
                <p className="text-slate-600 dark:text-slate-400 text-sm text-center py-4">{t('common.noData')}</p>
              )}
            </div>
          )}
        </div>

        {/* Recent Tests */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">{t('dashboard.recentTests')}</h3>
            <a href="/tests" className="text-primary-400 hover:text-primary-300 text-sm">{t('common.viewAll')} →</a>
          </div>
          {testsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-slate-700/50 rounded-lg animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {tests?.map((test) => (
                <div key={test.id} className="p-3 bg-slate-700/30 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <p className="text-white text-sm font-medium">{test.name}</p>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      test.status === 'running' ? 'bg-primary-500/20 text-primary-400' :
                      test.status === 'active' ? 'bg-primary-500/20 text-primary-400' :
                      test.status === 'completed' ? 'bg-slate-500/20 text-slate-600 dark:text-slate-400' :
                      'bg-amber-500/20 text-amber-400'
                    }`}>
                      {test.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-slate-600 dark:text-slate-400">
                    <span>{test.server_count} servers</span>
                    <span>{test.success_rate?.toFixed(0) || '—'}% success</span>
                  </div>
                </div>
              ))}
              {(!tests || tests.length === 0) && (
                <p className="text-slate-600 dark:text-slate-400 text-sm text-center py-4">{t('common.noData')}</p>
              )}
            </div>
          )}
        </div>

        {/* Recent Events */}
        <div className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">{t('dashboard.recentEvents')}</h3>
            <a href="/events" className="text-primary-400 hover:text-primary-300 text-sm">{t('common.viewAll')} →</a>
          </div>
          {eventsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-12 bg-slate-700/50 rounded-lg animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {events?.map((event) => (
                <div key={event.id} className="flex items-start gap-3 p-2 hover:bg-slate-200 dark:hover:bg-slate-700/30 rounded-lg transition-colors">
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                    event.level === 'ERROR' || event.level === 'CRITICAL' ? 'bg-red-400' :
                    event.level === 'WARNING' ? 'bg-amber-400' :
                    'bg-primary-400'
                  }`}></div>
                  <div className="min-w-0 flex-1">
                    <p className="text-white text-sm truncate">{event.message}</p>
                    <p className="text-slate-600 dark:text-slate-400 text-xs">{event.source} • {new Date(event.created_at).toLocaleTimeString('de-DE')}</p>
                  </div>
                </div>
              ))}
              {(!events || events.length === 0) && (
                <p className="text-slate-600 dark:text-slate-400 text-sm text-center py-4">{t('common.noData')}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
