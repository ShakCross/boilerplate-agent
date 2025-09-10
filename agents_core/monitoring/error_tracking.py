"""Advanced error tracking and monitoring."""

import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from agents_core.middleware.rate_limiting import cache_manager


class ErrorTracker:
    """Track and analyze errors across the system."""
    
    def __init__(self):
        self.cache = cache_manager
    
    def log_error(self, 
                 error: Exception,
                 context: Dict[str, Any],
                 severity: str = "error") -> str:
        """
        Log an error with context information.
        
        Args:
            error: Exception that occurred
            context: Additional context (user_id, endpoint, etc.)
            severity: Error severity (info, warning, error, critical)
        
        Returns:
            Error ID for tracking
        """
        error_id = f"error_{datetime.now().timestamp()}"
        
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context
        }
        
        # Store in cache for 24 hours
        if self.cache.is_available():
            try:
                self.cache.set(
                    f"error:{error_id}",
                    json.dumps(error_data),
                    ttl=86400  # 24 hours
                )
                
                # Add to recent errors list
                self._add_to_recent_errors(error_id, severity)
                
            except Exception as e:
                print(f"Failed to log error: {e}")
        
        return error_id
    
    def _add_to_recent_errors(self, error_id: str, severity: str):
        """Add error to recent errors list."""
        try:
            # Get current recent errors
            recent_errors = self.cache.get("recent_errors")
            if recent_errors:
                recent_list = json.loads(recent_errors)
            else:
                recent_list = []
            
            # Add new error
            recent_list.append({
                "error_id": error_id,
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            })
            
            # Keep only last 100 errors
            recent_list = recent_list[-100:]
            
            # Store back
            self.cache.set("recent_errors", json.dumps(recent_list), ttl=86400)
            
        except Exception as e:
            print(f"Failed to update recent errors: {e}")
    
    def get_error(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed error information."""
        if not self.cache.is_available():
            return None
        
        try:
            error_data = self.cache.get(f"error:{error_id}")
            if error_data:
                return json.loads(error_data)
        except Exception as e:
            print(f"Failed to get error {error_id}: {e}")
        
        return None
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors."""
        if not self.cache.is_available():
            return []
        
        try:
            recent_errors = self.cache.get("recent_errors")
            if recent_errors:
                recent_list = json.loads(recent_errors)
                return recent_list[-limit:]
        except Exception as e:
            print(f"Failed to get recent errors: {e}")
        
        return []
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        recent_errors = self.get_recent_errors(100)
        
        if not recent_errors:
            return {
                "total_errors": 0,
                "by_severity": {},
                "last_24h": 0,
                "error_rate": 0.0
            }
        
        # Count by severity
        severity_counts = {}
        last_24h_count = 0
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for error in recent_errors:
            severity = error.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count last 24h
            try:
                error_time = datetime.fromisoformat(error["timestamp"])
                if error_time > cutoff_time:
                    last_24h_count += 1
            except:
                pass
        
        # Calculate error rate (errors per hour in last 24h)
        error_rate = last_24h_count / 24.0
        
        return {
            "total_errors": len(recent_errors),
            "by_severity": severity_counts,
            "last_24h": last_24h_count,
            "error_rate": round(error_rate, 2),
            "last_error": recent_errors[-1] if recent_errors else None
        }
    
    def clear_old_errors(self, hours: int = 24):
        """Clear errors older than specified hours."""
        if not self.cache.is_available():
            return False
        
        try:
            recent_errors = self.get_recent_errors(1000)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter out old errors
            filtered_errors = []
            for error in recent_errors:
                try:
                    error_time = datetime.fromisoformat(error["timestamp"])
                    if error_time > cutoff_time:
                        filtered_errors.append(error)
                except:
                    # Keep errors with parsing issues
                    filtered_errors.append(error)
            
            # Store filtered list
            self.cache.set("recent_errors", json.dumps(filtered_errors), ttl=86400)
            return True
            
        except Exception as e:
            print(f"Failed to clear old errors: {e}")
            return False


class PerformanceMonitor:
    """Monitor system performance metrics."""
    
    def __init__(self):
        self.cache = cache_manager
    
    def record_response_time(self, endpoint: str, duration_ms: float):
        """Record response time for an endpoint."""
        if not self.cache.is_available():
            return
        
        try:
            # Get current metrics
            key = f"perf:{endpoint}:response_times"
            current_data = self.cache.get(key)
            
            if current_data:
                metrics = json.loads(current_data)
            else:
                metrics = {
                    "count": 0,
                    "total_ms": 0,
                    "min_ms": float('inf'),
                    "max_ms": 0,
                    "recent_times": []
                }
            
            # Update metrics
            metrics["count"] += 1
            metrics["total_ms"] += duration_ms
            metrics["min_ms"] = min(metrics["min_ms"], duration_ms)
            metrics["max_ms"] = max(metrics["max_ms"], duration_ms)
            
            # Keep last 100 response times
            metrics["recent_times"].append(duration_ms)
            metrics["recent_times"] = metrics["recent_times"][-100:]
            
            # Store updated metrics
            self.cache.set(key, json.dumps(metrics), ttl=3600)  # 1 hour
            
        except Exception as e:
            print(f"Failed to record response time: {e}")
    
    def get_performance_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get performance statistics for an endpoint."""
        if not self.cache.is_available():
            return {"status": "unavailable"}
        
        try:
            key = f"perf:{endpoint}:response_times"
            data = self.cache.get(key)
            
            if not data:
                return {"status": "no_data"}
            
            metrics = json.loads(data)
            
            if metrics["count"] == 0:
                return {"status": "no_data"}
            
            # Calculate statistics
            avg_ms = metrics["total_ms"] / metrics["count"]
            
            # Calculate percentiles from recent times
            recent_times = sorted(metrics["recent_times"])
            if recent_times:
                p50 = recent_times[len(recent_times) // 2]
                p95_idx = int(len(recent_times) * 0.95)
                p95 = recent_times[min(p95_idx, len(recent_times) - 1)]
            else:
                p50 = p95 = avg_ms
            
            return {
                "status": "available",
                "total_requests": metrics["count"],
                "avg_response_time_ms": round(avg_ms, 2),
                "min_response_time_ms": round(metrics["min_ms"], 2),
                "max_response_time_ms": round(metrics["max_ms"], 2),
                "p50_response_time_ms": round(p50, 2),
                "p95_response_time_ms": round(p95, 2),
                "recent_requests": len(metrics["recent_times"])
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global instances
error_tracker = ErrorTracker()
performance_monitor = PerformanceMonitor()
