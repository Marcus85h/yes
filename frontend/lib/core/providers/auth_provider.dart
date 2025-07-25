import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthProvider extends ChangeNotifier {
  bool _isLoading = false;
  bool _isAuthenticated = false;
  Map<String, dynamic>? _user;
  String? _error;

  // Getters
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get user => _user;
  String? get error => _error;

  // 初始化检查认证状态
  Future<void> checkAuthStatus() async {
    try {
      final token = StorageService.getString('auth_token');
      if (token != null) {
        final userProfile = await ApiService.getProfile();
        _user = userProfile;
        _isAuthenticated = true;
        notifyListeners();
      }
    } catch (e) {
      await logout();
    }
  }

  // 登录
  Future<bool> login(String email, String password) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await ApiService.login(email, password);
      _user = response['user'];
      _isAuthenticated = true;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // 注册
  Future<bool> register(Map<String, dynamic> userData) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await ApiService.register(userData);
      _user = response['user'];
      _isAuthenticated = true;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // 登出
  Future<void> logout() async {
    try {
      await ApiService.logout();
    } catch (e) {
      debugPrint('Logout error: $e');
    } finally {
      _user = null;
      _isAuthenticated = false;
      notifyListeners();
    }
  }

  // 更新用户资料
  Future<bool> updateProfile(Map<String, dynamic> profileData) async {
    _setLoading(true);
    _clearError();

    try {
      final updatedProfile = await ApiService.updateProfile(profileData);
      _user = updatedProfile;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(ApiService.getErrorMessage(e));
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // 刷新用户资料
  Future<void> refreshProfile() async {
    try {
      final userProfile = await ApiService.getProfile();
      _user = userProfile;
      notifyListeners();
    } catch (e) {
      debugPrint('Refresh profile error: $e');
    }
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