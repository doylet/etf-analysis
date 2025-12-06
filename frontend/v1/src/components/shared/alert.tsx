import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  title?: string;
  children: React.ReactNode;
}

export function Alert({ className, variant = 'default', size = 'md', title, children, ...props }: AlertProps) {
  const Icon = {
    default: Info,
    success: CheckCircle,
    warning: AlertTriangle,
    error: XCircle,
  }[variant];

  return (
    <div
      className={cn(
        'relative w-full rounded-lg border',
        {
          'bg-blue-50 border-blue-200 text-blue-900': variant === 'default',
          'bg-green-50 border-green-200 text-green-900': variant === 'success',
          'bg-yellow-50 border-yellow-200 text-yellow-900': variant === 'warning',
          'bg-red-50 border-red-200 text-red-900': variant === 'error',
          'p-3': size === 'sm',
          'p-4': size === 'md',
          'p-6': size === 'lg',
        },
        className
      )}
      {...props}
    >
      <div className="flex items-start space-x-3">
        <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          {title && (
            <h3 className="font-medium mb-1">{title}</h3>
          )}
          <div className="text-sm">{children}</div>
        </div>
      </div>
    </div>
  );
}