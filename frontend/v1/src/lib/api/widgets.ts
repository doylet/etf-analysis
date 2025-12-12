// Widget API Client

/**
 * Widget API Client
 * 
 * All widget data fetching goes through this client.
 * Widgets return pre-calculated metrics from backend.
 */

export interface PerformanceMetrics {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  holdings_analyzed: number;
  period_days: number;
}

export interface WidgetResponse<T> {
  widget_name: string;
  success: boolean;
  data: T | null;
  metadata: {
    execution_time: string;
    parameters: Record<string, any>;
    widget_description: string;
  };
  error: any | null;
}

/**
 * Fetch performance widget data
 * 
 * @param timePeriod - Time period for analysis (1W, 1M, 3M, 6M, 1Y, 2Y, 5Y)
 * @returns Performance metrics calculated by backend
 */
export async function getPerformanceWidget(
  timePeriod: string = '1Y'
): Promise<WidgetResponse<PerformanceMetrics>> {
  const response = await fetch(
    `/api/widgets/performance?time_period=${timePeriod}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch performance widget: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch portfolio summary widget data
 */
export async function getPortfolioSummaryWidget(): Promise<WidgetResponse<any>> {
  const response = await fetch('/api/widgets/portfolio-summary', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio summary widget: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch holdings breakdown widget data
 */
export async function getHoldingsBreakdownWidget(
  breakdownType: 'sector' | 'geography' | 'asset_class' | 'all' = 'sector'
): Promise<WidgetResponse<any>> {
  const response = await fetch(
    `/api/widgets/holdings-breakdown?breakdown_type=${breakdownType}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch holdings breakdown: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Example: Using widget API in a component
 * 
 * ✅ CORRECT:
 * ```tsx
 * import { getPerformanceWidget } from '@/lib/api/widgets';
 * 
 * function PerformanceWidget() {
 *   const [data, setData] = useState<PerformanceMetrics | null>(null);
 *   const [period, setPeriod] = useState('1Y');
 *   
 *   useEffect(() => {
 *     getPerformanceWidget(period).then(response => {
 *       if (response.success) {
 *         setData(response.data);
 *       }
 *     });
 *   }, [period]);
 *   
 *   return (
 *     <div>
 *       <select onChange={(e) => setPeriod(e.target.value)}>
 *         <option value="1Y">1 Year</option>
 *         <option value="3M">3 Months</option>
 *       </select>
 *       <p>Total Return: {data?.total_return.toFixed(2)}%</p>
 *       <p>Sharpe Ratio: {data?.sharpe_ratio.toFixed(2)}</p>
 *     </div>
 *   );
 * }
 * ```
 * 
 * ❌ INCORRECT - Don't recalculate metrics:
 * ```tsx
 * function PerformanceWidget() {
 *   const [prices, setPrices] = useState([]);
 *   
 *   // DON'T DO THIS - let backend calculate
 *   const returns = prices.map((p, i) => 
 *     i > 0 ? (p - prices[i-1]) / prices[i-1] : 0
 *   );
 *   const avgReturn = returns.reduce((a, b) => a + b) / returns.length; // ❌
 *   
 *   return <p>Average Return: {avgReturn}%</p>;
 * }
 * ```
 */
