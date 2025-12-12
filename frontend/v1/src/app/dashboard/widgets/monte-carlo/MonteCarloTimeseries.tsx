/**
 * MonteCarloTimeseries - Dual-axis SVG chart for portfolio path projections
 * Shows median path, confidence bands, and drawdown analysis over time
 */

export interface TimeseriesDataPoint {
  days: number;
  years: number;
  percentile_10: number;
  percentile_50: number;
  percentile_90: number;
  median_drawdown: number;
}

interface MonteCarloTimeseriesProps {
  data: TimeseriesDataPoint[] | null;
  initialValue: number;
}

export function MonteCarloTimeseries({ data, initialValue }: MonteCarloTimeseriesProps) {
  if (!data || data.length === 0) {
    return (
      <div className="p-4 border border-blue-200 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
          Path Projections Unavailable
        </h3>
        <p className="text-xs text-blue-700 dark:text-blue-300">
          The timeseries visualization requires path statistics from the backend. Run a new simulation to generate this data.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Portfolio Path Projections</h3>
      <div className="relative h-80">
        <svg viewBox="0 0 800 300" className="w-full h-full text-muted-foreground">
          <defs>
            <linearGradient id="confidenceBand" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" className="[stop-color:hsl(var(--chart-1))]" stopOpacity="0.2" />
              <stop offset="100%" className="[stop-color:hsl(var(--chart-1))]" stopOpacity="0.05" />
            </linearGradient>
          </defs>
          
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line 
              key={`grid-${i}`}
              x1="60" 
              y1={50 + i * 50} 
              x2="740" 
              y2={50 + i * 50}
              stroke="currentColor"
              strokeOpacity="0.1"
              strokeDasharray="2,2"
            />
          ))}
          
          {/* Confidence band (10th to 90th percentile) */}
          <path
            d={data.map((d, i) => {
              const x = 60 + (i / (data.length - 1)) * 680;
              const yMax = initialValue > 0 ? 250 - ((d.percentile_90 / initialValue - 1) * 200) : 150;
              return `${i === 0 ? 'M' : 'L'} ${x} ${Math.max(50, Math.min(250, yMax))}`;
            }).join(' ') + ' ' + data.slice().reverse().map((d, i) => {
              const x = 740 - (i / (data.length - 1)) * 680;
              const yMin = initialValue > 0 ? 250 - ((d.percentile_10 / initialValue - 1) * 200) : 150;
              return `L ${x} ${Math.max(50, Math.min(250, yMin))}`;
            }).join(' ') + ' Z'}
            fill="url(#confidenceBand)"
          />
          
          {/* Median line (left axis - portfolio value) */}
          <path
            d={data.map((d, i) => {
              const x = 60 + (i / (data.length - 1)) * 680;
              const y = initialValue > 0 ? 250 - ((d.percentile_50 / initialValue - 1) * 200) : 150;
              return `${i === 0 ? 'M' : 'L'} ${x} ${Math.max(50, Math.min(250, y))}`;
            }).join(' ')}
            fill="none"
            className="stroke-chart-1"
            strokeWidth="2"
          />
          
          {/* Median drawdown line (right axis - inverted) */}
          <path
            d={data.map((d, i) => {
              const x = 60 + (i / (data.length - 1)) * 680;
              const y = 50 + Math.abs(d.median_drawdown) * 4; // Scale: 50% drawdown = 200px
              return `${i === 0 ? 'M' : 'L'} ${x} ${Math.min(250, y)}`;
            }).join(' ')}
            fill="none"
            className="stroke-financial-negative"
            strokeWidth="1.5"
            strokeDasharray="4,2"
          />
          
          {/* Y-axis labels (left - returns) */}
          <text x="5" y="55" fontSize="10" fill="currentColor" opacity="0.6">+100%</text>
          <text x="15" y="155" fontSize="10" fill="currentColor" opacity="0.6">0%</text>
          <text x="5" y="255" fontSize="10" fill="currentColor" opacity="0.6">-50%</text>
          
          {/* Y-axis labels (right - drawdown) */}
          <text x="750" y="55" fontSize="10" className="fill-financial-negative" opacity="0.8">0%</text>
          <text x="745" y="155" fontSize="10" className="fill-financial-negative" opacity="0.8">-25%</text>
          <text x="745" y="255" fontSize="10" className="fill-financial-negative" opacity="0.8">-50%</text>
          
          {/* X-axis labels (time in years) */}
          {[0, 0.25, 0.5, 0.75, 1].map(fraction => {
            const x = 60 + fraction * 680;
            const years = (data[Math.floor(fraction * (data.length - 1))]?.years || 0).toFixed(1);
            return (
              <text key={fraction} x={x} y="275" fontSize="10" fill="currentColor" opacity="0.6" textAnchor="middle">
                {years}y
              </text>
            );
          })}
          
          {/* Axis labels */}
          <text x="400" y="295" fontSize="11" fill="currentColor" opacity="0.7" textAnchor="middle">Time (Years)</text>
          <text x="30" y="20" fontSize="11" className="fill-chart-1" opacity="0.9" textAnchor="middle">Returns</text>
          <text x="770" y="20" fontSize="11" className="fill-financial-negative" opacity="0.9" textAnchor="middle">Drawdown</text>
        </svg>
        
        <div className="mt-2 flex items-center justify-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-chart-1 rounded"></div>
            <span className="text-muted-foreground">Median Path</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-chart-1/20 border border-chart-1/40 rounded"></div>
            <span className="text-muted-foreground">10th-90th Percentile</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-6 h-0.5 bg-financial-negative" style={{borderTop: '1.5px dashed'}}></div>
            <span className="text-muted-foreground">Median Drawdown</span>
          </div>
        </div>
      </div>
    </div>
  );
}
