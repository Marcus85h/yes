import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class UserProvider extends ChangeNotifier {
  bool _isLoading = false;
  List<Map<String, dynamic>> _users = [];
  Map<String, dynamic>? _selectedUser;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;
  String _searchQuery = '';

  // Getters
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get users => _users;
  Map<String, dynamic>? get selectedUser => _selectedUser;
  String? get error => _error;
  bool get hasMore => _hasMore;
  String get searchQuery => _searchQuery;

  // 获取用户列表
  Future<void> getUsers({bool refresh = false, String? search}) async {
    if (refresh) {
      _currentPage = 1;
      _users.clear();
      _hasMore = true;
    }

    if (!_hasMore || _isLoading) return;

    _setLoading(true);
    _clearError();

    try {
      final newUsers = await ApiService.getUsers(
        page: _currentPage,
        search: search ?? _searchQuery,
      );

      if (refresh || _currentPage == 1) {
        _users = newUsers;
      } else {
        _users.addAll(newUsers);
      }

      _hasMore = newUsers.isNotEmpty;
      if (_hasMore) {
        _currentPage++;
      }

      if (search != null) {
        _searchQuery = search;
      }

      notifyListeners();
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
    } finally {
      _setLoading(false);
    }
  }

  // 搜索用户
  Future<void> searchUsers(String query) async {
    await getUsers(refresh: true, search: query);
  }

  // 选择用户
  void selectUser(Map<String, dynamic> user) {
    _selectedUser = user;
    notifyListeners();
  }

  // 清除选中的用户
  void clearSelectedUser() {
    _selectedUser = null;
    notifyListeners();
  }

  // 刷新用户列表
  Future<void> refreshUsers() async {
    await getUsers(refresh: true);
  }

  // 加载更多用户
  Future<void> loadMoreUsers() async {
    await getUsers();
  }

  // 清除搜索
  void clearSearch() {
    _searchQuery = '';
    getUsers(refresh: true);
  }

  // 私有方法
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }
} 