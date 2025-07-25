import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class SplashPage extends StatelessWidget {
  const SplashPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.favorite, color: Colors.white, size: 64),
            SizedBox(height: 24),
            CircularProgressIndicator(color: Colors.white),
            SizedBox(height: 16),
            Text('加载中...', style: TextStyle(color: Colors.white, fontSize: 18)),
          ],
        ),
      ),
    );
  }
} 