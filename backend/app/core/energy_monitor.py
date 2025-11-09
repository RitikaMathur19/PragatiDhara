"""
Energy monitoring and sustainability metrics
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

import psutil
import cpuinfo


@dataclass
class EnergyMetrics:
    """Energy and performance metrics."""
    start_time: float
    end_time: Optional[float] = None
    cpu_usage_samples: list = field(default_factory=list)
    memory_usage_samples: list = field(default_factory=list)
    request_count: int = 0
    total_processing_time: float = 0.0
    energy_score: float = 0.0


class EnergyMonitor:
    """Monitor energy consumption and system performance for sustainable AI."""
    
    def __init__(self):
        self.metrics = EnergyMetrics(start_time=time.time())
        self.monitoring = False
        self.cpu_info = cpuinfo.get_cpu_info()
        self.baseline_cpu = 0.0
        self.baseline_memory = 0.0
        
    def start_monitoring(self) -> None:
        """Start energy monitoring."""
        self.monitoring = True
        self.baseline_cpu = psutil.cpu_percent(interval=1)
        self.baseline_memory = psutil.virtual_memory().percent
        
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return final metrics."""
        self.monitoring = False
        self.metrics.end_time = time.time()
        return self.get_summary_metrics()
        
    def record_request(self, processing_time: float, cpu_usage: float, memory_usage: float) -> None:
        """Record metrics for a single request."""
        if not self.monitoring:
            return
            
        self.metrics.request_count += 1
        self.metrics.total_processing_time += processing_time
        self.metrics.cpu_usage_samples.append(cpu_usage)
        self.metrics.memory_usage_samples.append(memory_usage)
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Calculate energy efficiency score (0-100, higher is better)
        cpu_efficiency = max(0, 100 - cpu_percent)
        memory_efficiency = max(0, 100 - memory.percent)
        energy_score = (cpu_efficiency + memory_efficiency) / 2
        
        return {
            "timestamp": time.time(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "model": self.cpu_info.get("brand_raw", "Unknown")
            },
            "memory": {
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            },
            "sustainability": {
                "energy_efficiency_score": round(energy_score, 2),
                "cpu_efficient": cpu_percent < 50,
                "memory_efficient": memory.percent < 70,
                "overall_efficient": energy_score > 70
            },
            "requests": {
                "total_processed": self.metrics.request_count,
                "avg_processing_time": (
                    round(self.metrics.total_processing_time / max(1, self.metrics.request_count), 3)
                )
            }
        }
        
    def get_sustainability_score(self) -> Dict[str, Any]:
        """Calculate overall sustainability score."""
        if not self.metrics.cpu_usage_samples:
            return {"score": 100, "grade": "A+", "details": "No load processed yet"}
            
        avg_cpu = sum(self.metrics.cpu_usage_samples) / len(self.metrics.cpu_usage_samples)
        avg_memory = sum(self.metrics.memory_usage_samples) / len(self.metrics.memory_usage_samples)
        avg_processing_time = self.metrics.total_processing_time / max(1, self.metrics.request_count)
        
        # Score calculation (0-100)
        cpu_score = max(0, 100 - avg_cpu)  # Lower CPU usage = higher score
        memory_score = max(0, 100 - avg_memory)  # Lower memory usage = higher score
        speed_score = max(0, 100 - min(avg_processing_time * 100, 100))  # Faster = higher score
        
        overall_score = (cpu_score + memory_score + speed_score) / 3
        
        # Grade assignment
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        else:
            grade = "D"
            
        return {
            "score": round(overall_score, 2),
            "grade": grade,
            "details": {
                "cpu_efficiency": round(cpu_score, 2),
                "memory_efficiency": round(memory_score, 2),
                "processing_speed": round(speed_score, 2),
                "avg_cpu_usage": round(avg_cpu, 2),
                "avg_memory_usage": round(avg_memory, 2),
                "avg_processing_time_ms": round(avg_processing_time * 1000, 2)
            }
        }
        
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get comprehensive session metrics."""
        duration = (self.metrics.end_time or time.time()) - self.metrics.start_time
        
        return {
            "session": {
                "duration_seconds": round(duration, 2),
                "start_time": datetime.fromtimestamp(self.metrics.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.metrics.end_time or time.time()).isoformat()
            },
            "performance": self.get_current_metrics(),
            "sustainability": self.get_sustainability_score(),
            "recommendations": self._get_efficiency_recommendations()
        }
        
    def _get_efficiency_recommendations(self) -> list:
        """Generate efficiency improvement recommendations."""
        recommendations = []
        current = self.get_current_metrics()
        
        if current["cpu"]["usage_percent"] > 70:
            recommendations.append("Consider reducing CPU-intensive operations or implementing caching")
            
        if current["memory"]["usage_percent"] > 80:
            recommendations.append("Memory usage is high - consider optimizing data structures")
            
        if self.metrics.request_count > 0:
            avg_time = self.metrics.total_processing_time / self.metrics.request_count
            if avg_time > 1.0:
                recommendations.append("Request processing time is slow - consider optimization")
                
        if not recommendations:
            recommendations.append("System is running efficiently - great job on sustainability!")
            
        return recommendations