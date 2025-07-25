import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

class UserCard extends StatelessWidget {
  final Map<String, dynamic> user;

  const UserCard({
    super.key,
    required this.user,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // 头像
            CircleAvatar(
              radius: 30,
              backgroundImage: user['avatar'] != null
                  ? NetworkImage(user['avatar'])
                  : null,
              child: user['avatar'] == null
                  ? Text(
                      user['name']?[0] ?? '?',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    )
                  : null,
            ),
            
            const SizedBox(width: 16),
            
            // 用户信息
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    user['name'] ?? '未知用户',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user['bio'] ?? '这个人很懒，什么都没写',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.textSecondaryColor,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.location_on,
                        size: 16,
                        color: AppTheme.textSecondaryColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        user['location'] ?? '未知地区',
                        style: TextStyle(
                          color: AppTheme.textSecondaryColor,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Icon(
                        Icons.access_time,
                        size: 16,
                        color: AppTheme.textSecondaryColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _formatLastSeen(user['last_seen']),
                        style: TextStyle(
                          color: AppTheme.textSecondaryColor,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            // 编辑按钮
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () {
                // TODO: 实现编辑资料功能
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('编辑资料功能开发中')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  String _formatLastSeen(String? lastSeen) {
    if (lastSeen == null) return '离线';
    
    try {
      final time = DateTime.parse(lastSeen);
      final now = DateTime.now();
      final difference = now.difference(time);
      
      if (difference.inMinutes < 1) {
        return '在线';
      } else if (difference.inHours < 1) {
        return '${difference.inMinutes}分钟前';
      } else if (difference.inDays < 1) {
        return '${difference.inHours}小时前';
      } else {
        return '${difference.inDays}天前';
      }
    } catch (e) {
      return '离线';
    }
  }
} 