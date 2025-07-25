import 'package:flutter/material.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';

class RoomListPage extends StatelessWidget {
  const RoomListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天房间'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: 实现搜索房间功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('搜索房间功能开发中')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              // TODO: 实现创建房间功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('创建房间功能开发中')),
              );
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.people_outline,
              size: 80,
              color: AppTheme.textSecondaryColor,
            ),
            const SizedBox(height: 16),
            Text(
              '房间功能开发中',
              style: TextStyle(
                color: AppTheme.textSecondaryColor,
                fontSize: 18,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '多人聊天房间功能正在开发中',
              style: TextStyle(
                color: AppTheme.textHintColor,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
} 