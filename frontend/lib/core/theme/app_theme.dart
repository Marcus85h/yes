import 'package:flutter/material.dart';

class AppColors {
  static const Color primary = Color(0xFFFF3D3D); // 主色
  static const Color background = Color(0xFFFFFFFF); // 明亮背景
  static const Color textPrimary = Color(0xFF212121); // 主文字色
  static const Color divider = Color(0xFF9E9E9E); // 辅助色
  static const Color darkBackground = Color(0xFF121212); // 暗黑模式背景

  static const LinearGradient giftGradient = LinearGradient(
    colors: [Color(0xFFFF6E6E), Color(0xFFFF3D3D)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

final ThemeData lightTheme = ThemeData(
  primaryColor: AppColors.primary,
  scaffoldBackgroundColor: AppColors.background,
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: AppColors.textPrimary),
    bodyMedium: TextStyle(color: AppColors.textPrimary),
  ),
  dividerColor: AppColors.divider,
  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.background,
    foregroundColor: AppColors.textPrimary,
    elevation: 0,
  ),
  colorScheme: ColorScheme.light(
    primary: AppColors.primary,
    background: AppColors.background,
    onPrimary: Colors.white,
    onBackground: AppColors.textPrimary,
    secondary: AppColors.divider,
  ),
);

final ThemeData darkTheme = ThemeData(
  primaryColor: AppColors.primary,
  scaffoldBackgroundColor: AppColors.darkBackground,
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white),
    bodyMedium: TextStyle(color: Colors.white),
  ),
  dividerColor: AppColors.divider,
  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.darkBackground,
    foregroundColor: Colors.white,
    elevation: 0,
  ),
  colorScheme: ColorScheme.dark(
    primary: AppColors.primary,
    background: AppColors.darkBackground,
    onPrimary: Colors.white,
    onBackground: Colors.white,
    secondary: AppColors.divider,
  ),
); 