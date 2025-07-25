import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import '../config/app_config.dart';
import 'webrtc_service.dart';
import 'websocket_service.dart';

/// 群组通话类型
enum GroupCallType {
  groupCall,    // 群组通话
  liveStream,   // 直播
  webinar,      // 网络研讨会
}

/// 参与者角色
enum ParticipantRole {
  host,         // 主持人
  coHost,       // 联席主持人
  participant,  // 参与者
  viewer,       // 观众（仅直播）
}

/// 参与者状态
enum ParticipantStatus {
  joining,
  connected,
  disconnected,
  muted,
  videoOff,
  speaking,
}

/// 群组通话参与者
class GroupParticipant {
  final String userId;
  final String userName;
  final String? userAvatar;
  final ParticipantRole role;
  ParticipantStatus status;
  final MediaStream? stream;
  final DateTime joinedAt;
  DateTime? lastActiveAt;
  
  GroupParticipant({
    required this.userId,
    required this.userName,
    this.userAvatar,
    required this.role,
    this.status = ParticipantStatus.joining,
    this.stream,
    required this.joinedAt,
    this.lastActiveAt,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'user_name': userName,
      'user_avatar': userAvatar,
      'role': role.name,
      'status': status.name,
      'joined_at': joinedAt.toIso8601String(),
      'last_active_at': lastActiveAt?.toIso8601String(),
    };
  }
  
  factory GroupParticipant.fromJson(Map<String, dynamic> json) {
    return GroupParticipant(
      userId: json['user_id'],
      userName: json['user_name'],
      userAvatar: json['user_avatar'],
      role: ParticipantRole.values.firstWhere(
        (e) => e.name == json['role'],
        orElse: () => ParticipantRole.participant,
      ),
      status: ParticipantStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => ParticipantStatus.joining,
      ),
      joinedAt: DateTime.parse(json['joined_at']),
      lastActiveAt: json['last_active_at'] != null 
          ? DateTime.parse(json['last_active_at'])
          : null,
    );
  }
}

/// 群组通话配置
class GroupCallConfig {
  final int maxParticipants;
  final int maxViewers;
  final bool enableRecording;
  final bool enableChat;
  final bool enableScreenShare;
  final Duration maxDuration;
  final VideoQuality videoQuality;
  
  const GroupCallConfig({
    this.maxParticipants = 9,
    this.maxViewers = 1000,
    this.enableRecording = false,
    this.enableChat = true,
    this.enableScreenShare = true,
    this.maxDuration = const Duration(hours: 2),
    this.videoQuality = VideoQuality.medium,
  });
}

/// 群组通话状态
enum GroupCallState {
  creating,
  waiting,
  active,
  paused,
  ended,
  error,
}

class GroupCallService {
  static GroupCallService? _instance;
  static GroupCallService get instance => _instance ??= GroupCallService._();
  
  GroupCallService._();
  
  // 群组通话状态
  GroupCallState _callState = GroupCallState.creating;
  String? _callId;
  GroupCallType _callType = GroupCallType.groupCall;
  GroupCallConfig _config = const GroupCallConfig();
  
  // 参与者管理
  final Map<String, GroupParticipant> _participants = {};
  final Map<String, RTCPeerConnection> _peerConnections = {};
  final Map<String, RTCVideoRenderer> _remoteRenderers = {};
  
  // 本地流
  MediaStream? _localStream;
  RTCVideoRenderer? _localRenderer;
  
  // 屏幕共享
  MediaStream? _screenStream;
  bool _isScreenSharing = false;
  
  // 通话统计
  DateTime? _callStartTime;
  int _totalParticipants = 0;
  int _peakParticipants = 0;
  
  // 回调函数
  Function(GroupCallState)? onCallStateChanged;
  Function(GroupParticipant)? onParticipantJoined;
  Function(GroupParticipant)? onParticipantLeft;
  Function(GroupParticipant)? onParticipantStatusChanged;
  Function(String)? onError;
  VoidCallback? onCallEnded;
  
  // Getters
  GroupCallState get callState => _callState;
  String? get callId => _callId;
  GroupCallType get callType => _callType;
  List<GroupParticipant> get participants => _participants.values.toList();
  bool get isScreenSharing => _isScreenSharing;
  int get totalParticipants => _totalParticipants;
  int get peakParticipants => _peakParticipants;
  
