import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/primary_button.dart';

class RegisterPage extends StatelessWidget {
  const RegisterPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('注册')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: '手机号',
                prefixIcon: Icon(Icons.phone),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            TextField(
              decoration: const InputDecoration(
                labelText: '验证码',
                prefixIcon: Icon(Icons.verified),
                suffixIcon: Icon(Icons.send),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              decoration: const InputDecoration(
                labelText: '密码',
                prefixIcon: Icon(Icons.lock),
              ),
              obscureText: true,
            ),
            const SizedBox(height: 32),
            PrimaryButton(text: '注册', onPressed: () {}),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {},
              child: const Text('已有账号？登录'),
            ),
          ],
        ),
      ),
    );
  }
} 