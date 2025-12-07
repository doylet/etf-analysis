import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { 
  AlertCircle, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  TrendingDown,
  Wifi,
  WifiOff,
  Database,
  Clock
} from "lucide-react"

// Error State Variants
const errorStateVariants = cva(
  "flex flex-col items-center justify-center text-center p-6",
  {
    variants: {
      variant: {
        default: "text-muted-foreground",
        danger: "text-financial-negative",
        warning: "text-amber-600",
        info: "text-blue-600",
      },
      size: {
        sm: "p-4 space-y-2",
        default: "p-6 space-y-4",
        lg: "p-8 space-y-6",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ErrorStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof errorStateVariants> {
  title: string
  description?: string
  icon?: React.ReactNode
  action?: {
    label: string
    onClick: () => void
    loading?: boolean
  }
  showRetry?: boolean
  onRetry?: () => void
  retryLoading?: boolean
}

const ErrorState = React.forwardRef<HTMLDivElement, ErrorStateProps>(
  ({ 
    className, 
    variant, 
    size, 
    title, 
    description, 
    icon, 
    action,
    showRetry = false,
    onRetry,
    retryLoading = false,
    ...props 
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(errorStateVariants({ variant, size }), className)}
        {...props}
      >
        {icon && (
          <div className="mb-4">
            {icon}
          </div>
        )}
        
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-foreground">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-muted-foreground max-w-md">
              {description}
            </p>
          )}
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mt-4">
          {showRetry && onRetry && (
            <Button
              onClick={onRetry}
              disabled={retryLoading}
              variant="outline"
              size="sm"
            >
              {retryLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Try Again
            </Button>
          )}
          
          {action && (
            <Button
              onClick={action.onClick}
              disabled={action.loading}
              size="sm"
            >
              {action.loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                action.label
              )}
            </Button>
          )}
        </div>
      </div>
    )
  }
)
ErrorState.displayName = "ErrorState"

// Specialized Error Components

// Network Error
export const NetworkError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant"> & { offline?: boolean }
>(({ offline = false, className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title={offline ? "You're Offline" : "Connection Error"}
    description={
      offline 
        ? "Please check your internet connection and try again."
        : "Unable to connect to our servers. Please try again in a moment."
    }
    icon={offline ? <WifiOff className="h-12 w-12" /> : <Wifi className="h-12 w-12" />}
    variant="warning"
    className={className}
    showRetry
    {...props}
  />
))
NetworkError.displayName = "NetworkError"

// Data Error (Financial specific)
export const DataError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant">
>(({ className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title="Data Unavailable"
    description="Portfolio data is temporarily unavailable. Market data providers may be experiencing issues."
    icon={<TrendingDown className="h-12 w-12" />}
    variant="danger"
    className={className}
    showRetry
    {...props}
  />
))
DataError.displayName = "DataError"

// Server Error
export const ServerError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant">
>(({ className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title="Server Error"
    description="Our servers are experiencing technical difficulties. We're working to resolve this issue."
    icon={<Database className="h-12 w-12" />}
    variant="danger" 
    className={className}
    showRetry
    {...props}
  />
))
ServerError.displayName = "ServerError"

// Timeout Error
export const TimeoutError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant">
>(({ className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title="Request Timeout"
    description="The request took too long to complete. This might be due to poor network connectivity."
    icon={<Clock className="h-12 w-12" />}
    variant="warning"
    className={className}
    showRetry
    {...props}
  />
))
TimeoutError.displayName = "TimeoutError"

// Permission Error
export const PermissionError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant">
>(({ className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title="Access Denied"
    description="You don't have permission to view this data. Please contact your administrator."
    icon={<XCircle className="h-12 w-12" />}
    variant="danger"
    className={className}
    {...props}
  />
))
PermissionError.displayName = "PermissionError"

// Market Closed Error
export const MarketClosedError = React.forwardRef<
  HTMLDivElement,
  Omit<ErrorStateProps, "title" | "icon" | "variant">
>(({ className, ...props }, ref) => (
  <ErrorState
    ref={ref}
    title="Market Closed"
    description="Live market data is not available outside trading hours. Showing last available data."
    icon={<Clock className="h-12 w-12" />}
    variant="info"
    className={className}
    {...props}
  />
))
MarketClosedError.displayName = "MarketClosedError"

// Empty State Component
export interface EmptyStateProps extends Omit<ErrorStateProps, "variant"> {
  showCreateAction?: boolean
  createLabel?: string
  onCreate?: () => void
}

export const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ 
    className,
    showCreateAction = false,
    createLabel = "Get Started",
    onCreate,
    ...props 
  }, ref) => (
    <ErrorState
      ref={ref}
      variant="default"
      className={className}
      action={showCreateAction && onCreate ? {
        label: createLabel,
        onClick: onCreate
      } : undefined}
      {...props}
    />
  )
)
EmptyState.displayName = "EmptyState"

// Specialized Empty States

// Empty Portfolio
export const EmptyPortfolio = React.forwardRef<HTMLDivElement, { onAddHolding?: () => void }>(
  ({ onAddHolding }, ref) => (
    <EmptyState
      ref={ref}
      title="No Holdings"
      description="Your portfolio is empty. Add your first holding to start tracking your investments."
      icon={<TrendingDown className="h-12 w-12 text-muted-foreground" />}
      showCreateAction
      createLabel="Add Holding"
      onCreate={onAddHolding}
    />
  )
)
EmptyPortfolio.displayName = "EmptyPortfolio"

// No Search Results
export const NoSearchResults = React.forwardRef<
  HTMLDivElement, 
  { searchTerm?: string; onClearSearch?: () => void }
>(({ searchTerm, onClearSearch }, ref) => (
  <EmptyState
    ref={ref}
    title="No Results Found"
    description={
      searchTerm 
        ? `No results found for "${searchTerm}". Try adjusting your search criteria.`
        : "No results match your current filters."
    }
    icon={<AlertCircle className="h-12 w-12 text-muted-foreground" />}
    showCreateAction={!!onClearSearch}
    createLabel="Clear Search"
    onCreate={onClearSearch}
  />
))
NoSearchResults.displayName = "NoSearchResults"

// Error Boundary Component
export interface ErrorBoundaryFallbackProps {
  error: Error
  resetError: () => void
}

export const ErrorBoundaryFallback: React.FC<ErrorBoundaryFallbackProps> = ({ 
  error, 
  resetError 
}) => (
  <ErrorState
    title="Something went wrong"
    description={`An unexpected error occurred: ${error.message}`}
    icon={<AlertTriangle className="h-12 w-12" />}
    variant="danger"
    showRetry
    onRetry={resetError}
  />
)

// Hook for handling async errors
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null)
  const [isRetrying, setIsRetrying] = React.useState(false)

  const handleError = React.useCallback((error: Error) => {
    console.error('Error:', error)
    setError(error)
  }, [])

  const retry = React.useCallback(async (retryFn: () => Promise<void>) => {
    setIsRetrying(true)
    setError(null)
    try {
      await retryFn()
    } catch (error) {
      handleError(error as Error)
    } finally {
      setIsRetrying(false)
    }
  }, [handleError])

  const clearError = React.useCallback(() => {
    setError(null)
    setIsRetrying(false)
  }, [])

  return { error, isRetrying, handleError, retry, clearError }
}

export { 
  ErrorState, 
  errorStateVariants 
}