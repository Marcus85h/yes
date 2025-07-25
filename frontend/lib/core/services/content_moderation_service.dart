import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import '../config/app_config.dart';
import 'api_service.dart';

/// 内容类型
enum ContentType {
  text,
  image,
  video,
  audio,
}

/// 审核结果
enum ModerationResult {
  safe,
  unsafe,
  review,
}

/// 违规类型
enum ViolationType {
  pornographic,
  violent,
  hate,
  spam,
  fraud,
  other,
}

/// 审核详情
class ModerationDetail {
  final ModerationResult result;
  final List<ViolationType> violations;
  final double confidence;
  final String? reason;
  final Map<String, dynamic>? metadata;
  
  ModerationDetail({
    required this.result,
    required this.violations,
    required this.confidence,
    this.reason,
    this.metadata,
  });
  
  factory ModerationDetail.fromJson(Map<String, dynamic> json) {
    return ModerationDetail(
      result: ModerationResult.values.firstWhere(
        (e) => e.name == json['result'],
        orElse: () => ModerationResult.safe,
      ),
      violations: (json['violations'] as List?)
          ?.map((v) => ViolationType.values.firstWhere(
                (e) => e.name == v,
                orElse: () => ViolationType.other,
              ))
          .toList() ?? [],
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      reason: json['reason'],
      metadata: json['metadata'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'result': result.name,
      'violations': violations.map((v) => v.name).toList(),
      'confidence': confidence,
      'reason': reason,
      'metadata': metadata,
    };
  }
}

class ContentModerationService {
  static ContentModerationService? _instance;
  static ContentModerationService get instance => _instance ??= ContentModerationService._();
  
  ContentModerationService._();
  
  // 本地敏感词库
  final Set<String> _localSensitiveWords = {
    '色情', '暴力', '赌博', '毒品', '诈骗', '传销',
    '政治敏感', '宗教敏感', '民族歧视', '地域歧视',
  };
  
  // 本地图片特征检测
  final List<String> _imageHashCache = [];
  
  /// 审核文本内容
  Future<ModerationDetail> moderateText(String text) async {
    try {
      // 本地敏感词检测
      final localResult = _checkLocalSensitiveWords(text);
      if (localResult.result != ModerationResult.safe) {
        return localResult;
      }
      
      // 调用服务器API进行深度检测
      final response = await ApiService.moderateText(text);
      return ModerationDetail.fromJson(response);
      
    } catch (e) {
      print('文本审核失败: $e');
      // 如果服务器检测失败，返回本地检测结果
      return _checkLocalSensitiveWords(text);
    }
  }
  
  /// 审核图片内容
  Future<ModerationDetail> moderateImage(File imageFile) async {
    try {
      // 本地图片特征检测
      final localResult = await _checkLocalImageFeatures(imageFile);
      if (localResult.result != ModerationResult.safe) {
        return localResult;
      }
      
      // 调用服务器API进行深度检测
      final response = await ApiService.moderateImage(imageFile);
      return ModerationDetail.fromJson(response);
      
    } catch (e) {
      print('图片审核失败: $e');
      // 如果服务器检测失败，返回本地检测结果
      return await _checkLocalImageFeatures(imageFile);
    }
  }
  
  /// 审核视频内容
  Future<ModerationDetail> moderateVideo(File videoFile) async {
    try {
      // 本地视频特征检测
      final localResult = await _checkLocalVideoFeatures(videoFile);
      if (localResult.result != ModerationResult.safe) {
        return localResult;
      }
      
      // 调用服务器API进行深度检测
      final response = await ApiService.moderateVideo(videoFile);
      return ModerationDetail.fromJson(response);
      
    } catch (e) {
      print('视频审核失败: $e');
      // 如果服务器检测失败，返回本地检测结果
      return await _checkLocalVideoFeatures(videoFile);
    }
  }
  
  /// 审核音频内容
  Future<ModerationDetail> moderateAudio(File audioFile) async {
    try {
      // 本地音频特征检测
      final localResult = await _checkLocalAudioFeatures(audioFile);
      if (localResult.result != ModerationResult.safe) {
        return localResult;
      }
      
      // 调用服务器API进行深度检测
      final response = await ApiService.moderateAudio(audioFile);
      return ModerationDetail.fromJson(response);
      
    } catch (e) {
      print('音频审核失败: $e');
      // 如果服务器检测失败，返回本地检测结果
      return await _checkLocalAudioFeatures(audioFile);
    }
  }
  
