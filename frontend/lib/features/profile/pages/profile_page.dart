import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../settings/pages/language_settings_page.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: 实现设置功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('设置功能开发中')),
              );
            },
          ),
        ],
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          final user = authProvider.user;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // 用户信息卡片
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 40,
                          backgroundImage: user?['avatar'] != null
                              ? NetworkImage(user['avatar'])
                              : null,
                          child: user?['avatar'] == null
                              ? Text(
                                  user?['name']?[0] ?? '?',
                                  style: const TextStyle(
                                    fontSize: 32,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              : null,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                user?['name'] ?? '未知用户',
                                style: Theme.of(context).textTheme.headlineSmall,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                user?['email'] ?? '未知邮箱',
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: AppTheme.textSecondaryColor,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                user?['bio'] ?? '这个人很懒，什么都没写',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: AppTheme.textSecondaryColor,
                                ),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () {
                            Navigator.pushNamed(context, '/edit-profile');
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 功能列表
                Card(
                  child: Column(
                    children: [
                      _buildProfileItem(
                        icon: Icons.person,
                        title: '个人资料',
                        subtitle: '编辑个人信息',
                        onTap: () {
                          Navigator.pushNamed(context, '/edit-profile');
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.security,
                        title: '隐私设置',
                        subtitle: '管理隐私和安全',
                        onTap: () {
                          // TODO: 实现隐私设置功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('隐私设置功能开发中')),
                          );
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.notifications,
                        title: '通知设置',
                        subtitle: '管理推送通知',
                        onTap: () {
                          // TODO: 实现通知设置功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('通知设置功能开发中')),
                          );
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.language,
                        title: '语言设置',
                        subtitle: '选择应用语言',
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const LanguageSettingsPage(),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // 其他功能
                Card(
                  child: Column(
                    children: [
                      _buildProfileItem(
                        icon: Icons.help,
                        title: '帮助与反馈',
                        subtitle: '获取帮助和反馈',
                        onTap: () {
                          // TODO: 实现帮助功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('帮助功能开发中')),
                          );
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.info,
                        title: '关于我们',
                        subtitle: '了解应用信息',
                        onTap: () {
                          // TODO: 实现关于功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('关于功能开发中')),
                          );
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.privacy_tip,
                        title: '隐私政策',
                        subtitle: '查看隐私政策',
                        onTap: () {
                          // TODO: 实现隐私政策功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('隐私政策功能开发中')),
                          );
                        },
                      ),
                      _buildProfileItem(
                        icon: Icons.description,
                        title: '用户协议',
                        subtitle: '查看用户协议',
                        onTap: () {
                          // TODO: 实现用户协议功能
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('用户协议功能开发中')),
                          );
                        },
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 退出登录按钮
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () async {
                      final confirmed = await showDialog<bool>(
                        context: context,
                        builder: (context) {
                          return AlertDialog(
                            title: const Text('退出登录'),
                            content: const Text('确定要退出登录吗？'),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context, false),
                                child: const Text('取消'),
                              ),
                              TextButton(
                                onPressed: () => Navigator.pop(context, true),
                                child: const Text('退出'),
                              ),
                            ],
                          );
                        },
                      );
                      
                      if (confirmed == true) {
                        await authProvider.logout();
                        if (context.mounted) {
                          AppRouter.navigateToAuth();
                        }
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.errorColor,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('退出登录'),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildProfileItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          color: AppTheme.primaryColor,
          size: 20,
        ),
      ),
      title: Text(title),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: AppTheme.textSecondaryColor,
          fontSize: 12,
        ),
      ),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
} 