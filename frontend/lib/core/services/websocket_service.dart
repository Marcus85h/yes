import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../config/app_config.dart';
import 'storage_service.dart';

class WebSocketService {
  static WebSocketService? _instance;
  static WebSocketService get instance => _instance ??= WebSocketService._();
  
  WebSocketService._();
  
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _messageController;
  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  bool _isConnected = false;
  bool _isConnecting = false;
  int _reconnectAttempts = 0;
  final int _maxReconnectAttempts = 5;
  
  // 连接状态
  bool get isConnected => _isConnected;
  bool get isConnecting => _isConnecting;
  
  // 消息流
  Stream<Map<String, dynamic>> get messageStream => 
      _messageController?.stream ?? Stream.empty();
  
  /// 连接到WebSocket服务器
  Future<bool> connect({String? roomId}) async {
    if (_isConnected || _isConnecting) return _isConnected;
    
    try {
      _isConnecting = true;
      
      // 获取认证token
      final token = await StorageService.getString('auth_token');
      if (token == null) {
        throw Exception('未找到认证token');
      }
      
      // 构建WebSocket URL
      String wsUrl = AppConfig.getWebSocketUrl(token, roomId ?? '');
      
      // 创建WebSocket连接
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      // 创建消息控制器
      _messageController = StreamController<Map<String, dynamic>>.broadcast();
      
      // 监听消息
      _channel!.stream.listen(
        (data) => _handleMessage(data),
        onError: (error) => _handleError(error),
        onDone: () => _handleDisconnect(),
      );
      
      _isConnected = true;
      _isConnecting = false;
      _reconnectAttempts = 0;
      
      // 启动心跳
      _startHeartbeat();
      
      print('WebSocket连接成功');
      return true;
      
    } catch (e) {
      _isConnecting = false;
      print('WebSocket连接失败: $e');
      return false;
    }
  }
  
  /// 断开连接
  void disconnect() {
    _stopHeartbeat();
    _stopReconnectTimer();
    
    _channel?.sink.close(status.goingAway);
    _channel = null;
    
    _messageController?.close();
    _messageController = null;
    
    _isConnected = false;
    _isConnecting = false;
    
    print('WebSocket连接已断开');
  }
  
  /// 发送消息
  void send(Map<String, dynamic> message) {
    if (!_isConnected || _channel == null) {
      print('WebSocket未连接，无法发送消息');
      return;
    }
    
    try {
      final jsonMessage = jsonEncode(message);
      _channel!.sink.add(jsonMessage);
      print('发送消息: $jsonMessage');
    } catch (e) {
      print('发送消息失败: $e');
    }
  }
  
  /// 发送聊天消息
  void sendChatMessage(String content, {String messageType = 'text'}) {
    send({
      'type': 'chat_message',
      'content': content,
      'message_type': messageType,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }
  
  /// 发送正在输入状态
  void sendTyping(bool isTyping) {
    send({
      'type': 'typing',
      'is_typing': isTyping,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }
  
  /// 发送已读回执
  void sendReadReceipt(String messageId) {
    send({
      'type': 'read_receipt',
      'message_id': messageId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }
  
  /// 处理接收到的消息
  void _handleMessage(dynamic data) {
    try {
      Map<String, dynamic> message;
      
      if (data is String) {
        message = jsonDecode(data);
      } else if (data is Map<String, dynamic>) {
        message = data;
      } else {
        print('未知消息格式: $data');
        return;
      }
      
      print('接收消息: $message');
      
      // 发送到消息流
      _messageController?.add(message);
      
    } catch (e) {
      print('处理消息失败: $e');
    }
  }
  
  /// 处理连接错误
  void _handleError(dynamic error) {
    print('WebSocket错误: $error');
    _isConnected = false;
    _isConnecting = false;
    
    // 尝试重连
    _scheduleReconnect();
  }
  
  /// 处理连接断开
  void _handleDisconnect() {
    print('WebSocket连接断开');
    _isConnected = false;
    _isConnecting = false;
    
    // 尝试重连
    _scheduleReconnect();
  }
  
  /// 启动心跳
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_isConnected) {
        send({
          'type': 'heartbeat',
          'timestamp': DateTime.now().toIso8601String(),
        });
      }
    });
  }
  
  /// 停止心跳
  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }
  
  /// 安排重连
  void _scheduleReconnect() {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      print('达到最大重连次数，停止重连');
      return;
    }
    
    _stopReconnectTimer();
    
    final delay = Duration(seconds: _reconnectAttempts * 2 + 1);
    _reconnectTimer = Timer(delay, () {
      _reconnectAttempts++;
      print('尝试重连 (${_reconnectAttempts}/$_maxReconnectAttempts)');
      connect();
    });
  }
  
  /// 停止重连定时器
  void _stopReconnectTimer() {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
  }
}

/// WebSocket消息类型
class WebSocketMessageType {
  static const String connectionEstablished = 'connection_established';
  static const String chatMessage = 'chat_message';
  static const String userTyping = 'user_typing';
  static const String userJoined = 'user_joined';
  static const String userLeft = 'user_left';
  static const String heartbeat = 'heartbeat';
  static const String error = 'error';
}

/// WebSocket消息模型
class WebSocketMessage {
  final String type;
  final Map<String, dynamic> data;
  final String? timestamp;
  
  WebSocketMessage({
    required this.type,
    required this.data,
    this.timestamp,
  });
  
  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] ?? '',
      data: json['data'] ?? {},
      timestamp: json['timestamp'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'data': data,
      'timestamp': timestamp ?? DateTime.now().toIso8601String(),
    };
  }
} 