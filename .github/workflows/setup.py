#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化设置脚本
用于配置API密钥和基本设置
"""

import os
import sys
import json
import getpass
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from chatgpt_client import ChatGPTClient


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("微信自动聊天机器人 - 初始化设置")
    print("=" * 60)
    print()


def get_openai_api_key() -> str:
    """获取OpenAI API密钥"""
    print("步骤 1: 配置OpenAI API密钥")
    print("-" * 40)
    
    while True:
        api_key = getpass.getpass("请输入您的OpenAI API密钥 (输入时不会显示): ").strip()
        
        if not api_key:
            print("❌ API密钥不能为空，请重新输入")
            continue
            
        if not api_key.startswith('sk-'):
            print("❌ API密钥格式不正确，应以'sk-'开头")
            continue
            
        # 测试API密钥
        print("正在测试API密钥...")
        try:
            client = ChatGPTClient(api_key=api_key)
            if client.test_connection():
                print("✅ API密钥验证成功")
                return api_key
            else:
                print("❌ API密钥验证失败，请检查密钥是否正确")
        except Exception as e:
            print(f"❌ API密钥测试出错: {e}")
            
        retry = input("是否重新输入API密钥? (y/n): ").strip().lower()
        if retry != 'y':
            break
            
    return ""


def configure_wechat_settings() -> Dict[str, Any]:
    """配置微信设置"""
    print("\n步骤 2: 配置微信设置")
    print("-" * 40)
    
    settings = {}
    
    # 自动回复开关
    while True:
        auto_reply = input("是否启用自动回复? (y/n, 默认y): ").strip().lower()
        if auto_reply in ['', 'y', 'yes']:
            settings['enable_auto_reply'] = True
            break
        elif auto_reply in ['n', 'no']:
            settings['enable_auto_reply'] = False
            break
        else:
            print("请输入 y 或 n")
            
    # 回复延迟
    while True:
        try:
            delay = input("回复延迟时间(秒, 默认1.0): ").strip()
            if not delay:
                settings['reply_delay'] = 1.0
                break
            delay = float(delay)
            if delay < 0:
                print("延迟时间不能为负数")
                continue
            settings['reply_delay'] = delay
            break
        except ValueError:
            print("请输入有效的数字")
            
    # 白名单设置
    while True:
        whitelist_enabled = input("是否启用白名单? (y/n, 默认y): ").strip().lower()
        if whitelist_enabled in ['', 'y', 'yes']:
            settings['whitelist_enabled'] = True
            break
        elif whitelist_enabled in ['n', 'no']:
            settings['whitelist_enabled'] = False
            break
        else:
            print("请输入 y 或 n")
            
    return settings


def configure_security_settings() -> Dict[str, Any]:
    """配置安全设置"""
    print("\n步骤 3: 配置安全设置")
    print("-" * 40)
    
    settings = {}
    
    # 白名单好友
    if input("是否现在添加白名单好友? (y/n): ").strip().lower() == 'y':
        whitelist = []
        print("请输入好友名称 (输入空行结束):")
        while True:
            friend = input("好友名称: ").strip()
            if not friend:
                break
            whitelist.append(friend)
        settings['whitelist'] = whitelist
        
    return settings


def configure_persona_settings() -> Dict[str, Any]:
    """配置人设设置"""
    print("\n步骤 4: 配置人设设置")
    print("-" * 40)
    
    settings = {}
    
    # 默认人设
    personas = ['default', 'friendly', 'professional', 'cute']
    print("可选的人设:")
    for i, persona in enumerate(personas, 1):
        print(f"  {i}. {persona}")
        
    while True:
        try:
            choice = input(f"选择默认人设 (1-{len(personas)}, 默认1): ").strip()
            if not choice:
                settings['current'] = 'default'
                break
            choice = int(choice)
            if 1 <= choice <= len(personas):
                settings['current'] = personas[choice - 1]
                break
            else:
                print(f"请输入 1-{len(personas)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")
            
    return settings


def save_configuration(api_key: str, wechat_settings: Dict, security_settings: Dict, persona_settings: Dict):
    """保存配置"""
    print("\n步骤 5: 保存配置")
    print("-" * 40)
    
    try:
        # 创建配置对象
        config = Config()
        
        # 设置API密钥
        config.openai_api_key = api_key
        
        # 更新微信设置
        for key, value in wechat_settings.items():
            if 'wechat' not in config.config:
                config.config['wechat'] = {}
            config.config['wechat'][key] = value
            
        # 更新安全设置
        for key, value in security_settings.items():
            if 'security' not in config.config:
                config.config['security'] = {}
            config.config['security'][key] = value
            
        # 更新人设设置
        for key, value in persona_settings.items():
            if 'persona' not in config.config:
                config.config['persona'] = {}
            config.config['persona'][key] = value
            
        # 保存配置
        config.save()
        
        print("✅ 配置保存成功")
        return True
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False


def show_final_instructions():
    """显示最终使用说明"""
    print("\n" + "=" * 60)
    print("🎉 初始化设置完成!")
    print("=" * 60)
    print()
    print("使用说明:")
    print("1. 运行 'python main.py' 启动机器人")
    print("2. 扫描二维码登录微信")
    print("3. 机器人将自动回复好友消息")
    print()
    print("配置文件位置:")
    print("- config.json: 主配置文件")
    print("- persona.json: 人设配置文件")
    print()
    print("注意事项:")
    print("- 请确保您的OpenAI API密钥有足够的余额")
    print("- 建议先在小范围测试后再广泛使用")
    print("- 定期检查日志文件了解运行状态")
    print()
    print("如需修改配置，请编辑 config.json 文件")
    print("=" * 60)


def main():
    """主函数"""
    print_banner()
    
    # 检查是否已存在配置文件
    if os.path.exists('config.json'):
        overwrite = input("检测到已存在配置文件，是否重新配置? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("取消配置，退出程序")
            return
            
    # 获取OpenAI API密钥
    api_key = get_openai_api_key()
    if not api_key:
        print("❌ 未提供有效的API密钥，退出程序")
        return
        
    # 配置微信设置
    wechat_settings = configure_wechat_settings()
    
    # 配置安全设置
    security_settings = configure_security_settings()
    
    # 配置人设设置
    persona_settings = configure_persona_settings()
    
    # 保存配置
    if save_configuration(api_key, wechat_settings, security_settings, persona_settings):
        show_final_instructions()
    else:
        print("❌ 配置保存失败，请检查文件权限")


if __name__ == "__main__":
    main() 