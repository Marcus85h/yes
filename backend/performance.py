"""
性能监控和优化模块
包含缓存、数据库优化、性能监控等功能
"""

import functools
import logging
import threading
import time
from typing import Any, Callable, Dict, Optional

import psutil
from django.conf import settings
from django.core.cache import cache
from django.db import connection, reset_queries
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus指标
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
DB_QUERY_DURATION = Histogram("db_query_duration_seconds", "Database query duration")
CACHE_HIT_RATIO = Gauge("cache_hit_ratio", "Cache hit ratio")
ACTIVE_CONNECTIONS = Gauge("active_connections", "Active database connections")


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def start_request(self, method: str, endpoint: str):
        """开始请求监控"""
        self.request_count += 1
        self.current_request: Dict[str, Any] = {
            "method": method,
            "endpoint": endpoint,
            "start_time": float(time.time()),
            "db_queries": int(len(connection.queries)),
        }

    def end_request(self, status_code: int):
        """结束请求监控"""
        if hasattr(self, "current_request"):
            duration = time.time() - self.current_request["start_time"]
            db_queries = len(connection.queries) - self.current_request["db_queries"]

            # 记录指标
            REQUEST_COUNT.labels(
                method=self.current_request["method"],
                endpoint=self.current_request["endpoint"],
                status=status_code,
            ).inc()

            REQUEST_DURATION.observe(duration)

            # 记录日志
            logger.info(
                f"请求性能 - 方法: {self.current_request['method']}, "
                f"端点: {self.current_request['endpoint']}, "
                f"状态: {status_code}, "
                f"耗时: {duration:.3f}s, "
                f"数据库查询: {db_queries}"
            )

    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_hits += 1
        self._update_cache_ratio()

    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_misses += 1
        self._update_cache_ratio()

    def _update_cache_ratio(self):
        """更新缓存命中率"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            ratio = self.cache_hits / total
            CACHE_HIT_RATIO.set(ratio)


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.default_timeout = 300  # 5分钟

    def get_or_set(self, key: str, default_func: Callable, timeout: Optional[int] = None) -> Any:
        """获取或设置缓存"""
        value = cache.get(key)
        if value is None:
            value = default_func()
            cache.set(key, value, timeout or self.default_timeout)
            return value
        return value

    def invalidate_pattern(self, pattern: str):
        """按模式清除缓存"""
        # 这里需要根据具体的缓存后端实现
        # Redis支持模式删除
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(pattern)
        else:
            # 对于不支持模式删除的缓存后端，记录警告
            logger.warning(f"缓存后端不支持模式删除: {pattern}")

    def warm_up_cache(self, cache_items: list[tuple[str, Callable, int]]):
        """预热缓存"""
        for key, func, timeout in cache_items:
            try:
                value = func()
                cache.set(key, value, timeout)
                logger.info(f"缓存预热成功: {key}")
            except Exception as e:
                logger.error(f"缓存预热失败: {key}, 错误: {e}")


class DatabaseOptimizer:
    """数据库优化器"""

    def __init__(self):
        self.slow_query_threshold = 1.0  # 1秒

    def monitor_queries(self, func: Callable) -> Callable:
        """监控数据库查询"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            initial_queries = len(connection.queries)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                query_count = len(connection.queries) - initial_queries

                # 记录慢查询
                if duration > self.slow_query_threshold:
                    logger.warning(
                        f"慢查询检测 - 函数: {func.__name__}, "
                        f"耗时: {duration:.3f}s, "
                        f"查询数: {query_count}"
                    )

                DB_QUERY_DURATION.observe(duration)

        return wrapper

    def optimize_queryset(self, queryset, select_related=None, prefetch_related=None):
        """优化查询集"""
        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        return queryset

    def get_connection_stats(self) -> dict:
        """获取数据库连接统计"""
        return {
            "total_connections": len(connection.queries),
            "connection_time": connection.connection.connection_time,
            "server_version": connection.connection.server_version,
        }


class SystemMonitor:
    """系统监控器"""

    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """开始系统监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        """停止系统监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)

                # 内存使用率
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # 磁盘使用率
                disk = psutil.disk_usage("/")
                disk_percent = disk.percent

                # 记录指标
                logger.info(
                    f"系统状态 - CPU: {cpu_percent}%, "
                    f"内存: {memory_percent}%, "
                    f"磁盘: {disk_percent}%"
                )

                # 检查阈值
                if cpu_percent > 80 or memory_percent > 80 or disk_percent > 90:
                    logger.warning(
                        f"系统资源警告 - CPU: {cpu_percent}%, "
                        f"内存: {memory_percent}%, "
                        f"磁盘: {disk_percent}%"
                    )

                time.sleep(60)  # 每分钟检查一次

            except Exception as e:
                logger.error(f"系统监控错误: {e}")
                time.sleep(60)


# 创建全局实例
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
db_optimizer = DatabaseOptimizer()
system_monitor = SystemMonitor()


def performance_decorator(func: Callable) -> Callable:
    """性能装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        initial_queries = len(connection.queries)

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            query_count = len(connection.queries) - initial_queries

            logger.info(
                f"函数性能 - {func.__name__}: "
                f"耗时: {duration:.3f}s, "
                f"数据库查询: {query_count}"
            )

    return wrapper


def cache_result(timeout: int = 300):
    """缓存结果装饰器"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                performance_monitor.record_cache_hit()
                return result

            # 缓存未命中，执行函数
            performance_monitor.record_cache_miss()
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator
