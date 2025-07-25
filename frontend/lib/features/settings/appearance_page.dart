import 'package:flutter/material.dart';
import '../../core/theme/dark_theme_switch.dart';

class AppearancePage extends StatefulWidget {
  const AppearancePage({Key? key}) : super(key: key);

  @override
  State<AppearancePage> createState() => _AppearancePageState();
}

class _AppearancePageState extends State<AppearancePage> {
  bool isDark = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('外观设置')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('暗黑模式', style: TextStyle(fontSize: 18)),
            DarkThemeSwitch(isDark: isDark, onChanged: (v) => setState(() => isDark = v)),
          ],
        ),
      ),
    );
  }
} 