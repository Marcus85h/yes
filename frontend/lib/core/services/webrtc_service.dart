import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';
import 'websocket_service.dart';

class WebRTCService {
  static WebRTCService? _instance;
  static WebRTCService get instance => _instance ??= WebRTCService._();
  
  WebRTCService._();
  
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  MediaStream? _remoteStream;
  
  // 状态管理
  bool _isInitialized = false;
  bool _isConnected = false;
  bool _isCallActive = false;
  String? _sessionId;
  String? _remoteUserId;
  
  // 回调函数
  Function(MediaStream)? onLocalStream;
  Function(MediaStream)? onRemoteStream;
  Function(String)? onConnectionStateChanged;
  Function(String)? onIceConnectionStateChanged;
  Function(String)? onError;
  VoidCallback? onCallEnded;
  
  // 配置
  final Map<String, dynamic> _configuration = {
    'iceServers': [
      {'urls': 'stun:stun.l.google.com:19302'},
      {'urls': 'stun:stun1.l.google.com:19302'},
    ],
  };
  
  final Map<String, dynamic> _constraints = {
    'mandatory': {
      'OfferToReceiveAudio': true,
      'OfferToReceiveVideo': true,
    },
    'optional': [],
  };
  
  // Getters
  bool get isInitialized => _isInitialized;
  bool get isConnected => _isConnected;
  bool get isCallActive => _isCallActive;
  MediaStream? get localStream => _localStream;
  MediaStream? get remoteStream => _remoteStream;
  
  /// 初始化WebRTC
  Future<bool> initialize() async {
    try {
      // 初始化WebRTC
      await _initializePeerConnection();
      _isInitialized = true;
      print('WebRTC初始化成功');
      return true;
    } catch (e) {
      print('WebRTC初始化失败: $e');
      onError?.call('WebRTC初始化失败: $e');
      return false;
    }
  }
  
  /// 初始化对等连接
  Future<void> _initializePeerConnection() async {
    _peerConnection = await createPeerConnection(_configuration, _constraints);
    
    // 监听连接状态变化
    _peerConnection!.onConnectionState = (RTCPeerConnectionState state) {
      final stateStr = state.toString().split('.').last;
      print('连接状态: $stateStr');
      onConnectionStateChanged?.call(stateStr);
      
      if (state == RTCPeerConnectionState.RTCPeerConnectionStateConnected) {
        _isConnected = true;
      } else if (state == RTCPeerConnectionState.RTCPeerConnectionStateDisconnected) {
        _isConnected = false;
      }
    };
    
    // 监听ICE连接状态
    _peerConnection!.onIceConnectionState = (RTCIceConnectionState state) {
      final stateStr = state.toString().split('.').last;
      print('ICE连接状态: $stateStr');
      onIceConnectionStateChanged?.call(stateStr);
    };
    
    // 监听远程流
    _peerConnection!.onTrack = (RTCTrackEvent event) {
      if (event.streams.isNotEmpty) {
        _remoteStream = event.streams[0];
        onRemoteStream?.call(_remoteStream!);
        print('收到远程流');
      }
    };
    
    // 监听ICE候选
    _peerConnection!.onIceCandidate = (RTCIceCandidate candidate) {
      _sendIceCandidate(candidate);
    };
  }
  
  /// 开始通话
  Future<bool> startCall(String sessionId, String remoteUserId, {bool isVideo = true}) async {
    if (!_isInitialized) {
      final initialized = await initialize();
      if (!initialized) return false;
    }
    
    try {
      _sessionId = sessionId;
      _remoteUserId = remoteUserId;
      _isCallActive = true;
      
      // 获取本地媒体流
      await _getLocalStream(isVideo: isVideo);
      
      // 添加本地流到对等连接
      _localStream!.getTracks().forEach((track) {
        _peerConnection!.addTrack(track, _localStream!);
      });
      
      // 创建Offer
      final offer = await _peerConnection!.createOffer();
      await _peerConnection!.setLocalDescription(offer);
      
      // 发送Offer到远程用户
      _sendOffer(offer);
      
      print('开始通话: $sessionId');
      return true;
      
    } catch (e) {
      print('开始通话失败: $e');
      onError?.call('开始通话失败: $e');
      return false;
    }
  }
  
  /// 接听通话
  Future<bool> answerCall(String sessionId, String remoteUserId, RTCSessionDescription offer, {bool isVideo = true}) async {
    if (!_isInitialized) {
      final initialized = await initialize();
      if (!initialized) return false;
    }
    
    try {
      _sessionId = sessionId;
      _remoteUserId = remoteUserId;
      _isCallActive = true;
      
      // 获取本地媒体流
      await _getLocalStream(isVideo: isVideo);
      
      // 添加本地流到对等连接
      _localStream!.getTracks().forEach((track) {
        _peerConnection!.addTrack(track, _localStream!);
      });
      
      // 设置远程Offer
      await _peerConnection!.setRemoteDescription(offer);
      
      // 创建Answer
      final answer = await _peerConnection!.createAnswer();
      await _peerConnection!.setLocalDescription(answer);
      
      // 发送Answer到远程用户
      _sendAnswer(answer);
      
      print('接听通话: $sessionId');
      return true;
      
    } catch (e) {
      print('接听通话失败: $e');
      onError?.call('接听通话失败: $e');
      return false;
    }
  }
  
