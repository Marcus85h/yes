import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/chat_provider.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';

class ChatListPage extends StatefulWidget {
  const ChatListPage({super.key});

  @override
  State<ChatListPage> createState() => _ChatListPageState();
}

class _ChatListPageState extends State<ChatListPage> {
  @override
  void initState() {
    super.initState();
    _loadChats();
  }

  void _loadChats() async {
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    await chatProvider.getChats();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: 实现搜索聊天功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('搜索聊天功能开发中')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // TODO: 实现更多功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('更多功能开发中')),
              );
            },
          ),
        ],
      ),
      body: Consumer<ChatProvider>(
        builder: (context, chatProvider, child) {
          if (chatProvider.isLoading && chatProvider.chats.isEmpty) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (chatProvider.chats.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.chat_bubble_outline,
                    size: 80,
                    color: AppTheme.textSecondaryColor,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '还没有聊天记录',
                    style: TextStyle(
                      color: AppTheme.textSecondaryColor,
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '开始与朋友聊天吧',
                    style: TextStyle(
                      color: AppTheme.textHintColor,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () {
                      // TODO: 实现开始聊天功能
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('开始聊天功能开发中')),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('开始聊天'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              await chatProvider.refreshChats();
            },
            child: ListView.builder(
              itemCount: chatProvider.chats.length,
              itemBuilder: (context, index) {
                final chat = chatProvider.chats[index];
                return _buildChatItem(chat);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildChatItem(Map<String, dynamic> chat) {
    final otherUser = chat['other_user'];
    final lastMessage = chat['last_message'];
    final unreadCount = chat['unread_count'] ?? 0;

    return ListTile(
      leading: Stack(
        children: [
          CircleAvatar(
            radius: 25,
            backgroundImage: otherUser?['avatar'] != null
                ? NetworkImage(otherUser['avatar'])
                : null,
            child: otherUser?['avatar'] == null
                ? Text(
                    otherUser?['name']?[0] ?? '?',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  )
                : null,
          ),
          if (otherUser?['is_online'] == true)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: AppTheme.successColor,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Theme.of(context).scaffoldBackgroundColor,
                    width: 2,
                  ),
                ),
              ),
            ),
        ],
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(
              otherUser?['name'] ?? '未知用户',
              style: TextStyle(
                fontWeight: unreadCount > 0 ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
          Text(
            _formatTime(chat['updated_at']),
            style: TextStyle(
              color: AppTheme.textHintColor,
              fontSize: 12,
            ),
          ),
        ],
      ),
      subtitle: Row(
        children: [
          Expanded(
            child: Text(
              lastMessage?['content'] ?? '暂无消息',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: unreadCount > 0
                    ? AppTheme.textPrimaryColor
                    : AppTheme.textSecondaryColor,
                fontWeight: unreadCount > 0 ? FontWeight.w500 : FontWeight.normal,
              ),
            ),
          ),
          if (unreadCount > 0) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.errorColor,
                borderRadius: BorderRadius.circular(10),
              ),
              constraints: const BoxConstraints(
                minWidth: 16,
                minHeight: 16,
              ),
              child: Text(
                unreadCount > 99 ? '99+' : unreadCount.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ],
      ),
      onTap: () {
        AppRouter.navigateToChatDetail(
          chat['id'],
          otherUser: otherUser,
        );
      },
      onLongPress: () {
        _showChatOptions(chat);
      },
    );
  }

  void _showChatOptions(Map<String, dynamic> chat) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.delete),
                title: const Text('删除聊天'),
                onTap: () {
                  Navigator.pop(context);
                  _deleteChat(chat);
                },
              ),
              ListTile(
                leading: const Icon(Icons.block),
                title: const Text('屏蔽用户'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现屏蔽用户功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('屏蔽用户功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.report),
                title: const Text('举报用户'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现举报用户功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('举报用户功能开发中')),
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _deleteChat(Map<String, dynamic> chat) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('删除聊天'),
          content: const Text('确定要删除这个聊天记录吗？此操作不可撤销。'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                // TODO: 实现删除聊天功能
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('删除聊天功能开发中')),
                );
              },
              child: const Text('删除'),
            ),
          ],
        );
      },
    );
  }

  String _formatTime(String? timeStr) {
    if (timeStr == null) return '';
    
    try {
      final time = DateTime.parse(timeStr);
      final now = DateTime.now();
      final difference = now.difference(time);
      
      if (difference.inDays > 0) {
        return '${difference.inDays}天前';
      } else if (difference.inHours > 0) {
        return '${difference.inHours}小时前';
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