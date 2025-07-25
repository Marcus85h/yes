import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image/image.dart' as img;
import 'package:video_compress/video_compress.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:device_info_plus/device_info_plus.dart';
import '../config/app_config.dart';

/// 网络类型
enum NetworkType {
  wifi,
  mobile4g,
  mobile3g,
  mobile2g,
  unknown,
}

/// 设备性能等级
enum DevicePerformance {
  high,
  medium,
  low,
}

/// 视频质量设置
class VideoQuality {
  final int width;
  final int height;
  final int bitrate;
  final int frameRate;
  
  const VideoQuality({
    required this.width,
    required this.height,
    required this.bitrate,
    required this.frameRate,
  });
  
  static const VideoQuality high = VideoQuality(
    width: 1280,
    height: 720,
    bitrate: 2000000,
    frameRate: 30,
  );
  
  static const VideoQuality medium = VideoQuality(
    width: 854,
    height: 480,
    bitrate: 1000000,
    frameRate: 25,
  );
  
  static const VideoQuality low = VideoQuality(
    width: 640,
    height: 360,
    bitrate: 500000,
    frameRate: 20,
  );
}

class PerformanceService {
  static PerformanceService? _instance;
  static PerformanceService get instance => _instance ??= PerformanceService._();
  
  PerformanceService._();
  
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  final Connectivity _connectivity = Connectivity();
  
  // 缓存目录
  Directory? _cacheDir;
  Directory? _tempDir;
  
  // 性能配置
  DevicePerformance _devicePerformance = DevicePerformance.medium;
  NetworkType _currentNetwork = NetworkType.unknown;
  VideoQuality _currentVideoQuality = VideoQuality.medium;
  
  // 缓存管理
  final Map<String, dynamic> _memoryCache = {};
  final int _maxMemoryCacheSize = 100; // MB
  int _currentMemoryUsage = 0;
  
  // 性能监控
  final List<double> _frameRates = [];
  final List<int> _latencies = [];
  final List<double> _bandwidthUsage = [];
  
  // Getters
  DevicePerformance get devicePerformance => _devicePerformance;
  NetworkType get currentNetwork => _currentNetwork;
  VideoQuality get currentVideoQuality => _currentVideoQuality;
  
  /// 初始化性能服务
  Future<void> initialize() async {
    await _initializeDirectories();
    await _detectDevicePerformance();
    await _setupNetworkMonitoring();
    await _cleanupCache();
    
    print('性能服务初始化完成');
  }
  
  /// 初始化目录
  Future<void> _initializeDirectories() async {
    _cacheDir = await getApplicationCacheDirectory();
    _tempDir = await getTemporaryDirectory();
    
    // 创建子目录
    await _cacheDir!.create(recursive: true);
    await _tempDir!.create(recursive: true);
  }
  
  /// 检测设备性能
  Future<void> _detectDevicePerformance() async {
    try {
      if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        final sdkInt = androidInfo.version.sdkInt;
        final memory = androidInfo.totalMemory;
        
        if (sdkInt >= 30 && memory > 4 * 1024 * 1024 * 1024) {
          _devicePerformance = DevicePerformance.high;
        } else if (sdkInt >= 24 && memory > 2 * 1024 * 1024 * 1024) {
          _devicePerformance = DevicePerformance.medium;
        } else {
          _devicePerformance = DevicePerformance.low;
        }
      } else if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        final systemVersion = iosInfo.systemVersion;
        final memory = iosInfo.totalMemory;
        
        if (double.parse(systemVersion) >= 14.0 && memory > 4 * 1024 * 1024 * 1024) {
          _devicePerformance = DevicePerformance.high;
        } else if (double.parse(systemVersion) >= 12.0 && memory > 2 * 1024 * 1024 * 1024) {
          _devicePerformance = DevicePerformance.medium;
        } else {
          _devicePerformance = DevicePerformance.low;
        }
      }
      
