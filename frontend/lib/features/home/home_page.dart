import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/primary_button.dart';

class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('首页')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('欢迎来到首页', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            PrimaryButton(text: '开始探索', onPressed: () {}),
          ],
        ),
      ),
    );
  }
} 