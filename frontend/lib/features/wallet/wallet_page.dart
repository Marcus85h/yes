import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/primary_button.dart';

class WalletPage extends StatelessWidget {
  const WalletPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('钱包')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('当前余额', style: TextStyle(fontSize: 18)),
            const SizedBox(height: 12),
            const Text('¥ 100.00', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.primary)),
            const SizedBox(height: 24),
            PrimaryButton(text: '充值', onPressed: () {}),
          ],
        ),
      ),
    );
  }
} 