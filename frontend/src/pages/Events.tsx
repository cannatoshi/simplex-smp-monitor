import { useTranslation } from 'react-i18next'

export default function Events() {
  const { t } = useTranslation()
  
  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
        {t('nav.events')}
      </h1>
      <div className="bg-white dark:bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-200 dark:border-slate-800 p-6">
        <p className="text-slate-600 dark:text-slate-600 dark:text-slate-400">
          Events content coming soon...
        </p>
      </div>
    </div>
  )
}
