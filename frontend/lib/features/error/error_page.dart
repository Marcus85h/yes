import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class ErrorPage extends StatelessWidget {
  final String? message;
  const ErrorPage({Key? key, this.message}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, color: AppColors.primary, size: 64),
            const SizedBox(height: 24),
            Text(message ?? '发生未知错误', style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 32),
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
    );
  }
} 