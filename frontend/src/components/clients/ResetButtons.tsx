/**
 * SimpleX SMP Monitor by cannatoshi
 * GitHub: https://github.com/cannatoshi/simplex-smp-monitor
 * Licensed under AGPL-3.0
 * 
 * ResetButtons Component
 * 
 * Dropdown menu with reset actions:
 * - Reset Messages: Delete all messages + reset counters
 * - Recalculate Counters: Recalculate from database
 * - Clear Latency Data: Clear latency only
 * - Full Reset: Delete all + reset counters
 */

import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Brand colors
const neonBlue = '#88CED0';

interface Props {
  clientId: string;
  onResetComplete?: () => void;
}

// Get CSRF token from cookies
const getCsrfToken = (): string => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === 'csrftoken') return value;
  }
  return '';
};

export default function ResetButtons({ clientId, onResetComplete }: Props) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setConfirm(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-hide result after 3 seconds
  useEffect(() => {
    if (result) {
      const timer = setTimeout(() => setResult(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [result]);

  const handleAction = async (action: string) => {
    if (confirm !== action) {
      setConfirm(action);
      return;
    }

    setLoading(action);
    setConfirm(null);

    try {
      const response = await fetch(`/api/v1/clients/${clientId}/${action}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setResult({ success: true, message: data.message });
        onResetComplete?.();
      } else {
        setResult({ success: false, message: data.error || 'Error' });
      }
    } catch (error) {
      setResult({ success: false, message: 'Request failed' });
    } finally {
      setLoading(null);
      setIsOpen(false);
    }
  };

  const actions = [
    {
      key: 'reset-counters',
      icon: '🔄',
      label: t('resetButtons.recalculateCounters'),
      description: t('resetButtons.recalculateDesc'),
      danger: false,
    },
    {
      key: 'reset-latency',
      icon: '⏱️',
      label: t('resetButtons.clearLatency'),
      description: t('resetButtons.clearLatencyDesc'),
      danger: false,
    },
    {
      key: 'reset-messages',
      icon: '🗑️',
      label: t('resetButtons.resetMessages'),
      description: t('resetButtons.resetMessagesDesc'),
      danger: true,
    },
    {
      key: 'reset-all',
      icon: '⚠️',
      label: t('resetButtons.fullReset'),
      description: t('resetButtons.fullResetDesc'),
      danger: true,
    },
  ];

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button - matching neonButtonStyle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1.5 rounded-lg text-sm font-medium inline-flex items-center gap-1.5 hover:opacity-90 transition-opacity"
        style={{
          backgroundColor: 'rgb(30, 41, 59)',
          color: neonBlue,
          border: `1px solid ${neonBlue}`,
          boxShadow: '0 0 8px rgba(136, 206, 208, 0.4)'
        }}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {t('resetButtons.reset')}
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-slate-800 border border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden">
          <div className="p-2 border-b border-slate-700">
            <p className="text-xs text-slate-400 px-2">{t('resetButtons.selectAction')}</p>
          </div>
          
          <div className="py-1">
            {actions.map((action) => (
              <button
                key={action.key}
                onClick={() => handleAction(action.key)}
                disabled={loading !== null}
                className={`w-full px-4 py-3 text-left hover:bg-slate-700/50 transition-colors flex items-start gap-3 ${
                  action.danger ? 'hover:bg-red-900/20' : ''
                } ${loading === action.key ? 'opacity-50' : ''}`}
              >
                <span className="text-lg mt-0.5">{action.icon}</span>
                <div className="flex-1">
                  <p className={`font-medium ${action.danger ? 'text-red-400' : 'text-white'}`}>
                    {confirm === action.key ? t('resetButtons.clickToConfirm') : action.label}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">{action.description}</p>
                </div>
                {loading === action.key && (
                  <div 
                    className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin mt-1"
                    style={{ borderColor: neonBlue, borderTopColor: 'transparent' }}
                  />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Result Toast - fixed position */}
      {result && (
        <div 
          className={`fixed top-4 right-4 px-4 py-3 rounded-lg text-sm shadow-lg z-[9999] ${
            result.success ? 'bg-green-900/95 text-green-300 border border-green-700' : 'bg-red-900/95 text-red-300 border border-red-700'
          }`}
        >
          {result.success ? '✓' : '✗'} {result.message}
        </div>
      )}
    </div>
  );
}