      // 根据设备性能设置视频质量
      _setOptimalVideoQuality();
      
    } catch (e) {
      print('设备性能检测失败: $e');
      _devicePerformance = DevicePerformance.medium;
    }
  }
  
  /// 设置网络监控
  Future<void> _setupNetworkMonitoring() async {
    _connectivity.onConnectivityChanged.listen((result) {
      _updateNetworkType(result);
      _adjustVideoQualityForNetwork();
    });
    
    // 获取当前网络状态
    final result = await _connectivity.checkConnectivity();
    _updateNetworkType(result);
  }
  
  /// 更新网络类型
  void _updateNetworkType(ConnectivityResult result) {
    switch (result) {
      case ConnectivityResult.wifi:
        _currentNetwork = NetworkType.wifi;
        break;
      case ConnectivityResult.mobile:
        // 这里可以进一步检测4G/3G/2G
        _currentNetwork = NetworkType.mobile4g;
        break;
      default:
        _currentNetwork = NetworkType.unknown;
    }
  }
  
  /// 设置最优视频质量
  void _setOptimalVideoQuality() {
    switch (_devicePerformance) {
      case DevicePerformance.high:
        _currentVideoQuality = VideoQuality.high;
        break;
      case DevicePerformance.medium:
        _currentVideoQuality = VideoQuality.medium;
        break;
      case DevicePerformance.low:
        _currentVideoQuality = VideoQuality.low;
        break;
    }
  }
  
  /// 根据网络调整视频质量
  void _adjustVideoQualityForNetwork() {
    switch (_currentNetwork) {
      case NetworkType.wifi:
        // WiFi环境下可以使用高质量
        if (_devicePerformance == DevicePerformance.high) {
          _currentVideoQuality = VideoQuality.high;
        } else {
          _currentVideoQuality = VideoQuality.medium;
        }
        break;
      case NetworkType.mobile4g:
        _currentVideoQuality = VideoQuality.medium;
        break;
      case NetworkType.mobile3g:
      case NetworkType.mobile2g:
        _currentVideoQuality = VideoQuality.low;
        break;
      default:
        _currentVideoQuality = VideoQuality.low;
    }
  }
  
  /// 压缩图片
  Future<File> compressImage(File imageFile, {int? maxWidth, int? maxHeight, int? quality}) async {
    try {
      final bytes = await imageFile.readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image == null) throw Exception('无法解码图片');
      
      // 计算压缩尺寸
      int targetWidth = maxWidth ?? _currentVideoQuality.width;
      int targetHeight = maxHeight ?? _currentVideoQuality.height;
      
      // 保持宽高比
      final ratio = image.width / image.height;
      if (ratio > 1) {
        targetHeight = (targetWidth / ratio).round();
      } else {
        targetWidth = (targetHeight * ratio).round();
      }
      
      // 压缩图片
      final compressed = img.copyResize(image, width: targetWidth, height: targetHeight);
      final compressedBytes = img.encodeJpg(compressed, quality: quality ?? 85);
      
      // 保存压缩后的图片
      final compressedFile = File('${_tempDir!.path}/compressed_${DateTime.now().millisecondsSinceEpoch}.jpg');
      await compressedFile.writeAsBytes(compressedBytes);
      
      return compressedFile;
      
    } catch (e) {
      print('图片压缩失败: $e');
      return imageFile; // 返回原文件
    }
  }
  
  /// 压缩视频
  Future<File?> compressVideo(File videoFile) async {
    try {
      final result = await VideoCompress.compressVideo(
        videoFile.path,
        quality: _getVideoCompressionQuality(),
        deleteOrigin: false,
        includeAudio: true,
      );
      
      if (result?.file != null) {
        return result!.file;
      }
      
      return null;
    } catch (e) {
      print('视频压缩失败: $e');
      return null;
    }
  }
  
  /// 获取视频压缩质量
  VideoQuality _getVideoCompressionQuality() {
    switch (_currentVideoQuality) {
      case VideoQuality.high:
        return VideoQuality.medium; // 压缩时降级
      case VideoQuality.medium:
        return VideoQuality.low;
      case VideoQuality.low:
        return VideoQuality.low;
    }
  }
  
  /// 缓存管理
  Future<void> cacheData(String key, dynamic data, {int? size}) async {
    try {
      final dataSize = size ?? _estimateDataSize(data);
      
      // 检查内存使用量
      if (_currentMemoryUsage + dataSize > _maxMemoryCacheSize * 1024 * 1024) {
        await _cleanupMemoryCache();
      }
      
      _memoryCache[key] = {
        'data': data,
        'size': dataSize,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      _currentMemoryUsage += dataSize;
      
    } catch (e) {
      print('缓存数据失败: $e');
    }
  }
  
  /// 获取缓存数据
  dynamic getCachedData(String key) {
    final cached = _memoryCache[key];
    if (cached != null) {
      // 更新访问时间
      cached['timestamp'] = DateTime.now().millisecondsSinceEpoch;
      return cached['data'];
    }
    return null;
  }
  
  /// 清理内存缓存
  Future<void> _cleanupMemoryCache() async {
    if (_memoryCache.isEmpty) return;
    
    // 按访问时间排序
    final sortedKeys = _memoryCache.keys.toList()
      ..sort((a, b) => _memoryCache[b]!['timestamp'] - _memoryCache[a]!['timestamp']);
    
    // 删除最旧的缓存
    while (_currentMemoryUsage > _maxMemoryCacheSize * 1024 * 1024 * 0.8 && sortedKeys.isNotEmpty) {
      final key = sortedKeys.removeLast();
      final cached = _memoryCache.remove(key);
      if (cached != null) {
        _currentMemoryUsage -= cached['size'];
      }
    }
  }
  
  /// 清理文件缓存
  Future<void> _cleanupCache() async {
    try {
      if (_cacheDir != null) {
        final files = _cacheDir!.listSync();
        final now = DateTime.now();
        
        for (final file in files) {
          if (file is File) {
            final stat = file.statSync();
            final age = now.difference(stat.modified);
            
            // 删除超过7天的缓存文件
            if (age.inDays > 7) {
              await file.delete();
            }
          }
        }
      }
    } catch (e) {
      print('清理缓存失败: $e');
    }
  }
  
  /// 估算数据大小
  int _estimateDataSize(dynamic data) {
    if (data is String) {
      return data.length;
    } else if (data is Uint8List) {
      return data.length;
    } else if (data is Map || data is List) {
      return 1024; // 估算值
    }
    return 512; // 默认值
  }
  
  /// 性能监控
  void recordFrameRate(double fps) {
    _frameRates.add(fps);
    if (_frameRates.length > 100) {
      _frameRates.removeAt(0);
    }
  }
  
  void recordLatency(int latency) {
    _latencies.add(latency);
    if (_latencies.length > 100) {
      _latencies.removeAt(0);
    }
  }
  
  void recordBandwidthUsage(double bandwidth) {
    _bandwidthUsage.add(bandwidth);
    if (_bandwidthUsage.length > 100) {
      _bandwidthUsage.removeAt(0);
    }
  }
  
  /// 获取性能统计
  Map<String, dynamic> getPerformanceStats() {
    return {
      'device_performance': _devicePerformance.name,
      'network_type': _currentNetwork.name,
      'video_quality': {
        'width': _currentVideoQuality.width,
        'height': _currentVideoQuality.height,
        'bitrate': _currentVideoQuality.bitrate,
        'frame_rate': _currentVideoQuality.frameRate,
      },
      'average_frame_rate': _frameRates.isNotEmpty 
          ? _frameRates.reduce((a, b) => a + b) / _frameRates.length 
          : 0.0,
      'average_latency': _latencies.isNotEmpty 
          ? _latencies.reduce((a, b) => a + b) / _latencies.length 
          : 0,
      'average_bandwidth': _bandwidthUsage.isNotEmpty 
          ? _bandwidthUsage.reduce((a, b) => a + b) / _bandwidthUsage.length 
          : 0.0,
      'memory_cache_size': _currentMemoryUsage,
      'memory_cache_count': _memoryCache.length,
    };
  }
  
  /// 获取网络状态信息
  Future<Map<String, dynamic>> getNetworkInfo() async {
    try {
      final result = await _connectivity.checkConnectivity();
      return {
        'type': result.name,
        'is_connected': result != ConnectivityResult.none,
        'network_type': _currentNetwork.name,
      };
    } catch (e) {
      return {
        'type': 'unknown',
        'is_connected': false,
        'network_type': 'unknown',
      };
    }
  }
  
  /// 预加载资源
  Future<void> preloadResources(List<String> urls) async {
    for (final url in urls) {
      try {
        // 这里可以实现资源预加载逻辑
        await Future.delayed(const Duration(milliseconds: 100));
      } catch (e) {
        print('预加载资源失败: $url - $e');
      }
    }
  }
  
  /// 优化内存使用
  void optimizeMemory() {
    // 清理内存缓存
    _cleanupMemoryCache();
    
    // 清理性能监控数据
    if (_frameRates.length > 50) {
      _frameRates.removeRange(0, _frameRates.length - 50);
    }
    if (_latencies.length > 50) {
      _latencies.removeRange(0, _latencies.length - 50);
    }
    if (_bandwidthUsage.length > 50) {
      _bandwidthUsage.removeRange(0, _bandwidthUsage.length - 50);
    }
  }
} 