/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        base:    '#0a0a0a',
        surface: '#111111',
        subtle:  '#161616',
        muted:   '#1a1a1a',
        border: {
          DEFAULT: '#1f1f1f',
          hover:   '#2a2a2a',
        },
        accent: {
          DEFAULT: '#4f46e5',
          hover:   '#4338ca',
        },
        zinc: {
          925: '#0f0f0f',
        },
      },
      fontSize: {
        '2xs': ['11px', { lineHeight: '16px', letterSpacing: '0.08em' }],
      },
      borderRadius: {
        DEFAULT: '6px',
      },
      boxShadow: {
        'border': '0 0 0 1px #1f1f1f',
        'focus':  '0 0 0 2px #0a0a0a, 0 0 0 4px #4f46e5',
        'card':   '0 1px 3px rgba(0,0,0,0.4)',
      },
      animation: {
        'fade-in':   'fadeIn 200ms ease forwards',
        'shimmer':   'shimmer 1.5s infinite',
        'spin-slow': 'spin 2s linear infinite',
      },
    },
  },
  plugins: [],
}
