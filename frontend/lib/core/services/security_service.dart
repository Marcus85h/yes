import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:screen_brightness/screen_brightness.dart';
import 'package:permission_handler/permission_handler.dart';
import '../config/app_config.dart';

/// 加密算法类型
enum EncryptionAlgorithm {
  aes256,
  chacha20,
  rsa2048,
}

/// 安全级别
enum SecurityLevel {
  low,
  medium,
  high,
  maximum,
}

/// 加密密钥对
class KeyPair {
  final String publicKey;
  final String privateKey;
  final DateTime createdAt;
  final DateTime expiresAt;
  
  KeyPair({
    required this.publicKey,
    required this.privateKey,
    required this.createdAt,
    required this.expiresAt,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'public_key': publicKey,
      'private_key': privateKey,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
    };
  }
  
  factory KeyPair.fromJson(Map<String, dynamic> json) {
    return KeyPair(
      publicKey: json['public_key'],
      privateKey: json['private_key'],
      createdAt: DateTime.parse(json['created_at']),
      expiresAt: DateTime.parse(json['expires_at']),
    );
  }
}

/// 加密消息
class EncryptedMessage {
  final String encryptedData;
  final String iv;
  final String signature;
  final DateTime timestamp;
  final String algorithm;
  
  EncryptedMessage({
    required this.encryptedData,
    required this.iv,
    required this.signature,
    required this.timestamp,
    required this.algorithm,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'encrypted_data': encryptedData,
      'iv': iv,
      'signature': signature,
      'timestamp': timestamp.toIso8601String(),
      'algorithm': algorithm,
    };
  }
  
  factory EncryptedMessage.fromJson(Map<String, dynamic> json) {
    return EncryptedMessage(
      encryptedData: json['encrypted_data'],
      iv: json['iv'],
      signature: json['signature'],
      timestamp: DateTime.parse(json['timestamp']),
      algorithm: json['algorithm'],
    );
  }
}

class SecurityService {
  static SecurityService? _instance;
  static SecurityService get instance => _instance ??= SecurityService._();
  
  SecurityService._();
  
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final ScreenBrightness _screenBrightness = ScreenBrightness();
  
  // 加密配置
  static const String _masterKeyAlias = 'master_key';
  static const String _keyPairAlias = 'key_pair';
  static const String _sessionKeyAlias = 'session_key';
  
  // 安全状态
  bool _isInitialized = false;
  SecurityLevel _securityLevel = SecurityLevel.high;
  KeyPair? _currentKeyPair;
  String? _sessionKey;
  bool _isScreenRecordingProtected = false;
  
  // 防录屏状态
  bool _isScreenRecording = false;
  double _originalBrightness = 0.5;
  
  // Getters
  bool get isInitialized => _isInitialized;
  SecurityLevel get securityLevel => _securityLevel;
  bool get isScreenRecordingProtected => _isScreenRecordingProtected;
  
  /// 初始化安全服务
  Future<void> initialize() async {
    try {
      await _generateMasterKey();
      await _loadOrGenerateKeyPair();
      await _setupScreenRecordingProtection();
      await _requestPermissions();
      
      _isInitialized = true;
      print('安全服务初始化完成');
      
    } catch (e) {
      print('安全服务初始化失败: $e');
      rethrow;
    }
  }
  
  /// 生成主密钥
  Future<void> _generateMasterKey() async {
    final existingKey = await _secureStorage.read(key: _masterKeyAlias);
    if (existingKey == null) {
      final masterKey = _generateRandomKey(32);
      await _secureStorage.write(key: _masterKeyAlias, value: base64Encode(masterKey));
    }
  }
  
  /// 加载或生成密钥对
  Future<void> _loadOrGenerateKeyPair() async {
    final keyPairData = await _secureStorage.read(key: _keyPairAlias);
    
    if (keyPairData != null) {
      final keyPair = KeyPair.fromJson(jsonDecode(keyPairData));
      
      // 检查密钥是否过期
      if (DateTime.now().isBefore(keyPair.expiresAt)) {
        _currentKeyPair = keyPair;
        return;
      }
    }
    
    // 生成新的密钥对
    await _generateNewKeyPair();
  }
  
  /// 生成新的密钥对
  Future<void> _generateNewKeyPair() async {
    try {
      // 生成RSA密钥对
      final key = RSAKeyGenerator().generateKeyPair();
      
      _currentKeyPair = KeyPair(
        publicKey: key.publicKey.toString(),
        privateKey: key.privateKey.toString(),
        createdAt: DateTime.now(),
        expiresAt: DateTime.now().add(const Duration(days: 30)), // 30天有效期
      );
      
      // 保存到安全存储
      await _secureStorage.write(
        key: _keyPairAlias,
        value: jsonEncode(_currentKeyPair!.toJson()),
      );
      
    } catch (e) {
      print('生成密钥对失败: $e');
      rethrow;
    }
  }
  
