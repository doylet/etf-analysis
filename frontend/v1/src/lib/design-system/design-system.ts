/**
 * Design System Theme Configuration
 * Semantic layer on top of design tokens
 */

import { colors, typography, spacing, borderRadius, shadows, zIndex, componentSizes } from './design-tokens';

// Semantic Color Assignments
export const theme = {
  colors: {
    // Background colors
    background: {
      primary: colors.gray[50],
      secondary: colors.gray[100],
      tertiary: colors.gray[200],
      inverse: colors.gray[900],
      paper: '#ffffff',
      overlay: 'rgba(0, 0, 0, 0.5)'
    },

    // Text colors
    text: {
      primary: colors.gray[900],
      secondary: colors.gray[600],
      tertiary: colors.gray[500],
      disabled: colors.gray[400],
      inverse: colors.gray[50],
      link: colors.primary[600],
      linkHover: colors.primary[700]
    },

    // Border colors
    border: {
      primary: colors.gray[200],
      secondary: colors.gray[300],
      focus: colors.primary[500],
      error: colors.error[500],
      success: colors.success[500],
      warning: colors.warning[500]
    },

    // Interactive states
    interactive: {
      primary: colors.primary[600],
      primaryHover: colors.primary[700],
      primaryActive: colors.primary[800],
      primaryDisabled: colors.gray[300],
      
      secondary: colors.gray[100],
      secondaryHover: colors.gray[200],
      secondaryActive: colors.gray[300],
      
      danger: colors.error[600],
      dangerHover: colors.error[700],
      dangerActive: colors.error[800],
      
      success: colors.success[600],
      successHover: colors.success[700],
      successActive: colors.success[800]
    },

    // Feedback colors
    feedback: {
      error: colors.error[500],
      errorBg: colors.error[50],
      errorBorder: colors.error[200],
      
      warning: colors.warning[500],
      warningBg: colors.warning[50],
      warningBorder: colors.warning[200],
      
      success: colors.success[500],
      successBg: colors.success[50],
      successBorder: colors.success[200],
      
      info: colors.info[500],
      infoBg: colors.info[50],
      infoBorder: colors.info[200]
    }
  },

  typography: {
    fontFamily: typography.fontFamily,
    
    // Text styles with semantic names
    heading: {
      h1: {
        fontSize: typography.fontSize['4xl'][0],
        lineHeight: typography.fontSize['4xl'][1].lineHeight,
        fontWeight: typography.fontWeight.bold,
        letterSpacing: typography.letterSpacing.tight
      },
      h2: {
        fontSize: typography.fontSize['3xl'][0],
        lineHeight: typography.fontSize['3xl'][1].lineHeight,
        fontWeight: typography.fontWeight.bold,
        letterSpacing: typography.letterSpacing.tight
      },
      h3: {
        fontSize: typography.fontSize['2xl'][0],
        lineHeight: typography.fontSize['2xl'][1].lineHeight,
        fontWeight: typography.fontWeight.semibold,
        letterSpacing: typography.letterSpacing.normal
      },
      h4: {
        fontSize: typography.fontSize.xl[0],
        lineHeight: typography.fontSize.xl[1].lineHeight,
        fontWeight: typography.fontWeight.semibold,
        letterSpacing: typography.letterSpacing.normal
      },
      h5: {
        fontSize: typography.fontSize.lg[0],
        lineHeight: typography.fontSize.lg[1].lineHeight,
        fontWeight: typography.fontWeight.medium,
        letterSpacing: typography.letterSpacing.normal
      },
      h6: {
        fontSize: typography.fontSize.base[0],
        lineHeight: typography.fontSize.base[1].lineHeight,
        fontWeight: typography.fontWeight.medium,
        letterSpacing: typography.letterSpacing.normal
      }
    },

    body: {
      large: {
        fontSize: typography.fontSize.lg[0],
        lineHeight: typography.fontSize.lg[1].lineHeight,
        fontWeight: typography.fontWeight.normal
      },
      base: {
        fontSize: typography.fontSize.base[0],
        lineHeight: typography.fontSize.base[1].lineHeight,
        fontWeight: typography.fontWeight.normal
      },
      small: {
        fontSize: typography.fontSize.sm[0],
        lineHeight: typography.fontSize.sm[1].lineHeight,
        fontWeight: typography.fontWeight.normal
      },
      extraSmall: {
        fontSize: typography.fontSize.xs[0],
        lineHeight: typography.fontSize.xs[1].lineHeight,
        fontWeight: typography.fontWeight.normal
      }
    },

    label: {
      large: {
        fontSize: typography.fontSize.base[0],
        fontWeight: typography.fontWeight.medium,
        letterSpacing: typography.letterSpacing.normal
      },
      base: {
        fontSize: typography.fontSize.sm[0],
        fontWeight: typography.fontWeight.medium,
        letterSpacing: typography.letterSpacing.normal
      },
      small: {
        fontSize: typography.fontSize.xs[0],
        fontWeight: typography.fontWeight.medium,
        letterSpacing: typography.letterSpacing.wide
      }
    },

    caption: {
      fontSize: typography.fontSize.xs[0],
      lineHeight: typography.fontSize.xs[1].lineHeight,
      fontWeight: typography.fontWeight.normal,
      letterSpacing: typography.letterSpacing.wide
    }
  },

  spacing: {
    ...spacing,
    // Semantic spacing aliases
    component: {
      paddingX: spacing[4],
      paddingY: spacing[2],
      gap: spacing[3],
      section: spacing[8]
    },
    layout: {
      container: spacing[6],
      section: spacing[16],
      header: spacing[4],
      sidebar: spacing[6]
    }
  },

  radius: {
    ...borderRadius,
    // Component-specific radius
    button: borderRadius.md,
    input: borderRadius.md,
    card: borderRadius.lg,
    modal: borderRadius.xl,
    avatar: borderRadius.full
  },

  shadows: {
    ...shadows,
    // Component-specific shadows
    card: shadows.sm,
    cardHover: shadows.md,
    modal: shadows.xl,
    dropdown: shadows.lg,
    tooltip: shadows.md
  },

  zIndex,

  animation: {
    // Semantic animation presets
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)'
  }
} as const;

