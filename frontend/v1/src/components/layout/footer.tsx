import React from 'react';

interface FooterProps {
  appName?: string;
  phase?: string;
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({
  appName = 'ETF Analysis Dashboard - NextJS Frontend',
  phase = 'Phase 8: Modern Frontend Foundation',
  className = ''
}) => {
  return (
    <footer className={`bg-white border-t mt-12 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center">
          <p className="text-sm text-gray-500">
            {appName}
          </p>
          <p className="text-sm text-gray-400 mt-2 sm:mt-0">
            {phase}
          </p>
        </div>
      </div>
    </footer>
  );
};