#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人设管理模块
支持从persona.json文件加载和管理不同的人设配置
"""

import os
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PersonaManager:
    """人设管理类"""
    
    def __init__(self, persona_file: str = 'persona.json'):
        """
        初始化人设管理器
        
        Args:
            persona_file: 人设配置文件路径
        """
        self.persona_file = persona_file
        self.personas = {}
        self.current_persona = 'default'
        
    def load_persona(self):
        """加载人设配置"""
        try:
            if os.path.exists(self.persona_file):
                with open(self.persona_file, 'r', encoding='utf-8') as f:
                    self.personas = json.load(f)
                logger.info(f"人设配置加载成功: {self.persona_file}")
            else:
                logger.warning(f"人设配置文件不存在，创建默认配置: {self.persona_file}")
                self._create_default_personas()
                self.save_persona()
                
        except Exception as e:
            logger.error(f"加载人设配置失败: {e}")
            self._create_default_personas()
            
    def _create_default_personas(self):
        """创建默认人设配置"""
        self.personas = {
            "default": {
                "name": "默认助手",
                "description": "一个友好、专业的聊天助手",
                "personality": "温和、耐心、乐于助人",
                "language_style": "正式但友好",
                "emoji_usage": "适度",
                "response_length": "中等",
                "specialties": ["日常聊天", "问题解答", "情感支持"],
                "system_prompt": "你是一个友好、专业的聊天助手。请保持温和、耐心的态度，用正式但友好的语言回复用户。"
            },
            "friendly": {
                "name": "活泼好友",
                "description": "一个活泼开朗、充满活力的聊天伙伴",
                "personality": "开朗、幽默、充满活力",
                "language_style": "轻松、活泼",
                "emoji_usage": "频繁",
                "response_length": "简短",
                "specialties": ["娱乐聊天", "笑话分享", "心情调节"],
                "system_prompt": "你是一个活泼开朗的聊天伙伴。请用轻松、幽默的语气回复，经常使用表情符号，让对话充满活力。"
            },
            "professional": {
                "name": "专业顾问",
                "description": "一个专业、严谨的咨询顾问",
                "personality": "专业、严谨、理性",
                "language_style": "正式、专业",
                "emoji_usage": "很少",
                "response_length": "详细",
                "specialties": ["专业咨询", "问题分析", "建议提供"],
                "system_prompt": "你是一个专业的咨询顾问。请用专业、严谨的态度回复，提供有价值的建议和分析。"
            },
            "cute": {
                "name": "可爱萌妹",
                "description": "一个可爱、温柔的小姐姐",
                "personality": "可爱、温柔、体贴",
                "language_style": "可爱、温柔",
                "emoji_usage": "丰富",
                "response_length": "中等",
                "specialties": ["情感陪伴", "生活分享", "温柔安慰"],
                "system_prompt": "你是一个可爱、温柔的小姐姐。请用温柔、体贴的语气回复，经常使用可爱的表情符号，给用户温暖的感觉。"
            }
        }
        
    def save_persona(self):
        """保存人设配置"""
        try:
            with open(self.persona_file, 'w', encoding='utf-8') as f:
                json.dump(self.personas, f, ensure_ascii=False, indent=2)
            logger.info(f"人设配置保存成功: {self.persona_file}")
        except Exception as e:
            logger.error(f"保存人设配置失败: {e}")
            
    def get_current_persona(self) -> Dict:
        """获取当前人设配置"""
        return self.personas.get(self.current_persona, self.personas.get('default', {}))
        
    def set_current_persona(self, persona_name: str) -> bool:
        """
        设置当前人设
        
        Args:
            persona_name: 人设名称
            
        Returns:
            设置是否成功
        """
        if persona_name in self.personas:
            self.current_persona = persona_name
            logger.info(f"已切换到人设: {persona_name}")
            return True
        else:
            logger.error(f"人设不存在: {persona_name}")
            return False
            
    def get_persona_list(self) -> List[str]:
        """获取所有人设名称列表"""
        return list(self.personas.keys())
        
    def get_persona_info(self, persona_name: str) -> Optional[Dict]:
        """
        获取指定人设的详细信息
        
        Args:
            persona_name: 人设名称
            
        Returns:
            人设信息字典，不存在时返回None
        """
        return self.personas.get(persona_name)
        
    def add_persona(self, name: str, persona_config: Dict) -> bool:
        """
        添加新人设
        
        Args:
            name: 人设名称
            persona_config: 人设配置
            
        Returns:
            添加是否成功
        """
        try:
            if name in self.personas:
                logger.warning(f"人设已存在: {name}")
                return False
                
            # 验证必要字段
            required_fields = ['name', 'description', 'personality', 'system_prompt']
            for field in required_fields:
                if field not in persona_config:
                    logger.error(f"人设配置缺少必要字段: {field}")
                    return False
                    
            self.personas[name] = persona_config
            logger.info(f"已添加新人设: {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加人设失败: {e}")
            return False
            
    def update_persona(self, name: str, persona_config: Dict) -> bool:
        """
        更新人设配置
        
        Args:
            name: 人设名称
            persona_config: 新的人设配置
            
        Returns:
            更新是否成功
        """
        try:
            if name not in self.personas:
                logger.error(f"人设不存在: {name}")
                return False
                
            # 保留原有配置，只更新提供的字段
            original_config = self.personas[name]
            original_config.update(persona_config)
            self.personas[name] = original_config
            
            logger.info(f"已更新人设: {name}")
            return True
            
        except Exception as e:
            logger.error(f"更新人设失败: {e}")
            return False
            
    def delete_persona(self, name: str) -> bool:
        """
        删除人设
        
        Args:
            name: 人设名称
            
        Returns:
            删除是否成功
        """
        try:
            if name == 'default':
                logger.error("不能删除默认人设")
                return False
                
            if name not in self.personas:
                logger.error(f"人设不存在: {name}")
                return False
                
            del self.personas[name]
            
            # 如果删除的是当前人设，切换到默认人设
            if self.current_persona == name:
                self.current_persona = 'default'
                
            logger.info(f"已删除人设: {name}")
            return True
            
        except Exception as e:
            logger.error(f"删除人设失败: {e}")
            return False
            
    def get_persona_system_prompt(self, persona_name: str = None) -> str:
        """
        获取人设的系统提示词
        
        Args:
            persona_name: 人设名称，为None时使用当前人设
            
        Returns:
            系统提示词
        """
        if persona_name is None:
            persona_name = self.current_persona
            
        persona = self.personas.get(persona_name, self.personas.get('default', {}))
        return persona.get('system_prompt', '')
        
    def validate_persona_config(self, config: Dict) -> List[str]:
        """
        验证人设配置
        
        Args:
            config: 人设配置
            
        Returns:
            错误信息列表
        """
        errors = []
        required_fields = ['name', 'description', 'personality', 'system_prompt']
        
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必要字段: {field}")
            elif not config[field]:
                errors.append(f"字段不能为空: {field}")
                
        # 检查可选字段
        optional_fields = ['language_style', 'emoji_usage', 'response_length', 'specialties']
        for field in optional_fields:
            if field in config and not config[field]:
                errors.append(f"可选字段不能为空: {field}")
                
        return errors 