  /// 创建群组通话
  Future<bool> createGroupCall({
    required GroupCallType type,
    required String title,
    String? description,
    GroupCallConfig? config,
    List<String>? inviteUserIds,
  }) async {
    try {
      _callType = type;
      _config = config ?? const GroupCallConfig();
      
      // 生成通话ID
      _callId = _generateCallId();
      
      // 初始化本地流
      await _initializeLocalStream();
      
      // 创建WebRTC连接
      await _createPeerConnections();
      
      // 通知服务器创建群组通话
      await _notifyServerCreateCall(title, description, inviteUserIds);
      
      _callState = GroupCallState.waiting;
      onCallStateChanged?.call(_callState);
      
      return true;
      
    } catch (e) {
      print('创建群组通话失败: $e');
      onError?.call('创建群组通话失败: $e');
      return false;
    }
  }
  
  /// 加入群组通话
  Future<bool> joinGroupCall(String callId, {ParticipantRole role = ParticipantRole.participant}) async {
    try {
      _callId = callId;
      
      // 获取通话信息
      final callInfo = await _getCallInfo(callId);
      _callType = GroupCallType.values.firstWhere(
        (e) => e.name == callInfo['type'],
        orElse: () => GroupCallType.groupCall,
      );
      
      // 初始化本地流
      await _initializeLocalStream();
      
      // 加入现有连接
      await _joinExistingCall(callInfo, role);
      
      _callState = GroupCallState.active;
      onCallStateChanged?.call(_callState);
      
      return true;
      
    } catch (e) {
      print('加入群组通话失败: $e');
      onError?.call('加入群组通话失败: $e');
      return false;
    }
  }
  
  /// 开始直播
  Future<bool> startLiveStream({
    required String title,
    String? description,
    bool enableChat = true,
    bool enableRecording = false,
  }) async {
    try {
      _callType = GroupCallType.liveStream;
      _config = GroupCallConfig(
        maxParticipants: 1, // 主播
        maxViewers: 1000,
        enableChat: enableChat,
        enableRecording: enableRecording,
        enableScreenShare: true,
      );
      
      // 创建直播
      final success = await createGroupCall(
        type: GroupCallType.liveStream,
        title: title,
        description: description,
        config: _config,
      );
      
      if (success) {
        _callState = GroupCallState.active;
        onCallStateChanged?.call(_callState);
      }
      
      return success;
      
    } catch (e) {
      print('开始直播失败: $e');
      onError?.call('开始直播失败: $e');
      return false;
    }
  }
  
  /// 结束群组通话
  Future<void> endGroupCall() async {
    try {
      _callState = GroupCallState.ended;
      onCallStateChanged?.call(_callState);
      
      // 通知服务器结束通话
      await _notifyServerEndCall();
      
      // 清理资源
      await _cleanup();
      
      onCallEnded?.call();
      
    } catch (e) {
      print('结束群组通话失败: $e');
    }
  }
  
  /// 邀请用户
  Future<bool> inviteUsers(List<String> userIds) async {
    try {
      await _notifyServerInviteUsers(userIds);
      return true;
    } catch (e) {
      print('邀请用户失败: $e');
      return false;
    }
  }
  
  /// 踢出用户
  Future<bool> kickUser(String userId) async {
    try {
      await _notifyServerKickUser(userId);
      
      // 断开连接
      await _disconnectUser(userId);
      
      return true;
    } catch (e) {
      print('踢出用户失败: $e');
      return false;
    }
  }
  
  /// 切换角色
  Future<bool> changeUserRole(String userId, ParticipantRole newRole) async {
    try {
      await _notifyServerChangeRole(userId, newRole);
      
      final participant = _participants[userId];
      if (participant != null) {
        participant.role = newRole;
        onParticipantStatusChanged?.call(participant);
      }
      
      return true;
    } catch (e) {
      print('切换角色失败: $e');
      return false;
    }
  }
  
  /// 静音/取消静音
  Future<void> toggleMute() async {
    if (_localStream != null) {
      final audioTrack = _localStream!.getAudioTracks().firstOrNull;
      if (audioTrack != null) {
        audioTrack.enabled = !audioTrack.enabled;
        await _notifyServerMuteStatus(!audioTrack.enabled);
      }
    }
  }
  
