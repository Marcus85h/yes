#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT客户端模块
处理与OpenAI API的交互，生成智能回复
"""

import os
import json
import logging
import time
from typing import List, Dict, Optional
import openai

logger = logging.getLogger(__name__)


class ChatGPTClient:
    """ChatGPT客户端类"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        初始化ChatGPT客户端
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.max_retries = 3
        self.retry_delay = 1
        
        # 设置OpenAI客户端
        self._setup_client()
        
    def _setup_client(self):
        """设置OpenAI客户端"""
        try:
            openai.api_key = self.api_key
            # 对于较新版本的openai库
            if hasattr(openai, 'OpenAI'):
                self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"ChatGPT客户端初始化成功，使用模型: {self.model}")
        except Exception as e:
            logger.error(f"ChatGPT客户端初始化失败: {e}")
            raise
            
    def generate_reply(self, user_message: str, persona: Dict = None, context: List = None) -> Optional[str]:
        """
        生成AI回复
        
        Args:
            user_message: 用户消息
            persona: 人设配置
            context: 聊天上下文
            
        Returns:
            生成的回复内容，失败时返回None
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(persona)
            
            # 构建消息列表
            messages = self._build_messages(system_prompt, user_message, context)
            
            # 调用API
            response = self._call_api(messages)
            
            if response:
                return response.strip()
            else:
                logger.error("API调用失败，未获得有效回复")
                return None
                
        except Exception as e:
            logger.error(f"生成回复时出错: {e}")
            return None
            
    def _build_system_prompt(self, persona: Dict = None) -> str:
        """构建系统提示词"""
        base_prompt = """你是一个友好的微信聊天助手。请根据用户的消息生成自然、有趣的回复。
        
回复要求：
1. 保持友好和礼貌的语气
2. 回复要简洁，不要太长
3. 根据用户消息的内容和情绪进行回应
4. 避免过于正式或机械化的回复
5. 可以适当使用表情符号增加亲和力
"""
        
        if persona:
            persona_desc = persona.get('description', '')
            personality = persona.get('personality', '')
            if persona_desc:
                base_prompt += f"\n人设描述: {persona_desc}"
            if personality:
                base_prompt += f"\n性格特点: {personality}"
                
        return base_prompt
        
    def _build_messages(self, system_prompt: str, user_message: str, context: List = None) -> List[Dict]:
        """构建消息列表"""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加聊天上下文
        if context:
            for msg in context[-10:]:  # 只保留最近10条消息
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
                    
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
        
    def _call_api(self, messages: List[Dict]) -> Optional[str]:
        """调用OpenAI API"""
        for attempt in range(self.max_retries):
            try:
                if self.client:
                    # 使用新版本API
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7,
                        timeout=30
                    )
                    return response.choices[0].message.content
                else:
                    # 使用旧版本API
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                    
            except openai.error.RateLimitError:
                logger.warning(f"API速率限制，等待重试... (尝试 {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay * (attempt + 1))
            except openai.error.APIError as e:
                logger.error(f"API调用错误: {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"未知错误: {e}")
                return None
                
        return None
        
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_message = "你好"
            reply = self.generate_reply(test_message)
            if reply:
                logger.info("ChatGPT API连接测试成功")
                return True
            else:
                logger.error("ChatGPT API连接测试失败")
                return False
        except Exception as e:
            logger.error(f"API连接测试出错: {e}")
            return False 