  /// 获取本地媒体流
  Future<void> _getLocalStream({bool isVideo = true}) async {
    final constraints = {
      'audio': true,
      'video': isVideo ? {
        'mandatory': {
          'minWidth': '640',
          'minHeight': '480',
          'minFrameRate': '30',
        },
        'facingMode': 'user',
        'optional': [],
      } : false,
    };
    
    _localStream = await navigator.mediaDevices.getUserMedia(constraints);
    onLocalStream?.call(_localStream!);
    print('获取本地流成功');
  }
  
  /// 切换摄像头
  Future<void> switchCamera() async {
    if (_localStream != null) {
      final videoTrack = _localStream!.getVideoTracks().firstOrNull;
      if (videoTrack != null) {
        await Helper.switchCamera(videoTrack);
        print('切换摄像头');
      }
    }
  }
  
  /// 静音/取消静音
  Future<void> toggleMute() async {
    if (_localStream != null) {
      final audioTrack = _localStream!.getAudioTracks().firstOrNull;
      if (audioTrack != null) {
        audioTrack.enabled = !audioTrack.enabled;
        print('${audioTrack.enabled ? "取消静音" : "静音"}');
      }
    }
  }
  
  /// 开启/关闭摄像头
  Future<void> toggleCamera() async {
    if (_localStream != null) {
      final videoTrack = _localStream!.getVideoTracks().firstOrNull;
      if (videoTrack != null) {
        videoTrack.enabled = !videoTrack.enabled;
        print('${videoTrack.enabled ? "开启摄像头" : "关闭摄像头"}');
      }
    }
  }
  
  /// 结束通话
  Future<void> endCall() async {
    try {
      _isCallActive = false;
      _isConnected = false;
      
      // 发送结束通话信号
      _sendCallEnded();
      
      // 释放资源
      await _dispose();
      
      onCallEnded?.call();
      print('通话结束');
      
    } catch (e) {
      print('结束通话失败: $e');
    }
  }
  
  /// 释放资源
  Future<void> _dispose() async {
    _localStream?.dispose();
    _localStream = null;
    
    _remoteStream?.dispose();
    _remoteStream = null;
    
    await _peerConnection?.close();
    _peerConnection = null;
    
    _isInitialized = false;
    _sessionId = null;
    _remoteUserId = null;
  }
  
  /// 处理远程Offer
  Future<void> handleRemoteOffer(RTCSessionDescription offer) async {
    try {
      await _peerConnection!.setRemoteDescription(offer);
      
      final answer = await _peerConnection!.createAnswer();
      await _peerConnection!.setLocalDescription(answer);
      
      _sendAnswer(answer);
      
    } catch (e) {
      print('处理远程Offer失败: $e');
      onError?.call('处理远程Offer失败: $e');
    }
  }
  
  /// 处理远程Answer
  Future<void> handleRemoteAnswer(RTCSessionDescription answer) async {
    try {
      await _peerConnection!.setRemoteDescription(answer);
    } catch (e) {
      print('处理远程Answer失败: $e');
      onError?.call('处理远程Answer失败: $e');
    }
  }
  
  /// 处理ICE候选
  Future<void> handleIceCandidate(RTCIceCandidate candidate) async {
    try {
      await _peerConnection!.addCandidate(candidate);
    } catch (e) {
      print('处理ICE候选失败: $e');
    }
  }
  
  // WebSocket信令方法
  void _sendOffer(RTCSessionDescription offer) {
    WebSocketService.instance.send({
      'type': 'webrtc_offer',
      'session_id': _sessionId,
      'remote_user_id': _remoteUserId,
      'sdp': offer.sdp,
      'type': offer.type,
    });
  }
  
  void _sendAnswer(RTCSessionDescription answer) {
    WebSocketService.instance.send({
      'type': 'webrtc_answer',
      'session_id': _sessionId,
      'remote_user_id': _remoteUserId,
      'sdp': answer.sdp,
      'type': answer.type,
    });
  }
  
  void _sendIceCandidate(RTCIceCandidate candidate) {
    WebSocketService.instance.send({
      'type': 'webrtc_ice_candidate',
      'session_id': _sessionId,
      'remote_user_id': _remoteUserId,
      'candidate': candidate.candidate,
      'sdpMLineIndex': candidate.sdpMLineIndex,
      'sdpMid': candidate.sdpMid,
    });
  }
  
  void _sendCallEnded() {
    WebSocketService.instance.send({
      'type': 'webrtc_call_ended',
      'session_id': _sessionId,
      'remote_user_id': _remoteUserId,
    });
  }
}

/// WebRTC通话状态
enum CallState {
  idle,
  calling,
  ringing,
  connected,
  ended,
  error,
}

/// WebRTC通话类型
enum CallType {
  audio,
  video,
} 