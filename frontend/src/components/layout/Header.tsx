import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { LANGUAGES, LanguageCode } from '../../i18n/config'

interface HeaderProps {
  darkMode: boolean
  setDarkMode: (value: boolean) => void
}

export default function Header({ darkMode, setDarkMode }: HeaderProps) {
  const { t, i18n } = useTranslation()
  const location = useLocation()
  const [langOpen, setLangOpen] = useState(false)

  const navItems = [
    { path: '/', label: t('nav.dashboard'), key: 'dashboard' },
    { path: '/servers', label: t('nav.servers'), key: 'servers' },
    { path: '/clients', label: t('nav.clients'), key: 'clients' },
    { path: '/tests', label: t('nav.tests'), key: 'tests' },
    { path: '/events', label: t('nav.events'), key: 'events' },
  ]

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  const currentLang = LANGUAGES[i18n.language as LanguageCode] || LANGUAGES.en

  return (
    <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <span className="text-2xl">🔍</span>
              <span className="text-xl font-semibold text-slate-900 dark:text-white">
                SimpleX SMP Monitor
              </span>
            </Link>
            
            {/* WebSocket Status */}
            <div className="ml-4 flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800">
              <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
              <span className="text-xs text-slate-500 dark:text-slate-400">React</span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.key}
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center space-x-3">
            {/* Language Switcher */}
            <div className="relative">
              <button
                onClick={() => setLangOpen(!langOpen)}
                className="px-3 py-1.5 rounded-lg text-sm font-medium border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors inline-flex items-center space-x-1"
              >
                <span>{currentLang.name}</span>
                <svg
                  className={`w-3 h-3 ml-1 transition-transform ${langOpen ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {langOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-slate-800 shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  {Object.entries(LANGUAGES).map(([code, meta]) => (
                    <button
                      key={code}
                      onClick={() => {
                        i18n.changeLanguage(code)
                        setLangOpen(false)
                      }}
                      className={`w-full px-3 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-between transition-colors ${
                        i18n.language === code ? 'bg-primary-50 dark:bg-primary-900/30' : ''
                      }`}
                    >
                      <span className="text-slate-700 dark:text-slate-300">{meta.name}</span>
                      {i18n.language === code && (
                        <span className="text-primary-500 text-xs">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {darkMode ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-slate-200 dark:border-slate-800 px-4 py-2">
        <div className="flex flex-wrap gap-2">
          {navItems.map((item) => (
            <Link
              key={item.key}
              to={item.path}
              className={`px-3 py-1.5 rounded-lg text-sm ${
                isActive(item.path)
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}
