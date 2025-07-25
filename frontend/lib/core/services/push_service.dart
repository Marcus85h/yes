import 'dart:convert';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../config/app_config.dart';
import 'api_service.dart';

/// 推送消息类型
enum PushMessageType {
  chat,
  call,
  gift,
  system,
  marketing,
}

/// 推送消息数据
class PushMessage {
  final String id;
  final String title;
  final String body;
  final PushMessageType type;
  final Map<String, dynamic>? data;
  final DateTime timestamp;
  final bool isRead;
  
  PushMessage({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    this.data,
    required this.timestamp,
    this.isRead = false,
  });
  
  factory PushMessage.fromJson(Map<String, dynamic> json) {
    return PushMessage(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      type: PushMessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => PushMessageType.system,
      ),
      data: json['data'],
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
      isRead: json['is_read'] ?? false,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'type': type.name,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
      'is_read': isRead,
    };
  }
}

class PushService {
  static PushService? _instance;
  static PushService get instance => _instance ??= PushService._();
  
  PushService._();
  
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  
  // 回调函数
  Function(PushMessage)? onMessageReceived;
  Function(PushMessage)? onNotificationTapped;
  Function(String)? onTokenRefreshed;
  
  // 状态
  bool _isInitialized = false;
  String? _fcmToken;
  bool _permissionGranted = false;
  
  // Getters
  bool get isInitialized => _isInitialized;
  String? get fcmToken => _fcmToken;
  bool get permissionGranted => _permissionGranted;
  
  /// 初始化推送服务
  Future<bool> initialize() async {
    try {
      // 初始化Firebase
      await Firebase.initializeApp();
      
      // 请求权限
      await _requestPermission();
      
      // 初始化本地通知
      await _initializeLocalNotifications();
      
      // 获取FCM Token
      await _getFCMToken();
      
      // 设置消息处理器
      _setupMessageHandlers();
      
      _isInitialized = true;
      print('推送服务初始化成功');
      return true;
      
    } catch (e) {
      print('推送服务初始化失败: $e');
      return false;
    }
  }
  
