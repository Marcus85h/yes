import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/services/analytics_service.dart';
import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class AdminDashboardPage extends StatefulWidget {
  const AdminDashboardPage({Key? key}) : super(key: key);

  @override
  State<AdminDashboardPage> createState() => _AdminDashboardPageState();
}

class _AdminDashboardPageState extends State<AdminDashboardPage>
    with TickerProviderStateMixin {
  late TabController _tabController;
  
  // 统计数据
  Map<String, dynamic> _stats = {};
  List<Map<String, dynamic>> _recentUsers = [];
  List<Map<String, dynamic>> _recentActivities = [];
  List<Map<String, dynamic>> _systemAlerts = [];
  
  // 图表数据
  List<FlSpot> _userGrowthData = [];
  List<FlSpot> _revenueData = [];
  List<FlSpot> _activeUsersData = [];
  
  // 加载状态
  bool _isLoading = true;
  bool _isRefreshing = false;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadDashboardData();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  /// 加载仪表板数据
  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    
    try {
      await Future.wait([
        _loadStats(),
        _loadRecentUsers(),
        _loadRecentActivities(),
        _loadSystemAlerts(),
        _loadChartData(),
      ]);
    } catch (e) {
      _showErrorSnackBar('加载数据失败: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  /// 刷新数据
  Future<void> _refreshData() async {
    setState(() => _isRefreshing = true);
    await _loadDashboardData();
    setState(() => _isRefreshing = false);
  }
  
  /// 加载统计数据
  Future<void> _loadStats() async {
    final response = await ApiService.get('/admin/stats/');
    setState(() {
      _stats = response['data'] ?? {};
    });
  }
  
  /// 加载最近用户
  Future<void> _loadRecentUsers() async {
    final response = await ApiService.get('/admin/users/recent/');
    setState(() {
      _recentUsers = List<Map<String, dynamic>>.from(response['data'] ?? []);
    });
  }
  
  /// 加载最近活动
  Future<void> _loadRecentActivities() async {
    final response = await ApiService.get('/admin/activities/recent/');
    setState(() {
      _recentActivities = List<Map<String, dynamic>>.from(response['data'] ?? []);
    });
  }
  
  /// 加载系统警报
  Future<void> _loadSystemAlerts() async {
    final response = await ApiService.get('/admin/alerts/');
    setState(() {
      _systemAlerts = List<Map<String, dynamic>>.from(response['data'] ?? []);
    });
  }
  
  /// 加载图表数据
  Future<void> _loadChartData() async {
    final response = await ApiService.get('/admin/charts/');
    final data = response['data'] ?? {};
    
    setState(() {
      _userGrowthData = _parseChartData(data['user_growth'] ?? []);
      _revenueData = _parseChartData(data['revenue'] ?? []);
      _activeUsersData = _parseChartData(data['active_users'] ?? []);
    });
  }
  
  /// 解析图表数据
  List<FlSpot> _parseChartData(List<dynamic> data) {
    return data.asMap().entries.map((entry) {
      final index = entry.key.toDouble();
      final value = (entry.value['value'] ?? 0).toDouble();
      return FlSpot(index, value);
    }).toList();
  }
  
  /// 显示错误提示
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('管理后台'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isRefreshing ? null : _refreshData,
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _navigateToSettings(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '概览', icon: Icon(Icons.dashboard)),
            Tab(text: '用户', icon: Icon(Icons.people)),
            Tab(text: '数据', icon: Icon(Icons.analytics)),
            Tab(text: '系统', icon: Icon(Icons.computer)),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(),
                _buildUsersTab(),
                _buildAnalyticsTab(),
                _buildSystemTab(),
              ],
            ),
    );
  }
  
  /// 概览标签页
  Widget _buildOverviewTab() {
    return RefreshIndicator(
      onRefresh: _refreshData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatsCards(),
            const SizedBox(height: 24),
            _buildQuickActions(),
            const SizedBox(height: 24),
            _buildRecentActivities(),
            const SizedBox(height: 24),
            _buildSystemAlerts(),
          ],
        ),
      ),
    );
  }
  
  /// 统计卡片
  Widget _buildStatsCards() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard(
          '总用户数',
          '${_stats['total_users'] ?? 0}',
          Icons.people,
          Colors.blue,
        ),
        _buildStatCard(
          '活跃用户',
          '${_stats['active_users'] ?? 0}',
          Icons.person_add,
          Colors.green,
        ),
        _buildStatCard(
          '今日收入',
          '¥${_stats['today_revenue'] ?? 0}',
          Icons.attach_money,
          Colors.orange,
        ),
        _buildStatCard(
          '在线通话',
          '${_stats['active_calls'] ?? 0}',
          Icons.call,
          Colors.purple,
        ),
      ],
    );
  }
  
  /// 统计卡片
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 快速操作
  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '快速操作',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    '用户管理',
                    Icons.people,
                    Colors.blue,
                    () => _navigateToUserManagement(),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildActionButton(
                    '内容审核',
                    Icons.security,
                    Colors.orange,
                    () => _navigateToContentModeration(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    '系统设置',
                    Icons.settings,
                    Colors.grey,
                    () => _navigateToSystemSettings(),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildActionButton(
                    '数据导出',
                    Icons.download,
                    Colors.green,
                    () => _exportData(),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  /// 操作按钮
  Widget _buildActionButton(String title, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: color.withOpacity(0.3)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 最近活动
  Widget _buildRecentActivities() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '最近活动',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () => _navigateToActivityLog(),
                  child: const Text('查看全部'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._recentActivities.take(5).map((activity) => _buildActivityItem(activity)),
          ],
        ),
      ),
    );
  }
  
  /// 活动项目
  Widget _buildActivityItem(Map<String, dynamic> activity) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: _getActivityColor(activity['type']),
            child: Icon(
              _getActivityIcon(activity['type']),
              size: 16,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  activity['description'] ?? '',
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  activity['timestamp'] ?? '',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 系统警报
  Widget _buildSystemAlerts() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '系统警报',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () => _navigateToAlerts(),
                  child: const Text('查看全部'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._systemAlerts.take(3).map((alert) => _buildAlertItem(alert)),
          ],
        ),
      ),
    );
  }
  
  /// 警报项目
  Widget _buildAlertItem(Map<String, dynamic> alert) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _getAlertColor(alert['level']).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _getAlertColor(alert['level']).withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(
            _getAlertIcon(alert['level']),
            color: _getAlertColor(alert['level']),
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert['title'] ?? '',
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  alert['message'] ?? '',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 用户标签页
  Widget _buildUsersTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildUserStats(),
          const SizedBox(height: 24),
          _buildRecentUsersList(),
        ],
      ),
    );
  }
  
  /// 用户统计
  Widget _buildUserStats() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '用户统计',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildUserStatItem('新注册', '${_stats['new_users_today'] ?? 0}', Colors.green),
                ),
                Expanded(
                  child: _buildUserStatItem('在线用户', '${_stats['online_users'] ?? 0}', Colors.blue),
                ),
                Expanded(
                  child: _buildUserStatItem('付费用户', '${_stats['premium_users'] ?? 0}', Colors.orange),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  /// 用户统计项目
  Widget _buildUserStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
  
  /// 最近用户列表
  Widget _buildRecentUsersList() {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '最近注册用户',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () => _navigateToUserManagement(),
                  child: const Text('管理用户'),
                ),
              ],
            ),
          ),
          ..._recentUsers.map((user) => _buildUserItem(user)),
        ],
      ),
    );
  }
  
  /// 用户项目
  Widget _buildUserItem(Map<String, dynamic> user) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: user['avatar'] != null
            ? NetworkImage(user['avatar'])
            : null,
        child: user['avatar'] == null
            ? Text(user['name']?.substring(0, 1) ?? 'U')
            : null,
      ),
      title: Text(user['name'] ?? 'Unknown'),
      subtitle: Text(user['email'] ?? ''),
      trailing: Chip(
        label: Text(user['status'] ?? 'active'),
        backgroundColor: _getUserStatusColor(user['status']),
        labelStyle: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      onTap: () => _navigateToUserDetails(user['id']),
    );
  }
  
  /// 数据分析标签页
  Widget _buildAnalyticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildChartCard('用户增长', _userGrowthData, Colors.blue),
          const SizedBox(height: 24),
          _buildChartCard('收入趋势', _revenueData, Colors.green),
          const SizedBox(height: 24),
          _buildChartCard('活跃用户', _activeUsersData, Colors.orange),
        ],
      ),
    );
  }
  
  /// 图表卡片
  Widget _buildChartCard(String title, List<FlSpot> data, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true),
                  titlesData: FlTitlesData(show: false),
                  borderData: FlBorderData(show: true),
                  lineBarsData: [
                    LineChartBarData(
                      spots: data,
                      isCurved: true,
                      color: color,
                      barWidth: 3,
                      dotData: FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 系统标签页
  Widget _buildSystemTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildSystemStatus(),
          const SizedBox(height: 24),
          _buildPerformanceMetrics(),
          const SizedBox(height: 24),
          _buildSystemLogs(),
        ],
      ),
    );
  }
  
  /// 系统状态
  Widget _buildSystemStatus() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '系统状态',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildStatusItem('服务器状态', '正常', Colors.green),
            _buildStatusItem('数据库状态', '正常', Colors.green),
            _buildStatusItem('缓存状态', '正常', Colors.green),
            _buildStatusItem('存储状态', '正常', Colors.green),
          ],
        ),
      ),
    );
  }
  
  /// 状态项目
  Widget _buildStatusItem(String label, String status, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                status,
                style: TextStyle(color: color, fontWeight: FontWeight.w500),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  /// 性能指标
  Widget _buildPerformanceMetrics() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '性能指标',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildMetricItem('CPU使用率', '${_stats['cpu_usage'] ?? 0}%'),
            _buildMetricItem('内存使用率', '${_stats['memory_usage'] ?? 0}%'),
            _buildMetricItem('磁盘使用率', '${_stats['disk_usage'] ?? 0}%'),
            _buildMetricItem('网络延迟', '${_stats['network_latency'] ?? 0}ms'),
          ],
        ),
      ),
    );
  }
  
  /// 指标项目
  Widget _buildMetricItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
  
  /// 系统日志
  Widget _buildSystemLogs() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '系统日志',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () => _viewSystemLogs(),
                  child: const Text('查看全部'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // 这里可以显示最近的系统日志
            const Text('暂无系统日志'),
          ],
        ),
      ),
    );
  }
  
  // 辅助方法
  
  Color _getActivityColor(String? type) {
    switch (type) {
      case 'user_register':
        return Colors.green;
      case 'user_login':
        return Colors.blue;
      case 'payment':
        return Colors.orange;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getActivityIcon(String? type) {
    switch (type) {
      case 'user_register':
        return Icons.person_add;
      case 'user_login':
        return Icons.login;
      case 'payment':
        return Icons.payment;
      case 'error':
        return Icons.error;
      default:
        return Icons.info;
    }
  }
  
  Color _getAlertColor(String? level) {
    switch (level) {
      case 'critical':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      case 'info':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getAlertIcon(String? level) {
    switch (level) {
      case 'critical':
        return Icons.error;
      case 'warning':
        return Icons.warning;
      case 'info':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }
  
  Color _getUserStatusColor(String? status) {
    switch (status) {
      case 'active':
        return Colors.green;
      case 'inactive':
        return Colors.grey;
      case 'banned':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }
  
  // 导航方法
  
  void _navigateToSettings() {
    // 导航到设置页面
  }
  
  void _navigateToUserManagement() {
    // 导航到用户管理页面
  }
  
  void _navigateToContentModeration() {
    // 导航到内容审核页面
  }
  
  void _navigateToSystemSettings() {
    // 导航到系统设置页面
  }
  
  void _navigateToActivityLog() {
    // 导航到活动日志页面
  }
  
  void _navigateToAlerts() {
    // 导航到警报页面
  }
  
  void _navigateToUserDetails(String userId) {
    // 导航到用户详情页面
  }
  
  void _viewSystemLogs() {
    // 查看系统日志
  }
  
  void _exportData() {
    // 导出数据
  }
} 