/**
 * FinancialAmount Component
 * Professional Data-Focused Design System for ETF Analysis
 * 
 * Specialized component for displaying financial amounts with proper formatting
 */

import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import type { FinancialAmountProps } from '@/lib/design-tokens';

const financialAmountVariants = cva(
  'font-financial inline-flex items-baseline transition-colors duration-200',
  {
    variants: {
      variant: {
        default: 'text-text-primary',
        positive: 'text-financial-positive',
        negative: 'text-financial-negative',
        neutral: 'text-financial-neutral',
      },
      size: {
        xs: 'text-financial-xs',
        sm: 'text-financial-sm',
        base: 'text-financial-base',
        lg: 'text-financial-lg',
        xl: 'text-financial-xl',
        '2xl': 'text-financial-2xl',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'base',
    },
  }
);

const currencySymbolVariants = cva(
  'font-medium',
  {
    variants: {
      size: {
        xs: 'text-xs',
        sm: 'text-sm',
        base: 'text-base',
        lg: 'text-lg',
        xl: 'text-xl',
        '2xl': 'text-2xl',
      },
    },
    defaultVariants: {
      size: 'base',
    },
  }
);

const FinancialAmount = React.forwardRef<HTMLSpanElement, FinancialAmountProps>(
  ({
    amount,
    currency = 'USD',
    precision = 2,
    suffix = '',
    showTrend = false,
    size = 'base',
    variant: variantProp,
    showSign = false,
    showCurrency = true,
    className,
    ...props
  }, ref) => {
    // Auto-determine variant based on amount if not explicitly provided
    const variant = React.useMemo(() => {
      if (variantProp) return variantProp;
      if (showTrend) {
        if (amount > 0) return 'positive';
        if (amount < 0) return 'negative';
      }
      return 'default';
    }, [amount, variantProp, showTrend]);

    // Format the currency amount
    const formatAmount = React.useCallback(() => {
      const absAmount = Math.abs(amount);
      const sign = amount >= 0 ? (showSign ? '+' : '') : '-';
      
      // Format the number with proper locale and precision
      let formatted: string;
      
      if (currency === null || currency === undefined) {
        // No currency formatting, just number
        formatted = absAmount.toLocaleString('en-US', {
          minimumFractionDigits: precision,
          maximumFractionDigits: precision,
        });
      } else {
        // With currency formatting
        formatted = absAmount.toLocaleString('en-US', {
          minimumFractionDigits: precision,
          maximumFractionDigits: precision,
        });
      }

      return { sign, formatted: formatted + suffix };
    }, [amount, precision, showSign, currency, suffix]);

    // Get currency symbol
    const getCurrencySymbol = React.useCallback(() => {
      if (currency === null || currency === undefined) return '';
      const symbols: Record<string, string> = {
        USD: '$',
        EUR: '€',
        GBP: '£',
        JPY: '¥',
        CAD: 'C$',
        AUD: 'A$',
      };
      return symbols[currency] || currency;
    }, [currency]);

    const { sign, formatted } = formatAmount();
    const currencySymbol = (showCurrency && currency) ? getCurrencySymbol() : '';

    // Handle size mapping for compatibility
    const mappedSize = size === 'md' ? 'base' : size;

    return (
      <span
        ref={ref}
        className={cn(financialAmountVariants({ variant, size: mappedSize }), className)}
        title={`${sign}${currencySymbol}${formatted}`}
        {...props}
      >
        {/* Sign */}
        {sign && (
          <span className="mr-0.5" aria-hidden="true">
            {sign}
          </span>
        )}
        
        {/* Currency Symbol */}
        {showCurrency && currencySymbol && (
          <span 
            className={cn(currencySymbolVariants({ size: mappedSize }), 'mr-0.5')}
            aria-hidden="true"
          >
            {currencySymbol}
          </span>
        )}
        
        {/* Amount */}
        <span className="tabular-nums">
          {formatted}
        </span>
        
        {/* Screen reader friendly version */}
        <span className="sr-only">
          {amount >= 0 ? '' : 'negative '}
          {formatted} {currency}
        </span>
      </span>
    );
  }
);

FinancialAmount.displayName = 'FinancialAmount';

// Convenience components for common use cases
const FinancialAmountPositive = React.forwardRef<HTMLSpanElement, Omit<FinancialAmountProps, 'variant'>>(
  (props, ref) => (
    <FinancialAmount ref={ref} variant="positive" {...props} />
  )
);
FinancialAmountPositive.displayName = 'FinancialAmountPositive';

const FinancialAmountNegative = React.forwardRef<HTMLSpanElement, Omit<FinancialAmountProps, 'variant'>>(
  (props, ref) => (
    <FinancialAmount ref={ref} variant="negative" {...props} />
  )
);
FinancialAmountNegative.displayName = 'FinancialAmountNegative';

const FinancialAmountNeutral = React.forwardRef<HTMLSpanElement, Omit<FinancialAmountProps, 'variant'>>(
  (props, ref) => (
    <FinancialAmount ref={ref} variant="neutral" {...props} />
  )
);
FinancialAmountNeutral.displayName = 'FinancialAmountNeutral';

// Utility function for formatting without component
export const formatFinancialAmount = (
  amount: number,
  options: {
    currency?: string;
    precision?: number;
    showSign?: boolean;
    showCurrency?: boolean;
  } = {}
): string => {
  const {
    currency = 'USD',
    precision = 2,
    showSign = false,
    showCurrency = true,
  } = options;

  const absAmount = Math.abs(amount);
  const sign = amount >= 0 ? (showSign ? '+' : '') : '-';
  
  const formatted = absAmount.toLocaleString('en-US', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });

  const symbols: Record<string, string> = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    CAD: 'C$',
    AUD: 'A$',
  };
  
  const currencySymbol = showCurrency ? (symbols[currency] || currency) : '';

  return `${sign}${currencySymbol}${formatted}`;
};

export {
  FinancialAmount,
  FinancialAmountPositive,
  FinancialAmountNegative,
  FinancialAmountNeutral,
  financialAmountVariants,
};

export type { FinancialAmountProps };