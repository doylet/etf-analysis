import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { CheckCircle, AlertCircle, XCircle, Clock, Zap, TrendingUp, TrendingDown, Minus } from "lucide-react"

const statusIndicatorVariants = cva(
  "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        success: "bg-financial-positive-subtle text-financial-positive border border-financial-positive-light",
        warning: "bg-warning-subtle text-warning border border-warning-light", 
        danger: "bg-financial-negative-subtle text-financial-negative border border-financial-negative-light",
        info: "bg-scheme-primary-subtle text-scheme-primary border border-scheme-primary-light",
        neutral: "bg-theme-subtle text-theme-primary border border-theme-soft",
        processing: "bg-scheme-primary-subtle text-scheme-primary border border-scheme-primary-light animate-pulse",
        positive: "bg-financial-positive-subtle text-financial-positive border border-financial-positive-light",
        negative: "bg-financial-negative-subtle text-financial-negative border border-financial-negative-light",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        default: "px-3 py-1 text-xs",
        lg: "px-4 py-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "neutral",
      size: "default",
    },
  }
)

const statusIcons = {
  success: CheckCircle,
  warning: AlertCircle,
  danger: XCircle,
  info: AlertCircle,
  neutral: Minus,
  processing: Clock,
  positive: TrendingUp,
  negative: TrendingDown,
}

export interface StatusIndicatorProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof statusIndicatorVariants> {
  icon?: React.ComponentType<{ className?: string }> | false
  pulse?: boolean
}

const StatusIndicator = React.forwardRef<HTMLSpanElement, StatusIndicatorProps>(
  ({ className, variant = "neutral", size, icon, pulse, children, ...props }, ref) => {
    const IconComponent = icon === false ? null : icon || statusIcons[variant as keyof typeof statusIcons]
    
    return (
      <span
        ref={ref}
        className={cn(
          statusIndicatorVariants({ variant, size }),
          pulse && "animate-pulse",
          className
        )}
        role="status"
        aria-live="polite"
        {...props}
      >
        {IconComponent && (
          <IconComponent className="h-3 w-3 flex-shrink-0" aria-hidden="true" />
        )}
        {children && (
          <span className="tabular-nums">{children}</span>
        )}
      </span>
    )
  }
)
StatusIndicator.displayName = "StatusIndicator"

// Convenience components for common financial status patterns
export const PositionStatus = React.forwardRef<
  HTMLSpanElement,
  Omit<StatusIndicatorProps, "variant"> & {
    value: number
    showIcon?: boolean
  }
>(({ value, showIcon = true, children, ...props }, ref) => {
  const variant = value > 0 ? "positive" : value < 0 ? "negative" : "neutral"
  
  return (
    <StatusIndicator
      ref={ref}
      variant={variant}
      icon={showIcon ? undefined : false}
      {...props}
    >
      {children}
    </StatusIndicator>
  )
})
PositionStatus.displayName = "PositionStatus"

export const MarketStatus = React.forwardRef<
  HTMLSpanElement,
  Omit<StatusIndicatorProps, "variant"> & {
    status: "open" | "closed" | "pre-market" | "after-hours" | "weekend"
  }
>(({ status, children, ...props }, ref) => {
  const variantMap = {
    open: "success" as const,
    "pre-market": "warning" as const,
    "after-hours": "warning" as const,
    closed: "neutral" as const,
    weekend: "neutral" as const,
  }
  
  const iconMap = {
    open: Zap,
    "pre-market": Clock,
    "after-hours": Clock,
    closed: Minus,
    weekend: Minus,
  }
  
  return (
    <StatusIndicator
      ref={ref}
      variant={variantMap[status]}
      icon={iconMap[status]}
      {...props}
    >
      {children || status.charAt(0).toUpperCase() + status.slice(1)}
    </StatusIndicator>
  )
})
MarketStatus.displayName = "MarketStatus"

export const DataStatus = React.forwardRef<
  HTMLSpanElement,
  Omit<StatusIndicatorProps, "variant"> & {
    status: "live" | "delayed" | "stale" | "error" | "loading"
  }
>(({ status, children, ...props }, ref) => {
  const variantMap = {
    live: "success" as const,
    delayed: "warning" as const,
    stale: "neutral" as const,
    error: "danger" as const,
    loading: "processing" as const,
  }
  
  return (
    <StatusIndicator
      ref={ref}
      variant={variantMap[status]}
      pulse={status === "loading"}
      {...props}
    >
      {children || status.charAt(0).toUpperCase() + status.slice(1)}
    </StatusIndicator>
  )
})
DataStatus.displayName = "DataStatus"

export { StatusIndicator, statusIndicatorVariants }