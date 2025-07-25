import 'package:flutter/material.dart';
import '../../../../core/services/security_service.dart';

class DetectionHistoryList extends StatelessWidget {
  final List<Map<String, dynamic>> detections;
  final VoidCallback onRefresh;

  const DetectionHistoryList({
    super.key,
    required this.detections,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    if (detections.isEmpty) {
      return _buildEmptyState();
    }

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: detections.length,
        itemBuilder: (context, index) {
          final detection = detections[index];
          return _buildDetectionCard(context, detection);
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
            Icons.security,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '暂无检测记录',
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

  Widget _buildDetectionCard(BuildContext context, Map<String, dynamic> detection) {
    final detectionType = detection['detection_type'] ?? '';
    final severity = detection['severity'] ?? 'low';
    final ipAddress = detection['ip_address'] ?? '';
    final isConfirmed = detection['is_confirmed'] ?? false;
    final isFalsePositive = detection['is_false_positive'] ?? false;
    final actionTaken = detection['action_taken'] ?? '';
    final createdAt = detection['created_at'] ?? '';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: _buildSeverityIcon(severity),
        title: Text(_getDetectionTypeText(detectionType)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('IP地址: $ipAddress'),
            Text('时间: ${_formatDateTime(createdAt)}'),
            if (actionTaken.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                '处理措施: ${_getActionText(actionTaken)}',
                style: TextStyle(
                  color: _getActionColor(actionTaken),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ],
        ),
        trailing: _buildStatusChip(isConfirmed, isFalsePositive),
        onTap: () => _showDetectionDetails(context, detection),
      ),
    );
  }

  Widget _buildSeverityIcon(String severity) {
    IconData icon;
    Color color;

    switch (severity) {
      case 'critical':
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
        icon = Icons.check_circle;
        color = Colors.green;
        break;
    }

    return CircleAvatar(
      backgroundColor: color.withOpacity(0.1),
      child: Icon(icon, color: color, size: 20),
    );
  }

  Widget _buildStatusChip(bool isConfirmed, bool isFalsePositive) {
    if (isFalsePositive) {
      return const Chip(
        label: Text('误报'),
        backgroundColor: Colors.grey,
        labelStyle: TextStyle(color: Colors.white, fontSize: 12),
      );
    } else if (isConfirmed) {
      return const Chip(
        label: Text('已确认'),
        backgroundColor: Colors.red,
        labelStyle: TextStyle(color: Colors.white, fontSize: 12),
      );
    } else {
      return const Chip(
        label: Text('待确认'),
        backgroundColor: Colors.orange,
        labelStyle: TextStyle(color: Colors.white, fontSize: 12),
      );
    }
  }

  String _getDetectionTypeText(String detectionType) {
    switch (detectionType) {
      case 'screenshot':
        return '截图检测';
      case 'screen_recording':
        return '录屏检测';
      case 'mirroring':
        return '投屏检测';
      case 'virtual_display':
        return '虚拟显示器检测';
      case 'recording_app':
        return '录屏应用检测';
      case 'suspicious_activity':
        return '可疑活动';
      default:
        return '未知检测';
    }
  }

  String _getActionText(String action) {
    switch (action) {
      case 'warn':
        return '警告';
      case 'block':
        return '临时阻止';
      case 'ban':
        return '永久封禁';
      default:
        return '无';
    }
  }

  Color _getActionColor(String action) {
    switch (action) {
      case 'warn':
        return Colors.orange;
      case 'block':
        return Colors.red;
      case 'ban':
        return Colors.red[900]!;
      default:
        return Colors.grey;
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

  void _showDetectionDetails(BuildContext context, Map<String, dynamic> detection) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_getDetectionTypeText(detection['detection_type'] ?? '')),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('检测时间: ${_formatDateTime(detection['created_at'] ?? '')}'),
            Text('IP地址: ${detection['ip_address'] ?? ''}'),
            Text('严重程度: ${detection['severity'] ?? ''}'),
            if (detection['action_taken']?.isNotEmpty == true)
              Text('处理措施: ${_getActionText(detection['action_taken'])}'),
            const SizedBox(height: 16),
            const Text(
              '详细信息:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(detection['details']?.toString() ?? '无详细信息'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('关闭'),
          ),
          if (!(detection['is_false_positive'] ?? false))
            TextButton(
              onPressed: () => _reportFalsePositive(context, detection),
              child: const Text('报告误报'),
            ),
        ],
      ),
    );
  }

  void _reportFalsePositive(BuildContext context, Map<String, dynamic> detection) {
    final TextEditingController reasonController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('报告误报'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('请说明为什么这是误报:'),
            const SizedBox(height: 16),
            TextField(
              controller: reasonController,
              decoration: const InputDecoration(
                hintText: '请输入原因...',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (reasonController.text.trim().isNotEmpty) {
                Navigator.pop(context);
                await _submitFalsePositiveReport(detection['id'], reasonController.text);
              }
            },
            child: const Text('提交'),
          ),
        ],
      ),
    );
  }

  Future<void> _submitFalsePositiveReport(String detectionId, String reason) async {
    try {
      final securityService = SecurityService();
      final success = await securityService.reportFalsePositive(detectionId, reason);
      
      if (success) {
        // 刷新数据
        onRefresh();
      }
    } catch (e) {
      debugPrint('报告误报失败: $e');
    }
  }
} 