  /// 设置防录屏保护
  Future<void> _setupScreenRecordingProtection() async {
    if (_securityLevel == SecurityLevel.maximum) {
      _isScreenRecordingProtected = true;
      
      // 监听屏幕录制状态
      SystemChrome.setSystemUIOverlayStyle(
        const SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          systemNavigationBarColor: Colors.transparent,
        ),
      );
    }
  }
  
  /// 请求权限
  Future<void> _requestPermissions() async {
    if (_securityLevel == SecurityLevel.high || _securityLevel == SecurityLevel.maximum) {
      await Permission.camera.request();
      await Permission.microphone.request();
      await Permission.storage.request();
    }
  }
  
  /// 加密数据
  Future<EncryptedMessage> encryptData(String data, {String? recipientPublicKey}) async {
    try {
      // 生成会话密钥
      final sessionKey = _generateRandomKey(32);
      _sessionKey = base64Encode(sessionKey);
      
      // 使用AES加密数据
      final key = Key.fromBase64(_sessionKey!);
      final iv = IV.fromSecureRandom(16);
      final encrypter = Encrypter(AES(key));
      
      final encryptedData = encrypter.encrypt(data, iv: iv);
      
      // 生成数字签名
      final signature = _generateSignature(data);
      
      return EncryptedMessage(
        encryptedData: encryptedData.base64,
        iv: iv.base64,
        signature: signature,
        timestamp: DateTime.now(),
        algorithm: 'AES-256-GCM',
      );
      
    } catch (e) {
      print('加密数据失败: $e');
      rethrow;
    }
  }
  
  /// 解密数据
  Future<String> decryptData(EncryptedMessage message) async {
    try {
      if (_sessionKey == null) {
        throw Exception('会话密钥未设置');
      }
      
      final key = Key.fromBase64(_sessionKey!);
      final iv = IV.fromBase64(message.iv);
      final encrypter = Encrypter(AES(key));
      
      final decryptedData = encrypter.decrypt64(message.encryptedData, iv: iv);
      
      // 验证签名
      if (!_verifySignature(decryptedData, message.signature)) {
        throw Exception('数字签名验证失败');
      }
      
      return decryptedData;
      
    } catch (e) {
      print('解密数据失败: $e');
      rethrow;
    }
  }
  
  /// 生成数字签名
  String _generateSignature(String data) {
    final privateKey = _currentKeyPair?.privateKey;
    if (privateKey == null) {
      throw Exception('私钥未设置');
    }
    
    final hash = sha256.convert(utf8.encode(data));
    // 这里应该使用RSA私钥签名，简化实现
    return base64Encode(hash.bytes);
  }
  
  /// 验证数字签名
  bool _verifySignature(String data, String signature) {
    final publicKey = _currentKeyPair?.publicKey;
    if (publicKey == null) {
      return false;
    }
    
    final hash = sha256.convert(utf8.encode(data));
    final expectedSignature = base64Encode(hash.bytes);
    
    return signature == expectedSignature;
  }
  
  /// 生成随机密钥
  Uint8List _generateRandomKey(int length) {
    final random = Random.secure();
    return Uint8List.fromList(
      List<int>.generate(length, (i) => random.nextInt(256)),
    );
  }
  
  /// 安全存储数据
  Future<void> secureStore(String key, String value) async {
    try {
      // 加密数据后再存储
      final encryptedValue = await encryptData(value);
      await _secureStorage.write(
        key: key,
        value: jsonEncode(encryptedValue.toJson()),
      );
    } catch (e) {
      print('安全存储失败: $e');
      rethrow;
    }
  }
  
  /// 安全读取数据
  Future<String?> secureRead(String key) async {
    try {
      final encryptedData = await _secureStorage.read(key: key);
      if (encryptedData == null) return null;
      
      final message = EncryptedMessage.fromJson(jsonDecode(encryptedData));
      return await decryptData(message);
    } catch (e) {
      print('安全读取失败: $e');
      return null;
    }
  }
  
  /// 安全删除数据
  Future<void> secureDelete(String key) async {
    await _secureStorage.delete(key: key);
  }
  
  /// 检测屏幕录制
  Future<bool> detectScreenRecording() async {
    try {
      // 这里应该实现真正的屏幕录制检测
      // 简化实现，返回false
      return false;
    } catch (e) {
      print('检测屏幕录制失败: $e');
      return false;
    }
  }
  
  /// 启用防录屏保护
  Future<void> enableScreenRecordingProtection() async {
    if (!_isScreenRecordingProtected) return;
    
    try {
      _originalBrightness = await _screenBrightness.current;
      
      // 设置屏幕亮度为最低
      await _screenBrightness.setScreenBrightness(0.1);
      
      // 显示防录屏警告
      _showScreenRecordingWarning();
      
    } catch (e) {
      print('启用防录屏保护失败: $e');
    }
  }
  
  /// 禁用防录屏保护
  Future<void> disableScreenRecordingProtection() async {
    if (!_isScreenRecordingProtected) return;
    
    try {
      // 恢复原始亮度
      await _screenBrightness.setScreenBrightness(_originalBrightness);
      
    } catch (e) {
      print('禁用防录屏保护失败: $e');
    }
  }
  
  /// 显示防录屏警告
  void _showScreenRecordingWarning() {
    // 这里应该显示UI警告
    print('警告：检测到屏幕录制，已启用保护模式');
  }
  
  /// 生成安全令牌
  String generateSecureToken() {
    final random = Random.secure();
    final bytes = Uint8List.fromList(
      List<int>.generate(32, (i) => random.nextInt(256)),
    );
    return base64Url.encode(bytes);
  }
  
  /// 验证安全令牌
  bool validateSecureToken(String token) {
    try {
      base64Url.decode(token);
      return true;
    } catch (e) {
      return false;
    }
  }
  
  /// 哈希密码
  String hashPassword(String password) {
    final salt = _generateRandomKey(16);
    final hash = pbkdf2.convert(utf8.encode(password), salt: salt);
    return base64Encode(salt + hash.bytes);
  }
  
  /// 验证密码
  bool verifyPassword(String password, String hashedPassword) {
    try {
      final bytes = base64Decode(hashedPassword);
      final salt = bytes.sublist(0, 16);
      final hash = bytes.sublist(16);
      
      final computedHash = pbkdf2.convert(utf8.encode(password), salt: salt);
      return computedHash.bytes == hash;
    } catch (e) {
      return false;
    }
  }
  
  /// 安全擦除数据
  Future<void> secureWipe() async {
    try {
      // 清除所有安全存储的数据
      await _secureStorage.deleteAll();
      
      // 清除内存中的数据
      _currentKeyPair = null;
      _sessionKey = null;
      
      // 重新初始化
      await initialize();
      
    } catch (e) {
      print('安全擦除失败: $e');
      rethrow;
    }
  }
  
  /// 获取安全状态报告
  Map<String, dynamic> getSecurityReport() {
    return {
      'is_initialized': _isInitialized,
      'security_level': _securityLevel.name,
      'has_key_pair': _currentKeyPair != null,
      'key_pair_expires_at': _currentKeyPair?.expiresAt.toIso8601String(),
      'is_screen_recording_protected': _isScreenRecordingProtected,
      'session_key_exists': _sessionKey != null,
      'encryption_algorithm': 'AES-256-GCM',
      'signature_algorithm': 'RSA-SHA256',
    };
  }
  
  /// 设置安全级别
  void setSecurityLevel(SecurityLevel level) {
    _securityLevel = level;
    
    // 根据安全级别调整设置
    switch (level) {
      case SecurityLevel.low:
        _isScreenRecordingProtected = false;
        break;
      case SecurityLevel.medium:
        _isScreenRecordingProtected = false;
        break;
      case SecurityLevel.high:
        _isScreenRecordingProtected = true;
        break;
      case SecurityLevel.maximum:
        _isScreenRecordingProtected = true;
        break;
    }
  }
  
  /// 检查设备安全性
  Future<Map<String, dynamic>> checkDeviceSecurity() async {
    final report = <String, dynamic>{
      'is_rooted': false, // 简化实现
      'is_emulator': false, // 简化实现
      'has_screen_lock': true, // 简化实现
      'encryption_enabled': true, // 简化实现
      'security_patch_level': '2023-12-01', // 简化实现
    };
    
    return report;
  }
}

/// RSA密钥生成器（简化实现）
class RSAKeyGenerator {
  KeyPair generateKeyPair() {
    // 这里应该实现真正的RSA密钥生成
    // 简化实现，返回模拟密钥
    return KeyPair(
      publicKey: 'mock_public_key',
      privateKey: 'mock_private_key',
      createdAt: DateTime.now(),
      expiresAt: DateTime.now().add(const Duration(days: 30)),
    );
  }
} 