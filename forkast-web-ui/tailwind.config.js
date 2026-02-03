/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        dark: {
          900: '#0f172a', // Slate 900
          800: '#1e293b', // Slate 800
          700: '#334155', // Slate 700
        },
        brand: {
          blue: '#3b82f6',
          purple: '#8b5cf6',
          green: '#22c55e',
          red: '#ef4444',
        }
      }
    },
  },
  plugins: [],
}
