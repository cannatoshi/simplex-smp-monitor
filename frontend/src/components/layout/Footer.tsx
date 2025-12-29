import { useTranslation } from 'react-i18next'

export default function Footer() {
  const { t } = useTranslation()
  
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 py-6 mt-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <span className="text-slate-500 text-sm">{t('footer.copyright')}</span>
        <span className="text-slate-500 text-sm font-mono">
          i(N) cod(E) w(E) trus(T) › {t('footer.version')}
        </span>
      </div>
    </footer>
  )
}
