import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/services/webrtc_service.dart';
import '../../../core/theme/app_theme.dart';

class VideoCallPage extends StatefulWidget {
  final String remoteUserId;
  final String remoteUserName;
  final String? remoteUserAvatar;
  final CallType callType;
  final bool isIncoming;
  final RTCSessionDescription? offer;

  const VideoCallPage({
    Key? key,
    required this.remoteUserId,
    required this.remoteUserName,
    this.remoteUserAvatar,
    required this.callType,
    this.isIncoming = false,
    this.offer,
  }) : super(key: key);

  @override
  State<VideoCallPage> createState() => _VideoCallPageState();
}

class _VideoCallPageState extends State<VideoCallPage> with WidgetsBindingObserver {
  final WebRTCService _webrtcService = WebRTCService.instance;
  
  CallState _callState = CallState.idle;
  bool _isMuted = false;
  bool _isCameraOff = false;
  bool _isSpeakerOn = true;
  bool _isFrontCamera = true;
  
  RTCVideoRenderer? _localRenderer;
  RTCVideoRenderer? _remoteRenderer;
  
  String _sessionId = '';
  String _callDuration = '00:00';
  int _callStartTime = 0;
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeRenderers();
    _setupWebRTC();
    _startCall();
  }
  
  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _localRenderer?.dispose();
    _remoteRenderer?.dispose();
    super.dispose();
  }
  
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused) {
      // 应用进入后台，暂停视频
      _pauseVideo();
    } else if (state == AppLifecycleState.resumed) {
      // 应用恢复前台，恢复视频
      _resumeVideo();
    }
  }
  
  /// 初始化视频渲染器
  Future<void> _initializeRenderers() async {
    _localRenderer = RTCVideoRenderer();
    _remoteRenderer = RTCVideoRenderer();
    
    await _localRenderer!.initialize();
    await _remoteRenderer!.initialize();
  }
  
  /// 设置WebRTC
  void _setupWebRTC() {
    _webrtcService.onLocalStream = (stream) {
      _localRenderer?.srcObject = stream;
    };
    
    _webrtcService.onRemoteStream = (stream) {
      _remoteRenderer?.srcObject = stream;
    };
    
    _webrtcService.onConnectionStateChanged = (state) {
      setState(() {
        if (state == 'connected') {
          _callState = CallState.connected;
          _startCallTimer();
        } else if (state == 'disconnected') {
          _callState = CallState.ended;
          _endCall();
        }
      });
    };
    
    _webrtcService.onError = (error) {
      setState(() {
        _callState = CallState.error;
      });
      _showErrorDialog(error);
    };
    
    _webrtcService.onCallEnded = () {
      _endCall();
    };
  }
  
  /// 开始通话
  Future<void> _startCall() async {
    setState(() {
      _callState = widget.isIncoming ? CallState.ringing : CallState.calling;
    });
    
    _sessionId = DateTime.now().millisecondsSinceEpoch.toString();
    
    try {
      bool success;
      if (widget.isIncoming && widget.offer != null) {
        success = await _webrtcService.answerCall(
          _sessionId,
          widget.remoteUserId,
          widget.offer!,
          isVideo: widget.callType == CallType.video,
        );
      } else {
        success = await _webrtcService.startCall(
          _sessionId,
          widget.remoteUserId,
          isVideo: widget.callType == CallType.video,
        );
      }
      
      if (!success) {
        setState(() {
          _callState = CallState.error;
        });
        _showErrorDialog('启动通话失败');
      }
    } catch (e) {
      setState(() {
        _callState = CallState.error;
      });
      _showErrorDialog('启动通话异常: $e');
    }
  }
  
  /// 开始通话计时器
  void _startCallTimer() {
    _callStartTime = DateTime.now().millisecondsSinceEpoch;
    Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_callState == CallState.connected) {
        final duration = DateTime.now().millisecondsSinceEpoch - _callStartTime;
        final minutes = (duration / 60000).floor();
        final seconds = ((duration % 60000) / 1000).floor();
        setState(() {
          _callDuration = '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
        });
      } else {
        timer.cancel();
      }
    });
  }
  
  /// 结束通话
  Future<void> _endCall() async {
    await _webrtcService.endCall();
    if (mounted) {
      Navigator.of(context).pop();
    }
  }
  
  /// 暂停视频
  void _pauseVideo() {
    // 实现视频暂停逻辑
  }
  
  /// 恢复视频
  void _resumeVideo() {
    // 实现视频恢复逻辑
  }
  
  /// 切换静音
  Future<void> _toggleMute() async {
    await _webrtcService.toggleMute();
    setState(() {
      _isMuted = !_isMuted;
    });
  }
  
  /// 切换摄像头
  Future<void> _toggleCamera() async {
    if (widget.callType == CallType.video) {
      await _webrtcService.toggleCamera();
      setState(() {
        _isCameraOff = !_isCameraOff;
      });
    }
  }
  
  /// 切换前后摄像头
  Future<void> _switchCamera() async {
    if (widget.callType == CallType.video) {
      await _webrtcService.switchCamera();
      setState(() {
        _isFrontCamera = !_isFrontCamera;
      });
    }
  }
  
  /// 切换扬声器
  void _toggleSpeaker() {
    setState(() {
      _isSpeakerOn = !_isSpeakerOn;
    });
    // 实现扬声器切换逻辑
  }
  
  /// 显示错误对话框
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('通话错误'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop();
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isVideo = widget.callType == CallType.video;
    
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            // 远程视频（全屏）
            if (isVideo && _remoteRenderer != null)
              RTCVideoView(
                _remoteRenderer!,
                objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
              ),
            
            // 本地视频（小窗口）
            if (isVideo && _localRenderer != null)
              Positioned(
                top: 60,
                right: 20,
                child: Container(
                  width: 120,
                  height: 160,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: RTCVideoView(
                      _localRenderer!,
                      objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
                    ),
                  ),
                ),
              ),
            
            // 顶部信息栏
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.black.withOpacity(0.7),
                      Colors.transparent,
                    ],
                  ),
                ),
                child: Column(
                  children: [
                    // 状态和时长
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          _getCallStateIcon(),
                          color: Colors.white,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _getCallStateText(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        if (_callState == CallState.connected) ...[
                          const SizedBox(width: 16),
                          Text(
                            _callDuration,
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 16),
                    // 用户信息
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (widget.remoteUserAvatar != null)
                          CircleAvatar(
                            radius: 20,
                            backgroundImage: NetworkImage(widget.remoteUserAvatar!),
                          )
                        else
                          CircleAvatar(
                            radius: 20,
                            backgroundColor: theme.primaryColor,
                            child: Text(
                              widget.remoteUserName.isNotEmpty 
                                  ? widget.remoteUserName[0].toUpperCase()
                                  : '?',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        const SizedBox(width: 12),
                        Text(
                          widget.remoteUserName,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            // 底部控制栏
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: const EdgeInsets.all(30),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      Colors.black.withOpacity(0.8),
                    ],
                  ),
                ),
                child: Column(
                  children: [
                    // 通话控制按钮
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        // 静音按钮
                        _buildControlButton(
                          icon: _isMuted ? Icons.mic_off : Icons.mic,
                          onPressed: _toggleMute,
                          isActive: _isMuted,
                        ),
                        
                        // 摄像头按钮（仅视频通话）
                        if (isVideo)
                          _buildControlButton(
                            icon: _isCameraOff ? Icons.videocam_off : Icons.videocam,
                            onPressed: _toggleCamera,
                            isActive: _isCameraOff,
                          ),
                        
                        // 扬声器按钮
                        _buildControlButton(
                          icon: _isSpeakerOn ? Icons.volume_up : Icons.volume_off,
                          onPressed: _toggleSpeaker,
                          isActive: !_isSpeakerOn,
                        ),
                        
                        // 切换摄像头按钮（仅视频通话）
                        if (isVideo)
                          _buildControlButton(
                            icon: Icons.flip_camera_ios,
                            onPressed: _switchCamera,
                          ),
                      ],
                    ),
                    
                    const SizedBox(height: 40),
                    
                    // 挂断按钮
                    GestureDetector(
                      onTap: _endCall,
                      child: Container(
                        width: 70,
                        height: 70,
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.call_end,
                          color: Colors.white,
                          size: 35,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            // 加载状态
            if (_callState == CallState.calling || _callState == CallState.ringing)
              Container(
                color: Colors.black.withOpacity(0.8),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const CircularProgressIndicator(
                        color: Colors.white,
                      ),
                      const SizedBox(height: 20),
                      Text(
                        _callState == CallState.calling ? '正在呼叫...' : '来电中...',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  /// 构建控制按钮
  Widget _buildControlButton({
    required IconData icon,
    required VoidCallback onPressed,
    bool isActive = false,
  }) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: 50,
        height: 50,
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.white.withOpacity(0.2),
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          color: isActive ? Colors.black : Colors.white,
          size: 24,
        ),
      ),
    );
  }
  
  /// 获取通话状态图标
  IconData _getCallStateIcon() {
    switch (_callState) {
      case CallState.calling:
        return Icons.call;
      case CallState.ringing:
        return Icons.ring_volume;
      case CallState.connected:
        return Icons.call_merge;
      case CallState.ended:
        return Icons.call_end;
      case CallState.error:
        return Icons.error;
      default:
        return Icons.call;
    }
  }
  
  /// 获取通话状态文本
  String _getCallStateText() {
    switch (_callState) {
      case CallState.calling:
        return '正在呼叫';
      case CallState.ringing:
        return '来电中';
      case CallState.connected:
        return '通话中';
      case CallState.ended:
        return '通话结束';
      case CallState.error:
        return '通话错误';
      default:
        return '准备中';
    }
  }
} 