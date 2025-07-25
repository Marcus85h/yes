import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/services/localization_service.dart';
import '../../../core/theme/app_theme.dart';

class LanguageSettingsPage extends StatefulWidget {
  const LanguageSettingsPage({super.key});

  @override
  State<LanguageSettingsPage> createState() => _LanguageSettingsPageState();
}

class _LanguageSettingsPageState extends State<LanguageSettingsPage> {
  late SupportedLanguage _selectedLanguage;

  @override
  void initState() {
    super.initState();
    _selectedLanguage = LocalizationService.instance.currentLanguage;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('语言设置'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: LocalizationService.instance.supportedLanguages.length,
        itemBuilder: (context, index) {
          final language = LocalizationService.instance.supportedLanguages[index];
          final isSelected = language == _selectedLanguage;
          
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: Text(
                language.flag,
                style: const TextStyle(fontSize: 24),
              ),
              title: Text(
                language.name,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  color: isSelected ? AppTheme.primaryColor : null,
                ),
              ),
              subtitle: Text('${language.code}'),
              trailing: isSelected
                  ? Icon(
                      Icons.check_circle,
                      color: AppTheme.primaryColor,
                    )
                  : null,
              onTap: () => _changeLanguage(language),
            ),
          );
        },
      ),
    );
  }

  Future<void> _changeLanguage(SupportedLanguage language) async {
    if (language == _selectedLanguage) return;

    setState(() {
      _selectedLanguage = language;
    });

    try {
      await LocalizationService.instance.changeLanguage(language);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('语言已切换为 ${language.name}'),
            backgroundColor: AppTheme.successColor,
          ),
        );
        
        // 延迟返回，让用户看到成功提示
        Future.delayed(const Duration(seconds: 1), () {
          if (mounted) {
            Navigator.pop(context);
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('切换语言失败: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }
  }
} 