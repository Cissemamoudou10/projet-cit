module.exports = {
  content: [
    './app/**/templates/**/*.html',
    './app/**/*.py',
  ],
  theme: {
    colors: {
      marine: { 950: '#18305A', 900: '#1F3864', 700: '#2E4F8F' },
      encre: '#1A1D23',
      gris: { lecture: '#4A4F58', trait: '#C9CFD8', eteint: '#A6ACB6', inerte: '#E2E7EE' },
      fond: {
        page: '#F7F8FA', bloc: '#FFFFFF', bande: '#F2F5F9',
        survol: '#EDF2FA', selection: '#E7ECF4',
      },
      etat: {
        conforme: '#0F6E56', 'conforme-fond': '#EEF7F3',
        attention: '#B07000', 'attention-fond': '#FDF6E7',
        ecart: '#B03030', 'ecart-fond': '#FCF0F0', 'ecart-fonce': '#9A2A2A',
      },
      sable: '#FBF8F1',
      focus: { DEFAULT: '#C7D5EC', ecart: '#EBC0C0' },
      blanc: '#FFFFFF',
      noir: '#000000',
      transparent: 'transparent',
      current: 'currentColor',
    },
    fontFamily: {
      titre: ['Barlow', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      corps: ['IBM Plex Sans', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      mono: ['IBM Plex Mono', 'ui-monospace', 'Cascadia Mono', 'Consolas', 'monospace'],
    },
    fontSize: {
      '2xs': ['11px', '1.3'],
      xs: ['12px', '1.4'],
      sm: ['13px', '1.45'],
      base: ['14px', '1.5'],
      md: ['15px', '1.35'],
      lg: ['18px', '1.3'],
      xl: ['24px', '1.2'],
    },
    borderRadius: { none: '0', DEFAULT: '2px', pilule: '9999px' },
    boxShadow: {
      none: 'none',
      superpose: '0 2px 6px rgba(26,29,35,.14)',
    },
    extend: {
      spacing: {
        1: '4px', 2: '8px', 3: '12px', 4: '16px', 6: '24px', 8: '32px', 12: '48px',
        ligne: '32px', 'ligne-large': '36px', controle: '32px',
      },
      minWidth: { 16: '4rem', 60: '15rem' },
      minHeight: { controle: '32px' },
      maxWidth: { utile: '1180px', large: '1240px' },
      transitionDuration: {
        survol: '120ms', menu: '150ms', badge: '180ms',
        notif: '200ms', secousse: '300ms', barre: '400ms',
      },
      keyframes: {
        secousse: {
          '0%,100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-3px)' },
          '75%': { transform: 'translateX(3px)' },
        },
        squelette: { '0%,100%': { opacity: '.5' }, '50%': { opacity: '1' } },
        glisser: {
          from: { transform: 'translateY(-12px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        ouvrir: {
          from: { transform: 'scale(.98)', opacity: '0' },
          to: { transform: 'scale(1)', opacity: '1' },
        },
      },
      animation: {
        secousse: 'secousse 300ms ease-in-out',
        squelette: 'squelette 1.2s ease-in-out infinite',
        glisser: 'glisser 200ms ease-out',
        ouvrir: 'ouvrir 150ms ease-out',
      },
    },
  },
  plugins: [],
}
