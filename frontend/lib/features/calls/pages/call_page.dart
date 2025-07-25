import 'package:flutter/material.dart';
import '../../../core/routes/app_router.dart';
import '../../../core/theme/app_theme.dart';

class CallPage extends StatefulWidget {
  final String callId;
  final String callType;
  final bool isIncoming;
  final Map<String, dynamic>? otherUser;

  const CallPage({
    super.key,
    required this.callId,
    required this.callType,
    required this.isIncoming,
    this.otherUser,
  });

  @override
  State<CallPage> createState() => _CallPageState();
}

class _CallPageState extends State<CallPage> {
  bool _isMuted = false;
  bool _isSpeakerOn = false;
  bool _isVideoEnabled = true;
  Duration _callDuration = Duration.zero;
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _callDuration += const Duration(seconds: 1);
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    String hours = twoDigits(duration.inHours);
    String minutes = twoDigits(duration.inMinutes.remainder(60));
    String seconds = twoDigits(duration.inSeconds.remainder(60));
    return "$hours:$minutes:$seconds";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          children: [
            // 状态栏
            Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _formatDuration(_callDuration),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Icon(
                    widget.callType == 'video' ? Icons.videocam : Icons.call,
                    color: Colors.white,
                    size: 20,
                  ),
                ],
              ),
            ),
            
            const Spacer(),
            
            // 用户信息
            Column(
              children: [
                CircleAvatar(
                  radius: 60,
                  backgroundImage: widget.otherUser?['avatar'] != null
                      ? NetworkImage(widget.otherUser!['avatar'])
                      : null,
                  child: widget.otherUser?['avatar'] == null
                      ? Text(
                          widget.otherUser?['name']?[0] ?? '?',
                          style: const TextStyle(
                            fontSize: 48,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        )
                      : null,
                ),
                const SizedBox(height: 16),
                Text(
                  widget.otherUser?['name'] ?? '未知用户',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  widget.isIncoming ? '来电' : '通话中',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
            
            const Spacer(),
            
            // 控制按钮
            Container(
              padding: const EdgeInsets.all(32),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // 静音按钮
                  _buildControlButton(
                    icon: _isMuted ? Icons.mic_off : Icons.mic,
                    color: _isMuted ? AppTheme.errorColor : Colors.white,
                    onPressed: () {
                      setState(() {
                        _isMuted = !_isMuted;
                      });
                      // TODO: 实现静音功能
                    },
                  ),
                  
                  // 挂断按钮
                  _buildControlButton(
                    icon: Icons.call_end,
                    color: AppTheme.errorColor,
                    size: 64,
                    onPressed: () {
                      // TODO: 实现挂断功能
                      AppRouter.pop();
                    },
                  ),
                  
                  // 扬声器按钮
                  _buildControlButton(
                    icon: _isSpeakerOn ? Icons.volume_up : Icons.volume_down,
                    color: _isSpeakerOn ? AppTheme.primaryColor : Colors.white,
                    onPressed: () {
                      setState(() {
                        _isSpeakerOn = !_isSpeakerOn;
                      });
                      // TODO: 实现扬声器功能
                    },
                  ),
                ],
              ),
            ),
            
            // 视频通话额外控制
            if (widget.callType == 'video') ...[
              Container(
                padding: const EdgeInsets.only(bottom: 32),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // 切换摄像头
                    _buildControlButton(
                      icon: Icons.flip_camera_ios,
                      color: Colors.white,
                      onPressed: () {
                        // TODO: 实现切换摄像头功能
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('切换摄像头功能开发中')),
                        );
                      },
                    ),
                    
                    // 开启/关闭视频
                    _buildControlButton(
                      icon: _isVideoEnabled ? Icons.videocam : Icons.videocam_off,
                      color: _isVideoEnabled ? Colors.white : AppTheme.errorColor,
                      onPressed: () {
                        setState(() {
                          _isVideoEnabled = !_isVideoEnabled;
                        });
                        // TODO: 实现视频开关功能
                      },
                    ),
                    
                    // 更多选项
                    _buildControlButton(
                      icon: Icons.more_vert,
                      color: Colors.white,
                      onPressed: () {
                        _showMoreOptions();
                      },
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required Color color,
    double size = 48,
    required VoidCallback onPressed,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        shape: BoxShape.circle,
        border: Border.all(color: color, width: 2),
      ),
      child: IconButton(
        icon: Icon(icon, color: color),
        onPressed: onPressed,
      ),
    );
  }

  void _showMoreOptions() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              ListTile(
                leading: const Icon(Icons.record_voice_over),
                title: const Text('录音'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现录音功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('录音功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.screen_share),
                title: const Text('屏幕共享'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现屏幕共享功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('屏幕共享功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.chat),
                title: const Text('发送消息'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现发送消息功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('发送消息功能开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.people),
                title: const Text('添加参与者'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 实现添加参与者功能
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('添加参与者功能开发中')),
                  );
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }
}

// 导入Timer
import 'dart:async'; 