import React from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  children,
  className = ''
}) => {
  return (
    <div className={`mb-6 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            {title}
          </h1>
          {description && (
            <p className="mt-1 text-sm text-gray-500 sm:text-base">
              {description}
            </p>
          )}
        </div>
        {children && (
          <div className="mt-4 sm:mt-0 sm:ml-4 flex-shrink-0">
            {children}
          </div>
        )}
      </div>
    </div>
  );
};