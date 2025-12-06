import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import portfolioAPI, { PortfolioSummaryResponse } from '../api/portfolio';
import '../styles/PortfolioSummary.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D'];

export default function PortfolioSummary() {
  const [data, setData] = useState<PortfolioSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    try {
      setLoading(true);
      const portfolioData = await portfolioAPI.getPortfolioSummary();
      setData(portfolioData);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load portfolio data');
      console.error('Portfolio load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="portfolio-container">
        <div className="loading-spinner">Loading portfolio data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-container">
        <div className="error-box">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={loadPortfolioData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="portfolio-container">
        <p>No portfolio data available</p>
      </div>
    );
  }

  // Prepare data for pie chart
  const chartData = data.holdings.map(holding => ({
    name: holding.symbol,
    value: holding.current_value,
    percentage: holding.weight_pct
  }));

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="portfolio-container">
      <h1>Portfolio Summary</h1>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Value</div>
          <div className="metric-value">{formatCurrency(data.total_value)}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Total Cost</div>
          <div className="metric-value">{formatCurrency(data.total_cost_basis)}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Total Gain/Loss</div>
          <div className={`metric-value ${data.total_unrealized_gain_loss >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(data.total_unrealized_gain_loss)}
          </div>
          <div className={`metric-subvalue ${data.total_unrealized_gain_loss_pct >= 0 ? 'positive' : 'negative'}`}>
            {formatPercent(data.total_unrealized_gain_loss_pct)}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Holdings Count</div>
          <div className="metric-value">{data.num_holdings}</div>
        </div>
      </div>

      {/* Holdings Breakdown */}
      <div className="holdings-section">
        <h2>Holdings Breakdown</h2>
        
        <div className="holdings-content">
          {/* Pie Chart */}
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} (${percentage.toFixed(1)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Holdings Table */}
          <div className="table-container">
            <table className="holdings-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Quantity</th>
                  <th>Avg Cost</th>
                  <th>Current Price</th>
                  <th>Value</th>
                  <th>Gain/Loss</th>
                  <th>Weight</th>
                </tr>
              </thead>
              <tbody>
                {data.holdings.map((holding) => (
                  <tr key={holding.symbol}>
                    <td className="symbol-cell">
                      <div className="symbol-name">{holding.symbol}</div>
                      <div className="instrument-name">{holding.name}</div>
                    </td>
                    <td>{holding.quantity.toFixed(4)}</td>
                    <td>{formatCurrency(holding.average_cost)}</td>
                    <td>{formatCurrency(holding.current_price)}</td>
                    <td>{formatCurrency(holding.current_value)}</td>
                    <td className={holding.unrealized_gain_loss >= 0 ? 'positive' : 'negative'}>
                      {formatCurrency(holding.unrealized_gain_loss)}
                      <div className="gain-pct">
                        {formatPercent(holding.unrealized_gain_loss_pct)}
                      </div>
                    </td>
                    <td>{holding.weight_pct.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="last-updated">
        Last updated: {new Date(data.last_updated).toLocaleString()}
      </div>
    </div>
  );
}
