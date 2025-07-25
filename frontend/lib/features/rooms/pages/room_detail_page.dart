import 'package:flutter/material.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';

class RoomDetailPage extends StatefulWidget {
  final String roomId;
  final Map<String, dynamic>? room;

  const RoomDetailPage({
    super.key,
    required this.roomId,
    this.room,
  });

  @override
  State<RoomDetailPage> createState() => _RoomDetailPageState();
}

class _RoomDetailPageState extends State<RoomDetailPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.room?['name'] ?? '聊天房间'),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              _showRoomOptions();
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
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                AppRouter.pop();
              },
              child: const Text('返回'),
            ),
          ],
        ),
      ),
    );
  }

  void _showRoomOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text('编辑房间'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现编辑房间功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('编辑房间功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.people),
                title: const Text('管理成员'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现管理成员功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('管理成员功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.settings),
                title: const Text('房间设置'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现房间设置功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('房间设置功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.exit_to_app),
                title: const Text('退出房间'),
                onTap: () {
                  Navigator.pop(context);
                  _leaveRoom();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _leaveRoom() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('退出房间'),
          content: const Text('确定要退出这个房间吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                AppRouter.pop();
              },
              child: const Text('退出'),
            ),
          ],
        );
      },
    );
  }
} 