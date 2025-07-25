import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class ChatProvider extends ChangeNotifier {
  bool _isLoading = false;
  List<Map<String, dynamic>> _chats = [];
  Map<String, List<Map<String, dynamic>>> _messages = {};
  Map<String, dynamic>? _currentChat;
  String? _error;
  Map<String, int> _unreadCounts = {};

  // Getters
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get chats => _chats;
  Map<String, List<Map<String, dynamic>>> get messages => _messages;
  Map<String, dynamic>? get currentChat => _currentChat;
  String? get error => _error;
  Map<String, int> get unreadCounts => _unreadCounts;

  // 获取聊天列表
  Future<void> getChats() async {
    _setLoading(true);
    _clearError();

    try {
      final chatList = await ApiService.getChats();
      _chats = chatList;
      
      // 计算未读消息数
      _calculateUnreadCounts();
      
      notifyListeners();
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
    } finally {
      _setLoading(false);
    }
  }

  // 获取聊天消息
  Future<void> getChatMessages(String chatId, {bool refresh = false}) async {
    if (refresh) {
      _messages[chatId] = [];
    }

    _setLoading(true);
    _clearError();

    try {
      final response = await ApiService.getChatMessages(chatId);
      final messageList = List<Map<String, dynamic>>.from(response['results'] ?? []);
      
      if (refresh) {
        _messages[chatId] = messageList;
      } else {
        final existingMessages = _messages[chatId] ?? [];
        _messages[chatId] = [...existingMessages, ...messageList];
      }

      // 标记消息为已读
      _markChatAsRead(chatId);
      
      notifyListeners();
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
    } finally {
      _setLoading(false);
    }
  }

  // 发送消息
  Future<bool> sendMessage(String chatId, String content, {String? type}) async {
    try {
      final message = await ApiService.sendMessage(chatId, content, type: type);
      
      // 添加到本地消息列表
      final chatMessages = _messages[chatId] ?? [];
      chatMessages.add(message);
      _messages[chatId] = chatMessages;
      
      // 更新聊天列表中的最后消息
      _updateChatLastMessage(chatId, message);
      
      notifyListeners();
      return true;
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
      return false;
    }
  }

  // 选择聊天
  void selectChat(Map<String, dynamic> chat) {
    _currentChat = chat;
    notifyListeners();
  }

  // 清除当前聊天
  void clearCurrentChat() {
    _currentChat = null;
    notifyListeners();
  }

  // 添加新消息到聊天
  void addMessageToChat(String chatId, Map<String, dynamic> message) {
    final chatMessages = _messages[chatId] ?? [];
    chatMessages.add(message);
    _messages[chatId] = chatMessages;
    
    // 更新聊天列表中的最后消息
    _updateChatLastMessage(chatId, message);
    
    // 如果不是当前聊天，增加未读计数
    if (_currentChat?['id'] != chatId) {
      _unreadCounts[chatId] = (_unreadCounts[chatId] ?? 0) + 1;
    }
    
    notifyListeners();
  }

  // 标记聊天为已读
  void _markChatAsRead(String chatId) {
    _unreadCounts[chatId] = 0;
  }

  // 更新聊天最后消息
  void _updateChatLastMessage(String chatId, Map<String, dynamic> message) {
    final chatIndex = _chats.indexWhere((chat) => chat['id'] == chatId);
    if (chatIndex != -1) {
      _chats[chatIndex]['last_message'] = message;
      _chats[chatIndex]['updated_at'] = message['created_at'];
    }
  }

  // 计算未读消息数
  void _calculateUnreadCounts() {
    _unreadCounts.clear();
    for (final chat in _chats) {
      final unreadCount = chat['unread_count'] ?? 0;
      if (unreadCount > 0) {
        _unreadCounts[chat['id']] = unreadCount;
      }
    }
  }

  // 获取聊天总未读数
  int get totalUnreadCount {
    return _unreadCounts.values.fold(0, (sum, count) => sum + count);
  }

  // 获取指定聊天的未读数
  int getUnreadCount(String chatId) {
    return _unreadCounts[chatId] ?? 0;
  }

  // 刷新聊天列表
  Future<void> refreshChats() async {
    await getChats();
  }

  // 刷新指定聊天的消息
  Future<void> refreshChatMessages(String chatId) async {
    await getChatMessages(chatId, refresh: true);
  }

  // 清除错误
  void clearError() {
    _clearError();
  }

  // 私有方法
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }
} 