// Component-specific theme configurations
export const componentThemes = {
  button: {
    sizes: componentSizes,
    variants: {
      primary: {
        backgroundColor: theme.colors.interactive.primary,
        color: theme.colors.text.inverse,
        borderColor: 'transparent',
        hover: {
          backgroundColor: theme.colors.interactive.primaryHover
        },
        active: {
          backgroundColor: theme.colors.interactive.primaryActive
        },
        disabled: {
          backgroundColor: theme.colors.interactive.primaryDisabled,
          color: theme.colors.text.disabled
        }
      },
      secondary: {
        backgroundColor: theme.colors.interactive.secondary,
        color: theme.colors.text.primary,
        borderColor: 'transparent',
        hover: {
          backgroundColor: theme.colors.interactive.secondaryHover
        },
        active: {
          backgroundColor: theme.colors.interactive.secondaryActive
        }
      },
      outline: {
        backgroundColor: 'transparent',
        color: theme.colors.text.primary,
        borderColor: theme.colors.border.primary,
        hover: {
          backgroundColor: theme.colors.background.secondary
        },
        active: {
          backgroundColor: theme.colors.interactive.secondaryActive
        }
      },
      ghost: {
        backgroundColor: 'transparent',
        color: theme.colors.text.secondary,
        borderColor: 'transparent',
        hover: {
          backgroundColor: theme.colors.interactive.secondary,
          color: theme.colors.text.primary
        },
        active: {
          backgroundColor: theme.colors.interactive.secondaryActive
        }
      },
      danger: {
        backgroundColor: theme.colors.interactive.danger,
        color: theme.colors.text.inverse,
        borderColor: 'transparent',
        hover: {
          backgroundColor: theme.colors.interactive.dangerHover
        },
        active: {
          backgroundColor: theme.colors.interactive.dangerActive
        }
      }
    }
  },

  card: {
    variants: {
      default: {
        backgroundColor: theme.colors.background.paper,
        borderColor: theme.colors.border.primary,
        shadow: theme.shadows.card,
        hover: {
          shadow: theme.shadows.cardHover
        }
      },
      outlined: {
        backgroundColor: theme.colors.background.paper,
        borderColor: theme.colors.border.secondary,
        borderWidth: '2px'
      },
      elevated: {
        backgroundColor: theme.colors.background.paper,
        borderColor: theme.colors.border.primary,
        shadow: theme.shadows.modal
      }
    }
  },

  alert: {
    variants: {
      info: {
        backgroundColor: theme.colors.feedback.infoBg,
        borderColor: theme.colors.feedback.infoBorder,
        color: theme.colors.feedback.info,
        iconColor: theme.colors.feedback.info
      },
      success: {
        backgroundColor: theme.colors.feedback.successBg,
        borderColor: theme.colors.feedback.successBorder,
        color: theme.colors.feedback.success,
        iconColor: theme.colors.feedback.success
      },
      warning: {
        backgroundColor: theme.colors.feedback.warningBg,
        borderColor: theme.colors.feedback.warningBorder,
        color: theme.colors.feedback.warning,
        iconColor: theme.colors.feedback.warning
      },
      error: {
        backgroundColor: theme.colors.feedback.errorBg,
        borderColor: theme.colors.feedback.errorBorder,
        color: theme.colors.feedback.error,
        iconColor: theme.colors.feedback.error
      }
    }
  }
} as const;

export type ThemeConfig = typeof theme;
export type ComponentThemes = typeof componentThemes;