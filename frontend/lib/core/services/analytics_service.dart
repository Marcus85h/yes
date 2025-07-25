import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../config/app_config.dart';
import 'api_service.dart';

/// 事件类型
enum EventType {
  // 用户行为事件
  app_launch,
  app_close,
  user_login,
  user_logout,
  user_register,
  profile_update,
  
  // 聊天事件
  chat_start,
  chat_message_sent,
  chat_message_received,
  chat_file_shared,
  chat_emoji_used,
  
  // 通话事件
  call_initiated,
  call_answered,
  call_ended,
  call_missed,
  call_duration,
  call_quality,
  
  // 支付事件
  payment_initiated,
  payment_completed,
  payment_failed,
  subscription_started,
  subscription_cancelled,
  
  // 内容事件
  content_viewed,
  content_liked,
  content_shared,
  content_reported,
  
  // 性能事件
  performance_issue,
  error_occurred,
  crash_occurred,
  
  // 功能使用事件
  feature_used,
  setting_changed,
  notification_received,
  notification_clicked,
}

/// 事件优先级
enum EventPriority {
  low,
  normal,
  high,
  critical,
}

/// 分析事件
class AnalyticsEvent {
  final String eventId;
  final EventType type;
  final String name;
  final Map<String, dynamic> properties;
  final DateTime timestamp;
  final EventPriority priority;
  final String? userId;
  final String? sessionId;
  
  AnalyticsEvent({
    required this.eventId,
    required this.type,
    required this.name,
    this.properties = const {},
    required this.timestamp,
    this.priority = EventPriority.normal,
    this.userId,
    this.sessionId,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'event_id': eventId,
      'type': type.name,
      'name': name,
      'properties': properties,
      'timestamp': timestamp.toIso8601String(),
      'priority': priority.name,
      'user_id': userId,
      'session_id': sessionId,
    };
  }
  
  factory AnalyticsEvent.fromJson(Map<String, dynamic> json) {
    return AnalyticsEvent(
      eventId: json['event_id'],
      type: EventType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => EventType.feature_used,
      ),
      name: json['name'],
      properties: Map<String, dynamic>.from(json['properties'] ?? {}),
      timestamp: DateTime.parse(json['timestamp']),
      priority: EventPriority.values.firstWhere(
        (e) => e.name == json['priority'],
        orElse: () => EventPriority.normal,
      ),
      userId: json['user_id'],
      sessionId: json['session_id'],
    );
  }
}

/// 用户会话
class UserSession {
  final String sessionId;
  final DateTime startTime;
  DateTime? endTime;
  final Map<String, dynamic> deviceInfo;
  final Map<String, dynamic> appInfo;
  final List<AnalyticsEvent> events;
  
  UserSession({
    required this.sessionId,
    required this.startTime,
    this.endTime,
    required this.deviceInfo,
    required this.appInfo,
    this.events = const [],
  });
  
  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }
  
  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime?.toIso8601String(),
      'duration': duration.inSeconds,
      'device_info': deviceInfo,
      'app_info': appInfo,
      'events_count': events.length,
    };
  }
}

/// 性能指标
class PerformanceMetrics {
  final double cpuUsage;
  final double memoryUsage;
  final double batteryLevel;
  final double networkLatency;
  final double frameRate;
  final int errorCount;
  final DateTime timestamp;
  
