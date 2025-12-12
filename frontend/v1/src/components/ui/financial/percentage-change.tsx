import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

const percentageChangeVariants = cva(
  "inline-flex items-center gap-1.5 font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "",
        subtle: "text-xs",
        bold: "font-semibold",
        badge: "px-2 py-1 rounded-full text-xs",
        compact: "gap-1 text-xs",
      },
      trend: {
        positive: "text-green-700",
        negative: "text-red-700", 
        neutral: "text-muted-foreground",
        auto: "", // Determined automatically based on value
      },
      size: {
        xs: "text-xs",
        sm: "text-sm", 
        default: "text-sm",
        lg: "text-base",
        xl: "text-lg",
      },
    },
    compoundVariants: [
      {
        variant: "badge",
        trend: "positive",
        className: "bg-financial-positive-subtle text-financial-positive border border-financial-positive-light",
      },
      {
        variant: "badge", 
        trend: "negative",
        className: "bg-financial-negative-subtle text-financial-negative border border-financial-negative-light",
      },
      {
        variant: "badge",
        trend: "neutral", 
        className: "bg-theme-subtle text-theme-primary border border-theme-soft",
      },
    ],
    defaultVariants: {
      variant: "default",
      trend: "auto",
      size: "default",
    },
  }
)

export interface PercentageChangeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof percentageChangeVariants> {
  value: number
  precision?: number
  showIcon?: boolean
  showSign?: boolean
  showPercent?: boolean
  animate?: boolean
}

const PercentageChange = React.forwardRef<HTMLSpanElement, PercentageChangeProps>(
  ({ 
    className, 
    variant, 
    trend: trendProp, 
    size, 
    value, 
    precision = 2,
    showIcon = true, 
    showSign = true,
    showPercent = true,
    animate = false,
    ...props 
  }, ref) => {
    // Auto-determine trend if not specified
    const trend = trendProp === "auto" || !trendProp 
      ? value > 0 ? "positive" : value < 0 ? "negative" : "neutral"
      : trendProp

    // Format the percentage value
    const formatValue = (val: number) => {
      const formatted = Math.abs(val).toFixed(precision)
      const sign = showSign ? (val > 0 ? "+" : val < 0 ? "-" : "") : ""
      const percent = showPercent ? "%" : ""
      return `${sign}${formatted}${percent}`
    }

    // Select appropriate icon
    const getIcon = () => {
      if (!showIcon) return null
      
      switch (trend) {
        case "positive":
          return <TrendingUp className="h-3 w-3 flex-shrink-0" />
        case "negative":
          return <TrendingDown className="h-3 w-3 flex-shrink-0" />
        case "neutral":
          return <Minus className="h-3 w-3 flex-shrink-0" />
        default:
          return null
      }
    }

    return (
      <span
        ref={ref}
        className={cn(
          percentageChangeVariants({ variant, trend, size }),
          animate && "transition-all duration-300 ease-in-out",
          className
        )}
        {...props}
      >
        {getIcon()}
        <span className="tabular-nums">
          {formatValue(value)}
        </span>
      </span>
    )
  }
)
PercentageChange.displayName = "PercentageChange"

// Convenience components for specific use cases
export const PercentageGain = React.forwardRef<
  HTMLSpanElement,
  Omit<PercentageChangeProps, "trend"> & { value: number }
>(({ value, ...props }, ref) => (
  <PercentageChange
    ref={ref}
    value={Math.abs(value)}
    trend="positive"
    {...props}
  />
))
PercentageGain.displayName = "PercentageGain"

export const PercentageLoss = React.forwardRef<
  HTMLSpanElement,
  Omit<PercentageChangeProps, "trend"> & { value: number }
>(({ value, ...props }, ref) => (
  <PercentageChange
    ref={ref}
    value={Math.abs(value)}
    trend="negative"
    {...props}
  />
))
PercentageLoss.displayName = "PercentageLoss"

export const PercentageBadge = React.forwardRef<
  HTMLSpanElement,
  Omit<PercentageChangeProps, "variant">
>(({ ...props }, ref) => (
  <PercentageChange
    ref={ref}
    variant="badge"
    {...props}
  />
))
PercentageBadge.displayName = "PercentageBadge"

// Hook for animating percentage changes
export const useAnimatedPercentage = (
  targetValue: number,
  duration: number = 1000
) => {
  const [currentValue, setCurrentValue] = React.useState(0)
  
  React.useEffect(() => {
    const startTime = Date.now()
    const startValue = currentValue
    const difference = targetValue - startValue
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3)
      const newValue = startValue + (difference * easeOutCubic)
      
      setCurrentValue(newValue)
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    
    requestAnimationFrame(animate)
  }, [targetValue, duration, currentValue])
  
  return currentValue
}

export { PercentageChange, percentageChangeVariants }