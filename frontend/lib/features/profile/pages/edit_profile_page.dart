import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/services/file_service.dart';
import '../../../core/theme/app_theme.dart';

class EditProfilePage extends StatefulWidget {
  const EditProfilePage({super.key});

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _nicknameController = TextEditingController();
  final _bioController = TextEditingController();
  final _locationController = TextEditingController();
  
  String? _selectedGender;
  DateTime? _selectedBirthDate;
  File? _selectedAvatar;
  bool _isLoading = false;
  bool _isUploading = false;
  
  final List<String> _genderOptions = ['男', '女', '其他'];
  
  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }
  
  @override
  void dispose() {
    _nicknameController.dispose();
    _bioController.dispose();
    _locationController.dispose();
    super.dispose();
  }
  
  void _loadUserProfile() {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final user = authProvider.user;
    
    if (user != null) {
      _nicknameController.text = user['nickname'] ?? '';
      _bioController.text = user['bio'] ?? '';
      _locationController.text = user['location'] ?? '';
      _selectedGender = user['gender'];
      
      if (user['birth_date'] != null) {
        try {
          _selectedBirthDate = DateTime.parse(user['birth_date']);
        } catch (e) {
          print('解析生日失败: $e');
        }
      }
    }
  }
  
  Future<void> _pickAvatar() async {
    try {
      setState(() => _isUploading = true);
      
      final file = await FileService.instance.pickImage(
        maxWidth: 512,
        maxHeight: 512,
        imageQuality: 80,
      );
      
      if (file != null) {
        setState(() {
          _selectedAvatar = file;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择头像失败: $e')),
      );
    } finally {
      setState(() => _isUploading = false);
    }
  }
  
  Future<void> _takePhoto() async {
    try {
      setState(() => _isUploading = true);
      
      final file = await FileService.instance.takePhoto(
        maxWidth: 512,
        maxHeight: 512,
        imageQuality: 80,
      );
      
      if (file != null) {
        setState(() {
          _selectedAvatar = file;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('拍摄头像失败: $e')),
      );
    } finally {
      setState(() => _isUploading = false);
    }
  }
  
  void _showAvatarOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('从相册选择'),
                onTap: () {
                  Navigator.pop(context);
                  _pickAvatar();
                },
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('拍摄照片'),
                onTap: () {
                  Navigator.pop(context);
                  _takePhoto();
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }
  
  void _showDatePicker() {
    showDatePicker(
      context: context,
      initialDate: _selectedBirthDate ?? DateTime.now().subtract(const Duration(days: 6570)), // 18岁
      firstDate: DateTime.now().subtract(const Duration(days: 36500)), // 100岁
      lastDate: DateTime.now().subtract(const Duration(days: 6570)), // 18岁
    ).then((date) {
      if (date != null) {
        setState(() {
          _selectedBirthDate = date;
        });
      }
    });
  }
  
  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      
      // 准备更新数据
      final updateData = {
        'nickname': _nicknameController.text.trim(),
        'bio': _bioController.text.trim(),
        'location': _locationController.text.trim(),
        'gender': _selectedGender,
        'birth_date': _selectedBirthDate?.toIso8601String(),
      };
      
      // 如果有新头像，先上传
      if (_selectedAvatar != null) {
        final avatarUrl = await FileService.instance.uploadImage(_selectedAvatar!);
        if (avatarUrl != null) {
          updateData['avatar'] = avatarUrl;
        }
      }
      
      // 更新用户资料
      final success = await authProvider.updateProfile(updateData);
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('资料更新成功')),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(authProvider.error ?? '更新失败')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('更新失败: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.user;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('编辑资料'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProfile,
            child: _isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('保存'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 头像选择
              Center(
                child: Column(
                  children: [
                    GestureDetector(
                      onTap: _showAvatarOptions,
                      child: Stack(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundImage: _selectedAvatar != null
                                ? FileImage(_selectedAvatar!)
                                : (user?['avatar'] != null
                                    ? NetworkImage(user!['avatar'])
                                    : null) as ImageProvider?,
                            child: _selectedAvatar == null && user?['avatar'] == null
                                ? Text(
                                    user?['nickname']?[0] ?? '?',
                                    style: const TextStyle(fontSize: 32),
                                  )
                                : null,
                          ),
                          if (_isUploading)
                            Positioned.fill(
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.black54,
                                  borderRadius: BorderRadius.circular(50),
                                ),
                                child: const Center(
                                  child: CircularProgressIndicator(
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                ),
                              ),
                            ),
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: BoxDecoration(
                                color: AppTheme.primaryColor,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(
                                Icons.camera_alt,
                                color: Colors.white,
                                size: 16,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: _showAvatarOptions,
                      child: const Text('更换头像'),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // 昵称
              TextFormField(
                controller: _nicknameController,
                decoration: const InputDecoration(
                  labelText: '昵称',
                  hintText: '请输入昵称',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return '请输入昵称';
                  }
                  if (value.trim().length > 20) {
                    return '昵称不能超过20个字符';
                  }
                  return null;
                },
              ),
              
              const SizedBox(height: 16),
              
              // 性别
              DropdownButtonFormField<String>(
                value: _selectedGender,
                decoration: const InputDecoration(
                  labelText: '性别',
                  border: OutlineInputBorder(),
                ),
                items: _genderOptions.map((gender) {
                  return DropdownMenuItem(
                    value: gender,
                    child: Text(gender),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedGender = value;
                  });
                },
              ),
              
              const SizedBox(height: 16),
              
              // 生日
              InkWell(
                onTap: _showDatePicker,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: '生日',
                    border: OutlineInputBorder(),
                  ),
                  child: Text(
                    _selectedBirthDate != null
                        ? '${_selectedBirthDate!.year}-${_selectedBirthDate!.month.toString().padLeft(2, '0')}-${_selectedBirthDate!.day.toString().padLeft(2, '0')}'
                        : '请选择生日',
                    style: TextStyle(
                      color: _selectedBirthDate != null
                          ? Theme.of(context).textTheme.bodyLarge?.color
                          : Colors.grey,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 位置
              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(
                  labelText: '位置',
                  hintText: '请输入位置',
                  border: OutlineInputBorder(),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 个人简介
              TextFormField(
                controller: _bioController,
                decoration: const InputDecoration(
                  labelText: '个人简介',
                  hintText: '介绍一下自己吧',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                maxLength: 200,
              ),
            ],
          ),
        ),
      ),
    );
  }
} 