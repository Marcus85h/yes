#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信自动聊天机器人主程序
支持扫码登录微信，自动回复好友消息
"""

import os
import sys
import time
import logging
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatgpt_client import ChatGPTClient
from config import Config
from wechat_client import WeChatClient
from persona_manager import PersonaManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeChatBot:
    """微信自动聊天机器人主类"""
    
    def __init__(self):
        """初始化机器人"""
        self.config = Config()
        self.persona_manager = PersonaManager()
        self.chatgpt_client = ChatGPTClient(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model
        )
        self.wechat_client = WeChatClient()
        self.is_running = False
        
    def start(self):
        """启动机器人"""
        try:
            logger.info("正在启动微信自动聊天机器人...")
            
            # 加载人设配置
            self.persona_manager.load_persona()
            
            # 登录微信
            if not self.wechat_client.login():
                logger.error("微信登录失败")
                return False
                
            logger.info("微信登录成功，开始监听消息...")
            self.is_running = True
            
            # 注册消息处理函数
            self.wechat_client.register_message_handler(self.handle_message)
            
            # 保持程序运行
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在关闭机器人...")
            self.stop()
        except Exception as e:
            logger.error(f"机器人运行出错: {e}")
            self.stop()
            
    def stop(self):
        """停止机器人"""
        self.is_running = False
        if self.wechat_client:
            self.wechat_client.logout()
        logger.info("机器人已停止")
        
    def handle_message(self, message):
        """处理接收到的微信消息"""
        try:
            # 获取消息信息
            sender = message.get('sender', '')
            content = message.get('content', '')
            msg_type = message.get('type', 'text')
            
            logger.info(f"收到来自 {sender} 的消息: {content}")
            
            # 只处理文本消息
            if msg_type != 'text':
                logger.info(f"忽略非文本消息: {msg_type}")
                return
                
            # 检查是否在白名单中
            if not self.config.is_friend_allowed(sender):
                logger.info(f"好友 {sender} 不在白名单中，忽略消息")
                return
                
            # 生成AI回复
            persona = self.persona_manager.get_current_persona()
            reply = self.chatgpt_client.generate_reply(
                user_message=content,
                persona=persona,
                context=self.get_chat_context(sender)
            )
            
            if reply:
                # 发送回复
                self.wechat_client.send_message(sender, reply)
                logger.info(f"已回复 {sender}: {reply}")
            else:
                logger.warning(f"AI回复生成失败")
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            
    def get_chat_context(self, sender: str) -> list:
        """获取与特定好友的聊天上下文"""
        # 这里可以实现聊天历史记录功能
        # 目前返回空列表，可以根据需要扩展
        return []


def main():
    """主函数"""
    print("=" * 50)
    print("微信自动聊天机器人")
    print("=" * 50)
    
    # 检查配置文件
    if not os.path.exists('config.json'):
        print("未找到配置文件，请先运行 setup.py 进行初始化配置")
        return
        
    # 创建并启动机器人
    bot = WeChatBot()
    bot.start()


if __name__ == "__main__":
    main() 