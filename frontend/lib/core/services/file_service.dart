import 'dart:io';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;
import '../config/app_config.dart';
import 'api_service.dart';

class FileService {
  static FileService? _instance;
  static FileService get instance => _instance ??= FileService._();
  
  FileService._();
  
  final ImagePicker _imagePicker = ImagePicker();
  
  /// 选择图片
  Future<File?> pickImage({
    ImageSource source = ImageSource.gallery,
    int? maxWidth,
    int? maxHeight,
    int imageQuality = 80,
  }) async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: source,
        maxWidth: maxWidth?.toDouble(),
        maxHeight: maxHeight?.toDouble(),
        imageQuality: imageQuality,
      );
      
      return image != null ? File(image.path) : null;
    } catch (e) {
      print('选择图片失败: $e');
      return null;
    }
  }
  
  /// 拍摄照片
  Future<File?> takePhoto({
    int? maxWidth,
    int? maxHeight,
    int imageQuality = 80,
  }) async {
    return pickImage(
      source: ImageSource.camera,
      maxWidth: maxWidth,
      maxHeight: maxHeight,
      imageQuality: imageQuality,
    );
  }
  
  /// 录制视频
  Future<File?> recordVideo({
    Duration maxDuration = const Duration(minutes: 5),
    int? maxFileSize,
  }) async {
    try {
      final XFile? video = await _imagePicker.pickVideo(
        source: ImageSource.camera,
        maxDuration: maxDuration,
      );
      
      if (video != null) {
        final file = File(video.path);
        
        // 检查文件大小
        if (maxFileSize != null && await file.length() > maxFileSize) {
          throw Exception('视频文件过大');
        }
        
        return file;
      }
      
      return null;
    } catch (e) {
      print('录制视频失败: $e');
      return null;
    }
  }
  
  /// 录制音频
  Future<File?> recordAudio({
    Duration maxDuration = const Duration(minutes: 5),
  }) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );
      
      if (result != null && result.files.isNotEmpty) {
        final file = File(result.files.first.path!);
        
        // 检查文件大小
        if (await file.length() > AppConfig.maxAudioSize) {
          throw Exception('音频文件过大');
        }
        
        return file;
      }
      
      return null;
    } catch (e) {
      print('录制音频失败: $e');
      return null;
    }
  }
  
  /// 选择文件
  Future<File?> pickFile({
    List<String>? allowedExtensions,
    int? maxFileSize,
  }) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.any,
        allowedExtensions: allowedExtensions,
        allowMultiple: false,
      );
      
      if (result != null && result.files.isNotEmpty) {
        final file = File(result.files.first.path!);
        
        // 检查文件大小
        if (maxFileSize != null && await file.length() > maxFileSize) {
          throw Exception('文件过大');
        }
        
        return file;
      }
      
      return null;
    } catch (e) {
      print('选择文件失败: $e');
      return null;
    }
  }
  
  /// 上传文件
  Future<String?> uploadFile(File file, String type) async {
    try {
      // 检查文件大小
      final fileSize = await file.length();
      if (!_validateFileSize(fileSize, type)) {
        throw Exception('文件大小超出限制');
      }
      
      // 检查文件类型
      if (!_validateFileType(file.path, type)) {
        throw Exception('不支持的文件类型');
      }
      
      // 上传到服务器
      final url = await ApiService.uploadFile(file, type);
      return url;
      
    } catch (e) {
      print('上传文件失败: $e');
      rethrow;
    }
  }
  
  /// 上传图片
  Future<String?> uploadImage(File imageFile) async {
    return uploadFile(imageFile, 'image');
  }
  
  /// 上传视频
  Future<String?> uploadVideo(File videoFile) async {
    return uploadFile(videoFile, 'video');
  }
  
  /// 上传音频
  Future<String?> uploadAudio(File audioFile) async {
    return uploadFile(audioFile, 'audio');
  }
  
  /// 压缩图片
  Future<File?> compressImage(File imageFile, {
    int maxWidth = 1024,
    int maxHeight = 1024,
    int quality = 80,
  }) async {
    try {
      // 这里可以使用 image 包进行图片压缩
      // 暂时返回原文件
      return imageFile;
    } catch (e) {
      print('压缩图片失败: $e');
      return null;
    }
  }
  
  /// 生成缩略图
  Future<File?> generateThumbnail(File videoFile) async {
    try {
      // 这里可以使用 video_thumbnail 包生成视频缩略图
      // 暂时返回空
      return null;
    } catch (e) {
      print('生成缩略图失败: $e');
      return null;
    }
  }
  
  /// 验证文件大小
  bool _validateFileSize(int fileSize, String type) {
    switch (type) {
      case 'image':
        return fileSize <= AppConfig.maxImageSize;
      case 'video':
        return fileSize <= AppConfig.maxVideoSize;
      case 'audio':
        return fileSize <= AppConfig.maxAudioSize;
      default:
        return fileSize <= 50 * 1024 * 1024; // 50MB
    }
  }
  
  /// 验证文件类型
  bool _validateFileType(String filePath, String type) {
    final extension = path.extension(filePath).toLowerCase().replaceAll('.', '');
    
    switch (type) {
      case 'image':
        return AppConfig.allowedImageTypes.contains(extension);
      case 'video':
        return AppConfig.allowedVideoTypes.contains(extension);
      case 'audio':
        return AppConfig.allowedAudioTypes.contains(extension);
      default:
        return true;
    }
  }
  
  /// 获取文件信息
  Future<Map<String, dynamic>> getFileInfo(File file) async {
    try {
      final stat = await file.stat();
      final extension = path.extension(file.path).toLowerCase();
      final fileName = path.basename(file.path);
      
      return {
        'name': fileName,
        'size': stat.size,
        'extension': extension.replaceAll('.', ''),
        'path': file.path,
        'modified': stat.modified.toIso8601String(),
      };
    } catch (e) {
      print('获取文件信息失败: $e');
      return {};
    }
  }
  
  /// 格式化文件大小
  String formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
}

/// 文件类型枚举
enum FileType {
  image,
  video,
  audio,
  document,
  other,
}

/// 文件上传进度回调
typedef FileUploadProgressCallback = void Function(int sent, int total);

/// 文件上传结果
class FileUploadResult {
  final bool success;
  final String? url;
  final String? error;
  final Map<String, dynamic>? metadata;
  
  FileUploadResult({
    required this.success,
    this.url,
    this.error,
    this.metadata,
  });
  
  factory FileUploadResult.success(String url, {Map<String, dynamic>? metadata}) {
    return FileUploadResult(
      success: true,
      url: url,
      metadata: metadata,
    );
  }
  
  factory FileUploadResult.error(String error) {
    return FileUploadResult(
      success: false,
      error: error,
    );
  }
} 