  /// 开启/关闭摄像头
  Future<void> toggleCamera() async {
    if (_localStream != null) {
      final videoTrack = _localStream!.getVideoTracks().firstOrNull;
      if (videoTrack != null) {
        videoTrack.enabled = !videoTrack.enabled;
        await _notifyServerVideoStatus(!videoTrack.enabled);
      }
    }
  }
  
  /// 开始屏幕共享
  Future<bool> startScreenShare() async {
    try {
      if (!_config.enableScreenShare) return false;
      
      _screenStream = await navigator.mediaDevices.getDisplayMedia({
        'video': true,
        'audio': false,
      });
      
      _isScreenSharing = true;
      
      // 替换视频轨道
      await _replaceVideoTrack(_screenStream!);
      
      await _notifyServerScreenShareStatus(true);
      
      return true;
    } catch (e) {
      print('开始屏幕共享失败: $e');
      return false;
    }
  }
  
  /// 停止屏幕共享
  Future<void> stopScreenShare() async {
    try {
      _isScreenSharing = false;
      
      // 恢复摄像头
      await _replaceVideoTrack(_localStream!);
      
      _screenStream?.dispose();
      _screenStream = null;
      
      await _notifyServerScreenShareStatus(false);
      
    } catch (e) {
      print('停止屏幕共享失败: $e');
    }
  }
  
  /// 录制通话
  Future<bool> startRecording() async {
    try {
      if (!_config.enableRecording) return false;
      
      await _notifyServerRecordingStatus(true);
      return true;
    } catch (e) {
      print('开始录制失败: $e');
      return false;
    }
  }
  
  /// 停止录制
  Future<void> stopRecording() async {
    try {
      await _notifyServerRecordingStatus(false);
    } catch (e) {
      print('停止录制失败: $e');
    }
  }
  
  /// 获取通话统计
  Map<String, dynamic> getCallStats() {
    final duration = _callStartTime != null 
        ? DateTime.now().difference(_callStartTime!).inSeconds
        : 0;
    
    return {
      'call_id': _callId,
      'call_type': _callType.name,
      'call_state': _callState.name,
      'duration': duration,
      'total_participants': _totalParticipants,
      'peak_participants': _peakParticipants,
      'current_participants': _participants.length,
      'is_screen_sharing': _isScreenSharing,
      'config': {
        'max_participants': _config.maxParticipants,
        'max_viewers': _config.maxViewers,
        'enable_recording': _config.enableRecording,
        'enable_chat': _config.enableChat,
        'enable_screen_share': _config.enableScreenShare,
      },
    };
  }
  
  // 私有方法
  
  /// 生成通话ID
  String _generateCallId() {
    return 'group_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(1000)}';
  }
  
  /// 初始化本地流
  Future<void> _initializeLocalStream() async {
    final constraints = {
      'audio': true,
      'video': {
        'mandatory': {
          'minWidth': _config.videoQuality.width.toString(),
          'minHeight': _config.videoQuality.height.toString(),
          'minFrameRate': _config.videoQuality.frameRate.toString(),
        },
        'facingMode': 'user',
        'optional': [],
      },
    };
    
    _localStream = await navigator.mediaDevices.getUserMedia(constraints);
    
    if (_localRenderer != null) {
      _localRenderer!.srcObject = _localStream;
    }
  }
  
  /// 创建对等连接
  Future<void> _createPeerConnections() async {
    // 这里应该为每个参与者创建连接
    // 简化实现
  }
  
  /// 通知服务器创建通话
  Future<void> _notifyServerCreateCall(String title, String? description, List<String>? inviteUserIds) async {
    WebSocketService.instance.send({
      'type': 'group_call_create',
      'call_id': _callId,
      'call_type': _callType.name,
      'title': title,
      'description': description,
      'config': {
        'max_participants': _config.maxParticipants,
        'max_viewers': _config.maxViewers,
        'enable_recording': _config.enableRecording,
        'enable_chat': _config.enableChat,
        'enable_screen_share': _config.enableScreenShare,
      },
      'invite_user_ids': inviteUserIds,
    });
  }
  
