import 'package:flutter/material.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/chat_provider.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';
import '../widgets/user_card.dart';
import '../widgets/feature_card.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('home.title'.tr()),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: 实现搜索功能
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('common.search'.tr())),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              // TODO: 实现通知功能
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('notifications.title'.tr())),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 欢迎信息
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'home.title'.tr(),
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'home.discover'.tr(),
                      style: TextStyle(
                        fontSize: 16,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 功能卡片
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.2,
              children: [
                _buildFeatureCard(
                  context,
                  icon: Icons.chat,
                  title: 'chat.title'.tr(),
                  subtitle: 'chat.conversations'.tr(),
                  onTap: () => Navigator.pushNamed(context, AppRouter.chatList),
                ),
                _buildFeatureCard(
                  context,
                  icon: Icons.video_call,
                  title: 'calls.title'.tr(),
                  subtitle: 'calls.videoCall'.tr(),
                  onTap: () => Navigator.pushNamed(context, AppRouter.call),
                ),
                _buildFeatureCard(
                  context,
                  icon: Icons.people,
                  title: 'rooms.title'.tr(),
                  subtitle: 'rooms.participants'.tr(),
                  onTap: () => Navigator.pushNamed(context, AppRouter.roomList),
                ),
                _buildFeatureCard(
                  context,
                  icon: Icons.person,
                  title: 'profile.title'.tr(),
                  subtitle: 'profile.editProfile'.tr(),
                  onTap: () => Navigator.pushNamed(context, AppRouter.profile),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // 推荐用户
            Text(
              'home.recommendations'.tr(),
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 120,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: 5,
                itemBuilder: (context, index) {
                  return Card(
                    margin: const EdgeInsets.only(right: 12),
                    child: Container(
                      width: 100,
                      padding: const EdgeInsets.all(8),
                      child: Column(
                        children: [
                          CircleAvatar(
                            radius: 30,
                            backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
                            child: Icon(
                              Icons.person,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'User ${index + 1}',
                            style: const TextStyle(fontSize: 12),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 32,
                color: AppTheme.primaryColor,
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: AppTheme.textSecondaryColor,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class HomeTab extends StatefulWidget {
  const HomeTab({super.key});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  void _loadUserProfile() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.refreshProfile();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('视频交友'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: 实现搜索功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('搜索功能开发中')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              // TODO: 实现通知功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('通知功能开发中')),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 用户信息卡片
            Consumer<AuthProvider>(
              builder: (context, authProvider, child) {
                final user = authProvider.user;
                if (user != null) {
                  return UserCard(user: user);
                }
                return const SizedBox.shrink();
              },
            ),
            
            const SizedBox(height: 24),
            
            // 功能模块
            Text(
              '功能模块',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            
            const SizedBox(height: 16),
            
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.2,
              children: [
                FeatureCard(
                  icon: Icons.videocam,
                  title: '视频通话',
                  subtitle: '开始视频聊天',
                  color: AppTheme.primaryColor,
                  onTap: () {
                    // TODO: 实现视频通话功能
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('视频通话功能开发中')),
                    );
                  },
                ),
                FeatureCard(
                  icon: Icons.call,
                  title: '语音通话',
                  subtitle: '开始语音聊天',
                  color: AppTheme.secondaryColor,
                  onTap: () {
                    // TODO: 实现语音通话功能
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('语音通话功能开发中')),
                    );
                  },
                ),
                FeatureCard(
                  icon: Icons.people,
                  title: '多人房间',
                  subtitle: '加入聊天房间',
                  color: AppTheme.accentColor,
                  onTap: () {
                    AppRouter.pushNamed(AppRouter.roomList);
                  },
                ),
                FeatureCard(
                  icon: Icons.explore,
                  title: '发现',
                  subtitle: '发现新朋友',
                  color: AppTheme.infoColor,
                  onTap: () {
                    // TODO: 实现发现功能
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('发现功能开发中')),
                    );
                  },
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // 最近聊天
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '最近聊天',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                TextButton(
                  onPressed: () {
                    AppRouter.pushNamed(AppRouter.chatList);
                  },
                  child: const Text('查看全部'),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                final chats = chatProvider.chats.take(3).toList();
                if (chats.isEmpty) {
                  return Container(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(
                          Icons.chat_bubble_outline,
                          size: 64,
                          color: AppTheme.textSecondaryColor,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '还没有聊天记录',
                          style: TextStyle(
                            color: AppTheme.textSecondaryColor,
                            fontSize: 16,
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
                      ],
                    ),
                  );
                }
                
                return Column(
                  children: chats.map((chat) {
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundImage: chat['other_user']?['avatar'] != null
                            ? NetworkImage(chat['other_user']['avatar'])
                            : null,
                        child: chat['other_user']?['avatar'] == null
                            ? Text(chat['other_user']?['name']?[0] ?? '?')
                            : null,
                      ),
                      title: Text(chat['other_user']?['name'] ?? '未知用户'),
                      subtitle: Text(
                        chat['last_message']?['content'] ?? '暂无消息',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      trailing: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            _formatTime(chat['updated_at']),
                            style: TextStyle(
                              color: AppTheme.textHintColor,
                              fontSize: 12,
                            ),
                          ),
                          if (chat['unread_count'] > 0)
                            Container(
                              padding: const EdgeInsets.all(4),
                              decoration: BoxDecoration(
                                color: AppTheme.errorColor,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              constraints: const BoxConstraints(
                                minWidth: 16,
                                minHeight: 16,
                              ),
                              child: Text(
                                chat['unread_count'] > 99
                                    ? '99+'
                                    : chat['unread_count'].toString(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                        ],
                      ),
                      onTap: () {
                        AppRouter.navigateToChatDetail(
                          chat['id'],
                          otherUser: chat['other_user'],
                        );
                      },
                    );
                  }).toList(),
                );
              },
            ),
          ],
        ),
      ),
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