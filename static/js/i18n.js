/**
 * SimpleX SMP Monitor - Internationalization System
 * Currently: English & German (more languages can be added later)
 */

const LANGUAGES = {
    'en': { name: 'English', flag: '🇬🇧', rtl: false },
    'de': { name: 'Deutsch', flag: '🇩🇪', rtl: false }
};

document.addEventListener('alpine:init', () => {
    Alpine.store('i18n', {
        lang: localStorage.getItem('lang') || 'en',
        translations: {},
        loaded: false,
        languages: LANGUAGES,

        async init() {
            await this.loadLanguage(this.lang);
        },

        async loadLanguage(lang) {
            if (!LANGUAGES[lang]) lang = 'en';

            try {
                const response = await fetch(`/static/js/lang/${lang}.json`);
                if (!response.ok) throw new Error('Language file not found');

                this.translations = await response.json();
                this.lang = lang;
                this.loaded = true;
                localStorage.setItem('lang', lang);

                document.documentElement.dir = LANGUAGES[lang].rtl ? 'rtl' : 'ltr';
                document.documentElement.lang = lang;

            } catch (error) {
                console.error(`Failed to load language ${lang}:`, error);
                if (lang !== 'en') {
                    await this.loadLanguage('en');
                }
            }
        },

        t(key, params = {}) {
            let text = key.split('.').reduce((obj, k) => obj?.[k], this.translations);

            if (!text) {
                console.warn(`Translation missing: ${key}`);
                return key;
            }

            Object.keys(params).forEach(param => {
                text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param]);
            });

            return text;
        },

        /**
         * Format relative time like "5 Minutes" or "2 Hours"
         * @param {string} isoDate - ISO date string from Django
         * @returns {string} Translated relative time
         */
        timeAgo(isoDate) {
            if (!isoDate) return '-';
            
            const now = new Date();
            const date = new Date(isoDate);
            const seconds = Math.floor((now - date) / 1000);
            
            const intervals = [
                { seconds: 31536000, singular: 'year', plural: 'years' },
                { seconds: 2592000, singular: 'month', plural: 'months' },
                { seconds: 604800, singular: 'week', plural: 'weeks' },
                { seconds: 86400, singular: 'day', plural: 'days' },
                { seconds: 3600, singular: 'hour', plural: 'hours' },
                { seconds: 60, singular: 'minute', plural: 'minutes' },
                { seconds: 1, singular: 'second', plural: 'seconds' }
            ];
            
            for (const interval of intervals) {
                const count = Math.floor(seconds / interval.seconds);
                if (count >= 1) {
                    const key = count === 1 ? interval.singular : interval.plural;
                    const unit = this.t(`time.${key}`);
                    return `${count} ${unit}`;
                }
            }
            
            return this.t('time.just_now');
        },

        get isRTL() {
            return LANGUAGES[this.lang]?.rtl || false;
        },

        get currentFlag() {
            return LANGUAGES[this.lang]?.flag || '🌐';
        },

        get currentName() {
            return LANGUAGES[this.lang]?.name || 'Unknown';
        },

        get languageList() {
            return Object.entries(LANGUAGES).map(([code, meta]) => ({
                code,
                ...meta
            }));
        }
    });
});

window.t = (key, params) => Alpine.store('i18n')?.t(key, params) || key;
