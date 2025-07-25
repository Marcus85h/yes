import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/services/security_service.dart';
import '../../../core/theme/app_theme.dart';
import '../widgets/security_status_card.dart';
import '../widgets/detection_history_list.dart';
import '../widgets/security_alerts_list.dart';

class SecurityPage extends StatefulWidget {
  const SecurityPage({super.key});

  @override
  State<SecurityPage> createState() => _SecurityPageState();
}

class _SecurityPageState extends State<SecurityPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final SecurityService _securityService = SecurityService();
  
  Map<String, dynamic> _securityStatus = {};
  List<Map<String, dynamic>> _detections = [];
  List<Map<String, dynamic>> _alerts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // 并行加载数据
      final futures = await Future.wait([
        _securityService.getSecurityStatus(),
        _securityService.getDetectionHistory(),
        _securityService.getSecurityAlerts(),
      ]);

      setState(() {
        _securityStatus = futures[0];
        _detections = List<Map<String, dynamic>>.from(futures[1]['detections'] ?? []);
        _alerts = List<Map<String, dynamic>>.from(futures[2]['alerts'] ?? []);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载数据失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('安全中心'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // 安全状态卡片
                SecurityStatusCard(securityStatus: _securityStatus),
                
                // 标签页
                Container(
                  color: AppTheme.primaryColor,
                  child: TabBar(
                    controller: _tabController,
                    indicatorColor: Colors.white,
                    labelColor: Colors.white,
                    unselectedLabelColor: Colors.white70,
                    tabs: const [
                      Tab(text: '检测历史'),
                      Tab(text: '安全警报'),
                      Tab(text: '防护设置'),
                    ],
                  ),
                ),
                
                // 标签页内容
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      // 检测历史
                      DetectionHistoryList(
                        detections: _detections,
                        onRefresh: _loadData,
                      ),
                      
                      // 安全警报
                      SecurityAlertsList(
                        alerts: _alerts,
                        onRefresh: _loadData,
                      ),
                      
                      // 防护设置
                      _buildProtectionSettings(),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildProtectionSettings() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 防录屏设置
        Card(
          child: ListTile(
            leading: const Icon(Icons.screen_lock_portrait, color: Colors.orange),
            title: const Text('防录屏检测'),
            subtitle: const Text('检测并阻止录屏行为'),
            trailing: Switch(
              value: true, // 从配置中获取
              onChanged: (value) {
                // 更新设置
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('设置已${value ? '启用' : '禁用'}')),
                );
              },
            ),
          ),
        ),
        
        // 截图检测设置
        Card(
          child: ListTile(
            leading: const Icon(Icons.camera_alt, color: Colors.blue),
            title: const Text('截图检测'),
            subtitle: const Text('检测频繁截图行为'),
            trailing: Switch(
              value: true,
              onChanged: (value) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('设置已${value ? '启用' : '禁用'}')),
                );
              },
            ),
          ),
        ),
        
        // 虚拟机检测设置
        Card(
          child: ListTile(
            leading: const Icon(Icons.computer, color: Colors.green),
            title: const Text('虚拟机检测'),
            subtitle: const Text('检测虚拟环境'),
            trailing: Switch(
              value: true,
              onChanged: (value) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('设置已${value ? '启用' : '禁用'}')),
                );
              },
            ),
          ),
        ),
        
        // 调试器检测设置
        Card(
          child: ListTile(
            leading: const Icon(Icons.bug_report, color: Colors.red),
            title: const Text('调试器检测'),
            subtitle: const Text('检测调试工具'),
            trailing: Switch(
              value: true,
              onChanged: (value) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('设置已${value ? '启用' : '禁用'}')),
                );
              },
            ),
          ),
        ),
        
        const SizedBox(height: 20),
        
        // 检测阈值设置
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '检测阈值设置',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                
                // 检测间隔
                Row(
                  children: [
                    const Expanded(
                      child: Text('检测间隔:'),
                    ),
                    DropdownButton<int>(
                      value: 5,
                      items: const [
                        DropdownMenuItem(value: 3, child: Text('3秒')),
                        DropdownMenuItem(value: 5, child: Text('5秒')),
                        DropdownMenuItem(value: 10, child: Text('10秒')),
                      ],
                      onChanged: (value) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('检测间隔已设置为${value}秒')),
                        );
                      },
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                // 警告阈值
                Row(
                  children: [
                    const Expanded(
                      child: Text('警告阈值:'),
                    ),
                    DropdownButton<int>(
                      value: 3,
                      items: const [
                        DropdownMenuItem(value: 1, child: Text('1次')),
                        DropdownMenuItem(value: 3, child: Text('3次')),
                        DropdownMenuItem(value: 5, child: Text('5次')),
                      ],
                      onChanged: (value) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('警告阈值已设置为${value}次')),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 20),
        
        // 防护措施设置
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '防护措施',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                
                // 检测到录屏时的动作
                const Text('检测到录屏时的动作:'),
                const SizedBox(height: 8),
                
                RadioListTile<String>(
                  title: const Text('仅警告'),
                  value: 'warn',
                  groupValue: 'warn',
                  onChanged: (value) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('防护措施已设置为仅警告')),
                    );
                  },
                ),
                
                RadioListTile<String>(
                  title: const Text('临时阻止'),
                  value: 'block',
                  groupValue: 'warn',
                  onChanged: (value) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('防护措施已设置为临时阻止')),
                    );
                  },
                ),
                
                RadioListTile<String>(
                  title: const Text('永久封禁'),
                  value: 'ban',
                  groupValue: 'warn',
                  onChanged: (value) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('防护措施已设置为永久封禁')),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
} 