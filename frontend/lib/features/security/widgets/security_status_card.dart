import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

class SecurityStatusCard extends StatelessWidget {
  final Map<String, dynamic> securityStatus;

  const SecurityStatusCard({
    super.key,
    required this.securityStatus,
  });

  @override
  Widget build(BuildContext context) {
    final recentDetections = securityStatus['recent_detections_count'] ?? 0;
    final activeAlerts = securityStatus['active_alerts_count'] ?? 0;
    final isBlocked = securityStatus['is_blocked'] ?? false;
    final lastDetection = securityStatus['last_detection'];

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isBlocked ? Icons.security : Icons.verified_user,
                  color: isBlocked ? Colors.red : Colors.green,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  isBlocked ? '账户已被限制' : '账户安全',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: isBlocked ? Colors.red : Colors.green,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // 统计信息
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    icon: Icons.warning,
                    label: '近期检测',
                    value: recentDetections.toString(),
                    color: recentDetections > 0 ? Colors.orange : Colors.grey,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    icon: Icons.notifications,
                    label: '安全警报',
                    value: activeAlerts.toString(),
                    color: activeAlerts > 0 ? Colors.red : Colors.grey,
                  ),
                ),
              ],
            ),
            
            if (lastDetection != null) ...[
              const SizedBox(height: 12),
              Text(
                '最后检测: ${_formatDateTime(lastDetection)}',
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
            ],
            
            if (isBlocked) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info, color: Colors.red, size: 16),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '您的账户因安全原因已被临时限制，请联系客服',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  String _formatDateTime(String dateTimeString) {
    try {
      final dateTime = DateTime.parse(dateTimeString);
      final now = DateTime.now();
      final difference = now.difference(dateTime);
      
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
      return '未知时间';
    }
  }
} 