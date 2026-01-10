/**
 * SimpleX SMP Monitor - Video Preview Modal
 * ==========================================
 * Copyright (c) 2026 cannatoshi
 * https://github.com/cannatoshi/simplex-smp-monitor
 *
 * YouTube video preview in a modal.
 */
import { useTranslation } from 'react-i18next';

// Design System Colors
const neonBlue = '#88CED0';
const neonGlow = '0 0 8px rgba(136, 206, 208, 0.4)';

interface VideoPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string | null;
  title?: string;
}

export default function VideoPreviewModal({ isOpen, onClose, videoId, title }: VideoPreviewModalProps) {
  const { t } = useTranslation();

  if (!isOpen || !videoId) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-4xl rounded-xl overflow-hidden"
        style={{ 
          backgroundColor: 'rgb(15, 23, 42)',
          border: `1px solid ${neonBlue}`,
          boxShadow: neonGlow
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <h3 
            className="font-medium truncate flex-1 mr-4"
            style={{ color: neonBlue }}
          >
            {title || t('music.videoPreview')}
          </h3>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-800 transition-colors"
            style={{ color: neonBlue }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Video */}
        <div className="relative aspect-video bg-black">
          <iframe
            src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
            title={title || 'Video Preview'}
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
}