import * as React from "react"

// Animation configuration
export interface AnimationConfig {
  duration: number
  easing: string
  delay?: number
  fillMode?: "none" | "forwards" | "backwards" | "both"
}

// Default animation configurations
export const animationPresets = {
  // Basic transitions
  fast: { duration: 150, easing: "cubic-bezier(0.4, 0, 0.2, 1)" },
  normal: { duration: 300, easing: "cubic-bezier(0.4, 0, 0.2, 1)" },
  slow: { duration: 500, easing: "cubic-bezier(0.4, 0, 0.2, 1)" },
  
  // Smooth easing functions
  ease: { duration: 300, easing: "cubic-bezier(0.25, 0.1, 0.25, 1)" },
  easeIn: { duration: 300, easing: "cubic-bezier(0.4, 0, 1, 1)" },
  easeOut: { duration: 300, easing: "cubic-bezier(0, 0, 0.2, 1)" },
  easeInOut: { duration: 300, easing: "cubic-bezier(0.4, 0, 0.2, 1)" },
  
  // Spring-like animations
  bounce: { duration: 600, easing: "cubic-bezier(0.68, -0.55, 0.265, 1.55)" },
  elastic: { duration: 800, easing: "cubic-bezier(0.175, 0.885, 0.32, 1.275)" },
  
  // Financial data specific
  financial: { duration: 400, easing: "cubic-bezier(0.25, 0.46, 0.45, 0.94)" },
  counter: { duration: 1200, easing: "cubic-bezier(0.25, 0.1, 0.25, 1)" },
  chart: { duration: 750, easing: "cubic-bezier(0.4, 0, 0.2, 1)" },
} as const

// Hook for managing animation states
export function useAnimation(config: AnimationConfig = animationPresets.normal) {
  const [isAnimating, setIsAnimating] = React.useState(false)
  const [isComplete, setIsComplete] = React.useState(false)
  const timeoutRef = React.useRef<NodeJS.Timeout | null>(null)

  const trigger = React.useCallback(() => {
    setIsAnimating(true)
    setIsComplete(false)
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    
    timeoutRef.current = setTimeout(() => {
      setIsAnimating(false)
      setIsComplete(true)
    }, config.duration + (config.delay || 0))
  }, [config.duration, config.delay])

  const reset = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsAnimating(false)
    setIsComplete(false)
  }, [])

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return { isAnimating, isComplete, trigger, reset }
}

// Hook for entrance animations
export function useEntranceAnimation(config: AnimationConfig = animationPresets.normal) {
  const [hasEntered, setHasEntered] = React.useState(false)
  const elementRef = React.useRef<HTMLElement>(null)

  React.useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasEntered) {
          setHasEntered(true)
        }
      },
      { threshold: 0.1 }
    )

    observer.observe(element)
    return () => observer.disconnect()
  }, [hasEntered])

  return { hasEntered, elementRef }
}

// Hook for stagger animations
export function useStaggerAnimation(
  count: number, 
  config: AnimationConfig = animationPresets.normal,
  staggerDelay: number = 100
) {
  const [activeIndex, setActiveIndex] = React.useState(-1)
  const timeoutsRef = React.useRef<NodeJS.Timeout[]>([])

  const trigger = React.useCallback(() => {
    // Clear existing timeouts
    timeoutsRef.current.forEach(timeout => clearTimeout(timeout))
    timeoutsRef.current = []
    
    setActiveIndex(-1)
    
    // Start stagger sequence
    for (let i = 0; i < count; i++) {
      const timeout = setTimeout(() => {
        setActiveIndex(i)
      }, i * staggerDelay)
      timeoutsRef.current.push(timeout)
    }
  }, [count, staggerDelay])

  const reset = React.useCallback(() => {
    timeoutsRef.current.forEach(timeout => clearTimeout(timeout))
    timeoutsRef.current = []
    setActiveIndex(-1)
  }, [])

  React.useEffect(() => {
    return () => {
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout))
    }
  }, [])

  return { activeIndex, trigger, reset }
}

