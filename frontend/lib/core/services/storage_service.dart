import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

class StorageService {
  static late SharedPreferences _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // 字符串存储
  static Future<bool> setString(String key, String value) async {
    return await _prefs.setString(key, value);
  }

  static String? getString(String key) {
    return _prefs.getString(key);
  }

  // 布尔值存储
  static Future<bool> setBool(String key, bool value) async {
    return await _prefs.setBool(key, value);
  }

  static bool? getBool(String key) {
    return _prefs.getBool(key);
  }

  // 整数存储
  static Future<bool> setInt(String key, int value) async {
    return await _prefs.setInt(key, value);
  }

  static int? getInt(String key) {
    return _prefs.getInt(key);
  }

  // 双精度浮点数存储
  static Future<bool> setDouble(String key, double value) async {
    return await _prefs.setDouble(key, value);
  }

  static double? getDouble(String key) {
    return _prefs.getDouble(key);
  }

  // 字符串列表存储
  static Future<bool> setStringList(String key, List<String> value) async {
    return await _prefs.setStringList(key, value);
  }

  static List<String>? getStringList(String key) {
    return _prefs.getStringList(key);
  }

  // 删除指定键
  static Future<bool> remove(String key) async {
    return await _prefs.remove(key);
  }

  // 清空所有数据
  static Future<bool> clear() async {
    return await _prefs.clear();
  }

  // 检查键是否存在
  static bool containsKey(String key) {
    return _prefs.containsKey(key);
  }

  // 获取所有键
  static Set<String> getKeys() {
    return _prefs.getKeys();
  }

  // 用户相关存储键
  static const String userProfileKey = 'user_profile';
  static const String userSettingsKey = 'user_settings';
  static const String chatHistoryKey = 'chat_history';
  static const String recentContactsKey = 'recent_contacts';
  static const String appSettingsKey = 'app_settings';

  // 保存用户资料
  static Future<bool> saveUserProfile(Map<String, dynamic> profile) async {
    try {
      final jsonString = _mapToJson(profile);
      return await setString(userProfileKey, jsonString);
    } catch (e) {
      if (kDebugMode) {
        print('Save user profile error: $e');
      }
      return false;
    }
  }

  // 获取用户资料
  static Map<String, dynamic>? getUserProfile() {
    try {
      final jsonString = getString(userProfileKey);
      if (jsonString != null) {
        return _jsonToMap(jsonString);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Get user profile error: $e');
      }
    }
    return null;
  }

  // 保存用户设置
  static Future<bool> saveUserSettings(Map<String, dynamic> settings) async {
    try {
      final jsonString = _mapToJson(settings);
      return await setString(userSettingsKey, jsonString);
    } catch (e) {
      if (kDebugMode) {
        print('Save user settings error: $e');
      }
      return false;
    }
  }

  // 获取用户设置
  static Map<String, dynamic>? getUserSettings() {
    try {
      final jsonString = getString(userSettingsKey);
      if (jsonString != null) {
        return _jsonToMap(jsonString);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Get user settings error: $e');
      }
    }
    return null;
  }

  // 保存聊天历史
  static Future<bool> saveChatHistory(String chatId, List<Map<String, dynamic>> messages) async {
    try {
      final key = '${chatHistoryKey}_$chatId';
      final jsonString = _listToJson(messages);
      return await setString(key, jsonString);
    } catch (e) {
      if (kDebugMode) {
        print('Save chat history error: $e');
      }
      return false;
    }
  }

  // 获取聊天历史
  static List<Map<String, dynamic>>? getChatHistory(String chatId) {
    try {
      final key = '${chatHistoryKey}_$chatId';
      final jsonString = getString(key);
      if (jsonString != null) {
        return _jsonToList(jsonString);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Get chat history error: $e');
      }
    }
    return null;
  }

  // 保存最近联系人
  static Future<bool> saveRecentContacts(List<Map<String, dynamic>> contacts) async {
    try {
      final jsonString = _listToJson(contacts);
      return await setString(recentContactsKey, jsonString);
    } catch (e) {
      if (kDebugMode) {
        print('Save recent contacts error: $e');
      }
      return false;
    }
  }

  // 获取最近联系人
  static List<Map<String, dynamic>>? getRecentContacts() {
    try {
      final jsonString = getString(recentContactsKey);
      if (jsonString != null) {
        return _jsonToList(jsonString);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Get recent contacts error: $e');
      }
    }
    return null;
  }

  // 保存应用设置
  static Future<bool> saveAppSettings(Map<String, dynamic> settings) async {
    try {
      final jsonString = _mapToJson(settings);
      return await setString(appSettingsKey, jsonString);
    } catch (e) {
      if (kDebugMode) {
        print('Save app settings error: $e');
      }
      return false;
    }
  }

  // 获取应用设置
  static Map<String, dynamic>? getAppSettings() {
    try {
      final jsonString = getString(appSettingsKey);
      if (jsonString != null) {
        return _jsonToMap(jsonString);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Get app settings error: $e');
      }
    }
    return null;
  }

  // 清除聊天历史
  static Future<bool> clearChatHistory(String chatId) async {
    final key = '${chatHistoryKey}_$chatId';
    return await remove(key);
  }

  // 清除所有聊天历史
  static Future<bool> clearAllChatHistory() async {
    final keys = getKeys().where((key) => key.startsWith(chatHistoryKey));
    bool success = true;
    for (final key in keys) {
      success = success && await remove(key);
    }
    return success;
  }

  // 工具方法：Map转JSON字符串
  static String _mapToJson(Map<String, dynamic> map) {
    return jsonEncode(map);
  }

  // 工具方法：JSON字符串转Map
  static Map<String, dynamic> _jsonToMap(String jsonString) {
    return Map<String, dynamic>.from(jsonDecode(jsonString));
  }

  // 工具方法：List转JSON字符串
  static String _listToJson(List<Map<String, dynamic>> list) {
    return jsonEncode(list);
  }

  // 工具方法：JSON字符串转List
  static List<Map<String, dynamic>> _jsonToList(String jsonString) {
    return List<Map<String, dynamic>>.from(jsonDecode(jsonString));
  }
}

// 导入dart:convert
import 'dart:convert'; 