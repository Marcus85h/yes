import '../../.env.dart';

class AppConfig {
  // 应用信息
  static const String appName = '视频交友';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';
  
  // API配置
  static const String baseUrl = Env.baseUrl;
  static const String wsUrl = Env.wsUrl;
  static const String webrtcUrl = Env.webrtcUrl;
  
  // 超时配置
  static const int connectTimeout = 30000; // 30秒
  static const int receiveTimeout = 30000; // 30秒
  static const int sendTimeout = 30000; // 30秒
  
  // 缓存配置
  static const int maxCacheAge = 7 * 24 * 60 * 60 * 1000; // 7天
  static const int maxCacheSize = 100 * 1024 * 1024; // 100MB
  
  // 图片配置
  static const String imageBaseUrl = 'https://images.videodating.com';
  static const int maxImageSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png', 'gif'];
  
  // 视频配置
  static const int maxVideoSize = 100 * 1024 * 1024; // 100MB
  static const int maxVideoDuration = 300; // 5分钟
  static const List<String> allowedVideoTypes = ['mp4', 'mov', 'avi'];
  
  // 音频配置
  static const int maxAudioSize = 50 * 1024 * 1024; // 50MB
  static const int maxAudioDuration = 300; // 5分钟
  static const List<String> allowedAudioTypes = ['mp3', 'wav', 'm4a'];
  
  // 通话配置
  static const int maxCallDuration = 3600; // 1小时
  static const int callQualityCheckInterval = 5000; // 5秒
  static const int reconnectAttempts = 3;
  static const int reconnectDelay = 2000; // 2秒
  
  // 消息配置
  static const int maxMessageLength = 1000;
  static const int messageLoadLimit = 50;
  static const int typingTimeout = 3000; // 3秒
  
  // 安全配置
  static const int maxLoginAttempts = 5;
  static const int lockoutDuration = 15 * 60; // 15分钟
  static const int sessionTimeout = 24 * 60 * 60; // 24小时
  
  // 支付配置
  static const List<String> supportedPaymentMethods = [
    'alipay',
    'wechat',
    'apple_pay',
    'google_pay',
  ];
  
  // 推送配置
  static const String fcmSenderId = 'your-fcm-sender-id';
  static const String fcmServerKey = 'your-fcm-server-key';
  
  // 第三方登录配置
  static const String wechatAppId = 'your-wechat-app-id';
  static const String wechatAppSecret = 'your-wechat-app-secret';
  static const String qqAppId = 'your-qq-app-id';
  static const String qqAppKey = 'your-qq-app-key';
  
  // 环境配置
  static const bool isProduction = Env.isProduction;
  static const bool isDebug = Env.isDebug;
  
  // 功能开关
  static const bool enableVideoCall = Env.enableVideoCall;
  static const bool enableAudioCall = Env.enableAudioCall;
  static const bool enableGiftSystem = Env.enableGiftSystem;
  static const bool enablePayment = Env.enablePayment;
  static const bool enablePushNotification = Env.enablePushNotification;
  static const bool enableThirdPartyLogin = Env.enableThirdPartyLogin;
  static const bool enableScreenRecording = Env.enableScreenRecording;
  
  // 调试配置
  static const bool enableLogging = !isProduction;
  static const bool enableAnalytics = true;
  static const bool enableCrashReporting = true;
  
  // 获取API URL
  static String getApiUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }
  
  // 获取图片URL
  static String getImageUrl(String path) {
    return '$imageBaseUrl$path';
  }
  
  // 获取WebSocket URL
  static String getWebSocketUrl(String token, String roomId) {
    return '$wsUrl?token=$token&room_id=$roomId';
  }
  
  // 获取WebRTC URL
  static String getWebRTCUrl(String token, String sessionId) {
    return '$webrtcUrl?token=$token&session_id=$sessionId';
  }
} 