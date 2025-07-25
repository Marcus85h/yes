import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/dark_theme_switch.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool isDark = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Demo App',
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
      home: Scaffold(
        appBar: AppBar(
          title: const Text('主色/主题演示'),
          actions: [
            DarkThemeSwitch(isDark: isDark, onChanged: (v) => setState(() => isDark = v)),
          ],
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('主色按钮', style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 16),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                ),
                onPressed: () {},
                child: const Text('按钮'),
              ),
              const SizedBox(height: 32),
              Container(
                width: 200,
                height: 40,
                decoration: const BoxDecoration(
                  gradient: AppColors.giftGradient,
                  borderRadius: BorderRadius.all(Radius.circular(8)),
                ),
                alignment: Alignment.center,
                child: const Text('渐变辅助色', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 