  /// 批量审核内容
  Future<List<ModerationDetail>> moderateBatch(List<Map<String, dynamic>> contents) async {
    try {
      final response = await ApiService.moderateBatch(contents);
      final results = response['results'] as List;
      return results.map((json) => ModerationDetail.fromJson(json)).toList();
    } catch (e) {
      print('批量审核失败: $e');
      return [];
    }
  }
  
  /// 本地敏感词检测
  ModerationDetail _checkLocalSensitiveWords(String text) {
    final violations = <ViolationType>[];
    final lowerText = text.toLowerCase();
    
    // 检查敏感词
    for (final word in _localSensitiveWords) {
      if (lowerText.contains(word.toLowerCase())) {
        violations.add(ViolationType.other);
        break;
      }
    }
    
    // 检查重复字符（可能的垃圾信息）
    if (_checkRepeatedCharacters(text)) {
      violations.add(ViolationType.spam);
    }
    
    // 检查特殊字符比例
    if (_checkSpecialCharacterRatio(text) > 0.5) {
      violations.add(ViolationType.spam);
    }
    
    if (violations.isNotEmpty) {
      return ModerationDetail(
        result: ModerationResult.unsafe,
        violations: violations,
        confidence: 0.8,
        reason: '检测到敏感内容',
      );
    }
    
    return ModerationDetail(
      result: ModerationResult.safe,
      violations: [],
      confidence: 1.0,
    );
  }
  
  /// 检查重复字符
  bool _checkRepeatedCharacters(String text) {
    if (text.length < 10) return false;
    
    int repeatedCount = 0;
    for (int i = 0; i < text.length - 1; i++) {
      if (text[i] == text[i + 1]) {
        repeatedCount++;
        if (repeatedCount > 5) return true;
      } else {
        repeatedCount = 0;
      }
    }
    return false;
  }
  
  /// 检查特殊字符比例
  double _checkSpecialCharacterRatio(String text) {
    if (text.isEmpty) return 0.0;
    
    int specialCount = 0;
    for (final char in text) {
      if (!RegExp(r'[a-zA-Z0-9\u4e00-\u9fa5]').hasMatch(char)) {
        specialCount++;
      }
    }
    
    return specialCount / text.length;
  }
  
  /// 本地图片特征检测
  Future<ModerationDetail> _checkLocalImageFeatures(File imageFile) async {
    try {
      final bytes = await imageFile.readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image == null) {
        return ModerationDetail(
          result: ModerationResult.unsafe,
          violations: [ViolationType.other],
          confidence: 0.9,
          reason: '无法解析图片',
        );
      }
      
      final violations = <ViolationType>[];
      
      // 检查图片尺寸
      if (image.width < 50 || image.height < 50) {
        violations.add(ViolationType.other);
      }
      
      // 检查图片比例
      final ratio = image.width / image.height;
      if (ratio > 10 || ratio < 0.1) {
        violations.add(ViolationType.other);
      }
      
      // 检查图片哈希（防止重复上传）
      final hash = _calculateImageHash(image);
      if (_imageHashCache.contains(hash)) {
        violations.add(ViolationType.spam);
      } else {
        _imageHashCache.add(hash);
        if (_imageHashCache.length > 1000) {
          _imageHashCache.removeAt(0);
        }
      }
      
      if (violations.isNotEmpty) {
        return ModerationDetail(
          result: ModerationResult.review,
          violations: violations,
          confidence: 0.6,
          reason: '图片特征异常',
        );
      }
      
      return ModerationDetail(
        result: ModerationResult.safe,
        violations: [],
        confidence: 0.7,
      );
      
    } catch (e) {
      print('本地图片检测失败: $e');
      return ModerationDetail(
        result: ModerationResult.review,
        violations: [ViolationType.other],
        confidence: 0.5,
        reason: '图片检测失败',
      );
    }
  }
  
