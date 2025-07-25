import 'package:flutter/material.dart';

class MessegePage extends StatelessWidget {
  const MessegePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('消息')),
      body: ListView.separated(
        itemCount: 10,
        separatorBuilder: (_, __) => const Divider(),
        itemBuilder: (context, i) => ListTile(
          leading: const CircleAvatar(child: Icon(Icons.person)),
          title: Text('用户 $i'),
          subtitle: const Text('这是一条消息内容...'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {},
        ),
      ),
    );
  }
} 