// Hook for smooth value transitions (e.g., counters)
export function useValueTransition(
  targetValue: number,
  config: AnimationConfig = animationPresets.counter
) {
  const [currentValue, setCurrentValue] = React.useState(targetValue)
  const [isTransitioning, setIsTransitioning] = React.useState(false)
  const rafRef = React.useRef<number | null>(null)
  const startTimeRef = React.useRef<number | null>(null)
  const startValueRef = React.useRef<number>(targetValue)

  React.useEffect(() => {
    if (Math.abs(currentValue - targetValue) < 0.01) return

    setIsTransitioning(true)
    startTimeRef.current = performance.now()
    startValueRef.current = currentValue

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) return

      const elapsed = timestamp - startTimeRef.current
      const progress = Math.min(elapsed / config.duration, 1)
      
      // Parse easing function (simplified for cubic-bezier)
      const easedProgress = progress // Simplified - in real implementation, parse and apply easing
      
      const newValue = startValueRef.current + 
        (targetValue - startValueRef.current) * easedProgress

      setCurrentValue(newValue)

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate)
      } else {
        setCurrentValue(targetValue)
        setIsTransitioning(false)
      }
    }

    rafRef.current = requestAnimationFrame(animate)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [targetValue, config.duration])

  return { currentValue, isTransitioning }
}

// Hook for managing reduced motion preferences
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches
  )

  React.useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [])

  return prefersReducedMotion
}

// HOC for conditional animations based on reduced motion
export function withAnimation<T extends object>(
  Component: React.ComponentType<T>,
  animatedProps: Partial<T> = {},
  staticProps: Partial<T> = {}
) {
  return React.forwardRef<any, T>((props, ref) => {
    const prefersReducedMotion = useReducedMotion()
    
    const finalProps = {
      ...props,
      ...(prefersReducedMotion ? staticProps : animatedProps),
      ref
    } as any

    return React.createElement(Component, finalProps)
  })
}

// CSS-in-JS animation utilities
export const createAnimation = (
  keyframes: Record<string, React.CSSProperties>,
  config: AnimationConfig
) => {
  const keyframeString = Object.entries(keyframes)
    .map(([percentage, styles]) => {
      const styleString = Object.entries(styles)
        .map(([prop, value]) => `${prop}: ${value}`)
        .join("; ")
      return `${percentage} { ${styleString} }`
    })
    .join(" ")

  return `
    @keyframes custom-animation {
      ${keyframeString}
    }
    animation: custom-animation ${config.duration}ms ${config.easing} ${config.delay || 0}ms ${config.fillMode || "both"};
  `
}

// Common animation keyframe definitions
export const animationKeyframes = {
  fadeIn: {
    "0%": { opacity: 0 },
    "100%": { opacity: 1 },
  },
  fadeInUp: {
    "0%": { opacity: 0, transform: "translateY(10px)" },
    "100%": { opacity: 1, transform: "translateY(0)" },
  },
  fadeInDown: {
    "0%": { opacity: 0, transform: "translateY(-10px)" },
    "100%": { opacity: 1, transform: "translateY(0)" },
  },
  slideInLeft: {
    "0%": { opacity: 0, transform: "translateX(-20px)" },
    "100%": { opacity: 1, transform: "translateX(0)" },
  },
  slideInRight: {
    "0%": { opacity: 0, transform: "translateX(20px)" },
    "100%": { opacity: 1, transform: "translateX(0)" },
  },
  scaleIn: {
    "0%": { opacity: 0, transform: "scale(0.95)" },
    "100%": { opacity: 1, transform: "scale(1)" },
  },
  pulse: {
    "0%": { transform: "scale(1)" },
    "50%": { transform: "scale(1.05)" },
    "100%": { transform: "scale(1)" },
  },
  bounce: {
    "0%, 20%, 53%, 80%, 100%": { transform: "translateY(0)" },
    "40%, 43%": { transform: "translateY(-8px)" },
    "70%": { transform: "translateY(-4px)" },
    "90%": { transform: "translateY(-2px)" },
  },
  shimmer: {
    "0%": { backgroundPosition: "-200% 0" },
    "100%": { backgroundPosition: "200% 0" },
  },
  countUp: {
    "0%": { transform: "translateY(100%) scale(0.8)", opacity: 0 },
    "50%": { transform: "translateY(-10%) scale(1.1)", opacity: 0.8 },
    "100%": { transform: "translateY(0%) scale(1)", opacity: 1 },
  },
} as const

export type AnimationKeyframe = keyof typeof animationKeyframes