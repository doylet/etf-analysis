import React from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { LucideIcon } from 'lucide-react';

interface WidgetInsightProps {
  title: string;
  description: string;
  icon: LucideIcon;
  variant?: 'default' | 'destructive';
}

export function WidgetInsight({ 
  title, 
  description, 
  icon: Icon,
  variant = 'default' 
}: WidgetInsightProps) {
  return (
    <Alert variant={variant}>
      <Icon className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
}
