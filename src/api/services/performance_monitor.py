"""Performance monitoring and metrics collection for widget API endpoints."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import time
import logging
from contextlib import contextmanager
from collections import defaultdict, deque
import threading
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance level classifications for widgets."""
    
    FAST = "fast"           # < 1 second
    MODERATE = "moderate"   # 1-5 seconds  
    SLOW = "slow"          # 5-30 seconds
    VERY_SLOW = "very_slow" # > 30 seconds


@dataclass
class PerformanceMetric:
    """Individual performance measurement."""
    
    widget_name: str
    execution_time: float
    timestamp: datetime
    parameters: Dict[str, Any]
    success: bool
    error_type: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cache_hit: bool = False
    
    @property
    def performance_level(self) -> PerformanceLevel:
        """Classify performance level based on execution time."""
        if self.execution_time < 1.0:
            return PerformanceLevel.FAST
        elif self.execution_time < 5.0:
            return PerformanceLevel.MODERATE
        elif self.execution_time < 30.0:
            return PerformanceLevel.SLOW
        else:
            return PerformanceLevel.VERY_SLOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['performance_level'] = self.performance_level.value
        return result


class WidgetPerformanceMonitor:
    """Centralized performance monitoring for all widget operations."""
    
    def __init__(self, max_metrics: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self._metrics: deque = deque(maxlen=max_metrics)
        self._widget_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_calls': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'recent_calls': deque(maxlen=100)
        })
        self._lock = threading.Lock()
        
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric."""
        with self._lock:
            self._metrics.append(metric)
            
            # Update widget statistics
            stats = self._widget_stats[metric.widget_name]
            stats['total_calls'] += 1
            stats['total_time'] += metric.execution_time
            stats['recent_calls'].append(metric.execution_time)
            
            if metric.success:
                stats['success_count'] += 1
            else:
                stats['error_count'] += 1
                
            stats['avg_time'] = stats['total_time'] / stats['total_calls']
            stats['min_time'] = min(stats['min_time'], metric.execution_time)
            stats['max_time'] = max(stats['max_time'], metric.execution_time)
            
    def get_widget_stats(self, widget_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific widget."""
        with self._lock:
            stats = self._widget_stats.get(widget_name, {})
            if not stats:
                return {}
                
            # Calculate additional metrics
            recent_calls = list(stats['recent_calls'])
            current_stats = stats.copy()
            
            if recent_calls:
                current_stats['recent_avg'] = sum(recent_calls) / len(recent_calls)
                current_stats['recent_min'] = min(recent_calls)
                current_stats['recent_max'] = max(recent_calls)
            
            current_stats['success_rate'] = (
                stats['success_count'] / stats['total_calls'] 
                if stats['total_calls'] > 0 else 0
            )
            
            # Remove the deque for JSON serialization
            current_stats.pop('recent_calls', None)
            
            return current_stats
    
    def get_all_widget_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all widgets."""
        return {
            widget_name: self.get_widget_stats(widget_name)
            for widget_name in self._widget_stats.keys()
        }
    
    def get_recent_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent performance metrics."""
        with self._lock:
            recent = list(self._metrics)[-limit:]
            return [metric.to_dict() for metric in recent]
    
    def get_slow_operations(self, threshold: float = 5.0, hours: int = 24) -> List[Dict[str, Any]]:
        """Get operations that exceeded performance threshold."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            slow_ops = [
                metric.to_dict() 
                for metric in self._metrics
                if (metric.execution_time > threshold and 
                    metric.timestamp > cutoff_time)
            ]
            
        return sorted(slow_ops, key=lambda x: x['execution_time'], reverse=True)
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of errors in the specified time window.""" 
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        error_counts = defaultdict(int)
        total_errors = 0
        
        with self._lock:
            for metric in self._metrics:
                if metric.timestamp > cutoff_time and not metric.success:
                    total_errors += 1
                    error_key = f"{metric.widget_name}:{metric.error_type or 'unknown'}"
                    error_counts[error_key] += 1
        
        return {
            'total_errors': total_errors,
            'error_breakdown': dict(error_counts),
            'time_window_hours': hours
        }
    
    def clear_metrics(self):
        """Clear all stored metrics and statistics."""
        with self._lock:
            self._metrics.clear()
            self._widget_stats.clear()


# Global performance monitor instance
performance_monitor = WidgetPerformanceMonitor()


@contextmanager
def monitor_widget_performance(
    widget_name: str, 
    parameters: Dict[str, Any] = None,
    track_memory: bool = False
):
    """
    Context manager for monitoring widget performance.
    
    Args:
        widget_name: Name of the widget being monitored
        parameters: Widget execution parameters
        track_memory: Whether to track memory usage (requires psutil)
    
    Usage:
        with monitor_widget_performance('portfolio_summary', {'portfolio_id': '123'}):
            result = execute_widget()
    """
    start_time = time.time()
    start_memory = None
    error_type = None
    success = True
    
    if track_memory:
        try:
            import psutil
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
    
    try:
        yield
    except Exception as e:
        success = False
        error_type = type(e).__name__
        raise
    finally:
        execution_time = time.time() - start_time
        memory_usage = None
        
        if track_memory and start_memory is not None:
            try:
                import psutil
                process = psutil.Process()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage = end_memory - start_memory
            except ImportError:
                pass
        
        metric = PerformanceMetric(
            widget_name=widget_name,
            execution_time=execution_time,
            timestamp=datetime.now(),
            parameters=parameters or {},
            success=success,
            error_type=error_type,
            memory_usage_mb=memory_usage
        )
        
        performance_monitor.record_metric(metric)
        
        # Log slow operations
        if execution_time > 10.0:
            logger.warning(
                f"Slow widget operation: {widget_name} took {execution_time:.2f}s"
            )


class PerformanceAlert:
    """Alert system for performance issues."""
    
    @staticmethod
    def check_performance_alerts() -> List[Dict[str, Any]]:
        """Check for performance issues and return alerts."""
        alerts = []
        
        # Check for consistently slow widgets
        stats = performance_monitor.get_all_widget_stats()
        for widget_name, widget_stats in stats.items():
            if widget_stats.get('avg_time', 0) > 10.0:
                alerts.append({
                    'type': 'slow_widget',
                    'widget': widget_name,
                    'avg_time': widget_stats['avg_time'],
                    'message': f'Widget {widget_name} averaging {widget_stats["avg_time"]:.2f}s'
                })
        
        # Check for high error rates
        for widget_name, widget_stats in stats.items():
            error_rate = 1.0 - widget_stats.get('success_rate', 1.0)
            if error_rate > 0.1:  # More than 10% errors
                alerts.append({
                    'type': 'high_error_rate',
                    'widget': widget_name,
                    'error_rate': error_rate,
                    'message': f'Widget {widget_name} has {error_rate*100:.1f}% error rate'
                })
        
        return alerts


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary for monitoring dashboard."""
    return {
        'widget_stats': performance_monitor.get_all_widget_stats(),
        'recent_metrics': performance_monitor.get_recent_metrics(20),
        'slow_operations': performance_monitor.get_slow_operations(5.0, 1),
        'error_summary': performance_monitor.get_error_summary(1),
        'alerts': PerformanceAlert.check_performance_alerts(),
        'timestamp': datetime.now().isoformat()
    }