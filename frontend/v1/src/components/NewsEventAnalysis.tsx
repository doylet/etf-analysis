'use client';

import { Newspaper, TrendingUp, TrendingDown, AlertCircle, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface NewsEventAnalysisProps {
  portfolioId?: string;
  timePeriod?: string;
}

interface NewsData {
  market_sentiment: {
    overall: 'positive' | 'negative' | 'neutral';
    score: number;
    confidence: number;
  };
  portfolio_impact: {
    estimated_impact: number;
    risk_level: 'low' | 'medium' | 'high';
    affected_holdings: string[];
  };
  recent_news: Array<{
    id: string;
    title: string;
    source: string;
    published: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    relevance_score: number;
    summary: string;
    affected_symbols: string[];
    url?: string;
  }>;
  events: Array<{
    type: 'earnings' | 'fed' | 'geopolitical' | 'economic';
    title: string;
    date: string;
    impact_level: 'low' | 'medium' | 'high';
    description: string;
  }>;
  alerts: Array<{
    level: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
  }>;
}

export default function NewsEventAnalysis({ 
  portfolioId, 
  timePeriod = '7D'
}: NewsEventAnalysisProps) {
  // Mock data for now - replace with actual API call
  const loading = false;
  const error = null;
  const data: NewsData = {
    market_sentiment: {
      overall: 'positive',
      score: 0.65,
      confidence: 0.78
    },
    portfolio_impact: {
      estimated_impact: 2.3,
      risk_level: 'medium',
      affected_holdings: ['AAPL', 'MSFT', 'GOOGL']
    },
    recent_news: [
      {
        id: '1',
        title: 'Fed Signals Potential Rate Cut in Q2',
        source: 'Reuters',
        published: '2024-01-15T10:30:00Z',
        sentiment: 'positive',
        relevance_score: 0.85,
        summary: 'Federal Reserve officials suggest possibility of interest rate reductions if inflation continues to moderate.',
        affected_symbols: ['SPY', 'QQQ'],
        url: 'https://example.com'
      },
      {
        id: '2',
        title: 'Apple Reports Record Q1 Earnings',
        source: 'Bloomberg',
        published: '2024-01-14T16:45:00Z',
        sentiment: 'positive',
        relevance_score: 0.92,
        summary: 'Apple exceeded expectations with strong iPhone sales and services revenue growth.',
        affected_symbols: ['AAPL'],
        url: 'https://example.com'
      },
      {
        id: '3',
        title: 'Tech Sector Volatility Expected',
        source: 'CNBC',
        published: '2024-01-13T14:20:00Z',
        sentiment: 'negative',
        relevance_score: 0.71,
        summary: 'Analysts warn of increased volatility in tech stocks due to regulatory concerns.',
        affected_symbols: ['MSFT', 'GOOGL', 'NVDA'],
        url: 'https://example.com'
      }
    ],
    events: [
      {
        type: 'earnings',
        title: 'Q1 Earnings Season Begins',
        date: '2024-01-16',
        impact_level: 'high',
        description: 'Major tech companies begin reporting quarterly earnings'
      },
      {
        type: 'fed',
        title: 'FOMC Meeting Minutes Release',
        date: '2024-01-18',
        impact_level: 'medium',
        description: 'Federal Reserve meeting minutes provide policy insights'
      },
      {
        type: 'economic',
        title: 'CPI Data Release',
        date: '2024-01-20',
        impact_level: 'high',
        description: 'Consumer Price Index data for December'
      }
    ],
    alerts: [
      {
        level: 'warning',
        message: 'High volatility expected in AAPL due to earnings announcement',
        timestamp: '2024-01-15T09:00:00Z'
      },
      {
        level: 'info',
        message: 'Fed meeting minutes may impact interest-sensitive holdings',
        timestamp: '2024-01-15T08:30:00Z'
      }
    ]
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            <Skeleton className="h-6 w-[200px]" />
          </div>
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-[150px]" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <Newspaper className="h-4 w-4" />
        <AlertTitle>News Analysis Error</AlertTitle>
        <AlertDescription>
          Unable to load news and event analysis data. Please check your configuration.
        </AlertDescription>
      </Alert>
    );
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-financial-positive';
      case 'negative': return 'text-financial-negative';
      default: return 'text-text-tertiary';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <TrendingUp className="h-4 w-4 text-financial-positive" />;
      case 'negative': return <TrendingDown className="h-4 w-4 text-financial-negative" />;
      default: return <div className="h-4 w-4" />;
    }
  };

  const getImpactColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-50 border-red-200 text-red-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default: return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Newspaper className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">News & Event Analysis</h2>
            </div>
            <p className="text-text-secondary text-sm">
              Market sentiment and portfolio impact analysis • {timePeriod}
            </p>
          </div>
          <Button variant="outline" size="sm">
            <ExternalLink className="h-4 w-4 mr-2" />
            View All News
          </Button>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Market Sentiment Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700">Market Sentiment</div>
              <div className={`text-2xl font-bold capitalize ${getSentimentColor(data.market_sentiment.overall)}`}>
                {data.market_sentiment.overall}
              </div>
              <div className="text-sm text-blue-600">
                Score: {(data.market_sentiment.score * 100).toFixed(0)}%
              </div>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Portfolio Impact</div>
              <div className={`text-2xl font-bold ${data.portfolio_impact.estimated_impact >= 0 ? 'text-financial-positive' : 'text-financial-negative'}`}>
                {data.portfolio_impact.estimated_impact > 0 ? '+' : ''}{data.portfolio_impact.estimated_impact.toFixed(1)}%
              </div>
              <Badge className={getImpactColor(data.portfolio_impact.risk_level)} variant="secondary">
                {data.portfolio_impact.risk_level.charAt(0).toUpperCase() + data.portfolio_impact.risk_level.slice(1)} Risk
              </Badge>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="text-sm text-text-tertiary">Affected Holdings</div>
              <div className="text-lg font-semibold text-text-primary">
                {data.portfolio_impact.affected_holdings.length} positions
              </div>
              <div className="flex gap-1 mt-1 flex-wrap">
                {data.portfolio_impact.affected_holdings.slice(0, 3).map(symbol => (
                  <Badge key={symbol} variant="outline" className="text-xs">
                    {symbol}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Active Alerts */}
          {data.alerts.length > 0 && (
            <div>
              <h3 className="font-medium text-text-primary mb-3">Active Alerts</h3>
              <div className="space-y-2">
                {data.alerts.map((alert, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${getAlertColor(alert.level)}`}>
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      <span className="font-medium">{alert.message}</span>
                    </div>
                    <div className="text-xs mt-1 opacity-75">
                      {formatTime(alert.timestamp)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent News */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Recent News</h3>
            <div className="space-y-3">
              {data.recent_news.map((article) => (
                <div key={article.id} className="p-4 border border-border rounded-lg hover:bg-background-secondary transition-colors">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getSentimentIcon(article.sentiment)}
                        <span className="font-medium text-text-primary">{article.title}</span>
                        <Badge variant="outline" className="text-xs">
                          {(article.relevance_score * 100).toFixed(0)}% relevant
                        </Badge>
                      </div>
                      <p className="text-sm text-text-secondary mb-2">
                        {article.summary}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-text-tertiary">
                        <span>{article.source}</span>
                        <span>{formatTime(article.published)}</span>
                        <div className="flex gap-1">
                          {article.affected_symbols.map(symbol => (
                            <Badge key={symbol} variant="secondary" className="text-xs">
                              {symbol}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    {article.url && (
                      <Button variant="ghost" size="sm" asChild>
                        <a href={article.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Events */}
          <div>
            <h3 className="font-medium text-text-primary mb-3">Upcoming Events</h3>
            <div className="space-y-2">
              {data.events.map((event, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className="capitalize">
                      {event.type}
                    </Badge>
                    <div>
                      <div className="font-medium text-text-primary">{event.title}</div>
                      <div className="text-sm text-text-tertiary">{event.description}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-text-primary">
                      {formatTime(event.date)}
                    </div>
                    <Badge className={getImpactColor(event.impact_level)} variant="secondary">
                      {event.impact_level} impact
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Analysis Summary */}
          <div className="p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg border">
            <h3 className="font-medium text-text-primary mb-2">Analysis Summary</h3>
            <div className="space-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Market Sentiment:</span> {data.market_sentiment.overall} with {(data.market_sentiment.confidence * 100).toFixed(0)}% confidence
              </div>
              <div>
                <span className="font-medium">Portfolio Risk:</span> {data.portfolio_impact.risk_level} risk level with {data.portfolio_impact.affected_holdings.length} positions potentially affected
              </div>
              <div>
                <span className="font-medium">Key Focus:</span> Monitor earnings announcements and Fed communications for market direction
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}