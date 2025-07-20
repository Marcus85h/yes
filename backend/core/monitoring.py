"""
性能监控模块
提供应用性能监控、日志记录和错误追踪功能
"""

import functools
import logging
import os
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

import psutil
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

# 性能指标存储
performance_metrics: Dict[str, Dict[str, Any]] = defaultdict(
    lambda: {
        "count": 0,
        "total_time": 0.0,
        "min_time": float("inf"),
        "max_time": 0.0,
        "recent_times": deque(maxlen=100),
    }
)

# 系统资源监控
system_metrics: Dict[str, deque] = {
    "cpu_usage": deque(maxlen=60),
    "memory_usage": deque(maxlen=60),
    "disk_usage": deque(maxlen=60),
    "network_io": deque(maxlen=60),
}

# 线程锁
metrics_lock = threading.Lock()


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.active_requests = 0

    def record_request(self, path: str, method: str, duration: float, status_code: int):
        """记录请求性能"""
        with metrics_lock:
            key = f"{method}:{path}"
            metrics = performance_metrics[key]
            metrics["count"] += 1
            metrics["total_time"] += duration
            metrics["min_time"] = min(metrics["min_time"], duration)
            metrics["max_time"] = max(metrics["max_time"], duration)
            metrics["recent_times"].append(duration)

            self.request_count += 1
            if status_code >= 400:
                self.error_count += 1

    def record_system_metrics(self):
        """记录系统资源使用情况"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()

            timestamp = time.time()

            system_metrics["cpu_usage"].append((timestamp, cpu_percent))
            system_metrics["memory_usage"].append((timestamp, memory.percent))
            system_metrics["disk_usage"].append((timestamp, disk.percent))
            system_metrics["network_io"].append(
                (timestamp, {"bytes_sent": network.bytes_sent, "bytes_recv": network.bytes_recv})
            )

        except Exception as e:
            logger.error(f"记录系统指标失败: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with metrics_lock:
            summary = {
                "uptime": time.time() - self.start_time,
                "total_requests": self.request_count,
                "error_rate": self.error_count / max(self.request_count, 1) * 100,
                "active_requests": self.active_requests,
                "endpoints": {},
            }

            for key, metrics in performance_metrics.items():
                if metrics["count"] > 0:
                    avg_time = metrics["total_time"] / metrics["count"]
                    summary["endpoints"][key] = {
                        "count": metrics["count"],
                        "avg_time": avg_time,
                        "min_time": metrics["min_time"],
                        "max_time": metrics["max_time"],
                        "recent_avg": (
                            sum(metrics["recent_times"]) / len(metrics["recent_times"])
                            if metrics["recent_times"]
                            else 0
                        ),
                    }

            return summary

    def get_system_summary(self) -> Dict[str, Any]:
        """获取系统资源摘要"""
        try:
            cpu_usage = [x[1] for x in system_metrics["cpu_usage"]]
            memory_usage = [x[1] for x in system_metrics["memory_usage"]]
            disk_usage = [x[1] for x in system_metrics["disk_usage"]]

            return {
                "cpu": {
                    "current": cpu_usage[-1] if cpu_usage else 0,
                    "average": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                    "max": max(cpu_usage) if cpu_usage else 0,
                },
                "memory": {
                    "current": memory_usage[-1] if memory_usage else 0,
                    "average": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                    "max": max(memory_usage) if memory_usage else 0,
                },
                "disk": {
                    "current": disk_usage[-1] if disk_usage else 0,
                    "average": sum(disk_usage) / len(disk_usage) if disk_usage else 0,
                    "max": max(disk_usage) if disk_usage else 0,
                },
            }
        except Exception as e:
            logger.error(f"获取系统摘要失败: {e}")
            return {}


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def performance_monitor_decorator(operation_name: Optional[str] = None):
    """性能监控装饰器"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 记录成功操作
                with metrics_lock:
                    metrics = performance_metrics[operation]
                    metrics["count"] += 1
                    metrics["total_time"] += duration
                    metrics["min_time"] = min(metrics["min_time"], duration)
                    metrics["max_time"] = max(metrics["max_time"], duration)
                    metrics["recent_times"].append(duration)

                # 记录慢操作
                if duration > 1.0:  # 超过1秒的操作
                    logger.warning(f"慢操作检测: {operation} 耗时 {duration:.2f}秒")

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"操作失败: {operation} 耗时 {duration:.2f}秒, 错误: {e}")
                raise

        return wrapper

    return decorator


class PerformanceMiddleware:
    """性能监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.time()
        performance_monitor.active_requests += 1

        try:
            response = self.get_response(request)
            duration = time.time() - start_time

            # 记录请求性能
            performance_monitor.record_request(
                path=request.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code,
            )

            # 添加性能头
            response["X-Response-Time"] = f"{duration:.3f}s"
            response["X-Request-ID"] = getattr(request, "request_id", "unknown")

            return response

        finally:
            performance_monitor.active_requests -= 1


class DatabaseQueryMonitor:
    """数据库查询监控"""

    def __init__(self):
        self.query_count = 0
        self.query_time = 0.0
        self.slow_queries = []

    def record_query(self, sql: str, duration: float):
        """记录数据库查询"""
        self.query_count += 1
        self.query_time += duration

        # 记录慢查询
        if duration > 0.1:  # 超过100ms的查询
            self.slow_queries.append(
                {"sql": sql, "duration": duration, "timestamp": timezone.now()}
            )

            # 只保留最近100条慢查询
            if len(self.slow_queries) > 100:
                self.slow_queries.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        """获取查询摘要"""
        return {
            "total_queries": self.query_count,
            "total_time": self.query_time,
            "avg_time": self.query_time / max(self.query_count, 1),
            "slow_queries_count": len(self.slow_queries),
        }


# 全局数据库监控器
db_monitor = DatabaseQueryMonitor()


def cache_monitor(func: Callable) -> Callable:
    """缓存监控装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

        # 检查缓存
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"缓存命中: {cache_key}")
            return cached_result

        # 执行函数
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        # 缓存结果
        cache.set(cache_key, result, timeout=300)  # 5分钟缓存
        logger.debug(f"缓存设置: {cache_key}, 耗时: {duration:.3f}s")

        return result

    return wrapper


def log_performance_metrics():
    """定期记录性能指标"""
    try:
        # 记录系统指标
        performance_monitor.record_system_metrics()

        # 获取性能摘要
        perf_summary = performance_monitor.get_performance_summary()
        sys_summary = performance_monitor.get_system_summary()

        # 记录到日志
        logger.info(f"性能摘要: {perf_summary}")
        logger.info(f"系统摘要: {sys_summary}")

        # 检查异常情况
        if perf_summary["error_rate"] > 5:
            logger.warning(f"错误率过高: {perf_summary['error_rate']:.2f}%")

        if sys_summary["cpu"]["current"] > 80:
            logger.warning(f"CPU使用率过高: {sys_summary['cpu']['current']:.2f}%")

        if sys_summary["memory"]["current"] > 85:
            logger.warning(f"内存使用率过高: {sys_summary['memory']['current']:.2f}%")

    except Exception as e:
        logger.error(f"记录性能指标失败: {e}")


# 导出装饰器别名
performance_monitor_decorator = performance_monitor_decorator
