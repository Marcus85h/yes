import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/chat_provider.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/websocket_service.dart';

class ChatDetailPage extends StatefulWidget {
  final String chatId;
  final Map<String, dynamic>? otherUser;

  const ChatDetailPage({
    super.key,
    required this.chatId,
    this.otherUser,
  });

  @override
  State<ChatDetailPage> createState() => _ChatDetailPageState();
}

class _ChatDetailPageState extends State<ChatDetailPage> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  bool _isTyping = false;
  Timer? _typingTimer;
  StreamSubscription<Map<String, dynamic>>? _messageSubscription;

  @override
  void initState() {
    super.initState();
    _loadMessages();
    _connectWebSocket();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _typingTimer?.cancel();
    _messageSubscription?.cancel();
    WebSocketService.instance.disconnect();
    super.dispose();
  }

  void _loadMessages() async {
    setState(() => _isLoading = true);
    
    try {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      await chatProvider.getChatMessages(widget.chatId);
      
      setState(() {
        _messages = chatProvider.messages[widget.chatId] ?? [];
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载消息失败: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _connectWebSocket() async {
    try {
      final success = await WebSocketService.instance.connect(roomId: widget.chatId);
      if (success) {
        _messageSubscription = WebSocketService.instance.messageStream.listen((message) {
          _handleWebSocketMessage(message);
        });
      }
    } catch (e) {
      print('WebSocket连接失败: $e');
    }
  }

  void _handleWebSocketMessage(Map<String, dynamic> message) {
    final messageType = message['type'];
    
    switch (messageType) {
      case 'chat_message':
        _addMessage(message);
        break;
      case 'user_typing':
        _handleUserTyping(message);
        break;
      case 'user_joined':
      case 'user_left':
        _handleUserStatusChange(message);
        break;
    }
  }

  void _addMessage(Map<String, dynamic> message) {
    setState(() {
      _messages.add(message);
    });
    _scrollToBottom();
  }

  void _handleUserTyping(Map<String, dynamic> message) {
    // TODO: 显示用户正在输入状态
  }

  void _handleUserStatusChange(Map<String, dynamic> message) {
    // TODO: 显示用户状态变化
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _sendMessage() {
    final content = _messageController.text.trim();
    if (content.isEmpty) return;

    // 发送WebSocket消息
    WebSocketService.instance.sendChatMessage(content);
    
    // 清空输入框
    _messageController.clear();
    
    // 停止输入状态
    _stopTyping();
  }

  void _startTyping() {
    if (!_isTyping) {
      setState(() => _isTyping = true);
      WebSocketService.instance.sendTyping(true);
    }
    
    _typingTimer?.cancel();
    _typingTimer = Timer(const Duration(seconds: 3), _stopTyping);
  }

  void _stopTyping() {
    if (_isTyping) {
      setState(() => _isTyping = false);
      WebSocketService.instance.sendTyping(false);
    }
    _typingTimer?.cancel();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              backgroundImage: widget.otherUser?['avatar'] != null
                  ? NetworkImage(widget.otherUser!['avatar'])
                  : null,
              child: widget.otherUser?['avatar'] == null
                  ? Text(widget.otherUser?['name']?[0] ?? '?')
                  : null,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.otherUser?['name'] ?? '未知用户',
                    style: const TextStyle(fontSize: 16),
                  ),
                  Text(
                    widget.otherUser?['is_online'] == true ? '在线' : '离线',
                    style: TextStyle(
                      fontSize: 12,
                      color: widget.otherUser?['is_online'] == true
                          ? AppTheme.successColor
                          : AppTheme.textSecondaryColor,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.videocam),
            onPressed: () {
              // TODO: 实现视频通话功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('视频通话功能开发中')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.call),
            onPressed: () {
              // TODO: 实现语音通话功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('语音通话功能开发中')),
              );
            },
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'profile':
                  // TODO: 实现查看用户资料功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('查看用户资料功能开发中')),
                  );
                  break;
                case 'block':
                  // TODO: 实现屏蔽用户功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('屏蔽用户功能开发中')),
                  );
                  break;
                case 'report':
                  // TODO: 实现举报用户功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('举报用户功能开发中')),
                  );
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: [
                    Icon(Icons.person),
                    SizedBox(width: 8),
                    Text('查看资料'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'block',
                child: Row(
                  children: [
                    Icon(Icons.block),
                    SizedBox(width: 8),
                    Text('屏蔽用户'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'report',
                child: Row(
                  children: [
                    Icon(Icons.report),
                    SizedBox(width: 8),
                    Text('举报用户'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                final messages = chatProvider.messages[widget.chatId] ?? [];
                
                if (chatProvider.isLoading && messages.isEmpty) {
                  return const Center(
                    child: CircularProgressIndicator(),
                  );
                }

                if (messages.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.chat_bubble_outline,
                          size: 64,
                          color: AppTheme.textSecondaryColor,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '开始聊天吧',
                          style: TextStyle(
                            color: AppTheme.textSecondaryColor,
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '发送第一条消息开始对话',
                          style: TextStyle(
                            color: AppTheme.textHintColor,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    return _buildMessageItem(message);
                  },
                );
              },
            ),
          ),
          
          // 输入框
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              border: Border(
                top: BorderSide(
                  color: AppTheme.borderColor,
                  width: 1,
                ),
              ),
            ),
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.attach_file),
                  onPressed: () {
                    // TODO: 实现文件附件功能
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('文件附件功能开发中')),
                    );
                  },
                ),
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: '输入消息...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.all(Radius.circular(24)),
                      ),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendMessage,
                  color: AppTheme.primaryColor,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageItem(Map<String, dynamic> message) {
    final isMe = message['sender']?['id'] == 'current_user_id'; // TODO: 获取当前用户ID
    final content = message['content'] ?? '';
    final timestamp = message['created_at'];
    final messageType = message['type'] ?? 'text';

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMe) ...[
            CircleAvatar(
              radius: 16,
              backgroundImage: message['sender']?['avatar'] != null
                  ? NetworkImage(message['sender']['avatar'])
                  : null,
              child: message['sender']?['avatar'] == null
                  ? Text(message['sender']?['name']?[0] ?? '?')
                  : null,
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: isMe ? AppTheme.primaryColor : AppTheme.surfaceColor,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 2,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: _buildMessageContent(messageType, content),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTime(timestamp),
                  style: TextStyle(
                    fontSize: 12,
                    color: AppTheme.textHintColor,
                  ),
                ),
              ],
            ),
          ),
          if (isMe) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundImage: message['sender']?['avatar'] != null
                  ? NetworkImage(message['sender']['avatar'])
                  : null,
              child: message['sender']?['avatar'] == null
                  ? Text(message['sender']?['name']?[0] ?? '?')
                  : null,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMessageContent(String type, String content) {
    switch (type) {
      case 'text':
        return Text(
          content,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
          ),
        );
      case 'image':
        return ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(
            content,
            width: 200,
            height: 150,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) {
              return Container(
                width: 200,
                height: 150,
                color: AppTheme.textSecondaryColor,
                child: const Icon(
                  Icons.broken_image,
                  color: Colors.white,
                ),
              );
            },
          ),
        );
      case 'file':
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.attach_file, color: Colors.white),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                content,
                style: const TextStyle(color: Colors.white),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        );
      default:
        return Text(
          content,
          style: const TextStyle(color: Colors.white),
        );
    }
  }

  String _formatTime(String? timeStr) {
    if (timeStr == null) return '';
    
    try {
      final time = DateTime.parse(timeStr);
      final now = DateTime.now();
      final difference = now.difference(time);
      
      if (difference.inDays > 0) {
        return '${time.month}-${time.day} ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
      } else if (difference.inHours > 0) {
        return '${time.hour}:${time.minute.toString().padLeft(2, '0')}';
      } else if (difference.inMinutes > 0) {
        return '${difference.inMinutes}分钟前';
      } else {
        return '刚刚';
      }
    } catch (e) {
      return '';
    }
  }
} 