  /// 计算图片哈希
  String _calculateImageHash(img.Image image) {
    // 简化的感知哈希算法
    final resized = img.copyResize(image, width: 8, height: 8);
    final grayscale = img.grayscale(resized);
    
    int hash = 0;
    for (int y = 0; y < 8; y++) {
      for (int x = 0; x < 8; x++) {
        final pixel = grayscale.getPixel(x, y);
        final gray = img.getLuminance(pixel);
        hash = (hash << 1) | (gray > 128 ? 1 : 0);
      }
    }
    
    return hash.toRadixString(16);
  }
  
  /// 本地视频特征检测
  Future<ModerationDetail> _checkLocalVideoFeatures(File videoFile) async {
    try {
      final violations = <ViolationType>[];
      
      // 检查文件大小
      final fileSize = await videoFile.length();
      if (fileSize > AppConfig.maxVideoSize) {
        violations.add(ViolationType.other);
      }
      
      // 检查文件扩展名
      final extension = videoFile.path.split('.').last.toLowerCase();
      if (!AppConfig.allowedVideoTypes.contains(extension)) {
        violations.add(ViolationType.other);
      }
      
      if (violations.isNotEmpty) {
        return ModerationDetail(
          result: ModerationResult.unsafe,
          violations: violations,
          confidence: 0.8,
          reason: '视频文件不符合要求',
        );
      }
      
      return ModerationDetail(
        result: ModerationResult.safe,
        violations: [],
        confidence: 0.6,
      );
      
    } catch (e) {
      print('本地视频检测失败: $e');
      return ModerationDetail(
        result: ModerationResult.review,
        violations: [ViolationType.other],
        confidence: 0.5,
        reason: '视频检测失败',
      );
    }
  }
  
  /// 本地音频特征检测
  Future<ModerationDetail> _checkLocalAudioFeatures(File audioFile) async {
    try {
      final violations = <ViolationType>[];
      
      // 检查文件大小
      final fileSize = await audioFile.length();
      if (fileSize > AppConfig.maxAudioSize) {
        violations.add(ViolationType.other);
      }
      
      // 检查文件扩展名
      final extension = audioFile.path.split('.').last.toLowerCase();
      if (!AppConfig.allowedAudioTypes.contains(extension)) {
        violations.add(ViolationType.other);
      }
      
      if (violations.isNotEmpty) {
        return ModerationDetail(
          result: ModerationResult.unsafe,
          violations: violations,
          confidence: 0.8,
          reason: '音频文件不符合要求',
        );
      }
      
      return ModerationDetail(
        result: ModerationResult.safe,
        violations: [],
        confidence: 0.6,
      );
      
    } catch (e) {
      print('本地音频检测失败: $e');
      return ModerationDetail(
        result: ModerationResult.review,
        violations: [ViolationType.other],
        confidence: 0.5,
        reason: '音频检测失败',
      );
    }
  }
  
  /// 添加自定义敏感词
  void addSensitiveWord(String word) {
    _localSensitiveWords.add(word.toLowerCase());
  }
  
  /// 移除敏感词
  void removeSensitiveWord(String word) {
    _localSensitiveWords.remove(word.toLowerCase());
  }
  
  /// 获取所有敏感词
  Set<String> getSensitiveWords() {
    return Set.from(_localSensitiveWords);
  }
  
  /// 清空敏感词库
  void clearSensitiveWords() {
    _localSensitiveWords.clear();
  }
  
  /// 获取审核统计
  Future<Map<String, dynamic>> getModerationStats() async {
    try {
      final response = await ApiService.getModerationStats();
      return response;
    } catch (e) {
      print('获取审核统计失败: $e');
      return {};
    }
  }
  
  /// 提交误判反馈
  Future<bool> submitFeedback(String contentId, ModerationResult expectedResult, String reason) async {
    try {
      final response = await ApiService.submitModerationFeedback({
        'content_id': contentId,
        'expected_result': expectedResult.name,
        'reason': reason,
      });
      return response['success'] == true;
    } catch (e) {
      print('提交反馈失败: $e');
      return false;
    }
  }
}

/// 内容审核配置
class ModerationConfig {
  static const bool enableLocalDetection = true;
  static const bool enableServerDetection = true;
  static const double confidenceThreshold = 0.8;
  static const int maxRetryAttempts = 3;
  static const Duration timeout = Duration(seconds: 30);
} 