  /// 请求推送权限
  Future<void> _requestPermission() async {
    try {
      final settings = await _firebaseMessaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );
      
      _permissionGranted = settings.authorizationStatus == AuthorizationStatus.authorized;
      print('推送权限状态: ${settings.authorizationStatus}');
      
    } catch (e) {
      print('请求推送权限失败: $e');
      _permissionGranted = false;
    }
  }
  
  /// 初始化本地通知
  Future<void> _initializeLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }
  
  /// 获取FCM Token
  Future<void> _getFCMToken() async {
    try {
      _fcmToken = await _firebaseMessaging.getToken();
      if (_fcmToken != null) {
        print('FCM Token: $_fcmToken');
        onTokenRefreshed?.call(_fcmToken!);
        
        // 上传Token到服务器
        await _uploadTokenToServer(_fcmToken!);
      }
    } catch (e) {
      print('获取FCM Token失败: $e');
    }
  }
  
  /// 设置消息处理器
  void _setupMessageHandlers() {
    // 前台消息处理
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    
    // 后台消息处理
    FirebaseMessaging.onMessageOpenedApp.listen(_handleBackgroundMessage);
    
    // Token刷新处理
    _firebaseMessaging.onTokenRefresh.listen((token) {
      _fcmToken = token;
      onTokenRefreshed?.call(token);
      _uploadTokenToServer(token);
    });
  }
  
  /// 处理前台消息
  void _handleForegroundMessage(RemoteMessage message) {
    print('收到前台消息: ${message.messageId}');
    
    final pushMessage = _convertToPushMessage(message);
    onMessageReceived?.call(pushMessage);
    
    // 显示本地通知
    _showLocalNotification(pushMessage);
  }
  
  /// 处理后台消息
  void _handleBackgroundMessage(RemoteMessage message) {
    print('收到后台消息: ${message.messageId}');
    
    final pushMessage = _convertToPushMessage(message);
    onNotificationTapped?.call(pushMessage);
  }
  
  /// 转换RemoteMessage为PushMessage
  PushMessage _convertToPushMessage(RemoteMessage message) {
    return PushMessage(
      id: message.messageId ?? DateTime.now().millisecondsSinceEpoch.toString(),
      title: message.notification?.title ?? '',
      body: message.notification?.body ?? '',
      type: _getMessageType(message.data['type']),
      data: message.data,
      timestamp: DateTime.now(),
    );
  }
  
  /// 获取消息类型
  PushMessageType _getMessageType(String? type) {
    switch (type) {
      case 'chat':
        return PushMessageType.chat;
      case 'call':
        return PushMessageType.call;
      case 'gift':
        return PushMessageType.gift;
      case 'marketing':
        return PushMessageType.marketing;
      default:
        return PushMessageType.system;
    }
  }
  
  /// 显示本地通知
  Future<void> _showLocalNotification(PushMessage message) async {
    const androidDetails = AndroidNotificationDetails(
      'default_channel',
      '默认通知',
      channelDescription: '应用默认通知频道',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );
    
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _localNotifications.show(
      message.hashCode,
      message.title,
      message.body,
      details,
      payload: jsonEncode(message.toJson()),
    );
  }
  
  /// 处理通知点击
  void _onNotificationTapped(NotificationResponse response) {
    try {
      if (response.payload != null) {
        final messageData = jsonDecode(response.payload!);
        final message = PushMessage.fromJson(messageData);
        onNotificationTapped?.call(message);
      }
    } catch (e) {
      print('处理通知点击失败: $e');
    }
  }
  
  /// 上传Token到服务器
  Future<void> _uploadTokenToServer(String token) async {
    try {
      await ApiService.updateFCMToken(token);
      print('FCM Token上传成功');
    } catch (e) {
      print('FCM Token上传失败: $e');
    }
  }
  
  /// 订阅主题
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _firebaseMessaging.subscribeToTopic(topic);
      print('订阅主题成功: $topic');
    } catch (e) {
      print('订阅主题失败: $e');
    }
  }
  
  /// 取消订阅主题
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _firebaseMessaging.unsubscribeFromTopic(topic);
      print('取消订阅主题成功: $topic');
    } catch (e) {
      print('取消订阅主题失败: $e');
    }
  }
  
  /// 获取推送历史
  Future<List<PushMessage>> getPushHistory({int page = 1, int pageSize = 20}) async {
    try {
      final response = await ApiService.getPushHistory(page: page, pageSize: pageSize);
      final messages = response['results'] as List;
      return messages.map((json) => PushMessage.fromJson(json)).toList();
    } catch (e) {
      print('获取推送历史失败: $e');
      return [];
    }
  }
  
  /// 标记消息为已读
  Future<bool> markAsRead(String messageId) async {
    try {
      final response = await ApiService.markPushAsRead(messageId);
      return response['success'] == true;
    } catch (e) {
      print('标记消息已读失败: $e');
      return false;
    }
  }
  
  /// 删除推送消息
  Future<bool> deleteMessage(String messageId) async {
    try {
      final response = await ApiService.deletePushMessage(messageId);
      return response['success'] == true;
    } catch (e) {
      print('删除推送消息失败: $e');
      return false;
    }
  }
  
  /// 设置推送设置
  Future<bool> updatePushSettings({
    bool? chatEnabled,
    bool? callEnabled,
    bool? giftEnabled,
    bool? systemEnabled,
    bool? marketingEnabled,
  }) async {
    try {
      final settings = <String, dynamic>{};
      if (chatEnabled != null) settings['chat_enabled'] = chatEnabled;
      if (callEnabled != null) settings['call_enabled'] = callEnabled;
      if (giftEnabled != null) settings['gift_enabled'] = giftEnabled;
      if (systemEnabled != null) settings['system_enabled'] = systemEnabled;
      if (marketingEnabled != null) settings['marketing_enabled'] = marketingEnabled;
      
      final response = await ApiService.updatePushSettings(settings);
      return response['success'] == true;
    } catch (e) {
      print('更新推送设置失败: $e');
      return false;
    }
  }
  
  /// 获取推送设置
  Future<Map<String, dynamic>> getPushSettings() async {
    try {
      final response = await ApiService.getPushSettings();
      return response;
    } catch (e) {
      print('获取推送设置失败: $e');
      return {};
    }
  }
  
  /// 清除所有通知
  Future<void> clearAllNotifications() async {
    await _localNotifications.cancelAll();
  }
  
  /// 获取未读消息数量
  Future<int> getUnreadCount() async {
    try {
      final response = await ApiService.getUnreadPushCount();
      return response['count'] ?? 0;
    } catch (e) {
      print('获取未读消息数量失败: $e');
      return 0;
    }
  }
}

/// 后台消息处理函数
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('处理后台消息: ${message.messageId}');
} 