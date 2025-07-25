import 'package:flutter/material.dart';

class DarkThemeSwitch extends StatelessWidget {
  final bool isDark;
  final ValueChanged<bool> onChanged;
  const DarkThemeSwitch({Key? key, required this.isDark, required this.onChanged}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        const Icon(Icons.light_mode),
        Switch(
          value: isDark,
          onChanged: onChanged,
        ),
        const Icon(Icons.dark_mode),
      ],
    );
  }
} 