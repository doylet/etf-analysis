/**
 * MetricCard Component
 * Professional Data-Focused Design System for ETF Analysis
 * 
 * Standardized metric display component optimized for financial data
 */

import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import type { MetricCardProps } from '@/lib/design-tokens';

const metricCardVariants = cva(
  'group relative rounded-lg border bg-card text-card-foreground shadow-sm transition-all duration-300 ease-out hover:scale-[1.02] hover:-translate-y-[2px] cursor-default max-w-[16.666667%] min-w-[200px] mb-3',
  {
    variants: {
      variant: {
        default: 'border-border hover:shadow-md hover:border-primary/30 hover:bg-gradient-to-br hover:from-card hover:to-primary/5',
        highlighted: 'border-border-focus bg-background-accent hover:shadow-lg hover:border-primary/50 hover:shadow-primary/10',
        subtle: 'border-border bg-muted hover:shadow-sm hover:border-border hover:bg-card',
      },
      size: {
        sm: 'p-2',
        base: 'p-3',
        lg: 'p-4',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'base',
    },
  }
);

const metricValueVariants = cva(
  'font-financial transition-all duration-300 ease-out',
  {
    variants: {
      trend: {
        positive: 'text-financial-positive group-hover:text-financial-positive-hover',
        negative: 'text-financial-negative group-hover:text-financial-negative-hover',
        neutral: 'text-financial-neutral group-hover:text-theme-primary',
      },
      size: {
        sm: 'text-financial-lg font-semibold',
        base: 'text-financial-xl font-bold',
        lg: 'text-financial-2xl font-bold',
      },
    },
    defaultVariants: {
      trend: 'neutral',
      size: 'base',
    },
  }
);

const metricTitleVariants = cva(
  'font-medium transition-all duration-300 ease-out group-hover:text-foreground',
  {
    variants: {
      size: {
        sm: 'text-xs text-text-secondary',
        base: 'text-sm text-text-secondary',
        lg: 'text-base text-text-secondary',
      },
    },
    defaultVariants: {
      size: 'base',
    },
  }
);

const metricChangeVariants = cva(
  'flex items-center gap-1 font-tabular text-sm transition-all duration-300 ease-out',
  {
    variants: {
      trend: {
        positive: 'text-financial-positive group-hover:text-financial-positive-hover group-hover:font-semibold',
        negative: 'text-financial-negative group-hover:text-financial-negative-hover group-hover:font-semibold',
        neutral: 'text-financial-neutral group-hover:text-theme-primary group-hover:font-semibold',
      },
    },
    defaultVariants: {
      trend: 'neutral',
    },
  }
);

const MetricCard = React.forwardRef<HTMLDivElement, MetricCardProps>(
  ({ 
    title, 
    value, 
    subtitle,
    icon: Icon,
    change, 
    trend, 
    size = 'base', 
    variant = 'default', 
    loading = false, 
    className, 
    ...props 
  }, ref) => {
    // Determine trend from change value if not explicitly provided
    const effectiveTrend = React.useMemo(() => {
      if (trend) return trend;
      if (change && typeof change.value === 'number') {
        if (change.value > 0) return 'positive';
        if (change.value < 0) return 'negative';
      }
      return 'neutral';
    }, [trend, change]);

    // Format the change value
    const formatChange = React.useCallback((changeValue: number | undefined, type: 'percentage' | 'absolute') => {
      if (typeof changeValue !== 'number' || isNaN(changeValue)) {
        return '--';
      }
      
      const sign = changeValue >= 0 ? '+' : '';
      if (type === 'percentage') {
        return `${sign}${changeValue.toFixed(2)}%`;
      }
      return `${sign}${changeValue.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    }, []);

    if (loading) {
      return (
        <div
          ref={ref}
          className={cn(metricCardVariants({ variant, size }), 'animate-pulse', className)}
          {...props}
        >
          <div className="space-y-3">
            <div className="h-4 bg-muted rounded w-3/4" />
            <div className="h-8 bg-muted rounded w-1/2" />
            {change && <div className="h-4 bg-muted rounded w-1/3" />}
          </div>
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(metricCardVariants({ variant, size }), className)}
        {...props}
      >
        <div className="space-y-2">
          {/* Title */}
          <div className="flex items-center justify-between">
            <h3 className={cn(metricTitleVariants({ size }))}>
              {title}
            </h3>
            {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
          </div>
          
          {/* Subtitle */}
          {subtitle && (
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          )}
          
          {/* Value */}
          <div className={cn(metricValueVariants({ trend: effectiveTrend, size }))}>
            {typeof value === 'number' ? 
              value.toLocaleString('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }) 
              : value
            }
          </div>
          
          {/* Change indicator */}
          {change && change.type && (
            <div className={cn(metricChangeVariants({ trend: effectiveTrend }))}>
              <span className="font-tabular">
                {formatChange(change.value, change.type)}
              </span>
              <span className="text-xs opacity-75">
                {change.type === 'percentage' ? 'vs prev' : 'change'}
              </span>
            </div>
          )}
        </div>
        
        {/* Loading overlay */}
        {loading && (
          <div className="absolute inset-0 bg-background/50 backdrop-blur-sm rounded-lg flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-border border-t-primary" />
          </div>
        )}
      </div>
    );
  }
);

MetricCard.displayName = 'MetricCard';

export { MetricCard, metricCardVariants };
export type { MetricCardProps };