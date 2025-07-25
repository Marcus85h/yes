import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/primary_button.dart';

class VerifyCodePage extends StatelessWidget {
  const VerifyCodePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('验证码验证')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: '请输入验证码',
                prefixIcon: Icon(Icons.verified),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 32),
            PrimaryButton(text: '确认', onPressed: () {}),
          ],
        ),
      ),
    );
  }
} 