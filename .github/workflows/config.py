#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
处理项目配置、API密钥和白名单管理
"""

import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = 'config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "openai": {
                "api_key": "",
                "model": "gpt-3.5-turbo",
                "max_tokens": 500,
                "temperature": 0.7
            },
            "wechat": {
                "enable_auto_reply": True,
                "reply_delay": 1.0,
                "max_reply_length": 200
            },
            "security": {
                "whitelist_enabled": True,
                "whitelist": [],
                "blacklist": []
            },
            "persona": {
                "current": "default",
                "auto_switch": False
            },
            "logging": {
                "level": "INFO",
                "file": "wechat_bot.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置和加载的配置
                    self._merge_config(default_config, loaded_config)
                    logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                logger.warning(f"配置文件不存在，使用默认配置: {self.config_file}")
                self._save_config(default_config)
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            
        return default_config
        
    def _merge_config(self, default: Dict, loaded: Dict):
        """合并配置"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
                
    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置文件保存成功: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            
    def save(self):
        """保存当前配置"""
        self._save_config(self.config)
        
    @property
    def openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return self.config.get('openai', {}).get('api_key', '')
        
    @openai_api_key.setter
    def openai_api_key(self, value: str):
        """设置OpenAI API密钥"""
        if 'openai' not in self.config:
            self.config['openai'] = {}
        self.config['openai']['api_key'] = value
        
    @property
    def openai_model(self) -> str:
        """获取OpenAI模型名称"""
        return self.config.get('openai', {}).get('model', 'gpt-3.5-turbo')
        
    @property
    def openai_max_tokens(self) -> int:
        """获取最大token数"""
        return self.config.get('openai', {}).get('max_tokens', 500)
        
    @property
    def openai_temperature(self) -> float:
        """获取温度参数"""
        return self.config.get('openai', {}).get('temperature', 0.7)
        
    @property
    def enable_auto_reply(self) -> bool:
        """是否启用自动回复"""
        return self.config.get('wechat', {}).get('enable_auto_reply', True)
        
    @property
    def reply_delay(self) -> float:
        """回复延迟时间"""
        return self.config.get('wechat', {}).get('reply_delay', 1.0)
        
    @property
    def max_reply_length(self) -> int:
        """最大回复长度"""
        return self.config.get('wechat', {}).get('max_reply_length', 200)
        
    @property
    def whitelist_enabled(self) -> bool:
        """是否启用白名单"""
        return self.config.get('security', {}).get('whitelist_enabled', True)
        
    @property
    def whitelist(self) -> List[str]:
        """获取白名单"""
        return self.config.get('security', {}).get('whitelist', [])
        
    @property
    def blacklist(self) -> List[str]:
        """获取黑名单"""
        return self.config.get('security', {}).get('blacklist', [])
        
    @property
    def current_persona(self) -> str:
        """获取当前人设"""
        return self.config.get('persona', {}).get('current', 'default')
        
    @current_persona.setter
    def current_persona(self, value: str):
        """设置当前人设"""
        if 'persona' not in self.config:
            self.config['persona'] = {}
        self.config['persona']['current'] = value
        
    def is_friend_allowed(self, friend_name: str) -> bool:
        """
        检查好友是否被允许
        
        Args:
            friend_name: 好友名称
            
        Returns:
            是否允许
        """
        # 如果未启用白名单，则允许所有好友
        if not self.whitelist_enabled:
            return True
            
        # 检查黑名单
        if friend_name in self.blacklist:
            return False
            
        # 检查白名单
        if not self.whitelist:  # 白名单为空，允许所有好友
            return True
            
        return friend_name in self.whitelist
        
    def add_to_whitelist(self, friend_name: str):
        """添加到白名单"""
        if 'security' not in self.config:
            self.config['security'] = {}
        if 'whitelist' not in self.config['security']:
            self.config['security']['whitelist'] = []
            
        if friend_name not in self.config['security']['whitelist']:
            self.config['security']['whitelist'].append(friend_name)
            logger.info(f"已添加 {friend_name} 到白名单")
            
    def remove_from_whitelist(self, friend_name: str):
        """从白名单移除"""
        if 'security' in self.config and 'whitelist' in self.config['security']:
            if friend_name in self.config['security']['whitelist']:
                self.config['security']['whitelist'].remove(friend_name)
                logger.info(f"已从白名单移除 {friend_name}")
                
    def add_to_blacklist(self, friend_name: str):
        """添加到黑名单"""
        if 'security' not in self.config:
            self.config['security'] = {}
        if 'blacklist' not in self.config['security']:
            self.config['security']['blacklist'] = []
            
        if friend_name not in self.config['security']['blacklist']:
            self.config['security']['blacklist'].append(friend_name)
            logger.info(f"已添加 {friend_name} 到黑名单")
            
    def remove_from_blacklist(self, friend_name: str):
        """从黑名单移除"""
        if 'security' in self.config and 'blacklist' in self.config['security']:
            if friend_name in self.config['security']['blacklist']:
                self.config['security']['blacklist'].remove(friend_name)
                logger.info(f"已从黑名单移除 {friend_name}")
                
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})
        
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        errors = []
        
        # 检查OpenAI API密钥
        if not self.openai_api_key:
            errors.append("OpenAI API密钥未设置")
            
        # 检查模型名称
        valid_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
        if self.openai_model not in valid_models:
            errors.append(f"不支持的模型: {self.openai_model}")
            
        # 检查数值范围
        if not (0 <= self.openai_temperature <= 2):
            errors.append("温度参数应在0-2之间")
            
        if self.openai_max_tokens <= 0:
            errors.append("最大token数应大于0")
            
        if self.reply_delay < 0:
            errors.append("回复延迟不能为负数")
            
        if errors:
            for error in errors:
                logger.error(f"配置错误: {error}")
            return False
            
        return True 