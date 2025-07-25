import 'dart:convert';
import 'package:easy_localization/easy_localization.dart';
import 'package:translator/translator.dart';
import 'package:flutter/foundation.dart';
import '../services/storage_service.dart';

/// 支持的语言
enum SupportedLanguage {
  zhCN('zh-CN', '简体中文', '🇨🇳'),
  zhTW('zh-TW', '繁體中文', '🇹🇼'),
  vi('vi', 'Tiếng Việt', '🇻🇳'),
  th('th', 'ไทย', '🇹🇭'),
  ja('ja', '日本語', '🇯🇵'),
  ko('ko', '한국어', '🇰🇷');

  const SupportedLanguage(this.code, this.name, this.flag);
  final String code;
  final String name;
  final String flag;
}

/// 本地化服务
class LocalizationService {
  static LocalizationService? _instance;
  static LocalizationService get instance => _instance ??= LocalizationService._();
  
  LocalizationService._();
  
  final GoogleTranslator _translator = GoogleTranslator();
  
  // 当前语言
  SupportedLanguage _currentLanguage = SupportedLanguage.zhCN;
  
  // 语言偏好存储键
  static const String _languageKey = 'app_language';
  
  // 回调函数
  Function(SupportedLanguage)? onLanguageChanged;
  
  // Getters
  SupportedLanguage get currentLanguage => _currentLanguage;
  List<SupportedLanguage> get supportedLanguages => SupportedLanguage.values;
  
  /// 初始化本地化服务
  Future<void> initialize() async {
    try {
      // 从存储中读取语言偏好
      final savedLanguage = await StorageService.getString(_languageKey);
      if (savedLanguage != null) {
        final language = SupportedLanguage.values.firstWhere(
          (lang) => lang.code == savedLanguage,
          orElse: () => SupportedLanguage.zhCN,
        );
        _currentLanguage = language;
      }
      
      print('本地化服务初始化完成，当前语言: ${_currentLanguage.name}');
    } catch (e) {
      print('本地化服务初始化失败: $e');
    }
  }
  
  /// 切换语言
  Future<void> changeLanguage(SupportedLanguage language) async {
    if (_currentLanguage == language) return;
    
    try {
      _currentLanguage = language;
      
      // 保存语言偏好
      await StorageService.setString(_languageKey, language.code);
      
      // 通知语言变化
      onLanguageChanged?.call(language);
      
      print('语言已切换为: ${language.name}');
    } catch (e) {
      print('切换语言失败: $e');
    }
  }
  
  /// 获取当前语言的Locale
  Locale get currentLocale {
    switch (_currentLanguage) {
      case SupportedLanguage.zhCN:
        return const Locale('zh', 'CN');
      case SupportedLanguage.zhTW:
        return const Locale('zh', 'TW');
      case SupportedLanguage.vi:
        return const Locale('vi', 'VN');
      case SupportedLanguage.th:
        return const Locale('th', 'TH');
      case SupportedLanguage.ja:
        return const Locale('ja', 'JP');
      case SupportedLanguage.ko:
        return const Locale('ko', 'KR');
    }
  }
  
  /// 自动翻译文本
  Future<String> translateText(String text, {SupportedLanguage? targetLanguage}) async {
    if (text.isEmpty) return text;
    
    try {
      final target = targetLanguage ?? _currentLanguage;
      
      // 如果目标语言是简体中文，直接返回原文
      if (target == SupportedLanguage.zhCN) return text;
      
      // 使用Google翻译API
      final translation = await _translator.translate(
        text,
        from: 'zh-CN',
        to: target.code,
      );
      
      return translation.text;
    } catch (e) {
      print('翻译失败: $e');
      return text; // 翻译失败时返回原文
    }
  }
  
  /// 批量翻译文本
  Future<Map<String, String>> translateBatch(
    Map<String, String> texts, {
    SupportedLanguage? targetLanguage,
  }) async {
    final target = targetLanguage ?? _currentLanguage;
    final result = <String, String>{};
    
    try {
      for (final entry in texts.entries) {
        result[entry.key] = await translateText(entry.value, targetLanguage: target);
      }
    } catch (e) {
      print('批量翻译失败: $e');
      // 翻译失败时返回原文
      result.addAll(texts);
    }
    
    return result;
  }
  
  /// 获取语言显示名称
  String getLanguageDisplayName(SupportedLanguage language) {
    return '${language.flag} ${language.name}';
  }
  
  /// 检测文本语言
  Future<String> detectLanguage(String text) async {
    try {
      final detection = await _translator.detect(text);
      return detection.languageCode;
    } catch (e) {
      print('语言检测失败: $e');
      return 'zh-CN'; // 默认返回中文
    }
  }
  
  /// 格式化日期时间
  String formatDateTime(DateTime dateTime, {String? pattern}) {
    final locale = currentLocale;
    final formatter = DateFormat(pattern ?? 'yyyy-MM-dd HH:mm:ss', locale.languageCode);
    return formatter.format(dateTime);
  }
  
  /// 格式化数字
  String formatNumber(num number, {String? pattern}) {
    final locale = currentLocale;
    final formatter = NumberFormat(pattern ?? '#,##0.##', locale.languageCode);
    return formatter.format(number);
  }
  
  /// 格式化货币
  String formatCurrency(num amount, {String? currencyCode}) {
    final locale = currentLocale;
    final formatter = NumberFormat.currency(
      locale: locale.languageCode,
      symbol: currencyCode ?? '¥',
    );
    return formatter.format(amount);
  }
} 