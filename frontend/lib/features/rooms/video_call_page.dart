import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class VideoCallPage extends StatelessWidget {
  const VideoCallPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          Center(
            child: Container(
              width: 240,
              height: 320,
              color: Colors.grey[900],
              child: const Center(
                child: Icon(Icons.videocam, color: Colors.white, size: 64),
              ),
            ),
          ),
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  icon: const Icon(Icons.mic_off, color: Colors.white, size: 32),
                  onPressed: () {},
                ),
                const SizedBox(width: 32),
                FloatingActionButton(
                  backgroundColor: AppColors.primary,
                  onPressed: () {},
                  child: const Icon(Icons.call_end, color: Colors.white),
                ),
                const SizedBox(width: 32),
                IconButton(
                  icon: const Icon(Icons.cameraswitch, color: Colors.white, size: 32),
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 