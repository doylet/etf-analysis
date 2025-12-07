import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const metricGroupVariants = cva(
  "space-y-4",
  {
    variants: {
      variant: {
        default: "",
        card: "p-6 rounded-lg border border-border-primary bg-background-primary shadow-sm",
        section: "p-4 border-l-4 border-scheme-primary bg-scheme-primary-subtle",
        grid: "",
      },
      layout: {
        vertical: "space-y-4",
        horizontal: "flex flex-wrap gap-4",
        grid: "grid gap-4",
      },
    },
    defaultVariants: {
      variant: "default",
      layout: "vertical",
    },
  }
)

const metricGroupGridVariants = cva(
  "",
  {
    variants: {
      columns: {
        2: "grid-cols-1 md:grid-cols-2",
        3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3", 
        4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
        auto: "grid-cols-[repeat(auto-fit,minmax(200px,1fr))]",
      },
    },
    defaultVariants: {
      columns: "auto",
    },
  }
)

export interface MetricGroupProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof metricGroupVariants> {
  title?: string
  subtitle?: string
  action?: React.ReactNode
  columns?: 2 | 3 | 4 | "auto"
}

const MetricGroup = React.forwardRef<HTMLDivElement, MetricGroupProps>(
  ({ className, variant, layout, columns, title, subtitle, action, children, ...props }, ref) => {
    const isGridLayout = layout === "grid" || columns
    const gridColumns = columns && isGridLayout ? columns : undefined

    return (
      <div
        ref={ref}
        className={cn(
          metricGroupVariants({ variant, layout: isGridLayout ? "grid" : layout }),
          isGridLayout && metricGroupGridVariants({ columns: gridColumns }),
          className
        )}
        {...props}
      >
        {(title || subtitle || action) && (
          <div className="flex items-start justify-between mb-4">
            <div className="space-y-1">
              {title && (
                <h3 className="text-lg font-semibold text-foreground">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-sm text-muted-foreground">
                  {subtitle}
                </p>
              )}
            </div>
            {action && <div>{action}</div>}
          </div>
        )}
        {children}
      </div>
    )
  }
)
MetricGroup.displayName = "MetricGroup"

// Specialized metric group components for common financial patterns
export const PortfolioMetrics = React.forwardRef<
  HTMLDivElement,
  Omit<MetricGroupProps, "variant" | "title">
>(({ className, ...props }, ref) => (
  <MetricGroup
    ref={ref}
    variant="card"
    title="Portfolio Metrics"
    subtitle="Key performance indicators"
    className={cn("bg-gradient-to-br from-blue-50 to-indigo-50", className)}
    {...props}
  />
))
PortfolioMetrics.displayName = "PortfolioMetrics"

export const RiskMetrics = React.forwardRef<
  HTMLDivElement,
  Omit<MetricGroupProps, "variant" | "title">
>(({ className, ...props }, ref) => (
  <MetricGroup
    ref={ref}
    variant="section"
    title="Risk Analysis"
    subtitle="Portfolio risk metrics and indicators"
    className={cn("border-l-amber-500 bg-amber-50/30", className)}
    {...props}
  />
))
RiskMetrics.displayName = "RiskMetrics"

export const PerformanceMetrics = React.forwardRef<
  HTMLDivElement,
  Omit<MetricGroupProps, "variant" | "title">
>(({ className, ...props }, ref) => (
  <MetricGroup
    ref={ref}
    variant="card"
    title="Performance"
    subtitle="Returns and growth metrics"
    className={cn("bg-gradient-to-br from-green-50 to-emerald-50", className)}
    {...props}
  />
))
PerformanceMetrics.displayName = "PerformanceMetrics"

export const CompactMetrics = React.forwardRef<
  HTMLDivElement,
  Omit<MetricGroupProps, "layout" | "variant">
>(({ className, ...props }, ref) => (
  <MetricGroup
    ref={ref}
    layout="horizontal"
    variant="default"
    className={cn("items-center", className)}
    {...props}
  />
))
CompactMetrics.displayName = "CompactMetrics"

// Hook for organizing metrics into groups
export const useMetricGroups = <T extends Record<string, unknown>>(
  metrics: T[], 
  groupBy: keyof T
) => {
  return React.useMemo(() => {
    const groups = metrics.reduce((acc, metric) => {
      const key = String(metric[groupBy])
      if (!acc[key]) {
        acc[key] = []
      }
      acc[key].push(metric)
      return acc
    }, {} as Record<string, T[]>)
    
    return Object.entries(groups).map(([key, items]) => ({
      group: key,
      metrics: items,
    }))
  }, [metrics, groupBy])
}

// Context for metric groups to share common styling and behavior
interface MetricGroupContextValue {
  variant?: "default" | "card" | "section" | "grid"
  size?: "sm" | "default" | "lg"
}

const MetricGroupContext = React.createContext<MetricGroupContextValue>({})

export const MetricGroupProvider: React.FC<{
  children: React.ReactNode
  value: MetricGroupContextValue
}> = ({ children, value }) => (
  <MetricGroupContext.Provider value={value}>
    {children}
  </MetricGroupContext.Provider>
)

export const useMetricGroupContext = () => {
  return React.useContext(MetricGroupContext)
}

export { 
  MetricGroup, 
  metricGroupVariants, 
  metricGroupGridVariants 
}