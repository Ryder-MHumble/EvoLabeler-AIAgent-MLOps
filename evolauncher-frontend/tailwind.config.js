/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Light theme colors - 优化配色
        light: {
          bg: '#F8FAFC',
          surface: '#FFFFFF',
          primary: '#3B82F6',
          secondary: '#8B5CF6',
          text: '#0F172A',
          'text-secondary': '#475569',
          border: '#E2E8F0'
        },
        // Dark theme colors - 优化配色
        dark: {
          bg: '#0F172A',
          surface: '#1E293B',
          primary: '#60A5FA',
          secondary: '#A78BFA',
          text: '#F1F5F9',
          'text-secondary': '#CBD5E1',
          border: '#334155'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif']
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.4s cubic-bezier(0.25, 0.1, 0.25, 1)',
        'glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideIn: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(74, 105, 255, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(74, 105, 255, 0.8)' }
        }
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(74, 105, 255, 0.3)',
        'glow-md': '0 0 20px rgba(74, 105, 255, 0.4)',
        'glow-lg': '0 0 30px rgba(74, 105, 255, 0.5)',
        'dark-glow-sm': '0 0 10px rgba(122, 162, 247, 0.3)',
        'dark-glow-md': '0 0 20px rgba(122, 162, 247, 0.4)',
        'dark-glow-lg': '0 0 30px rgba(122, 162, 247, 0.5)'
      }
    }
  },
  plugins: [
    require('@tailwindcss/typography')
  ]
}