  PerformanceMetrics({
    required this.cpuUsage,
    required this.memoryUsage,
    required this.batteryLevel,
    required this.networkLatency,
    required this.frameRate,
    required this.errorCount,
    required this.timestamp,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'cpu_usage': cpuUsage,
      'memory_usage': memoryUsage,
      'battery_level': batteryLevel,
      'network_latency': networkLatency,
      'frame_rate': frameRate,
      'error_count': errorCount,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class AnalyticsService {
  static AnalyticsService? _instance;
  static AnalyticsService get instance => _instance ??= AnalyticsService._();
  
  AnalyticsService._();
  
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  final PackageInfo _packageInfo = PackageInfo();
  
  // 会话管理
  UserSession? _currentSession;
  String? _currentUserId;
  
  // 事件队列
  final List<AnalyticsEvent> _eventQueue = [];
  final int _maxQueueSize = 100;
  
  // 性能监控
  final List<PerformanceMetrics> _performanceHistory = [];
  final int _maxPerformanceHistory = 50;
  
  // 配置
  bool _isEnabled = true;
  bool _isDebugMode = false;
  Duration _batchInterval = const Duration(minutes: 5);
  Timer? _batchTimer;
  
  // 回调函数
  Function(AnalyticsEvent)? onEventTracked;
  Function(List<AnalyticsEvent>)? onEventsBatched;
  Function(PerformanceMetrics)? onPerformanceRecorded;
  
  // Getters
  bool get isEnabled => _isEnabled;
  UserSession? get currentSession => _currentSession;
  String? get currentUserId => _currentUserId;
  
  /// 初始化分析服务
  Future<void> initialize() async {
    try {
      await _loadPackageInfo();
      await _startNewSession();
      _startBatchTimer();
      
      print('分析服务初始化完成');
    } catch (e) {
      print('分析服务初始化失败: $e');
    }
  }
  
  /// 加载包信息
  Future<void> _loadPackageInfo() async {
    _packageInfo = await PackageInfo.fromPlatform();
  }
  
  /// 开始新会话
  Future<void> _startNewSession() async {
    final sessionId = _generateSessionId();
    final deviceInfo = await _getDeviceInfo();
    final appInfo = await _getAppInfo();
    
    _currentSession = UserSession(
      sessionId: sessionId,
      startTime: DateTime.now(),
      deviceInfo: deviceInfo,
      appInfo: appInfo,
    );
    
    // 记录应用启动事件
    trackEvent(
      EventType.app_launch,
      'App Launched',
      properties: {
        'session_id': sessionId,
        'device_info': deviceInfo,
        'app_info': appInfo,
      },
    );
  }
  
  /// 结束当前会话
  Future<void> endSession() async {
    if (_currentSession != null) {
      _currentSession!.endTime = DateTime.now();
      
      // 记录应用关闭事件
      trackEvent(
        EventType.app_close,
        'App Closed',
        properties: {
          'session_duration': _currentSession!.duration.inSeconds,
          'events_count': _currentSession!.events.length,
        },
      );
      
      // 发送会话数据
      await _sendSessionData(_currentSession!);
      
      _currentSession = null;
    }
  }
  
  /// 设置用户ID
  void setUserId(String userId) {
    _currentUserId = userId;
    
    trackEvent(
      EventType.user_login,
      'User Login',
      properties: {'user_id': userId},
    );
  }
  
  /// 清除用户ID
  void clearUserId() {
    if (_currentUserId != null) {
      trackEvent(
        EventType.user_logout,
        'User Logout',
        properties: {'user_id': _currentUserId},
      );
    }
    
    _currentUserId = null;
  }
  
  /// 追踪事件
  void trackEvent(
    EventType type,
    String name, {
    Map<String, dynamic> properties = const {},
    EventPriority priority = EventPriority.normal,
  }) {
    if (!_isEnabled) return;
    
    final event = AnalyticsEvent(
      eventId: _generateEventId(),
      type: type,
      name: name,
      properties: properties,
      timestamp: DateTime.now(),
      priority: priority,
      userId: _currentUserId,
      sessionId: _currentSession?.sessionId,
    );
    
    _addEventToQueue(event);
    onEventTracked?.call(event);
    
    if (_isDebugMode) {
      print('Analytics Event: ${event.name} - ${event.properties}');
    }
  }
  
  /// 追踪用户行为
  void trackUserAction(String action, {Map<String, dynamic> properties = const {}}) {
    trackEvent(
      EventType.feature_used,
      action,
      properties: properties,
    );
  }
  
  /// 追踪错误
  void trackError(String error, {String? stackTrace, Map<String, dynamic> properties = const {}}) {
    trackEvent(
      EventType.error_occurred,
      'Error Occurred',
      properties: {
        'error': error,
        'stack_trace': stackTrace,
        ...properties,
      },
      priority: EventPriority.high,
    );
  }
  
  /// 追踪性能问题
  void trackPerformanceIssue(String issue, {Map<String, dynamic> properties = const {}}) {
    trackEvent(
      EventType.performance_issue,
      'Performance Issue',
      properties: {
        'issue': issue,
        ...properties,
      },
      priority: EventPriority.high,
    );
  }
  
  /// 记录性能指标
  void recordPerformanceMetrics({
    double? cpuUsage,
    double? memoryUsage,
    double? batteryLevel,
    double? networkLatency,
    double? frameRate,
    int? errorCount,
  }) {
    final metrics = PerformanceMetrics(
      cpuUsage: cpuUsage ?? 0.0,
      memoryUsage: memoryUsage ?? 0.0,
      batteryLevel: batteryLevel ?? 0.0,
      networkLatency: networkLatency ?? 0.0,
      frameRate: frameRate ?? 0.0,
      errorCount: errorCount ?? 0,
      timestamp: DateTime.now(),
    );
    
    _performanceHistory.add(metrics);
    
    // 限制历史记录大小
    if (_performanceHistory.length > _maxPerformanceHistory) {
      _performanceHistory.removeAt(0);
    }
    
    onPerformanceRecorded?.call(metrics);
  }
  
  /// 获取性能统计
  Map<String, dynamic> getPerformanceStats() {
    if (_performanceHistory.isEmpty) {
      return {};
    }
    
    final cpuUsage = _performanceHistory.map((m) => m.cpuUsage).toList();
    final memoryUsage = _performanceHistory.map((m) => m.memoryUsage).toList();
    final frameRate = _performanceHistory.map((m) => m.frameRate).toList();
    final latency = _performanceHistory.map((m) => m.networkLatency).toList();
    
    return {
      'average_cpu_usage': cpuUsage.reduce((a, b) => a + b) / cpuUsage.length,
      'average_memory_usage': memoryUsage.reduce((a, b) => a + b) / memoryUsage.length,
      'average_frame_rate': frameRate.reduce((a, b) => a + b) / frameRate.length,
      'average_latency': latency.reduce((a, b) => a + b) / latency.length,
      'max_cpu_usage': cpuUsage.reduce((a, b) => a > b ? a : b),
      'max_memory_usage': memoryUsage.reduce((a, b) => a > b ? a : b),
      'min_frame_rate': frameRate.reduce((a, b) => a < b ? a : b),
      'total_errors': _performanceHistory.map((m) => m.errorCount).reduce((a, b) => a + b),
      'metrics_count': _performanceHistory.length,
    };
  }
  
  /// 获取用户行为统计
  Map<String, dynamic> getUserBehaviorStats() {
    final events = _currentSession?.events ?? [];
    
    final eventCounts = <String, int>{};
    final featureUsage = <String, int>{};
    final errorCount = events.where((e) => e.type == EventType.error_occurred).length;
    
    for (final event in events) {
      eventCounts[event.type.name] = (eventCounts[event.type.name] ?? 0) + 1;
      
      if (event.type == EventType.feature_used) {
        featureUsage[event.name] = (featureUsage[event.name] ?? 0) + 1;
      }
    }
    
    return {
      'total_events': events.length,
      'event_counts': eventCounts,
      'feature_usage': featureUsage,
      'error_count': errorCount,
      'session_duration': _currentSession?.duration.inSeconds ?? 0,
    };
  }
  
  /// 启用/禁用分析
  void setEnabled(bool enabled) {
    _isEnabled = enabled;
  }
  
  /// 设置调试模式
  void setDebugMode(bool debug) {
    _isDebugMode = debug;
  }
  
  /// 设置批处理间隔
  void setBatchInterval(Duration interval) {
    _batchInterval = interval;
    _restartBatchTimer();
  }
  
  /// 立即发送事件
  Future<void> flushEvents() async {
    await _sendBatchedEvents();
  }
  
  // 私有方法
  
  /// 生成会话ID
  String _generateSessionId() {
    return 'session_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(10000)}';
  }
  
  /// 生成事件ID
  String _generateEventId() {
    return 'event_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(10000)}';
  }
  
  /// 获取设备信息
  Future<Map<String, dynamic>> _getDeviceInfo() async {
    try {
      if (defaultTargetPlatform == TargetPlatform.android) {
        final androidInfo = await _deviceInfo.androidInfo;
        return {
          'platform': 'Android',
          'version': androidInfo.version.release,
          'sdk': androidInfo.version.sdkInt,
          'device': androidInfo.model,
          'manufacturer': androidInfo.manufacturer,
          'brand': androidInfo.brand,
        };
      } else if (defaultTargetPlatform == TargetPlatform.iOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        return {
          'platform': 'iOS',
          'version': iosInfo.systemVersion,
          'device': iosInfo.model,
          'name': iosInfo.name,
        };
      }
    } catch (e) {
      print('获取设备信息失败: $e');
    }
    
    return {'platform': 'unknown'};
  }
  
  /// 获取应用信息
  Future<Map<String, dynamic>> _getAppInfo() async {
    return {
      'app_name': _packageInfo.appName,
      'package_name': _packageInfo.packageName,
      'version': _packageInfo.version,
      'build_number': _packageInfo.buildNumber,
    };
  }
  
  /// 添加事件到队列
  void _addEventToQueue(AnalyticsEvent event) {
    _eventQueue.add(event);
    
    // 限制队列大小
    if (_eventQueue.length > _maxQueueSize) {
      _eventQueue.removeAt(0);
    }
    
    // 高优先级事件立即发送
    if (event.priority == EventPriority.critical) {
      _sendEventImmediately(event);
    }
  }
  
  /// 立即发送事件
  Future<void> _sendEventImmediately(AnalyticsEvent event) async {
    try {
      await ApiService.trackAnalyticsEvent(event.toJson());
    } catch (e) {
      print('发送事件失败: $e');
    }
  }
  
  /// 开始批处理定时器
  void _startBatchTimer() {
    _batchTimer = Timer.periodic(_batchInterval, (_) {
      _sendBatchedEvents();
    });
  }
  
  /// 重启批处理定时器
  void _restartBatchTimer() {
    _batchTimer?.cancel();
    _startBatchTimer();
  }
  
  /// 发送批量事件
  Future<void> _sendBatchedEvents() async {
    if (_eventQueue.isEmpty) return;
    
    try {
      final events = List<AnalyticsEvent>.from(_eventQueue);
      _eventQueue.clear();
      
      await ApiService.trackAnalyticsEvents(
        events.map((e) => e.toJson()).toList(),
      );
      
      onEventsBatched?.call(events);
      
    } catch (e) {
      print('发送批量事件失败: $e');
      // 重新添加到队列
      _eventQueue.addAll(_eventQueue);
    }
  }
  
  /// 发送会话数据
  Future<void> _sendSessionData(UserSession session) async {
    try {
      await ApiService.trackAnalyticsSession(session.toJson());
    } catch (e) {
      print('发送会话数据失败: $e');
    }
  }
  
  /// 清理资源
  void dispose() {
    _batchTimer?.cancel();
    endSession();
  }
}

/// 预定义事件追踪器
class EventTracker {
  static void trackLogin(String method) {
    AnalyticsService.instance.trackEvent(
      EventType.user_login,
      'User Login',
      properties: {'method': method},
    );
  }
  
  static void trackCallStart(String callType) {
    AnalyticsService.instance.trackEvent(
      EventType.call_initiated,
      'Call Started',
      properties: {'call_type': callType},
    );
  }
  
  static void trackCallEnd(int duration) {
    AnalyticsService.instance.trackEvent(
      EventType.call_ended,
      'Call Ended',
      properties: {'duration': duration},
    );
  }
  
  static void trackPayment(String method, double amount) {
    AnalyticsService.instance.trackEvent(
      EventType.payment_completed,
      'Payment Completed',
      properties: {
        'method': method,
        'amount': amount,
      },
    );
  }
  
  static void trackFeatureUsage(String feature) {
    AnalyticsService.instance.trackEvent(
      EventType.feature_used,
      feature,
    );
  }
  
  static void trackError(String error, {String? stackTrace}) {
    AnalyticsService.instance.trackError(error, stackTrace: stackTrace);
  }
} 