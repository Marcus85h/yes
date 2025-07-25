import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class EndCallSummaryPage extends StatelessWidget {
  const EndCallSummaryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('通话总结')),
      body: Center(
        child: Card(
          margin: const EdgeInsets.all(32),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.check_circle, color: AppColors.primary, size: 48),
                const SizedBox(height: 16),
                const Text('通话已结束', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                const Text('通话时长：05:23'),
                const SizedBox(height: 8),
                const Text('花费：¥ 10.00'),
                const SizedBox(height: 8),
                const Text('送出礼物：玫瑰*3'),
                const SizedBox(height: 24),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () => Navigator.pop(context),
                  child: const Text('返回'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
} 