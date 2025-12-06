import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string;
  height?: string;
  variant?: 'rectangular' | 'circle';
}

export function Skeleton({ className, width, height, variant = 'rectangular', ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-gray-200',
        {
          'rounded': variant === 'rectangular',
          'rounded-full': variant === 'circle',
        },
        className
      )}
      style={{
        width: width || '100%',
        height: height || '1rem',
      }}
      {...props}
    />
  );
}