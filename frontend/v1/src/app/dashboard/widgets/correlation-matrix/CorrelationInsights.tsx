'use client';

import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { WidgetInsight } from '@/components/ui/widget-insight';

interface CorrelationInsightsProps {
  maxCorrelation: number;
  avgCorrelation: number;
  symbolCount: number;
}

export function CorrelationInsights({
  maxCorrelation,
  avgCorrelation,
  symbolCount,
}: CorrelationInsightsProps) {
  const insights: Array<{ 
    title: string; 
    description: string; 
    icon: typeof TrendingUp; 
    variant: 'default' | 'destructive' 
  }> = [];

  if (maxCorrelation > 0.9) {
    insights.push({
      title: 'Critical Correlation Risk',
      description: `Extremely high correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Assets are moving almost identically, indicating severe concentration risk. Immediate diversification recommended.`,
      icon: AlertTriangle,
      variant: 'destructive'
    });
  } else if (maxCorrelation > 0.8) {
    insights.push({
      title: 'High Correlation Alert',
      description: `Strong correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Some assets show high correlation, which may indicate concentrated risk. Consider diversification across ${symbolCount} holdings.`,
      icon: TrendingUp,
      variant: 'default'
    });
  } else if (maxCorrelation > 0.6) {
    insights.push({
      title: 'Moderate Correlation',
      description: `Moderate correlation detected (${(maxCorrelation * 100).toFixed(1)}%). Portfolio shows reasonable but not excessive correlation. Monitor for increased concentration.`,
      icon: TrendingUp,
      variant: 'default'
    });
  }

  if (avgCorrelation < 0.3 && symbolCount > 5) {
    insights.push({
      title: 'Well Diversified Portfolio',
      description: `Average correlation of ${(avgCorrelation * 100).toFixed(1)}% indicates good diversification across ${symbolCount} assets. Holdings are moving relatively independently.`,
      icon: CheckCircle,
      variant: 'default'
    });
  }

  return (
    <>
      {insights.map((insight, index) => (
        <WidgetInsight
          key={index}
          title={insight.title}
          description={insight.description}
          icon={insight.icon}
          variant={insight.variant}
        />
      ))}
    </>
  );
}
