import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_by_endpoint': {},
            'classification_accuracy': [],
            'response_times': [],
            'errors': [],
            'llm_calls': 0,
            'rag_searches': 0
        }
    
    def increment_request(self, endpoint: str):
        """Increment request counter"""
        self.metrics['requests_total'] += 1
        if endpoint not in self.metrics['requests_by_endpoint']:
            self.metrics['requests_by_endpoint'][endpoint] = 0
        self.metrics['requests_by_endpoint'][endpoint] += 1
    
    def record_response_time(self, endpoint: str, duration: float):
        """Record response time"""
        self.metrics['response_times'].append({
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_error(self, endpoint: str, error: str, status_code: int):
        """Record error"""
        self.metrics['errors'].append({
            'endpoint': endpoint,
            'error': error,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_classification_result(self, predicted: bool, actual: Optional[bool] = None):
        """Record classification result for accuracy tracking"""
        self.metrics['classification_accuracy'].append({
            'predicted': predicted,
            'actual': actual,
            'timestamp': datetime.now().isoformat()
        })
    
    def increment_llm_calls(self):
        """Increment LLM call counter"""
        self.metrics['llm_calls'] += 1
    
    def increment_rag_searches(self):
        """Increment RAG search counter"""
        self.metrics['rag_searches'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        response_times = [rt['duration'] for rt in self.metrics['response_times']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_requests': self.metrics['requests_total'],
            'requests_by_endpoint': self.metrics['requests_by_endpoint'],
            'average_response_time': round(avg_response_time, 3),
            'total_errors': len(self.metrics['errors']),
            'llm_calls': self.metrics['llm_calls'],
            'rag_searches': self.metrics['rag_searches'],
            'uptime': self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Get application uptime"""
        # This would be more sophisticated in production
        return "Running"

# Global metrics collector
metrics_collector = MetricsCollector()

def monitor_endpoint(endpoint_name: str):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Increment request counter
                metrics_collector.increment_request(endpoint_name)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Record response time
                duration = time.time() - start_time
                metrics_collector.record_response_time(endpoint_name, duration)
                
                logger.info(f"Endpoint {endpoint_name} completed in {duration:.3f}s")
                return result
                
            except Exception as e:
                # Record error
                duration = time.time() - start_time
                metrics_collector.record_error(endpoint_name, str(e), 500)
                logger.error(f"Endpoint {endpoint_name} failed after {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.performance_data = []
    
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Record operation performance"""
        self.performance_data.append({
            'operation': operation,
            'duration': duration,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.performance_data:
            return {}
        
        operations = {}
        for data in self.performance_data:
            op = data['operation']
            if op not in operations:
                operations[op] = {'count': 0, 'total_time': 0, 'success_count': 0}
            
            operations[op]['count'] += 1
            operations[op]['total_time'] += data['duration']
            if data['success']:
                operations[op]['success_count'] += 1
        
        # Calculate averages
        for op in operations:
            operations[op]['avg_time'] = operations[op]['total_time'] / operations[op]['count']
            operations[op]['success_rate'] = operations[op]['success_count'] / operations[op]['count']
        
        return operations

# Global performance monitor
performance_monitor = PerformanceMonitor()

def log_classification(title: str, description: str, result: Dict[str, Any], user: str):
    """Log classification result for audit trail"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'feature_title': title,
        'feature_description': description,
        'classification_result': result,
        'llm_used': 'openai' if os.getenv("OPENAI_API_KEY") else 'mock'
    }
    
    logger.info(f"Classification logged: {json.dumps(log_entry)}")
    
    # Record metrics
    metrics_collector.record_classification_result(result.get('needs_geo_logic', False))
    if os.getenv("OPENAI_API_KEY"):
        metrics_collector.increment_llm_calls()
    metrics_collector.increment_rag_searches()

def log_security_event(event_type: str, details: Dict[str, Any], user: Optional[str] = None):
    """Log security events"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'user': user,
        'details': details
    }
    
    logger.warning(f"Security event: {json.dumps(log_entry)}")

def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics_collector.get_summary(),
        'performance': performance_monitor.get_performance_summary(),
        'environment': {
            'openai_configured': bool(os.getenv("OPENAI_API_KEY")),
            'regulations_loaded': len(os.listdir('regulations')) if os.path.exists('regulations') else 0
        }
    }
