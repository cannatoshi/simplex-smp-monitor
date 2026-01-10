/**
 * SimpleX SMP Monitor - MiniPlayer Component
 * ==========================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * Compact audio player with Cache Panel.
 * Shows if playing from CACHE or YOUTUBE.
 * Click on source badge to toggle between LOCAL and STREAM.
 * Auto-switches to LOCAL when track becomes cached.
 */
import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { useAudioPlayerStore } from '../../stores/useAudioPlayerStore';
import { useVideoWidget } from '../../contexts/VideoWidgetContext';
import { getStreamUrl, fetchCacheSettings, updateCacheSettings, CacheSettings } from '../../api/music';

// Design System Colors
const neonBlue = '#88CED0';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';
const cyan = '#22D3EE';

const neonButtonStyle = {
  backgroundColor: 'rgb(30, 41, 59)',
  color: neonBlue,
  border: `1px solid ${neonBlue}`,
  boxShadow: neonGlow
};

const iconButtonStyle = { color: neonBlue };

// Helper to get backend URL (Django port in dev)
const getBackendOrigin = () => {
  if (window.location.port === '3001') {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return window.location.origin;
};

export default function MiniPlayer() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [streamUrl, setStreamUrl] = useState<string | null>(null);
  const [streamSource, setStreamSource] = useState<'cache' | 'youtube' | null>(null);
  const [preferLocal, setPreferLocal] = useState<boolean>(true); // Prefer local if available
  const [isMinimized, setIsMinimized] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showCachePanel, setShowCachePanel] = useState(false);
  const [cacheSettings, setCacheSettings] = useState<CacheSettings | null>(null);
  const [audioError, setAudioError] = useState<string | null>(null);
  const [lastCachedState, setLastCachedState] = useState<boolean | null>(null);
  const { openVideo } = useVideoWidget();

  const {
    isPlaying, isLoading, currentTrack, currentTime, duration, volume, isMuted,
    repeatMode, shuffleEnabled, cacheStatus, togglePlay, setCurrentTime, setDuration,
    setIsLoading, nextTrack, prevTrack, toggleShuffle, cycleRepeatMode, setVolume,
    toggleMute, pause, setCurrentTrack, setIsPlaying,
  } = useAudioPlayerStore();

  // Load cache settings when panel opens
  useEffect(() => {
    if (showCachePanel && !cacheSettings) {
      loadCacheSettings();
    }
  }, [showCachePanel]);

  const loadCacheSettings = async () => {
    try {
      const settings = await fetchCacheSettings();
      setCacheSettings(settings);
    } catch (err) {
      console.error('Failed to load cache settings:', err);
    }
  };

  const handleUpdateSettings = async (updates: Partial<CacheSettings>) => {
    if (!cacheSettings) return;
    try {
      const updated = await updateCacheSettings(updates);
      setCacheSettings(updated);
    } catch (err) {
      console.error('Failed to update settings:', err);
    }
  };

  const toggleSize = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setIsMinimized(!isMinimized);
      setIsAnimating(false);
    }, 150);
  };

  // Toggle between local and stream source
  const toggleSource = () => {
    if (!currentTrack) return;
    
    // Only allow toggle if track is cached
    if (!currentTrack.is_cached) {
      console.log('Track not cached, cannot switch to local');
      return;
    }
    
    const wasPlaying = isPlaying;
    const currentPos = audioRef.current?.currentTime || 0;
    
    // Pause current playback
    if (audioRef.current) {
      audioRef.current.pause();
    }
    
    // Toggle preference
    setPreferLocal(!preferLocal);
    setStreamUrl(null);
    setStreamSource(null);
    setAudioError(null);
    
    // Force reload with new source
    loadStreamUrl(currentTrack.id, !preferLocal, currentPos, wasPlaying);
  };

  // Load stream URL with source preference
  const loadStreamUrl = async (
    trackId: string, 
    useLocal: boolean, 
    seekTo: number = 0, 
    autoPlay: boolean = false
  ) => {
    setIsLoading(true);
    setAudioError(null);
    
    try {
      const data = await getStreamUrl(trackId);
      console.log('Stream response:', data);
      
      let finalUrl = data.url;
      let source = data.source;
      
      // If we prefer local and track is cached, use cache
      // If we prefer stream or track is not cached, use youtube (via proxy)
      if (useLocal && data.cached) {
        // Use local cache file
        finalUrl = getBackendOrigin() + data.url;
        source = 'cache';
      } else {
        // Use YouTube via proxy to bypass CORS
        finalUrl = `${getBackendOrigin()}/api/v1/music/tracks/${trackId}/proxy/`;
        source = 'youtube';
      }
      
      console.log('Final stream URL:', finalUrl, 'source:', source);
      setStreamUrl(finalUrl);
      setStreamSource(source);
      setIsLoading(false);
      
      // Seek and play if needed
      if (seekTo > 0 || autoPlay) {
        setTimeout(() => {
          const audio = audioRef.current;
          if (audio) {
            if (seekTo > 0) {
              audio.currentTime = seekTo;
            }
            if (autoPlay) {
              audio.play().catch(console.error);
            }
          }
        }, 100);
      }
    } catch (err) {
      console.error('Failed to get stream URL:', err);
      setAudioError('Failed to load audio');
      setIsLoading(false);
    }
  };

  // Load stream URL when track changes
  useEffect(() => {
    if (!currentTrack) { 
      setStreamUrl(null);
      setStreamSource(null);
      setAudioError(null);
      setLastCachedState(null);
      return; 
    }
    
    // Auto-select source: prefer local if cached
    const useLocal = preferLocal && currentTrack.is_cached;
    loadStreamUrl(currentTrack.id, useLocal);
    setLastCachedState(currentTrack.is_cached);
  }, [currentTrack?.id]);

  // AUTO-SWITCH: When track becomes cached while playing, switch to LOCAL
  useEffect(() => {
    if (!currentTrack) return;
    
    // Check if is_cached changed from false to true
    if (lastCachedState === false && currentTrack.is_cached === true) {
      console.log('Track just got cached! Auto-switching to LOCAL...');
      
      const wasPlaying = isPlaying;
      const currentPos = audioRef.current?.currentTime || 0;
      
      // Pause current playback
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      // Clear current stream
      setStreamUrl(null);
      setStreamSource(null);
      setAudioError(null);
      
      // Reload with local source, preserving position and play state
      setTimeout(() => {
        loadStreamUrl(currentTrack.id, true, currentPos, wasPlaying);
      }, 100);
    }
    
    // Update last cached state
    setLastCachedState(currentTrack.is_cached);
  }, [currentTrack?.is_cached]);

  // Audio element event handlers
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onLoadedMetadata = () => { 
      console.log('Audio loaded, duration:', audio.duration);
      setDuration(audio.duration); 
      setIsLoading(false);
      setAudioError(null);
    };
    
    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onEnded = () => nextTrack();
    
    const onCanPlay = () => { 
      console.log('Audio can play');
      setIsLoading(false);
      setAudioError(null);
      if (isPlaying) {
        audio.play().catch((e) => {
          console.error('Play failed:', e);
          setIsPlaying(false);
        });
      }
    };
    
    const onWaiting = () => setIsLoading(true);
    const onPlaying = () => {
      console.log('Audio playing');
      setIsLoading(false);
      setAudioError(null);
    };
    
    const onError = (e: Event) => {
      const target = e.target as HTMLAudioElement;
      const error = target.error;
      let errorMsg = 'Audio error';
      
      if (error) {
        switch (error.code) {
          case MediaError.MEDIA_ERR_ABORTED:
            errorMsg = 'Playback aborted';
            break;
          case MediaError.MEDIA_ERR_NETWORK:
            errorMsg = 'Network error';
            break;
          case MediaError.MEDIA_ERR_DECODE:
            errorMsg = 'Decode error';
            break;
          case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
            errorMsg = 'Format not supported';
            break;
        }
      }
      
      console.error('Audio error:', errorMsg, error);
      setAudioError(errorMsg);
      setIsLoading(false);
    };
    
    const onSeeked = () => {
      console.log('Seeked to:', audio.currentTime);
    };

    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('canplay', onCanPlay);
    audio.addEventListener('waiting', onWaiting);
    audio.addEventListener('playing', onPlaying);
    audio.addEventListener('error', onError);
    audio.addEventListener('seeked', onSeeked);

    return () => {
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('canplay', onCanPlay);
      audio.removeEventListener('waiting', onWaiting);
      audio.removeEventListener('playing', onPlaying);
      audio.removeEventListener('error', onError);
      audio.removeEventListener('seeked', onSeeked);
    };
  }, [isPlaying, nextTrack]);

  // Play/Pause control
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !streamUrl) return;
    
    if (isPlaying) {
      audio.play().catch((e) => {
        console.error('Play error:', e);
        setIsPlaying(false);
      });
    } else {
      audio.pause();
    }
  }, [isPlaying, streamUrl]);

  // Volume control
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.volume = isMuted ? 0 : volume;
  }, [volume, isMuted]);

  const formatTime = (seconds: number): string => {
    if (!seconds || !isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatBytes = (mb: number): string => {
    if (mb >= 1000) return `${(mb / 1000).toFixed(1)} GB`;
    return `${Math.round(mb)} MB`;
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    console.log('Seeking to:', newTime);
    audio.currentTime = newTime;
  };

  // STOP - Clear track completely
  const handleStop = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.src = '';
    }
    setStreamUrl(null);
    setStreamSource(null);
    setAudioError(null);
    setCurrentTrack(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  };

  // Open video - only works in stream mode
  const handleOpenVideo = () => {
    if (!currentTrack?.source_id) return;
    if (streamSource === 'cache') {
      // Switch to stream mode first, then open video
      toggleSource();
    }
    pause();
    openVideo(currentTrack.source_id, currentTrack.title);
  };

  if (!currentTrack) return null;

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  
  // Safe cache stats access
  const cacheStats = cacheStatus?.stats;
  const cacheSize = cacheStats?.cache_size;
  const cacheUsedMB = cacheSize?.total_mb ?? 0;
  const cacheMaxMB = cacheSize?.max_mb ?? 2000;
  const cachePercent = cacheSize?.usage_percent ?? 0;
  const cacheFileCount = cacheSize?.file_count ?? 0;
  const successRate = cacheStats?.success_rate ?? 100;
  const activeDownloads = cacheStatus?.active_downloads ?? [];
  const recentFailures = cacheStatus?.recent_failures ?? [];

  const chartData = [
    { name: 'Used', value: cacheUsedMB },
    { name: 'Free', value: Math.max(0, cacheMaxMB - cacheUsedMB) },
  ];

  // Source badge component - clickable to toggle
  const SourceBadge = ({ small = false }: { small?: boolean }) => {
    if (audioError) {
      return (
        <span 
          className={`${small ? 'text-[8px]' : 'text-[10px]'} font-medium px-1.5 rounded cursor-default`}
          style={{ color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.15)' }}
          title={audioError}
        >
          ERROR
        </span>
      );
    }
    
    if (!streamSource) return null;
    
    const isLocal = streamSource === 'cache';
    const canToggle = currentTrack?.is_cached;
    
    return (
      <span 
        className={`${small ? 'text-[8px]' : 'text-[10px]'} font-medium px-1.5 rounded transition-all ${canToggle ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}
        style={{ 
          color: isLocal ? '#22c55e' : '#f59e0b',
          backgroundColor: isLocal ? 'rgba(34, 197, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)'
        }}
        onClick={canToggle ? toggleSource : undefined}
        title={canToggle ? `Click to switch to ${isLocal ? 'STREAM' : 'LOCAL'}` : (isLocal ? 'Playing from cache' : 'Streaming from YouTube')}
      >
        {isLocal ? 'LOCAL' : 'STREAM'}
      </span>
    );
  };

  // ==================== MINIMIZED VIEW ====================
  if (isMinimized) {
    return (
      <>
        <div className={`flex items-center gap-3 h-full transition-all duration-150 ease-out ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
          <audio ref={audioRef} src={streamUrl || undefined} preload="auto" />
          
          {/* Thumbnail */}
          <button onClick={toggleSize} className="w-9 h-9 rounded-full overflow-hidden flex-shrink-0 transition-all hover:scale-110" style={{ border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
            {currentTrack.thumbnail_url ? <img src={currentTrack.thumbnail_url} alt="" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center bg-slate-800" style={{ color: cyan }}><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg></div>}
          </button>

          {/* Play/Pause */}
          <button onClick={togglePlay} disabled={isLoading || !!audioError} className="w-8 h-8 flex items-center justify-center rounded-full transition-all disabled:opacity-50" style={neonButtonStyle}>
            {isLoading ? <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> : isPlaying ? <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z" /></svg> : <svg className="w-3.5 h-3.5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>}
          </button>

          {/* Track Info + Source Badge */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium" style={{ color: neonBlue }}>{currentTrack.title}</span>
            <span className="text-[10px] text-slate-500">— {currentTrack.artist || 'Unknown'}</span>
            <SourceBadge small />
          </div>

          <div className="w-px h-6 bg-slate-700 mx-1" />

          {/* Cache Info */}
          {cacheStatus?.is_caching && (
            <div className="flex items-center gap-2 px-2 py-1 rounded-lg" style={{ backgroundColor: 'rgba(136, 206, 208, 0.1)', border: `1px solid ${neonBlue}` }}>
              <svg className="w-4 h-4 animate-pulse" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span className="text-xs font-medium" style={{ color: neonBlue }}>{cacheStatus?.active_downloads_count || 0}</span>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs" style={{ color: neonBlue }}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <span>{formatBytes(cacheUsedMB)}</span>
          </div>
        </div>
        
        {/* Cache Modal Portal */}
        {showCachePanel && createPortal(
          <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" onClick={() => setShowCachePanel(false)}>
            <div className="absolute inset-0 bg-black/70" />
            <div className="relative w-full max-w-2xl rounded-2xl overflow-hidden" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: `${neonGlow}, 0 25px 50px rgba(0,0,0,0.5)` }} onClick={(e) => e.stopPropagation()}>
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg className="w-6 h-6" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" /></svg>
                  <span className="text-lg font-bold" style={{ color: neonBlue }}>Cache Manager</span>
                </div>
                <button onClick={() => setShowCachePanel(false)} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-800" style={{ color: neonBlue }}>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
              <div className="p-6 grid grid-cols-2 gap-6 max-h-[70vh] overflow-y-auto">
                <div className="space-y-6">
                  <div className="flex items-center gap-6">
                    <div className="w-28 h-28 relative">
                      <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={chartData} cx="50%" cy="50%" innerRadius={35} outerRadius={50} paddingAngle={2} dataKey="value" strokeWidth={0}><Cell fill={neonBlue} /><Cell fill="#334155" /></Pie></PieChart></ResponsiveContainer>
                      <div className="absolute inset-0 flex items-center justify-center flex-col"><span className="text-xl font-bold" style={{ color: neonBlue }}>{Math.round(cachePercent)}%</span><span className="text-[10px] text-slate-500">used</span></div>
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="flex justify-between text-sm"><span className="text-slate-400">Used</span><span style={{ color: neonBlue }}>{formatBytes(cacheUsedMB)}</span></div>
                      <div className="flex justify-between text-sm"><span className="text-slate-400">Free</span><span className="text-slate-500">{formatBytes(cacheMaxMB - cacheUsedMB)}</span></div>
                      <div className="flex justify-between text-sm"><span className="text-slate-400">Files</span><span style={{ color: neonBlue }}>{cacheFileCount}</span></div>
                      <div className="flex justify-between text-sm"><span className="text-slate-400">Success</span><span style={{ color: neonBlue }}>{successRate.toFixed(1)}%</span></div>
                    </div>
                  </div>
                  {activeDownloads.length > 0 && <div className="space-y-2"><span className="text-sm font-medium text-slate-400">Active Downloads</span>{activeDownloads.map((dl) => <div key={dl.id} className="p-3 rounded-lg bg-slate-800/50 flex items-center gap-3"><svg className="w-5 h-5 animate-spin" style={{ color: cyan }} fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg><div className="flex-1 min-w-0"><p className="text-xs truncate" style={{ color: neonBlue }}>{dl.video_id}</p><p className="text-[10px] text-slate-500">{dl.status}</p></div></div>)}</div>}
                  {recentFailures.length > 0 && <div className="space-y-2"><span className="text-sm font-medium text-red-400">Recent Failures</span>{recentFailures.slice(0,3).map((f) => <div key={f.id} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20"><p className="text-xs text-red-400 truncate">{f.video_id}</p><p className="text-[10px] text-red-300/60 truncate">{f.error_message}</p></div>)}</div>}
                </div>
                <div className="space-y-4">
                  <span className="text-sm font-medium text-slate-400">Settings</span>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Max Size</span><select value={cacheSettings?.max_cache_size_mb || 2000} onChange={(e) => handleUpdateSettings({ max_cache_size_mb: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="500">500 MB</option><option value="1000">1 GB</option><option value="2000">2 GB</option><option value="5000">5 GB</option><option value="10000">10 GB</option></select></div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Auto Cleanup</span><button onClick={() => handleUpdateSettings({ auto_cleanup_enabled: !cacheSettings?.auto_cleanup_enabled })} className={`w-12 h-6 rounded-full relative ${cacheSettings?.auto_cleanup_enabled ? '' : 'bg-slate-700'}`} style={cacheSettings?.auto_cleanup_enabled ? { backgroundColor: neonBlue } : undefined}><div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${cacheSettings?.auto_cleanup_enabled ? 'left-7' : 'left-1'}`} /></button></div>
                  {cacheSettings?.auto_cleanup_enabled && <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Cleanup After</span><select value={cacheSettings?.cleanup_after_days || 30} onChange={(e) => handleUpdateSettings({ cleanup_after_days: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option><option value="60">60 days</option></select></div>}
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Bitrate</span><select value={cacheSettings?.preferred_bitrate || 192} onChange={(e) => handleUpdateSettings({ preferred_bitrate: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="128">128 kbps</option><option value="192">192 kbps</option><option value="256">256 kbps</option><option value="320">320 kbps</option></select></div>
                  <div className="p-3 rounded-lg bg-slate-800/30"><span className="text-xs text-slate-500">Format: MP3 (fixed for browser compatibility)</span></div>
                  <div className="pt-4 border-t border-slate-800"><a href="/cache-forensics" className="w-full py-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2" style={neonButtonStyle} onClick={() => setShowCachePanel(false)}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>Open Cache Forensics</a></div>
                </div>
              </div>
            </div>
          </div>,
          document.body
        )}
      </>
    );
  }

  // ==================== EXPANDED VIEW ====================
  return (
    <>
      <div className={`flex items-center gap-3 h-full transition-all duration-150 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
        <audio ref={audioRef} src={streamUrl || undefined} preload="auto" />

        {/* Thumbnail */}
        <button onClick={toggleSize} className="w-9 h-9 rounded-full overflow-hidden flex-shrink-0 transition-all hover:scale-110" style={{ border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
          {currentTrack.thumbnail_url ? <img src={currentTrack.thumbnail_url} alt="" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center bg-slate-800" style={{ color: cyan }}><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg></div>}
        </button>

        {/* Video Button - only show in STREAM mode */}
        {currentTrack.source_id && streamSource === 'youtube' && (
          <button onClick={handleOpenVideo} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-slate-800" style={{ color: neonBlue }} title="Watch Video">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </button>
        )}

        {/* Track Info + Source */}
        <div className="flex flex-col min-w-0 max-w-[120px]">
          <span className="text-xs font-medium truncate" style={{ color: neonBlue }}>{currentTrack.title}</span>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-slate-500 truncate">{currentTrack.artist || 'Unknown'}</span>
            <SourceBadge />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-1">
          <button onClick={toggleShuffle} className="w-7 h-7 flex items-center justify-center rounded-full" style={{ color: shuffleEnabled ? neonBlue : '#64748b', backgroundColor: shuffleEnabled ? 'rgba(136, 206, 208, 0.1)' : 'transparent' }}>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          </button>
          <button onClick={prevTrack} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-slate-800" style={iconButtonStyle}>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" /></svg>
          </button>
          <button onClick={togglePlay} disabled={isLoading || !!audioError} className="w-9 h-9 flex items-center justify-center rounded-full disabled:opacity-50" style={neonButtonStyle}>
            {isLoading ? <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> : isPlaying ? <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z" /></svg> : <svg className="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>}
          </button>
          <button onClick={nextTrack} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-slate-800" style={iconButtonStyle}>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" /></svg>
          </button>
          <button onClick={cycleRepeatMode} className="w-7 h-7 flex items-center justify-center rounded-full relative" style={{ color: repeatMode !== 'none' ? neonBlue : '#64748b' }}>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            {repeatMode === 'one' && <span className="absolute text-[8px] font-bold" style={{ color: neonBlue }}>1</span>}
          </button>
          {/* STOP */}
          <button onClick={handleStop} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-red-500/20 ml-1" style={{ color: '#ef4444' }} title="Stop & Close">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h12v12H6z" /></svg>
          </button>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 flex-1 max-w-[140px]">
          <span className="text-[10px] text-slate-500 w-7 text-right">{formatTime(currentTime)}</span>
          <div className="flex-1 h-1 bg-slate-700 rounded-full cursor-pointer group" onClick={handleProgressClick}>
            <div className="h-full rounded-full relative" style={{ width: `${progress}%`, backgroundColor: cyan }}>
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full opacity-0 group-hover:opacity-100" style={{ backgroundColor: cyan }} />
            </div>
          </div>
          <span className="text-[10px] text-slate-500 w-7">{formatTime(duration)}</span>
        </div>

        {/* Volume */}
        <div className="flex items-center gap-1">
          <button onClick={toggleMute} className="w-6 h-6 flex items-center justify-center rounded-full hover:bg-slate-800" style={iconButtonStyle}>
            {isMuted ? <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" /></svg> : <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>}
          </button>
          <input type="range" min="0" max="1" step="0.01" value={isMuted ? 0 : volume} onChange={(e) => setVolume(parseFloat(e.target.value))} className="w-12 h-1" style={{ accentColor: cyan }} />
        </div>

        <div className="w-px h-8 bg-slate-700 mx-1" />

        {/* Cache Toggle */}
        <div className="flex items-center gap-2">
          {cacheStatus?.is_caching && (
            <div className="flex items-center gap-2 px-2 py-1 rounded-lg relative overflow-hidden" style={{ backgroundColor: 'rgba(136, 206, 208, 0.15)', border: `1px solid ${neonBlue}` }}>
              <div className="absolute inset-0 opacity-30" style={{ background: `linear-gradient(90deg, transparent, ${neonBlue}, transparent)`, animation: 'shimmer 2s infinite' }} />
              <svg className="w-4 h-4 relative" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span className="text-xs font-bold relative" style={{ color: neonBlue }}>{cacheStatus?.active_downloads_count || 0}</span>
            </div>
          )}

          <button onClick={() => setShowCachePanel(!showCachePanel)} className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-slate-800/50 transition-colors">
            <div className="w-8 h-8 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={chartData} cx="50%" cy="50%" innerRadius={10} outerRadius={15} dataKey="value" strokeWidth={0}>
                    <Cell fill={neonBlue} />
                    <Cell fill="#334155" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[7px] font-bold" style={{ color: neonBlue }}>{Math.round(cachePercent)}%</span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-medium" style={{ color: neonBlue }}>{formatBytes(cacheUsedMB)}</span>
              <span className="text-[9px] text-slate-500">{cacheFileCount} files</span>
            </div>
            <svg className={`w-3 h-3 transition-transform ${showCachePanel ? 'rotate-180' : ''}`} style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Cache Modal Portal */}
      {showCachePanel && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" onClick={() => setShowCachePanel(false)}>
          <div className="absolute inset-0 bg-black/70" />
          <div className="relative w-full max-w-2xl rounded-2xl overflow-hidden" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: `${neonGlow}, 0 25px 50px rgba(0,0,0,0.5)` }} onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" /></svg>
                <span className="text-lg font-bold" style={{ color: neonBlue }}>Cache Manager</span>
              </div>
              <button onClick={() => setShowCachePanel(false)} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-800" style={{ color: neonBlue }}>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-6 max-h-[70vh] overflow-y-auto">
              <div className="space-y-6">
                <div className="flex items-center gap-6">
                  <div className="w-28 h-28 relative">
                    <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={chartData} cx="50%" cy="50%" innerRadius={35} outerRadius={50} paddingAngle={2} dataKey="value" strokeWidth={0}><Cell fill={neonBlue} /><Cell fill="#334155" /></Pie></PieChart></ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center flex-col"><span className="text-xl font-bold" style={{ color: neonBlue }}>{Math.round(cachePercent)}%</span><span className="text-[10px] text-slate-500">used</span></div>
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Used</span><span style={{ color: neonBlue }}>{formatBytes(cacheUsedMB)}</span></div>
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Free</span><span className="text-slate-500">{formatBytes(cacheMaxMB - cacheUsedMB)}</span></div>
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Files</span><span style={{ color: neonBlue }}>{cacheFileCount}</span></div>
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Success</span><span style={{ color: neonBlue }}>{successRate.toFixed(1)}%</span></div>
                  </div>
                </div>
                {activeDownloads.length > 0 && <div className="space-y-2"><span className="text-sm font-medium text-slate-400">Active Downloads</span>{activeDownloads.map((dl) => <div key={dl.id} className="p-3 rounded-lg bg-slate-800/50 flex items-center gap-3"><svg className="w-5 h-5 animate-spin" style={{ color: cyan }} fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg><div className="flex-1 min-w-0"><p className="text-xs truncate" style={{ color: neonBlue }}>{dl.video_id}</p><p className="text-[10px] text-slate-500">{dl.status}</p></div></div>)}</div>}
                {recentFailures.length > 0 && <div className="space-y-2"><span className="text-sm font-medium text-red-400">Recent Failures</span>{recentFailures.slice(0,3).map((f) => <div key={f.id} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20"><p className="text-xs text-red-400 truncate">{f.video_id}</p><p className="text-[10px] text-red-300/60 truncate">{f.error_message}</p></div>)}</div>}
              </div>
              <div className="space-y-4">
                <span className="text-sm font-medium text-slate-400">Settings</span>
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Max Size</span><select value={cacheSettings?.max_cache_size_mb || 2000} onChange={(e) => handleUpdateSettings({ max_cache_size_mb: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="500">500 MB</option><option value="1000">1 GB</option><option value="2000">2 GB</option><option value="5000">5 GB</option><option value="10000">10 GB</option></select></div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Auto Cleanup</span><button onClick={() => handleUpdateSettings({ auto_cleanup_enabled: !cacheSettings?.auto_cleanup_enabled })} className={`w-12 h-6 rounded-full relative ${cacheSettings?.auto_cleanup_enabled ? '' : 'bg-slate-700'}`} style={cacheSettings?.auto_cleanup_enabled ? { backgroundColor: neonBlue } : undefined}><div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${cacheSettings?.auto_cleanup_enabled ? 'left-7' : 'left-1'}`} /></button></div>
                {cacheSettings?.auto_cleanup_enabled && <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Cleanup After</span><select value={cacheSettings?.cleanup_after_days || 30} onChange={(e) => handleUpdateSettings({ cleanup_after_days: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option><option value="60">60 days</option></select></div>}
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30"><span className="text-sm text-slate-300">Bitrate</span><select value={cacheSettings?.preferred_bitrate || 192} onChange={(e) => handleUpdateSettings({ preferred_bitrate: parseInt(e.target.value) })} className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-700" style={{ color: neonBlue }}><option value="128">128 kbps</option><option value="192">192 kbps</option><option value="256">256 kbps</option><option value="320">320 kbps</option></select></div>
                <div className="p-3 rounded-lg bg-slate-800/30"><span className="text-xs text-slate-500">Format: MP3 (fixed for browser compatibility)</span></div>
                <div className="pt-4 border-t border-slate-800"><a href="/cache-forensics" className="w-full py-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2" style={neonButtonStyle} onClick={() => setShowCachePanel(false)}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>Open Cache Forensics</a></div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </>
  );
}