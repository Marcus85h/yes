import 'package:flutter/material.dart';
import '../home/home_page.dart';
import '../chat/messege_page.dart';
import '../wallet/wallet_page.dart';
import '../profile/profile_page.dart';

class MainScaffold extends StatefulWidget {
  const MainScaffold({Key? key}) : super(key: key);

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _index = 0;
  final _pages = const [
    HomePage(),
    MessegePage(),
    WalletPage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: '首页'),
          BottomNavigationBarItem(icon: Icon(Icons.message), label: '消息'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: '钱包'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: '我的'),
        ],
        type: BottomNavigationBarType.fixed,
      ),
    );
  }
} 