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
        dark: {
          950: '#0a0a0f',
          900: '#13131f',
          850: '#1a1a2e',
          800: '#1f1f35',
          750: '#252542',
          700: '#2a2a4a',
          600: '#3a3a5a',
          500: '#4a4a6a',
        },
        accent: {
          blue: '#3b82f6',
          blueHover: '#2563eb',
          green: '#10b981',
          red: '#ef4444',
          yellow: '#f59e0b',
          purple: '#8b5cf6',
        }
      },
      boxShadow: {
        'glow': '0 0 20px rgba(59, 130, 246, 0.15)',
        'glow-green': '0 0 20px rgba(16, 185, 129, 0.15)',
        'glow-red': '0 0 20px rgba(239, 68, 68, 0.15)',
      }
    },
  },
  plugins: [],
}
