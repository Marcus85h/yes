import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../../features/auth/pages/login_page.dart';
import '../../features/auth/pages/register_page.dart';
import '../../features/home/pages/home_page.dart';
import '../../features/chat/pages/chat_list_page.dart';
import '../../features/chat/pages/chat_detail_page.dart';
import '../../features/profile/pages/profile_page.dart';
import '../../features/profile/pages/edit_profile_page.dart';
import '../../features/calls/pages/call_page.dart';
import '../../features/rooms/pages/room_list_page.dart';
import '../../features/rooms/pages/room_detail_page.dart';
import '../../features/splash/pages/splash_page.dart';
import '../../features/security/pages/security_page.dart';

class AppRouter {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String home = '/home';
  static const String chatList = '/chat/list';
  static const String chatDetail = '/chat/detail';
  static const String profile = '/profile';
  static const String editProfile = '/edit-profile';
  static const String call = '/call';
  static const String roomList = '/room/list';
  static const String roomDetail = '/room/detail';
  static const String security = '/security';

  static String get initialRoute => splash;

  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return MaterialPageRoute(
          builder: (_) => const SplashPage(),
          settings: settings,
        );

      case login:
        return MaterialPageRoute(
          builder: (_) => const LoginPage(),
          settings: settings,
        );

      case register:
        return MaterialPageRoute(
          builder: (_) => const RegisterPage(),
          settings: settings,
        );

      case home:
        return MaterialPageRoute(
          builder: (_) => const HomePage(),
          settings: settings,
        );

      case chatList:
        return MaterialPageRoute(
          builder: (_) => const ChatListPage(),
          settings: settings,
        );

      case chatDetail:
        final args = settings.arguments as Map<String, dynamic>?;
        return MaterialPageRoute(
          builder: (_) => ChatDetailPage(
            chatId: args?['chatId'] ?? '',
            otherUser: args?['otherUser'],
          ),
          settings: settings,
        );

      case profile:
        return MaterialPageRoute(
          builder: (_) => const ProfilePage(),
          settings: settings,
        );

      case editProfile:
        return MaterialPageRoute(
          builder: (_) => const EditProfilePage(),
          settings: settings,
        );

      case call:
        final args = settings.arguments as Map<String, dynamic>?;
        return MaterialPageRoute(
          builder: (_) => CallPage(
            callId: args?['callId'] ?? '',
            callType: args?['callType'] ?? 'video',
            isIncoming: args?['isIncoming'] ?? false,
            otherUser: args?['otherUser'],
          ),
          settings: settings,
        );

      case roomList:
        return MaterialPageRoute(
          builder: (_) => const RoomListPage(),
          settings: settings,
        );

      case roomDetail:
        final args = settings.arguments as Map<String, dynamic>?;
        return MaterialPageRoute(
          builder: (_) => RoomDetailPage(
            roomId: args?['roomId'] ?? '',
            room: args?['room'],
          ),
          settings: settings,
        );

      case security:
        return MaterialPageRoute(
          builder: (_) => const SecurityPage(),
          settings: settings,
        );

      default:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('页面不存在'),
            ),
          ),
          settings: settings,
        );
    }
  }

  // 导航方法
  static Future<T?> pushNamed<T>(String routeName, {Object? arguments}) {
    return navigatorKey.currentState!.pushNamed<T>(routeName, arguments: arguments);
  }

  static Future<T?> pushReplacementNamed<T>(String routeName, {Object? arguments}) {
    return navigatorKey.currentState!.pushReplacementNamed<T>(routeName, arguments: arguments);
  }

  static Future<T?> pushNamedAndRemoveUntil<T>(String routeName, {Object? arguments}) {
    return navigatorKey.currentState!.pushNamedAndRemoveUntil<T>(
      routeName,
      (route) => false,
      arguments: arguments,
    );
  }

  static void pop<T>([T? result]) {
    navigatorKey.currentState!.pop<T>(result);
  }

  static bool canPop() {
    return navigatorKey.currentState!.canPop();
  }

  // 认证相关导航
  static void navigateToAuth() {
    pushNamedAndRemoveUntil(login);
  }

  static void navigateToHome() {
    pushNamedAndRemoveUntil(home);
  }

  // 聊天相关导航
  static void navigateToChatDetail(String chatId, {Map<String, dynamic>? otherUser}) {
    pushNamed(chatDetail, arguments: {
      'chatId': chatId,
      'otherUser': otherUser,
    });
  }

  // 通话相关导航
  static void navigateToCall(String callId, String callType, {bool isIncoming = false, Map<String, dynamic>? otherUser}) {
    pushNamed(call, arguments: {
      'callId': callId,
      'callType': callType,
      'isIncoming': isIncoming,
      'otherUser': otherUser,
    });
  }

  // 房间相关导航
  static void navigateToRoomDetail(String roomId, {Map<String, dynamic>? room}) {
    pushNamed(roomDetail, arguments: {
      'roomId': roomId,
      'room': room,
    });
  }

  // 安全相关导航
  static void navigateToSecurity() {
    pushNamed(security);
  }
} 