/**
 * Formatting Utilities
 * Centralized formatting functions for consistent display across widgets
 */

/**
 * Format a number as currency
 * @param amount - The amount to format
 * @param options - Additional Intl.NumberFormatOptions
 * @returns Formatted currency string
 */
export const formatCurrency = (
  amount: number | undefined | null,
  options?: Intl.NumberFormatOptions
): string => {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    ...options,
  }).format(amount);
};

/**
 * Format a number as percentage
 * @param value - The value to format (e.g., 0.15 for 15%)
 * @param decimals - Number of decimal places
 * @returns Formatted percentage string
 */
export const formatPercent = (
  value: number | undefined | null,
  decimals: number = 2
): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format a date string
 * @param dateString - ISO date string or Date object
 * @param format - 'short' or 'long' format
 * @returns Formatted date string
 */
export const formatDate = (
  dateString: string | Date,
  format: 'short' | 'long' = 'short'
): string => {
  if (!dateString) return 'N/A';
  try {
    const options: Intl.DateTimeFormatOptions = format === 'short'
      ? { year: 'numeric', month: 'short', day: 'numeric' }
      : { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    return date.toLocaleDateString('en-US', options);
  } catch {
    return 'Invalid Date';
  }
};

/**
 * Format a number with locale-specific formatting
 * @param value - The number to format
 * @param options - Additional Intl.NumberFormatOptions
 * @returns Formatted number string
 */
export const formatNumber = (
  value: number | undefined | null,
  options?: Intl.NumberFormatOptions
): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0';
  }
  return new Intl.NumberFormat('en-US', options).format(value);
};

/**
 * Format a number with compact notation (e.g., 1.2K, 3.4M)
 * @param value - The number to format
 * @returns Formatted compact string
 */
export const formatCompact = (
  value: number | undefined | null
): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0';
  }
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(value);
};

/**
 * Format basis points (e.g., 0.0025 -> 25 bps)
 * @param value - The value in decimal format
 * @returns Formatted basis points string
 */
export const formatBasisPoints = (
  value: number | undefined | null
): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0 bps';
  }
  return `${(value * 10000).toFixed(0)} bps`;
};