  /// 获取通话信息
  Future<Map<String, dynamic>> _getCallInfo(String callId) async {
    // 这里应该从服务器获取通话信息
    // 简化实现
    return {
      'call_id': callId,
      'type': 'groupCall',
      'participants': [],
    };
  }
  
  /// 加入现有通话
  Future<void> _joinExistingCall(Map<String, dynamic> callInfo, ParticipantRole role) async {
    WebSocketService.instance.send({
      'type': 'group_call_join',
      'call_id': _callId,
      'role': role.name,
    });
  }
  
  /// 通知服务器结束通话
  Future<void> _notifyServerEndCall() async {
    WebSocketService.instance.send({
      'type': 'group_call_end',
      'call_id': _callId,
    });
  }
  
  /// 通知服务器邀请用户
  Future<void> _notifyServerInviteUsers(List<String> userIds) async {
    WebSocketService.instance.send({
      'type': 'group_call_invite',
      'call_id': _callId,
      'user_ids': userIds,
    });
  }
  
  /// 通知服务器踢出用户
  Future<void> _notifyServerKickUser(String userId) async {
    WebSocketService.instance.send({
      'type': 'group_call_kick',
      'call_id': _callId,
      'user_id': userId,
    });
  }
  
  /// 通知服务器切换角色
  Future<void> _notifyServerChangeRole(String userId, ParticipantRole role) async {
    WebSocketService.instance.send({
      'type': 'group_call_change_role',
      'call_id': _callId,
      'user_id': userId,
      'role': role.name,
    });
  }
  
  /// 通知服务器静音状态
  Future<void> _notifyServerMuteStatus(bool isMuted) async {
    WebSocketService.instance.send({
      'type': 'group_call_mute',
      'call_id': _callId,
      'is_muted': isMuted,
    });
  }
  
  /// 通知服务器视频状态
  Future<void> _notifyServerVideoStatus(bool isVideoOff) async {
    WebSocketService.instance.send({
      'type': 'group_call_video',
      'call_id': _callId,
      'is_video_off': isVideoOff,
    });
  }
  
  /// 通知服务器屏幕共享状态
  Future<void> _notifyServerScreenShareStatus(bool isSharing) async {
    WebSocketService.instance.send({
      'type': 'group_call_screen_share',
      'call_id': _callId,
      'is_sharing': isSharing,
    });
  }
  
  /// 通知服务器录制状态
  Future<void> _notifyServerRecordingStatus(bool isRecording) async {
    WebSocketService.instance.send({
      'type': 'group_call_recording',
      'call_id': _callId,
      'is_recording': isRecording,
    });
  }
  
  /// 替换视频轨道
  Future<void> _replaceVideoTrack(MediaStream newStream) async {
    final newVideoTrack = newStream.getVideoTracks().firstOrNull;
    if (newVideoTrack == null) return;
    
    for (final connection in _peerConnections.values) {
      final senders = await connection.getSenders();
      final videoSender = senders.firstWhere(
        (sender) => sender.track?.kind == 'video',
        orElse: () => null,
      );
      
      if (videoSender != null) {
        await videoSender.replaceTrack(newVideoTrack);
      }
    }
  }
  
  /// 断开用户连接
  Future<void> _disconnectUser(String userId) async {
    final connection = _peerConnections[userId];
    if (connection != null) {
      await connection.close();
      _peerConnections.remove(userId);
    }
    
    final renderer = _remoteRenderers[userId];
    if (renderer != null) {
      renderer.dispose();
      _remoteRenderers.remove(userId);
    }
    
    _participants.remove(userId);
  }
  
  /// 清理资源
  Future<void> _cleanup() async {
    // 清理本地流
    _localStream?.dispose();
    _localStream = null;
    
    // 清理屏幕共享流
    _screenStream?.dispose();
    _screenStream = null;
    
    // 清理对等连接
    for (final connection in _peerConnections.values) {
      await connection.close();
    }
    _peerConnections.clear();
    
    // 清理渲染器
    for (final renderer in _remoteRenderers.values) {
      renderer.dispose();
    }
    _remoteRenderers.clear();
    
    // 清理参与者
    _participants.clear();
    
    // 重置状态
    _callId = null;
    _callState = GroupCallState.creating;
    _isScreenSharing = false;
    _callStartTime = null;
    _totalParticipants = 0;
    _peakParticipants = 0;
  }
} 