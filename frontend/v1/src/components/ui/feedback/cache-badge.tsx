import React from 'react';
import { Badge } from '@/components/ui/badge';

interface CacheBadgeProps {
  show?: boolean;
}

export function CacheBadge({ show = true }: CacheBadgeProps) {
  if (!show) return null;
  
  return (
    <Badge variant="secondary" className="text-xs">
      Cached
    </Badge>
  );
}
