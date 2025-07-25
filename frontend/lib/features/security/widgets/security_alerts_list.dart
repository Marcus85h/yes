import 'package:flutter/material.dart';
import '../../../../core/services/security_service.dart';

class SecurityAlertsList extends StatelessWidget {
  final List<Map<String, dynamic>> alerts;
  final VoidCallback onRefresh;

  const SecurityAlertsList({
    super.key,
    required this.alerts,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    if (alerts.isEmpty) {
      return _buildEmptyState();
    }

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: alerts.length,
        itemBuilder: (context, index) {
          final alert = alerts[index];
          return _buildAlertCard(context, alert);
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.notifications_none,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '暂无安全警报',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '您的账户目前很安全',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard(BuildContext context, Map<String, dynamic> alert) {
    final alertType = alert['alert_type'] ?? '';
    final priority = alert['priority'] ?? 'medium';
    final title = alert['title'] ?? '';
    final message = alert['message'] ?? '';
    final isRead = alert['is_read'] ?? false;
    final createdAt = alert['created_at'] ?? '';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: _buildPriorityIcon(priority),
        title: Row(
          children: [
            Expanded(child: Text(title)),
            if (!isRead)
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(message),
            const SizedBox(height: 4),
            Text(
              '时间: ${_formatDateTime(createdAt)}',
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
        trailing: _buildPriorityChip(priority),
        onTap: () => _showAlertDetails(context, alert),
      ),
    );
  }

  Widget _buildPriorityIcon(String priority) {
    IconData icon;
    Color color;

    switch (priority) {
      case 'urgent':
        icon = Icons.error;
        color = Colors.red;
        break;
      case 'high':
        icon = Icons.warning;
        color = Colors.orange;
        break;
      case 'medium':
        icon = Icons.info;
        color = Colors.blue;
        break;
      case 'low':
      default:
        icon = Icons.notifications;
        color = Colors.grey;
        break;
    }

    return CircleAvatar(
      backgroundColor: color.withOpacity(0.1),
      child: Icon(icon, color: color, size: 20),
    );
  }

  Widget _buildPriorityChip(String priority) {
    Color backgroundColor;
    String text;

    switch (priority) {
      case 'urgent':
        backgroundColor = Colors.red;
        text = '紧急';
        break;
      case 'high':
        backgroundColor = Colors.orange;
        text = '高';
        break;
      case 'medium':
        backgroundColor = Colors.blue;
        text = '中';
        break;
      case 'low':
      default:
        backgroundColor = Colors.grey;
        text = '低';
        break;
    }

    return Chip(
      label: Text(
        text,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      backgroundColor: backgroundColor,
    );
  }

  String _getAlertTypeText(String alertType) {
    switch (alertType) {
      case 'screen_recording':
        return '录屏警报';
      case 'suspicious_activity':
        return '可疑活动';
      case 'multiple_violations':
        return '多次违规';
      case 'account_compromise':
        return '账户泄露';
      default:
        return '未知警报';
    }
  }

  String _formatDateTime(String dateTimeString) {
    try {
      final dateTime = DateTime.parse(dateTimeString);
      return '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} '
          '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '未知时间';
    }
  }

  void _showAlertDetails(BuildContext context, Map<String, dynamic> alert) {
    final alertId = alert['id'];
    final isRead = alert['is_read'] ?? false;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(alert['title'] ?? ''),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('警报类型: ${_getAlertTypeText(alert['alert_type'] ?? '')}'),
            Text('优先级: ${alert['priority'] ?? ''}'),
            Text('时间: ${_formatDateTime(alert['created_at'] ?? '')}'),
            const SizedBox(height: 16),
            const Text(
              '详细信息:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(alert['message'] ?? ''),
            if (alert['details'] != null) ...[
              const SizedBox(height: 16),
              const Text(
                '技术详情:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(alert['details'].toString()),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('关闭'),
          ),
          if (!isRead)
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await _markAlertAsRead(alertId);
              },
              child: const Text('标记已读'),
            ),
        ],
      ),
    );
  }

  Future<void> _markAlertAsRead(String alertId) async {
    try {
      final securityService = SecurityService();
      final success = await securityService.markAlertAsRead(alertId);
      
      if (success) {
        // 刷新数据
        onRefresh();
      }
    } catch (e) {
      debugPrint('标记警报为已读失败: $e');
    }
  }
} 