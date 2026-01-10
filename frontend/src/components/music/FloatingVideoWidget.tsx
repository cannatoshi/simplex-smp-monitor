/**
 * SimpleX SMP Monitor - Floating Video Widget
 * ============================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * Draggable, resizable YouTube video widget.
 * Persists across navigation, fullscreen in content area only.
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

// Design System Colors
const neonBlue = '#88CED0';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';

type WidgetSize = 'small' | 'medium' | 'large' | 'fullscreen';

const SIZES: Record<Exclude<WidgetSize, 'fullscreen'>, { width: number; height: number }> = {
  small: { width: 320, height: 180 },
  medium: { width: 480, height: 270 },
  large: { width: 640, height: 360 },
};

interface FloatingVideoWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string | null;
  title?: string;
  startTime?: number;
}

export default function FloatingVideoWidget({ isOpen, onClose, videoId, title, startTime = 0 }: FloatingVideoWidgetProps) {
  const { t } = useTranslation();
  const widgetRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<WidgetSize>('medium');
  const [position, setPosition] = useState({ x: 100, y: 100 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isMinimized, setIsMinimized] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);

  // Reset position when opened
  useEffect(() => {
    if (isOpen && videoId && !hasInitialized) {
      // Position in bottom-right of content area
      const mainContent = document.querySelector('main');
      if (mainContent) {
        const rect = mainContent.getBoundingClientRect();
        setPosition({
          x: rect.right - SIZES.medium.width - 40,
          y: rect.bottom - SIZES.medium.height - 40,
        });
      }
      setSize('medium');
      setIsMinimized(false);
      setHasInitialized(true);
    }
    
    if (!isOpen) {
      setHasInitialized(false);
    }
  }, [isOpen, videoId, hasInitialized]);

  // Handle drag start
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (size === 'fullscreen') return;
    
    const target = e.target as HTMLElement;
    if (target.closest('button') || target.closest('iframe')) return;
    
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
  }, [position, size]);

  // Handle drag
  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const mainContent = document.querySelector('main');
      if (!mainContent) return;

      const rect = mainContent.getBoundingClientRect();
      const currentSize = size !== 'fullscreen' ? SIZES[size] : SIZES.medium;
      
      let newX = e.clientX - dragOffset.x;
      let newY = e.clientY - dragOffset.y;

      // Constrain to main content area
      newX = Math.max(rect.left + 10, Math.min(newX, rect.right - currentSize.width - 10));
      newY = Math.max(rect.top + 10, Math.min(newY, rect.bottom - currentSize.height - 10));

      setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset, size]);

  // Cycle through sizes
  const cycleSize = () => {
    const sizes: Exclude<WidgetSize, 'fullscreen'>[] = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(size as Exclude<WidgetSize, 'fullscreen'>);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setSize(sizes[nextIndex]);
  };

  // Toggle fullscreen (content area only)
  const toggleFullscreen = () => {
    if (size === 'fullscreen') {
      setSize('medium');
    } else {
      setSize('fullscreen');
    }
  };

  if (!isOpen || !videoId) return null;

  // Calculate fullscreen dimensions
  const getFullscreenStyle = (): React.CSSProperties => {
    const mainContent = document.querySelector('main');
    if (!mainContent) return {};
    
    const rect = mainContent.getBoundingClientRect();
    return {
      position: 'fixed',
      top: rect.top + 10,
      left: rect.left + 10,
      width: rect.width - 20,
      height: rect.height - 20,
      zIndex: 100,
    };
  };

  // Minimized view
  if (isMinimized) {
    return (
      <div
        className="fixed z-[100] rounded-lg overflow-hidden cursor-pointer group"
        style={{
          left: position.x,
          top: position.y,
          width: 220,
          backgroundColor: 'rgb(15, 23, 42)',
          border: `1px solid ${neonBlue}`,
          boxShadow: `${neonGlow}, 0 10px 25px -5px rgba(0, 0, 0, 0.5)`,
        }}
        onClick={() => setIsMinimized(false)}
      >
        <div className="flex items-center gap-2 p-2">
          {/* Video Icon */}
          <div 
            className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: 'rgba(136, 206, 208, 0.2)' }}
          >
            <svg className="w-4 h-4" style={{ color: neonBlue }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          
          {/* Title */}
          <span 
            className="text-xs truncate flex-1"
            style={{ color: neonBlue }}
          >
            {title || 'Video'}
          </span>
          
          {/* Close Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-red-500/20 transition-colors opacity-0 group-hover:opacity-100"
            style={{ color: '#ef4444' }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    );
  }

  const currentSize = size !== 'fullscreen' ? SIZES[size] : null;
  const isFullscreen = size === 'fullscreen';

  return (
    <div
      ref={widgetRef}
      className={`fixed rounded-xl overflow-hidden ${isDragging ? 'cursor-grabbing' : ''} ${isFullscreen ? '' : 'shadow-2xl'}`}
      style={isFullscreen ? {
        ...getFullscreenStyle(),
        backgroundColor: 'rgb(15, 23, 42)',
        border: `1px solid ${neonBlue}`,
        boxShadow: `${neonGlow}, 0 25px 50px -12px rgba(0, 0, 0, 0.7)`,
      } : {
        left: position.x,
        top: position.y,
        width: currentSize?.width,
        zIndex: 100,
        backgroundColor: 'rgb(15, 23, 42)',
        border: `1px solid ${neonBlue}`,
        boxShadow: `${neonGlow}, 0 25px 50px -12px rgba(0, 0, 0, 0.5)`,
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header */}
      <div 
        className={`flex items-center justify-between px-3 py-2 border-b border-slate-800 ${!isFullscreen ? 'cursor-grab' : ''}`}
        style={{ backgroundColor: 'rgb(15, 23, 42)' }}
      >
        {/* Drag Handle + Title */}
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {!isFullscreen && (
            <svg className="w-4 h-4 text-slate-600 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0z" />
            </svg>
          )}
          <span 
            className="text-xs font-medium truncate"
            style={{ color: neonBlue }}
          >
            {title || t('music.videoPreview')}
          </span>
        </div>
        
        {/* Controls */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Minimize */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsMinimized(true);
            }}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-slate-800 transition-colors"
            style={{ color: neonBlue }}
            title={t('music.minimizePlayer')}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>

          {/* Size Toggle */}
          {!isFullscreen && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                cycleSize();
              }}
              className="w-6 h-6 flex items-center justify-center rounded hover:bg-slate-800 transition-colors"
              style={{ color: neonBlue }}
              title={`Size: ${size}`}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          )}

          {/* Fullscreen */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              toggleFullscreen();
            }}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-slate-800 transition-colors"
            style={{ color: neonBlue }}
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
              </svg>
            )}
          </button>

          {/* Close */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-red-500/20 transition-colors"
            style={{ color: '#ef4444' }}
            title="Close"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Video */}
      <div 
        className="relative bg-black"
        style={{ 
          height: isFullscreen 
            ? 'calc(100% - 40px)' 
            : (currentSize?.height || 270) - 40 
        }}
      >
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&start=${Math.floor(startTime)}`}
          title={title || 'Video'}
          className="absolute inset-0 w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
}