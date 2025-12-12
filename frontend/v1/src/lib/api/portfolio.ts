// API Client Layer
// This is the ONLY way frontend should access backend data

/**
 * Portfolio API Client
 * 
 * All portfolio-related API calls go through this client.
 * Never duplicate these calls or calculations in components.
 */

export interface PortfolioSummary {
  total_value: number;
  total_cost_basis: number;
  total_unrealized_gain_loss: number;
  total_unrealized_gain_loss_pct: number;
  holdings: Holding[];
  num_holdings: number;
  last_updated: string;
}

export interface Holding {
  symbol: string;
  name: string;
  type: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_pct: number;
  weight_pct: number;
}

/**
 * Fetch portfolio summary
 * 
 * Returns complete portfolio metrics calculated by backend.
 * DO NOT recalculate any of these values in the frontend.
 */
export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const response = await fetch('/api/portfolio/summary', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio summary: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch portfolio holdings
 * 
 * Returns list of current positions.
 */
export async function getHoldings(): Promise<Holding[]> {
  const response = await fetch('/api/portfolio/holdings', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch holdings: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Example: Using the API client in a component
 * 
 * ✅ CORRECT:
 * ```tsx
 * import { getPortfolioSummary } from '@/lib/api/portfolio';
 * 
 * function Portfolio() {
 *   const [data, setData] = useState<PortfolioSummary | null>(null);
 *   
 *   useEffect(() => {
 *     getPortfolioSummary().then(setData);
 *   }, []);
 *   
 *   return (
 *     <div>
 *       <h1>Portfolio Value: ${data?.total_value.toLocaleString()}</h1>
 *       <p>Return: {data?.total_unrealized_gain_loss_pct.toFixed(2)}%</p>
 *     </div>
 *   );
 * }
 * ```
 * 
 * ❌ INCORRECT:
 * ```tsx
 * function Portfolio() {
 *   const [holdings, setHoldings] = useState([]);
 *   
 *   // DON'T DO THIS - calculation belongs in backend
 *   const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
 *   const costBasis = holdings.reduce((sum, h) => sum + h.cost_basis, 0);
 *   const portfolioReturn = (totalValue - costBasis) / costBasis * 100; // ❌
 *   
 *   return <p>Return: {portfolioReturn.toFixed(2)}%</p>;
 * }
 * ```
 */
