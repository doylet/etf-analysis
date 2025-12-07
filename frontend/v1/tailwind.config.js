/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
        financial: {
          positive: "hsl(var(--financial-positive))",
          negative: "hsl(var(--financial-negative))",
          neutral: "hsl(var(--financial-neutral))",
          warning: "hsl(var(--financial-warning))",
          info: "hsl(var(--financial-info))",
        },
        // Background colors
        'background-primary': 'rgb(var(--background-primary))',
        'background-secondary': 'rgb(var(--background-secondary))',
        // Text colors
        'text-primary': 'rgb(var(--text-primary))',
        'text-secondary': 'rgb(var(--text-secondary))',
        // Theme colors
        'theme-primary': 'var(--theme-primary)',
        'theme-secondary': 'var(--theme-secondary)',
        'theme-subtle': 'var(--theme-subtle)',
        // Border colors
        'border-primary': 'rgb(var(--border-primary))',
        'border-secondary': 'rgb(var(--border-secondary))',
        // Theme-aware utility colors  
        'scheme-primary': 'var(--color-scheme-primary)',
        'scheme-accent': 'var(--color-scheme-accent)',
        success: 'var(--color-success)',
        danger: 'var(--color-danger)', 
        warning: 'var(--color-warning)',
        info: 'var(--color-info)',
        neutral: 'var(--color-neutral)',
      },
      fontFamily: {
        // Financial data optimized fonts
        financial: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
        tabular: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // Financial data size scale
        'financial-xs': ['0.75rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-sm': ['0.875rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-base': ['1rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-lg': ['1.125rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-xl': ['1.25rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        'financial-2xl': ['1.5rem', { lineHeight: '1.2', letterSpacing: '0.025em' }],
      },
      spacing: {
        // Data-specific spacing
        'table-cell': '0.75rem',      // 12px table cell padding
        'table-row': '3rem',          // 48px minimum row height
        'table-header': '3.5rem',     // 56px header row height
        'card-padding': '1.25rem',    // 20px card internal spacing
        'metric-gap': '0.5rem',       // 8px between metric elements
        'metric-padding': '1rem',     // 16px metric container padding
      },
      boxShadow: {
        // Professional shadow system
        'card-subtle': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-default': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'card-elevated': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'modal': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },
      animation: {
        // Subtle animations for financial data
        'fade-in': 'fadeIn 200ms ease-out',
        'slide-up': 'slideUp 200ms ease-out',
        'pulse-subtle': 'pulseSubtle 2s ease-in-out infinite',
      },
    },
  },
  plugins: [
    // Custom plugin for financial utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.font-tabular': {
          fontFeatureSettings: '"tnum"',
          fontVariantNumeric: 'tabular-nums',
        },
        '.financial-positive': {
          color: theme('colors.financial.positive'),
        },
        '.financial-negative': {
          color: theme('colors.financial.negative'),
        },
        '.financial-neutral': {
          color: theme('colors.financial.neutral'),
        },
        '.grid-financial': {
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: theme('spacing.6'),
        },
      }
      addUtilities(newUtilities)
    }
  ],
};
