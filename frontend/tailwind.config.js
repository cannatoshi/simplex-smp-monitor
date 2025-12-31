/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Bestehende Primary Farbe (bleibt für Kompatibilität)
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // NEU: Unsere Akzentfarbe #88CED0 🔥
        accent: {
          50: '#f0fbfb',
          100: '#d9f4f5',
          200: '#b8e9eb',
          300: '#88CED0',  // Deine Hauptfarbe!
          400: '#88CED0',  // DEFAULT
          500: '#6db8ba',
          600: '#569a9c',
          700: '#477d7f',
          800: '#3c6668',
          900: '#345556',
          950: '#1a3536',
          DEFAULT: '#88CED0',
        },
        // NEU: Dark Theme Palette
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          850: '#162032',
          900: '#0f172a',
          950: '#0a0f1a',
        },
      },
      // NEU: Box Shadows mit Akzentfarbe
      boxShadow: {
        'glow-accent-sm': '0 0 10px rgba(136, 206, 208, 0.3)',
        'glow-accent-md': '0 0 20px rgba(136, 206, 208, 0.4)',
        'glow-accent-lg': '0 0 30px rgba(136, 206, 208, 0.5)',
      },
      // NEU: Animationen
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(136, 206, 208, 0.3)' },
          '50%': { boxShadow: '0 0 25px rgba(136, 206, 208, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}