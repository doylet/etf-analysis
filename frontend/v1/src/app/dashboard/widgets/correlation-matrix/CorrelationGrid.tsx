'use client';

const getCorrelationColor = (value: number): string => {
  const absValue = Math.abs(value);
  if (absValue >= 0.8) return value > 0 ? 'bg-red-500' : 'bg-blue-500';
  if (absValue >= 0.6) return value > 0 ? 'bg-red-400' : 'bg-blue-400';
  if (absValue >= 0.4) return value > 0 ? 'bg-orange-400' : 'bg-cyan-400';
  if (absValue >= 0.2) return value > 0 ? 'bg-yellow-400' : 'bg-teal-400';
  return 'bg-gray-300';
};

const getCorrelationIntensity = (value: number): number => {
  return Math.abs(value);
};

interface CorrelationGridProps {
  symbols: string[];
  correlationData: Record<string, Record<string, number>>;
}

export function CorrelationGrid({ symbols, correlationData }: CorrelationGridProps) {
  return (
    <div>
      <h4 className="text-sm font-medium mb-2">Correlation Heatmap</h4>
      <div className="overflow-x-auto">
        <div className="min-w-max">
          {/* Header Row */}
          <div className="flex">
            <div className="w-16 h-12 flex items-center justify-center text-sm font-medium">
              {/* Empty corner cell */}
            </div>
            {symbols.map((symbol) => (
              <div
                key={symbol}
                className="w-16 h-12 flex items-center justify-center text-xs font-medium border-l border-border"
              >
                {symbol}
              </div>
            ))}
          </div>

          {/* Data Rows */}
          {symbols.map((rowSymbol) => (
            <div key={rowSymbol} className="flex border-t border-border">
              {/* Row Header */}
              <div className="w-16 h-12 flex items-center justify-center text-xs font-medium bg-muted">
                {rowSymbol}
              </div>
              
              {/* Correlation Cells */}
              {symbols.map((colSymbol) => {
                const correlationValue = correlationData[rowSymbol]?.[colSymbol] ?? 0;
                const isIdentity = rowSymbol === colSymbol;
                
                return (
                  <div
                    key={colSymbol}
                    className={`w-16 h-12 flex items-center justify-center text-xs font-mono border-l border-border relative group cursor-help
                      ${isIdentity ? 'bg-gray-100' : getCorrelationColor(correlationValue)}
                      ${isIdentity ? 'text-gray-800' : 'text-white'}
                    `}
                    style={{
                      opacity: isIdentity ? 0.5 : 0.7 + (getCorrelationIntensity(correlationValue) * 0.3)
                    }}
                    title={`${rowSymbol} vs ${colSymbol}: ${(correlationValue * 100).toFixed(1)}%`}
                  >
                    {isIdentity ? '1.0' : (correlationValue * 100).toFixed(0)}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-4 text-sm">
        <span className="text-text-tertiary">Correlation strength:</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-300 rounded"></div>
          <span className="text-text-secondary">Weak (0-20%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-400 rounded"></div>
          <span className="text-text-secondary">Moderate (20-60%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-400 rounded"></div>
          <span className="text-text-secondary">Strong (60%+)</span>
        </div>
      </div>
    </div>
  );
}
