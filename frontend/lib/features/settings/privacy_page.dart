import 'package:flutter/material.dart';

class PrivacyPage extends StatelessWidget {
  const PrivacyPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('隐私设置')),
      body: ListView(
        children: const [
          SwitchListTile(
            value: true,
            onChanged: null,
            title: Text('允许被搜索'),
          ),
          SwitchListTile(
            value: false,
            onChanged: null,
            title: Text('显示在线状态'),
          ),
          ListTile(
            title: Text('拉黑列表'),
            trailing: Icon(Icons.chevron_right),
          ),
        ],
      ),
    );
  }
} 