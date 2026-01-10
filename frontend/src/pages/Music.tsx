/**
 * SimpleX SMP Monitor - Music Page
 * =================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * Full music library and player interface.
 * Features: Library, Search, Playlists with Pin support
 */
import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useVideoWidget } from '../contexts/VideoWidgetContext';
import { useAudioPlayerStore, Track } from '../stores/useAudioPlayerStore';
import {
  fetchTracks,
  fetchPlaylists,
  fetchPlaylist,
  createPlaylist,
  updatePlaylist,
  deletePlaylist,
  addTrackToPlaylist,
  removeTrackFromPlaylist,
  searchYouTube,
  addTrackFromYouTube,
  deleteTrack,
  cacheTrack,
  fetchCacheStatus,
  SearchResult,
  Playlist,
} from '../api/music';

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

const neonInputStyle = {
  backgroundColor: 'rgb(30, 41, 59)',
  color: '#fff',
  border: `1px solid ${neonBlue}`,
  boxShadow: neonGlow
};

const PINNED_PLAYLISTS_KEY = 'simplex-music-pinned-playlists';

export default function Music() {
  const { t } = useTranslation();
  const { openVideo } = useVideoWidget();
  
  const [tracks, setTracks] = useState<Track[]>([]);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('library');
  const [addingTrack, setAddingTrack] = useState<string | null>(null);
  
  const [pinnedPlaylistIds, setPinnedPlaylistIds] = useState<string[]>(() => {
    const saved = localStorage.getItem(PINNED_PLAYLISTS_KEY);
    return saved ? JSON.parse(saved) : [];
  });
  
  const [currentPage, setCurrentPage] = useState(1);
  const [columnsCount, setColumnsCount] = useState(5);
  const rowsCount = 3;
  const itemsPerPage = columnsCount * rowsCount;
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPlaylistName, setNewPlaylistName] = useState('');
  const [newPlaylistDesc, setNewPlaylistDesc] = useState('');
  
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPlaylist, setEditingPlaylist] = useState<Playlist | null>(null);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');
  
  const [showPlaylistDetail, setShowPlaylistDetail] = useState(false);
  const [detailPlaylist, setDetailPlaylist] = useState<Playlist | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  
  const [showAddToPlaylist, setShowAddToPlaylist] = useState(false);
  const [trackToAdd, setTrackToAdd] = useState<Track | null>(null);

  const [pinnedPlaylistData, setPinnedPlaylistData] = useState<Map<string, Playlist>>(new Map());

  const { currentTrack, isPlaying, setQueue, play, pause, setCacheStatus } = useAudioPlayerStore();

  useEffect(() => {
    localStorage.setItem(PINNED_PLAYLISTS_KEY, JSON.stringify(pinnedPlaylistIds));
  }, [pinnedPlaylistIds]);

  const calculateColumns = useCallback(() => {
    const width = window.innerWidth;
    if (width >= 1536) return 6;
    if (width >= 1280) return 5;
    if (width >= 1024) return 4;
    if (width >= 768) return 3;
    return 2;
  }, []);

  useEffect(() => {
    const handleResize = () => {
      const newColumns = calculateColumns();
      if (newColumns !== columnsCount) {
        setColumnsCount(newColumns);
        setCurrentPage(1);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [calculateColumns, columnsCount]);

  const totalPages = Math.ceil(searchResults.length / itemsPerPage);
  const paginatedResults = searchResults.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  useEffect(() => {
    loadTracks();
    loadPlaylists();
    loadCacheStatus();
  }, []);

  useEffect(() => {
    if (activeTab.startsWith('playlist-')) {
      const playlistId = activeTab.replace('playlist-', '');
      loadPinnedPlaylistData(playlistId);
    }
  }, [activeTab]);

  useEffect(() => {
    const interval = setInterval(loadCacheStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadTracks = async () => {
    try {
      setIsLoading(true);
      const data = await fetchTracks();
      setTracks(data as Track[]);
    } catch (err) {
      console.error('Failed to load tracks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPlaylists = async () => {
    try {
      const data = await fetchPlaylists();
      setPlaylists(data);
    } catch (err) {
      console.error('Failed to load playlists:', err);
    }
  };

  const loadCacheStatus = async () => {
    try {
      const status = await fetchCacheStatus();
      setCacheStatus(status);
    } catch (err) {
      console.error('Failed to load cache status:', err);
    }
  };

  const loadPinnedPlaylistData = async (playlistId: string) => {
    try {
      const playlist = await fetchPlaylist(playlistId);
      setPinnedPlaylistData(prev => new Map(prev).set(playlistId, playlist));
    } catch (err) {
      console.error('Failed to load playlist:', err);
    }
  };

  const loadPlaylistDetail = async (playlistId: string) => {
    setDetailLoading(true);
    try {
      const playlist = await fetchPlaylist(playlistId);
      setDetailPlaylist(playlist);
      setShowPlaylistDetail(true);
    } catch (err) {
      console.error('Failed to load playlist:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setCurrentPage(1);
    try {
      const results = await searchYouTube(searchQuery, 50);
      setSearchResults(results);
      setActiveTab('search');
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddTrack = async (result: SearchResult) => {
    setAddingTrack(result.video_id);
    try {
      const response = await addTrackFromYouTube(result.video_id);
      if (response.track) {
        setTracks((prev) => [response.track as Track, ...prev]);
        setSearchResults((prev) => prev.filter((r) => r.video_id !== result.video_id));
      }
    } catch (err) {
      console.error('Failed to add track:', err);
    } finally {
      setAddingTrack(null);
    }
  };

  const handlePlayTrack = (track: Track, index: number, queue: Track[] = tracks) => {
    if (currentTrack?.id === track.id) {
      if (isPlaying) pause();
      else play();
    } else {
      setQueue(queue, index);
      play();
    }
  };

  const handlePlayPlaylist = (playlist: Playlist, startIndex = 0) => {
    if (!playlist.entries || playlist.entries.length === 0) return;
    const playlistTracks = playlist.entries.map(e => e.track);
    setQueue(playlistTracks, startIndex);
    play();
  };

  const handleDeleteTrack = async (trackId: string) => {
    if (!confirm('Delete this track?')) return;
    try {
      await deleteTrack(trackId);
      setTracks((prev) => prev.filter((t) => t.id !== trackId));
    } catch (err) {
      console.error('Failed to delete track:', err);
    }
  };

  const handleCacheTrack = async (trackId: string) => {
    try {
      await cacheTrack(trackId);
      loadCacheStatus();
      setTimeout(loadTracks, 2000);
    } catch (err) {
      console.error('Failed to cache track:', err);
    }
  };

  const handleCreatePlaylist = async () => {
    if (!newPlaylistName.trim()) return;
    try {
      const playlist = await createPlaylist(newPlaylistName, newPlaylistDesc, 'user');
      setPlaylists((prev) => [playlist, ...prev]);
      setShowCreateModal(false);
      setNewPlaylistName('');
      setNewPlaylistDesc('');
    } catch (err) {
      console.error('Failed to create playlist:', err);
    }
  };

  const handleUpdatePlaylist = async () => {
    if (!editingPlaylist || !editName.trim()) return;
    try {
      const updated = await updatePlaylist(editingPlaylist.id, { name: editName, description: editDesc });
      setPlaylists((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      if (pinnedPlaylistData.has(editingPlaylist.id)) {
        setPinnedPlaylistData(prev => new Map(prev).set(editingPlaylist.id, updated));
      }
      setShowEditModal(false);
      setEditingPlaylist(null);
    } catch (err) {
      console.error('Failed to update playlist:', err);
    }
  };

  const handleDeletePlaylist = async (playlistId: string) => {
    if (!confirm('Delete this playlist?')) return;
    try {
      await deletePlaylist(playlistId);
      setPlaylists((prev) => prev.filter((p) => p.id !== playlistId));
      setPinnedPlaylistIds((prev) => prev.filter((id) => id !== playlistId));
      if (detailPlaylist?.id === playlistId) {
        setShowPlaylistDetail(false);
        setDetailPlaylist(null);
      }
      if (activeTab === `playlist-${playlistId}`) {
        setActiveTab('library');
      }
    } catch (err) {
      console.error('Failed to delete playlist:', err);
    }
  };

  const handleAddToPlaylist = async (playlistId: string) => {
    if (!trackToAdd) return;
    try {
      await addTrackToPlaylist(playlistId, trackToAdd.id);
      setShowAddToPlaylist(false);
      setTrackToAdd(null);
      loadPlaylists();
      if (pinnedPlaylistIds.includes(playlistId)) {
        loadPinnedPlaylistData(playlistId);
      }
    } catch (err) {
      console.error('Failed to add to playlist:', err);
    }
  };

  const handleRemoveFromPlaylist = async (playlistId: string, entryId: string) => {
    try {
      await removeTrackFromPlaylist(playlistId, entryId);
      if (pinnedPlaylistIds.includes(playlistId)) {
        loadPinnedPlaylistData(playlistId);
      }
      if (detailPlaylist?.id === playlistId) {
        loadPlaylistDetail(playlistId);
      }
      loadPlaylists();
    } catch (err) {
      console.error('Failed to remove track:', err);
    }
  };

  const togglePinPlaylist = (playlistId: string) => {
    setPinnedPlaylistIds((prev) => {
      if (prev.includes(playlistId)) {
        if (activeTab === `playlist-${playlistId}`) setActiveTab('playlists');
        return prev.filter((id) => id !== playlistId);
      } else {
        if (prev.length >= 5) {
          alert('Maximum 5 playlists can be pinned');
          return prev;
        }
        loadPinnedPlaylistData(playlistId);
        return [...prev, playlistId];
      }
    });
  };

  const openAddToPlaylist = (track: Track) => {
    setTrackToAdd(track);
    setShowAddToPlaylist(true);
  };

  const openEditPlaylist = (playlist: Playlist) => {
    setEditingPlaylist(playlist);
    setEditName(playlist.name);
    setEditDesc(playlist.description);
    setShowEditModal(true);
  };

  const formatDuration = (seconds: number | null): string => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const pinnedPlaylists = playlists.filter((p) => pinnedPlaylistIds.includes(p.id));

  const getPageNumbers = () => {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  };

  const renderTrackRow = (track: Track, index: number, queue: Track[], playlistId?: string, entryId?: string) => (
    <div
      key={track.id + (entryId || '')}
      className={`flex items-center gap-4 p-3 rounded-lg transition-colors group ${currentTrack?.id === track.id ? 'border' : 'bg-slate-800/50 hover:bg-slate-800 border border-transparent'}`}
      style={currentTrack?.id === track.id ? { backgroundColor: 'rgba(136, 206, 208, 0.1)', borderColor: 'rgba(136, 206, 208, 0.3)' } : undefined}
    >
      <button onClick={() => handlePlayTrack(track, index, queue)} className="relative w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 group/play" style={{ border: `1px solid ${currentTrack?.id === track.id ? neonBlue : 'transparent'}` }}>
        {track.thumbnail_url ? <img src={track.thumbnail_url} alt={track.title} className="w-full h-full object-cover" /> : (
          <div className="w-full h-full flex items-center justify-center bg-slate-700" style={{ color: neonBlue }}>
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg>
          </div>
        )}
        <div className={`absolute inset-0 flex items-center justify-center bg-black/60 transition-opacity ${currentTrack?.id === track.id && isPlaying ? 'opacity-100' : 'opacity-0 group-hover/play:opacity-100'}`}>
          {currentTrack?.id === track.id && isPlaying ? <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z" /></svg> : <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>}
        </div>
      </button>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate" style={{ color: currentTrack?.id === track.id ? neonBlue : 'white' }}>{track.title}</p>
        <p className="text-sm text-slate-500 truncate">{track.artist || t('music.unknownArtist')}</p>
      </div>
      <span className="text-sm text-slate-500 w-12 text-right">{formatDuration(track.duration)}</span>
      {track.is_cached ? <span className="px-2 py-1 text-xs rounded-full" style={{ backgroundColor: 'rgba(136, 206, 208, 0.2)', color: neonBlue }}>{t('music.cached')}</span> : <button onClick={() => handleCacheTrack(track.id)} className="px-2 py-1 text-xs rounded-lg transition-colors opacity-0 group-hover:opacity-100" style={neonButtonStyle}>{t('music.cache')}</button>}
      {!playlistId && <button onClick={() => openAddToPlaylist(track)} className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors opacity-0 group-hover:opacity-100 hover:bg-slate-700" style={{ color: neonBlue }} title={t('music.addToPlaylist')}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg></button>}
      {playlistId && entryId && <button onClick={() => handleRemoveFromPlaylist(playlistId, entryId)} className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100" title="Remove"><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" /></svg></button>}
      {!playlistId && <button onClick={() => handleDeleteTrack(track.id)} className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>}
    </div>
  );

  const renderPlaylistContent = (playlistId: string) => {
    const playlist = pinnedPlaylistData.get(playlistId);
    if (!playlist) return <div className="flex items-center justify-center py-12"><svg className="w-8 h-8 animate-spin" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg></div>;
    const playlistTracks = playlist.entries?.map(e => e.track) || [];
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold" style={{ color: neonBlue }}>{playlist.name}</h2>
            {playlist.description && <p className="text-sm text-slate-500">{playlist.description}</p>}
            <p className="text-xs text-slate-600 mt-1">{playlist.track_count} tracks · {formatDuration(playlist.total_duration)}</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => handlePlayPlaylist(playlist)} disabled={!playlist.entries?.length} className="px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50 flex items-center gap-2" style={neonButtonStyle}><svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>Play All</button>
            <button onClick={() => openEditPlaylist(playlist)} className="px-3 py-2 rounded-lg text-sm transition-colors hover:bg-slate-800" style={{ color: neonBlue }}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg></button>
            <button onClick={() => togglePinPlaylist(playlist.id)} className="px-3 py-2 rounded-lg text-sm transition-colors hover:bg-slate-800 text-yellow-500" title="Unpin">📌</button>
          </div>
        </div>
        {!playlist.entries?.length ? <div className="text-center py-12 text-slate-500"><p>Playlist is empty</p><p className="text-sm mt-1">Add tracks from your library</p></div> : <div className="space-y-2">{playlist.entries.map((entry, index) => renderTrackRow(entry.track, index, playlistTracks, playlist.id, entry.id))}</div>}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-shrink-0">
          <h1 className="text-2xl font-bold" style={{ color: neonBlue }}>{t('music.title')}</h1>
          <p className="text-slate-500 text-sm mt-1">{tracks.length} {t('music.tracks')} · {playlists.length} {t('music.playlists')}</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap justify-end">
          {activeTab === 'search' && searchResults.length > 0 && (
            <>
              <span className="text-xs text-slate-500 whitespace-nowrap">{t('music.page')} {currentPage}/{totalPages}</span>
              <div className="flex items-center gap-1">
                <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="px-2 py-1.5 rounded-lg text-sm transition-all hover:opacity-90 disabled:opacity-30" style={neonButtonStyle}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg></button>
                {getPageNumbers().map((pageNum) => <button key={pageNum} onClick={() => setCurrentPage(pageNum)} className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all" style={currentPage === pageNum ? neonButtonStyle : { color: '#64748b', backgroundColor: 'transparent', border: '1px solid transparent' }}>{pageNum}</button>)}
                <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage >= totalPages} className="px-2 py-1.5 rounded-lg text-sm transition-all hover:opacity-90 disabled:opacity-30" style={neonButtonStyle}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg></button>
              </div>
            </>
          )}
          <div className="flex items-center gap-2">
            <div className="relative">
              <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} placeholder={t('music.searchPlaceholder')} className="w-48 lg:w-64 px-4 py-1.5 pl-9 rounded-lg text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" style={neonInputStyle} />
              <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
            <button onClick={handleSearch} disabled={isSearching || !searchQuery.trim()} className="px-4 py-1.5 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50" style={neonButtonStyle}>
              {isSearching ? <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: cyan, animationDelay: '0ms' }} /><span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: cyan, animationDelay: '150ms' }} /><span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: cyan, animationDelay: '300ms' }} /></span> : t('music.search')}
            </button>
          </div>
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-800 mb-4 overflow-x-auto">
        {['library', 'search', 'playlists'].map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`pb-3 px-3 text-sm font-medium transition-colors relative whitespace-nowrap ${activeTab === tab ? '' : 'text-slate-500 hover:text-white'}`} style={{ color: activeTab === tab ? neonBlue : undefined }}>
            {tab === 'library' && t('music.library')}
            {tab === 'search' && <>{t('music.searchResults')}{searchResults.length > 0 && <span className="ml-2 px-1.5 py-0.5 text-xs rounded-full" style={{ backgroundColor: neonBlue, color: '#0f172a' }}>{searchResults.length}</span>}</>}
            {tab === 'playlists' && t('music.playlists')}
            {activeTab === tab && <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" style={{ backgroundColor: neonBlue }} />}
          </button>
        ))}
        {pinnedPlaylists.map((playlist) => (
          <button key={`tab-${playlist.id}`} onClick={() => setActiveTab(`playlist-${playlist.id}`)} className={`pb-3 px-3 text-sm font-medium transition-colors relative whitespace-nowrap flex items-center gap-1.5 ${activeTab === `playlist-${playlist.id}` ? '' : 'text-slate-500 hover:text-white'}`} style={{ color: activeTab === `playlist-${playlist.id}` ? neonBlue : undefined }}>
            <span className="text-yellow-500">📌</span>{playlist.name}
            {activeTab === `playlist-${playlist.id}` && <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" style={{ backgroundColor: neonBlue }} />}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto min-h-0">
        {activeTab === 'library' && (
          <div className="space-y-2">
            {isLoading ? <div className="flex items-center justify-center py-12"><svg className="w-8 h-8 animate-spin" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg></div> : tracks.length === 0 ? <div className="text-center py-12 text-slate-500"><svg className="w-16 h-16 mx-auto mb-4 opacity-50" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg><p className="text-lg mb-2">{t('music.noTracks')}</p><p className="text-sm">{t('music.noTracksHint')}</p></div> : tracks.map((track, index) => renderTrackRow(track, index, tracks))}
          </div>
        )}

        {activeTab === 'search' && (
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columnsCount}, minmax(0, 1fr))` }}>
            {searchResults.length === 0 ? <div className="col-span-full text-center py-12 text-slate-500"><p>{t('music.noResults')}</p><p className="text-sm mt-1">{t('music.noResultsHint')}</p></div> : paginatedResults.map((result) => (
              <div key={result.video_id} className="rounded-lg overflow-hidden transition-all flex flex-col" style={{ backgroundColor: 'rgb(30, 41, 59)', border: '1px solid rgba(136, 206, 208, 0.3)' }}>
                <div className="relative aspect-video bg-slate-700 group/thumb">
                  <img src={result.thumbnail_url || `https://img.youtube.com/vi/${result.video_id}/mqdefault.jpg`} alt={result.title} className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).src = `https://img.youtube.com/vi/${result.video_id}/hqdefault.jpg`; }} />
                  <button onClick={() => openVideo(result.video_id, result.title)} className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover/thumb:opacity-100 transition-opacity"><div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(136, 206, 208, 0.9)', boxShadow: neonGlow }}><svg className="w-6 h-6 text-slate-900 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg></div></button>
                  {result.duration && <span className="absolute bottom-1 right-1 px-1 py-0.5 text-[10px] rounded" style={{ backgroundColor: 'rgba(0,0,0,0.8)', color: neonBlue }}>{formatDuration(result.duration)}</span>}
                </div>
                <div className="p-2 flex-1 flex flex-col">
                  <p className="font-medium text-xs truncate" style={{ color: neonBlue }} title={result.title}>{result.title}</p>
                  <p className="text-[10px] text-slate-500 truncate mt-0.5">{result.artist || 'Unknown'}</p>
                  <button onClick={() => handleAddTrack(result)} disabled={addingTrack === result.video_id} className="mt-2 w-full py-1.5 rounded-lg text-xs font-medium transition-all hover:opacity-90 disabled:opacity-50" style={neonButtonStyle}>{addingTrack === result.video_id ? '...' : t('music.addToLibrary')}</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'playlists' && (
          <div className="space-y-4">
            <button onClick={() => setShowCreateModal(true)} className="px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 inline-flex items-center gap-2" style={neonButtonStyle}><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>{t('music.createPlaylist')}</button>
            {playlists.length === 0 ? <div className="text-center py-12 text-slate-500"><svg className="w-16 h-16 mx-auto mb-4 opacity-50" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg><p className="text-lg mb-2">{t('music.noPlaylists')}</p><p className="text-sm">{t('music.noPlaylistsHint')}</p></div> : (
              <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columnsCount}, minmax(0, 1fr))` }}>
                {playlists.map((playlist) => {
                  const isPinned = pinnedPlaylistIds.includes(playlist.id);
                  return (
                    <div key={playlist.id} className="rounded-lg p-4 transition-colors group cursor-pointer" style={{ backgroundColor: 'rgb(30, 41, 59)', border: `1px solid rgba(136, 206, 208, ${isPinned ? '0.6' : '0.3'})` }} onClick={() => loadPlaylistDetail(playlist.id)}>
                      <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-2 mx-auto" style={{ backgroundColor: 'rgba(136, 206, 208, 0.1)' }}>{isPinned ? '📌' : '📁'}</div>
                      <h3 className="font-medium text-center truncate text-sm" style={{ color: neonBlue }}>{playlist.name}</h3>
                      <p className="text-[10px] text-slate-500 text-center mt-1">{playlist.track_count} {t('music.tracks')}</p>
                      <div className="flex justify-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={(e) => { e.stopPropagation(); togglePinPlaylist(playlist.id); }} className={`px-2 py-1 text-[10px] rounded-lg transition-colors ${isPinned ? 'text-yellow-500 hover:bg-yellow-500/10' : 'text-slate-400 hover:bg-slate-700'}`} title={isPinned ? 'Unpin' : 'Pin'}>📌</button>
                        <button onClick={(e) => { e.stopPropagation(); openEditPlaylist(playlist); }} className="px-2 py-1 text-[10px] rounded-lg text-slate-400 hover:bg-slate-700 transition-colors">✏️</button>
                        <button onClick={(e) => { e.stopPropagation(); handleDeletePlaylist(playlist.id); }} className="px-2 py-1 text-[10px] rounded-lg text-red-400 hover:bg-red-500/10 transition-colors">🗑️</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab.startsWith('playlist-') && renderPlaylistContent(activeTab.replace('playlist-', ''))}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="w-full max-w-md rounded-xl p-6" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
            <h2 className="text-xl font-bold mb-4" style={{ color: neonBlue }}>{t('music.createPlaylist')}</h2>
            <div className="space-y-4">
              <div><label className="block text-sm text-slate-400 mb-1">{t('music.playlistName')}</label><input type="text" value={newPlaylistName} onChange={(e) => setNewPlaylistName(e.target.value)} placeholder={t('music.playlistNamePlaceholder')} className="w-full px-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50" style={neonInputStyle} /></div>
              <div><label className="block text-sm text-slate-400 mb-1">{t('music.playlistDesc')}</label><input type="text" value={newPlaylistDesc} onChange={(e) => setNewPlaylistDesc(e.target.value)} placeholder={t('music.playlistDescPlaceholder')} className="w-full px-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50" style={neonInputStyle} /></div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowCreateModal(false)} className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white border border-slate-700">{t('music.cancel')}</button>
              <button onClick={handleCreatePlaylist} disabled={!newPlaylistName.trim()} className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50" style={neonButtonStyle}>{t('music.create')}</button>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editingPlaylist && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="w-full max-w-md rounded-xl p-6" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
            <h2 className="text-xl font-bold mb-4" style={{ color: neonBlue }}>Edit Playlist</h2>
            <div className="space-y-4">
              <div><label className="block text-sm text-slate-400 mb-1">{t('music.playlistName')}</label><input type="text" value={editName} onChange={(e) => setEditName(e.target.value)} className="w-full px-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50" style={neonInputStyle} /></div>
              <div><label className="block text-sm text-slate-400 mb-1">{t('music.playlistDesc')}</label><input type="text" value={editDesc} onChange={(e) => setEditDesc(e.target.value)} className="w-full px-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50" style={neonInputStyle} /></div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => { setShowEditModal(false); setEditingPlaylist(null); }} className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white border border-slate-700">{t('music.cancel')}</button>
              <button onClick={handleUpdatePlaylist} disabled={!editName.trim()} className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50" style={neonButtonStyle}>Save</button>
            </div>
          </div>
        </div>
      )}

      {showPlaylistDetail && detailPlaylist && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-3xl max-h-[80vh] rounded-xl overflow-hidden flex flex-col" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold" style={{ color: neonBlue }}>{detailPlaylist.name}</h2>
                {detailPlaylist.description && <p className="text-sm text-slate-500">{detailPlaylist.description}</p>}
                <p className="text-xs text-slate-600 mt-1">{detailPlaylist.track_count} tracks · {formatDuration(detailPlaylist.total_duration)}</p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handlePlayPlaylist(detailPlaylist)} disabled={!detailPlaylist.entries?.length} className="px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50 flex items-center gap-2" style={neonButtonStyle}><svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>Play</button>
                <button onClick={() => togglePinPlaylist(detailPlaylist.id)} className={`px-3 py-2 rounded-lg text-sm transition-colors ${pinnedPlaylistIds.includes(detailPlaylist.id) ? 'text-yellow-500' : 'text-slate-400 hover:text-yellow-500'}`} title={pinnedPlaylistIds.includes(detailPlaylist.id) ? 'Unpin' : 'Pin'}>📌</button>
                <button onClick={() => { setShowPlaylistDetail(false); setDetailPlaylist(null); }} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-800 transition-colors" style={{ color: neonBlue }}><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg></button>
              </div>
            </div>
            <div className="flex-1 overflow-auto p-4">
              {detailLoading ? <div className="flex items-center justify-center py-12"><svg className="w-8 h-8 animate-spin" style={{ color: neonBlue }} fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg></div> : !detailPlaylist.entries?.length ? <div className="text-center py-12 text-slate-500"><p>Playlist is empty</p><p className="text-sm mt-1">Add tracks from your library</p></div> : <div className="space-y-2">{detailPlaylist.entries.map((entry, index) => { const playlistTracks = detailPlaylist.entries!.map(e => e.track); return renderTrackRow(entry.track, index, playlistTracks, detailPlaylist.id, entry.id); })}</div>}
            </div>
          </div>
        </div>
      )}

      {showAddToPlaylist && trackToAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="w-full max-w-md rounded-xl p-6" style={{ backgroundColor: 'rgb(15, 23, 42)', border: `1px solid ${neonBlue}`, boxShadow: neonGlow }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: neonBlue }}>{t('music.addToPlaylist')}</h2>
            <p className="text-sm text-slate-400 mb-4 truncate">{trackToAdd.title}</p>
            {playlists.length === 0 ? <p className="text-slate-500 text-center py-4">{t('music.noPlaylistsCreate')}</p> : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {playlists.map((playlist) => (
                  <button key={playlist.id} onClick={() => handleAddToPlaylist(playlist.id)} className="w-full px-4 py-3 rounded-lg text-left transition-all hover:opacity-90 flex items-center gap-3" style={{ backgroundColor: 'rgb(30, 41, 59)', border: '1px solid rgba(136, 206, 208, 0.2)' }}>
                    <span className="text-xl">{pinnedPlaylistIds.includes(playlist.id) ? '📌' : '📁'}</span>
                    <div className="flex-1 min-w-0"><p style={{ color: neonBlue }}>{playlist.name}</p><p className="text-xs text-slate-500">{playlist.track_count} {t('music.tracks')}</p></div>
                  </button>
                ))}
              </div>
            )}
            <button onClick={() => { setShowAddToPlaylist(false); setTrackToAdd(null); }} className="w-full mt-4 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white border border-slate-700">{t('music.cancel')}</button>
          </div>
        </div>
      )}
    </div>
  );
}