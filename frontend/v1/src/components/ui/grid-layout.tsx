import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const gridLayoutVariants = cva(
  "grid gap-6",
  {
    variants: {
      columns: {
        1: "grid-cols-1",
        2: "grid-cols-1 md:grid-cols-2",
        3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
        auto: "grid-cols-[repeat(auto-fit,minmax(300px,1fr))]",
        "auto-sm": "grid-cols-[repeat(auto-fit,minmax(240px,1fr))]",
        "auto-lg": "grid-cols-[repeat(auto-fit,minmax(400px,1fr))]",
      },
      gap: {
        xs: "gap-2",
        sm: "gap-4",
        default: "gap-6",
        lg: "gap-8",
        xl: "gap-12",
      },
      align: {
        start: "items-start",
        center: "items-center",
        end: "items-end",
        stretch: "items-stretch",
      },
    },
    defaultVariants: {
      columns: "auto",
      gap: "default",
      align: "stretch",
    },
  }
)

export interface GridLayoutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof gridLayoutVariants> {
  as?: React.ElementType
}

const GridLayout = React.forwardRef<HTMLDivElement, GridLayoutProps>(
  ({ className, columns, gap, align, as: Component = "div", ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn(gridLayoutVariants({ columns, gap, align, className }))}
        {...props}
      />
    )
  }
)
GridLayout.displayName = "GridLayout"

// Specialized layout components for common dashboard patterns
export interface DashboardLayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  sidebar?: React.ReactNode
  header?: React.ReactNode
  footer?: React.ReactNode
}

const DashboardLayout = React.forwardRef<HTMLDivElement, DashboardLayoutProps>(
  ({ className, sidebar, header, footer, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("min-h-screen bg-background-primary", className)}
        {...props}
      >
        {header && (
          <header className="bg-background-primary border-b border-theme-soft sticky top-0 z-10">
            {header}
          </header>
        )}
        
        <div className="flex flex-1">
          {sidebar && (
            <aside className="hidden lg:block w-64 bg-card border-r border-border">
              <div className="sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
                {sidebar}
              </div>
            </aside>
          )}
          
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
        
        {footer && (
          <footer className="bg-card border-t border-border mt-auto">
            {footer}
          </footer>
        )}
      </div>
    )
  }
)
DashboardLayout.displayName = "DashboardLayout"

// Metric grid for financial dashboards
export interface MetricGridProps extends React.HTMLAttributes<HTMLDivElement> {
  metrics?: number
}

const MetricGrid = React.forwardRef<HTMLDivElement, MetricGridProps>(
  ({ className, metrics = 4, children, ...props }, ref) => {
    const getColumns = (count: number) => {
      if (count <= 2) return "2"
      if (count <= 3) return "3" 
      return "4"
    }
    
    return (
      <GridLayout
        ref={ref}
        columns={getColumns(metrics) as GridLayoutProps['columns']}
        className={cn("mb-6", className)}
        {...props}
      >
        {children}
      </GridLayout>
    )
  }
)
MetricGrid.displayName = "MetricGrid"

// Content areas for different types of financial data
const ContentGrid = React.forwardRef<HTMLDivElement, GridLayoutProps>(
  ({ className, ...props }, ref) => (
    <GridLayout
      ref={ref}
      columns="auto-lg"
      gap="lg"
      className={cn("mt-8", className)}
      {...props}
    />
  )
)
ContentGrid.displayName = "ContentGrid"

// Chart grid for data visualization sections
const ChartGrid = React.forwardRef<HTMLDivElement, GridLayoutProps>(
  ({ className, columns = 2, ...props }, ref) => (
    <GridLayout
      ref={ref}
      columns={columns}
      gap="lg"
      className={cn("mt-6", className)}
      {...props}
    />
  )
)
ChartGrid.displayName = "ChartGrid"

// Professional section wrapper
export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  title?: string
  subtitle?: string
  action?: React.ReactNode
  as?: React.ElementType
}

const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ className, title, subtitle, action, as: Component = "section", children, ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn("space-y-6", className)}
        {...props}
      >
        {(title || subtitle || action) && (
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              {title && (
                <h2 className="text-2xl font-semibold tracking-tight text-gray-900">
                  {title}
                </h2>
              )}
              {subtitle && (
                <p className="text-sm text-gray-600">
                  {subtitle}
                </p>
              )}
            </div>
            {action && <div>{action}</div>}
          </div>
        )}
        {children}
      </Component>
    )
  }
)
Section.displayName = "Section"

export { 
  GridLayout, 
  DashboardLayout, 
  MetricGrid, 
  ContentGrid, 
  ChartGrid, 
  Section,
  gridLayoutVariants 
}