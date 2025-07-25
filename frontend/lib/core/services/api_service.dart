import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../config/app_config.dart';
import 'storage_service.dart';

class ApiService {
  static late Dio _dio;
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';

  static Future<void> init() async {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.baseUrl,
      connectTimeout: Duration(milliseconds: AppConfig.connectTimeout),
      receiveTimeout: Duration(milliseconds: AppConfig.receiveTimeout),
      sendTimeout: Duration(milliseconds: AppConfig.sendTimeout),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // 添加拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // 添加认证token
        final token = await StorageService.getString(_tokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onResponse: (response, handler) {
        handler.next(response);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Token过期，尝试刷新
          final refreshed = await _refreshToken();
          if (refreshed) {
            // 重新发送请求
            final token = await StorageService.getString(_tokenKey);
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(error.requestOptions);
            handler.resolve(response);
            return;
          }
        }
        handler.next(error);
      },
    ));

    if (AppConfig.isDebug) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => debugPrint(obj.toString()),
      ));
    }
  }

  static Future<bool> _refreshToken() async {
    try {
      final refreshToken = await StorageService.getString(_refreshTokenKey);
      if (refreshToken == null) return false;

      final response = await _dio.post('/auth/refresh/', data: {
        'refresh': refreshToken,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        await StorageService.setString(_tokenKey, data['access']);
        await StorageService.setString(_refreshTokenKey, data['refresh']);
        return true;
      }
    } catch (e) {
      debugPrint('Token refresh failed: $e');
    }
    return false;
  }

  // 用户认证相关
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post('/auth/login/', data: {
      'email': email,
      'password': password,
    });
    
    final data = response.data;
    await StorageService.setString(_tokenKey, data['access']);
    await StorageService.setString(_refreshTokenKey, data['refresh']);
    
    return data;
  }

  static Future<void> logout() async {
    try {
      await _dio.post('/auth/logout/');
    } catch (e) {
      debugPrint('Logout error: $e');
    } finally {
      await StorageService.remove(_tokenKey);
      await StorageService.remove(_refreshTokenKey);
    }
  }

  static Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    final response = await _dio.post('/auth/register/', data: userData);
    return response.data;
  }

  // 用户相关
  static Future<Map<String, dynamic>> getProfile() async {
    final response = await _dio.get('/users/profile/');
    return response.data;
  }

  static Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final response = await _dio.put('/users/profile/', data: data);
    return response.data;
  }

  static Future<List<Map<String, dynamic>>> getUsers({int? page, String? search}) async {
    final queryParams = <String, dynamic>{};
    if (page != null) queryParams['page'] = page;
    if (search != null) queryParams['search'] = search;
    
    final response = await _dio.get('/users/', queryParameters: queryParams);
    return List<Map<String, dynamic>>.from(response.data['results']);
  }

  // 聊天相关
  static Future<List<Map<String, dynamic>>> getChats() async {
    final response = await _dio.get('/chat/');
    return List<Map<String, dynamic>>.from(response.data['results']);
  }

  static Future<Map<String, dynamic>> getChatMessages(String chatId, {int? page}) async {
    final queryParams = <String, dynamic>{};
    if (page != null) queryParams['page'] = page;
    
    final response = await _dio.get('/chat/$chatId/messages/', queryParameters: queryParams);
    return response.data;
  }

  static Future<Map<String, dynamic>> sendMessage(String chatId, String content, {String? type}) async {
    final response = await _dio.post('/chat/$chatId/messages/', data: {
      'content': content,
      'type': type ?? 'text',
    });
    return response.data;
  }

  // 房间相关
  static Future<List<Map<String, dynamic>>> getRooms() async {
    final response = await _dio.get('/rooms/');
    return List<Map<String, dynamic>>.from(response.data['results']);
  }

  static Future<Map<String, dynamic>> createRoom(Map<String, dynamic> roomData) async {
    final response = await _dio.post('/rooms/', data: roomData);
    return response.data;
  }

  static Future<Map<String, dynamic>> joinRoom(String roomId) async {
    final response = await _dio.post('/rooms/$roomId/join/');
    return response.data;
  }

  // 通话相关
  static Future<Map<String, dynamic>> startCall(String userId, String type) async {
    final response = await _dio.post('/calls/', data: {
      'receiver': userId,
      'call_type': type, // 'audio' or 'video'
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> answerCall(String callId, bool accept) async {
    final response = await _dio.post('/calls/$callId/answer/', data: {
      'accept': accept,
    });
    return response.data;
  }

  static Future<void> endCall(String callId) async {
    await _dio.post('/calls/$callId/end/');
  }

  // 文件上传
  static Future<String> uploadFile(File file, String type) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(file.path),
      'type': type,
    });

    final response = await _dio.post('/upload/', data: formData);
    return response.data['url'];
  }

  // 错误处理
  static String getErrorMessage(dynamic error) {
    if (error is DioException) {
      if (error.response?.data is Map) {
        final data = error.response!.data;
        if (data['detail'] != null) return data['detail'];
        if (data['message'] != null) return data['message'];
        if (data['error'] != null) return data['error'];
      }
      return error.message ?? '网络请求失败';
    }
    return error.toString();
  }

  // 支付相关API
  static Future<Map<String, dynamic>> createPaymentOrder(Map<String, dynamic> orderData) async {
    final response = await _dio.post('/payments/orders/', data: orderData);
    return response.data;
  }

  static Future<Map<String, dynamic>> getAlipayParams(String orderId) async {
    final response = await _dio.get('/payments/alipay/$orderId/params/');
    return response.data;
  }

  static Future<Map<String, dynamic>> getWechatPayParams(String orderId) async {
    final response = await _dio.get('/payments/wechat/$orderId/params/');
    return response.data;
  }

  static Future<Map<String, dynamic>> verifyPayment(String orderId) async {
    final response = await _dio.post('/payments/$orderId/verify/');
    return response.data;
  }

  static Future<Map<String, dynamic>> queryPaymentStatus(String orderId) async {
    final response = await _dio.get('/payments/$orderId/status/');
    return response.data;
  }

  static Future<Map<String, dynamic>> getPaymentHistory({int? page, int? pageSize}) async {
    final queryParams = <String, dynamic>{};
    if (page != null) queryParams['page'] = page;
    if (pageSize != null) queryParams['page_size'] = pageSize;
    
    final response = await _dio.get('/payments/history/', queryParameters: queryParams);
    return response.data;
  }

  static Future<Map<String, dynamic>> requestRefund(String orderId, {String? reason}) async {
    final data = <String, dynamic>{};
    if (reason != null) data['reason'] = reason;
    
    final response = await _dio.post('/payments/$orderId/refund/', data: data);
    return response.data;
  }

  // 推送通知相关API
  static Future<Map<String, dynamic>> updateFCMToken(String token) async {
    final response = await _dio.post('/notifications/fcm-token/', data: {
      'token': token,
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> getPushHistory({int? page, int? pageSize}) async {
    final queryParams = <String, dynamic>{};
    if (page != null) queryParams['page'] = page;
    if (pageSize != null) queryParams['page_size'] = pageSize;
    
    final response = await _dio.get('/notifications/history/', queryParameters: queryParams);
    return response.data;
  }

  static Future<Map<String, dynamic>> markPushAsRead(String messageId) async {
    final response = await _dio.post('/notifications/$messageId/read/');
    return response.data;
  }

  static Future<Map<String, dynamic>> deletePushMessage(String messageId) async {
    final response = await _dio.delete('/notifications/$messageId/');
    return response.data;
  }

  static Future<Map<String, dynamic>> updatePushSettings(Map<String, dynamic> settings) async {
    final response = await _dio.put('/notifications/settings/', data: settings);
    return response.data;
  }

  static Future<Map<String, dynamic>> getPushSettings() async {
    final response = await _dio.get('/notifications/settings/');
    return response.data;
  }

  static Future<Map<String, dynamic>> getUnreadPushCount() async {
    final response = await _dio.get('/notifications/unread-count/');
    return response.data;
  }

  // 内容审核相关API
  static Future<Map<String, dynamic>> moderateText(String text) async {
    final response = await _dio.post('/moderation/text/', data: {
      'content': text,
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> moderateImage(File imageFile) async {
    final formData = FormData.fromMap({
      'image': await MultipartFile.fromFile(imageFile.path),
    });
    
    final response = await _dio.post('/moderation/image/', data: formData);
    return response.data;
  }

  static Future<Map<String, dynamic>> moderateVideo(File videoFile) async {
    final formData = FormData.fromMap({
      'video': await MultipartFile.fromFile(videoFile.path),
    });
    
    final response = await _dio.post('/moderation/video/', data: formData);
    return response.data;
  }

  static Future<Map<String, dynamic>> moderateAudio(File audioFile) async {
    final formData = FormData.fromMap({
      'audio': await MultipartFile.fromFile(audioFile.path),
    });
    
    final response = await _dio.post('/moderation/audio/', data: formData);
    return response.data;
  }

  static Future<Map<String, dynamic>> moderateBatch(List<Map<String, dynamic>> contents) async {
    final response = await _dio.post('/moderation/batch/', data: {
      'contents': contents,
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> getModerationStats() async {
    final response = await _dio.get('/moderation/stats/');
    return response.data;
  }

  static Future<Map<String, dynamic>> submitModerationFeedback(Map<String, dynamic> feedback) async {
    final response = await _dio.post('/moderation/feedback/', data: feedback);
    return response.data;
  }

  // 性能监控相关API
  static Future<Map<String, dynamic>> reportPerformanceMetrics(Map<String, dynamic> data) async {
    final response = await _dio.post('/performance/metrics/', data: data);
    return response.data;
  }

  static Future<Map<String, dynamic>> getPerformanceStats() async {
    final response = await _dio.get('/performance/stats/');
    return response.data;
  }

  // 数据分析相关API
  static Future<Map<String, dynamic>> trackAnalyticsEvent(Map<String, dynamic> data) async {
    final response = await _dio.post('/analytics/event/', data: data);
    return response.data;
  }

  static Future<Map<String, dynamic>> trackAnalyticsEvents(List<Map<String, dynamic>> events) async {
    final response = await _dio.post('/analytics/events/', data: {'events': events});
    return response.data;
  }

  static Future<Map<String, dynamic>> trackAnalyticsSession(Map<String, dynamic> data) async {
    final response = await _dio.post('/analytics/session/', data: data);
    return response.data;
  }

  // 群组通话相关API
  static Future<Map<String, dynamic>> createGroupCall(Map<String, dynamic> data) async {
    final response = await _dio.post('/group-calls/create/', data: data);
    return response.data;
  }

  static Future<Map<String, dynamic>> joinGroupCall(String callId, Map<String, dynamic> data) async {
    final response = await _dio.post('/group-calls/$callId/join/', data: data);
    return response.data;
  }

  static Future<Map<String, dynamic>> endGroupCall(String callId) async {
    final response = await _dio.post('/group-calls/$callId/end/', data: {});
    return response.data;
  }

  static Future<Map<String, dynamic>> getGroupCallInfo(String callId) async {
    final response = await _dio.get('/group-calls/$callId/');
    return response.data;
  }

  // 管理后台相关API
  static Future<Map<String, dynamic>> getAdminStats() async {
    final response = await _dio.get('/admin/stats/');
    return response.data;
  }

  static Future<Map<String, dynamic>> getAdminUsers({int page = 1, String? search}) async {
    final queryParams = <String, dynamic>{'page': page};
    if (search != null) queryParams['search'] = search;
    
    final response = await _dio.get('/admin/users/', queryParameters: queryParams);
    return response.data;
  }

  static Future<Map<String, dynamic>> getAdminActivities({int page = 1}) async {
    final response = await _dio.get('/admin/activities/', queryParameters: {'page': page});
    return response.data;
  }

  static Future<Map<String, dynamic>> getAdminAlerts() async {
    final response = await _dio.get('/admin/alerts/');
    return response.data;
  }

  static Future<Map<String, dynamic>> getAdminCharts() async {
    final response = await _dio.get('/admin/charts/');
    return response.data;
  }

  static Future<Map<String, dynamic>> updateUserStatus(String userId, String status) async {
    final response = await _dio.post('/admin/users/$userId/status/', data: {'status': status});
    return response.data;
  }

  static Future<Map<String, dynamic>> banUser(String userId, String reason) async {
    final response = await _dio.post('/admin/users/$userId/ban/', data: {'reason': reason});
    return response.data;
  }

  static Future<Map<String, dynamic>> exportData(String type) async {
    final response = await _dio.get('/admin/export/$type/');
    return response.data;
  }
} 