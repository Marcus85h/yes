import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class OnboardingPage extends StatelessWidget {
  const OnboardingPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.rocket_launch, color: AppColors.primary, size: 72),
              const SizedBox(height: 32),
              const Text('欢迎来到视频社交App', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              const Text('发现有趣的人，畅聊、互动、视频通话。', textAlign: TextAlign.center, style: TextStyle(fontSize: 16)),
              const SizedBox(height: 40),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: () {},
                child: const Text('立即体验'),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 