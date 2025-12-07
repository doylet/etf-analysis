import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Loader2, TrendingUp } from "lucide-react"

// Loading Spinner Component
const spinnerVariants = cva(
  "animate-spin",
  {
    variants: {
      size: {
        sm: "h-4 w-4",
        default: "h-6 w-6",
        lg: "h-8 w-8",
        xl: "h-12 w-12",
      },
      variant: {
        default: "text-theme-primary",
        primary: "text-scheme-primary",
        success: "text-financial-positive",
        warning: "text-warning",
        danger: "text-financial-negative",
      }
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

export interface LoadingSpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  label?: string
  icon?: React.ReactNode
}

const LoadingSpinner = React.forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  ({ className, size, variant, label, icon, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("flex items-center justify-center", className)}
        {...props}
      >
        <div className="flex flex-col items-center gap-2">
          {icon || <Loader2 className={cn(spinnerVariants({ size, variant }))} />}
          {label && (
            <span className="text-sm text-muted-foreground animate-pulse">{label}</span>
          )}
        </div>
      </div>
    )
  }
)
LoadingSpinner.displayName = "LoadingSpinner"

// Loading Card Skeleton
export interface LoadingCardProps {
  rows?: number
  showHeader?: boolean
  showFooter?: boolean
  className?: string
}

const LoadingCard = React.forwardRef<HTMLDivElement, LoadingCardProps>(
  ({ rows = 3, showHeader = true, showFooter = false, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "p-6 bg-card rounded-lg border border-border shadow-sm animate-pulse",
          className
        )}
      >
        {showHeader && (
          <div className="mb-4">
            <div className="h-5 bg-theme-subtle rounded w-1/3 mb-2"></div>
            <div className="h-3 bg-background-secondary rounded w-1/2"></div>
          </div>
        )}
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-4 bg-theme-subtle rounded flex-1"></div>
              <div className="h-4 bg-background-secondary rounded w-20"></div>
            </div>
          ))}
        </div>
        {showFooter && (
          <div className="mt-4 flex justify-between">
            <div className="h-4 bg-muted rounded w-16"></div>
            <div className="h-8 bg-muted-foreground/20 rounded w-20"></div>
          </div>
        )}
      </div>
    )
  }
)
LoadingCard.displayName = "LoadingCard"

// Loading Table Skeleton
export interface LoadingTableProps {
  rows?: number
  columns?: number
  showHeader?: boolean
  className?: string
}

const LoadingTable = React.forwardRef<HTMLDivElement, LoadingTableProps>(
  ({ rows = 5, columns = 4, showHeader = true, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("w-full animate-pulse", className)}
      >
        {showHeader && (
          <div className="grid gap-4 pb-4 border-b border-border mb-4"
               style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, i) => (
              <div key={i} className="h-4 bg-muted rounded"></div>
            ))}
          </div>
        )}
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <div
              key={rowIndex}
              className="grid gap-4"
              style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
            >
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div
                  key={colIndex}
                  className={cn(
                    "h-4 rounded",
                    colIndex === 0 ? "bg-muted" : "bg-muted/60"
                  )}
                ></div>
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }
)
LoadingTable.displayName = "LoadingTable"

// Financial Data Loading States
export const FinancialDataLoader = React.forwardRef<HTMLDivElement, { className?: string }>(
  ({ className }, ref) => (
    <div ref={ref} className={cn("p-6", className)}>
      <LoadingSpinner
        size="lg"
        variant="primary"
        label="Loading portfolio data..."
        icon={<TrendingUp className="h-8 w-8 animate-pulse text-blue-600" />}
      />
    </div>
  )
)
FinancialDataLoader.displayName = "FinancialDataLoader"

// Metric Card Loading State
export const LoadingMetricCard = React.forwardRef<HTMLDivElement, { className?: string }>(
  ({ className }, ref) => (
    <div
      ref={ref}
      className={cn(
        "p-4 bg-card rounded-lg border border-border shadow-sm animate-pulse",
        className
      )}
    >
      <div className="space-y-3">
        <div className="h-3 bg-muted rounded w-1/2"></div>
        <div className="h-8 bg-muted/60 rounded w-3/4"></div>
        <div className="flex items-center space-x-2">
          <div className="h-3 bg-muted rounded w-8"></div>
          <div className="h-3 bg-accent/60 rounded w-12"></div>
        </div>
      </div>
    </div>
  )
)
LoadingMetricCard.displayName = "LoadingMetricCard"

// Chart Loading State
export const LoadingChart = React.forwardRef<HTMLDivElement, { className?: string }>(
  ({ className }, ref) => (
    <div
      ref={ref}
      className={cn(
        "p-6 bg-card rounded-lg border border-border shadow-sm",
        className
      )}
    >
      <div className="animate-pulse">
        <div className="h-5 bg-muted rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-gradient-to-t from-muted/40 to-muted/20 rounded relative overflow-hidden">
          <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-primary/20 rounded-t"></div>
          <div className="absolute top-1/2 left-1/4 w-1/2 h-1/4 bg-accent/40 rounded"></div>
        </div>
      </div>
    </div>
  )
)
LoadingChart.displayName = "LoadingChart"

export { 
  LoadingSpinner, 
  LoadingCard, 
  LoadingTable, 
  spinnerVariants 
}