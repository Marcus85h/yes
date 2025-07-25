import 'package:flutter/material.dart';

class LanguagePage extends StatelessWidget {
  const LanguagePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('语言设置')),
      body: ListView(
        children: const [
          ListTile(title: Text('简体中文'), trailing: Icon(Icons.check)),
          ListTile(title: Text('繁體中文')),
          ListTile(title: Text('English')),
          ListTile(title: Text('日本語')),
          ListTile(title: Text('한국어')),
          ListTile(title: Text('Tiếng Việt')),
          ListTile(title: Text('ภาษาไทย')),
        ],
      ),
    );
  }
} 