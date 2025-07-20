#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信客户端模块
使用WXPY库实现微信登录、消息监听和发送功能
"""

import os
import time
import logging
import threading
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)

# 尝试导入WXPY，如果失败则使用ITchat作为备用方案
try:
    import wxpy
    WXPY_AVAILABLE = True
    logger.info("使用WXPY库作为微信客户端")
except ImportError:
    WXPY_AVAILABLE = False
    logger.warning("WXPY库未安装，尝试使用ITchat作为备用方案")
    try:
        import itchat
        ITCHAT_AVAILABLE = True
        logger.info("使用ITchat库作为微信客户端")
    except ImportError:
        ITCHAT_AVAILABLE = False
        logger.error("WXPY和ITchat库都未安装，请安装其中一个")


class WeChatClient:
    """微信客户端类"""
    
    def __init__(self):
        """初始化微信客户端"""
        self.bot = None
        self.is_logged_in = False
        self.message_handler = None
        self.login_thread = None
        
        if not WXPY_AVAILABLE and not ITCHAT_AVAILABLE:
            raise ImportError("需要安装WXPY或ITchat库")
            
    def login(self) -> bool:
        """
        登录微信
        
        Returns:
            登录是否成功
        """
        try:
            if WXPY_AVAILABLE:
                return self._login_with_wxpy()
            elif ITCHAT_AVAILABLE:
                return self._login_with_itchat()
            else:
                logger.error("没有可用的微信库")
                return False
        except Exception as e:
            logger.error(f"微信登录失败: {e}")
            return False
            
    def _login_with_wxpy(self) -> bool:
        """使用WXPY库登录"""
        try:
            logger.info("正在使用WXPY登录微信...")
            
            # 创建机器人实例
            self.bot = wxpy.Bot(
                cache_path='wxpy_cache.pkl',
                console_qr=True,  # 在控制台显示二维码
                qr_callback=self._qr_callback
            )
            
            # 等待登录完成
            if self.bot.alive:
                self.is_logged_in = True
                logger.info("WXPY微信登录成功")
                return True
            else:
                logger.error("WXPY微信登录失败")
                return False
                
        except Exception as e:
            logger.error(f"WXPY登录出错: {e}")
            return False
            
    def _login_with_itchat(self) -> bool:
        """使用ITchat库登录"""
        try:
            logger.info("正在使用ITchat登录微信...")
            
            # 在新线程中运行登录
            self.login_thread = threading.Thread(target=self._itchat_login_thread)
            self.login_thread.daemon = True
            self.login_thread.start()
            
            # 等待登录完成
            timeout = 60  # 60秒超时
            start_time = time.time()
            
            while not self.is_logged_in and time.time() - start_time < timeout:
                time.sleep(1)
                
            if self.is_logged_in:
                logger.info("ITchat微信登录成功")
                return True
            else:
                logger.error("ITchat微信登录超时")
                return False
                
        except Exception as e:
            logger.error(f"ITchat登录出错: {e}")
            return False
            
    def _itchat_login_thread(self):
        """ITchat登录线程"""
        try:
            itchat.auto_login(
                hotReload=True,
                enableCmdQR=2,  # 命令行二维码
                statusStorageDir='itchat_cache.pkl'
            )
            self.is_logged_in = True
            self.bot = itchat
            
            # 注册消息处理函数
            @itchat.msg_register(itchat.content.TEXT)
            def handle_text_message(msg):
                if self.message_handler:
                    message_data = {
                        'sender': msg['FromUserName'],
                        'content': msg['Text'],
                        'type': 'text',
                        'timestamp': msg['CreateTime']
                    }
                    self.message_handler(message_data)
                    
            # 开始运行
            itchat.run()
            
        except Exception as e:
            logger.error(f"ITchat登录线程出错: {e}")
            
    def _qr_callback(self, uuid, status, qrcode):
        """二维码回调函数"""
        if status == '0':
            logger.info("请扫描二维码登录微信")
        elif status == '200':
            logger.info("二维码扫描成功，正在登录...")
        elif status == '201':
            logger.info("二维码已扫描，请在手机上确认登录")
        elif status == '408':
            logger.warning("登录超时，请重新扫描二维码")
            
    def register_message_handler(self, handler: Callable):
        """
        注册消息处理函数
        
        Args:
            handler: 消息处理函数，接收消息字典作为参数
        """
        self.message_handler = handler
        
        if WXPY_AVAILABLE and self.bot:
            # 注册WXPY消息处理
            @self.bot.register()
            def handle_message(msg):
                if msg.type == 'Text':
                    message_data = {
                        'sender': msg.sender.name,
                        'content': msg.text,
                        'type': 'text',
                        'timestamp': time.time()
                    }
                    handler(message_data)
                    
    def send_message(self, receiver: str, content: str) -> bool:
        """
        发送消息
        
        Args:
            receiver: 接收者名称或ID
            content: 消息内容
            
        Returns:
            发送是否成功
        """
        try:
            if not self.is_logged_in:
                logger.error("微信未登录，无法发送消息")
                return False
                
            if WXPY_AVAILABLE:
                return self._send_with_wxpy(receiver, content)
            elif ITCHAT_AVAILABLE:
                return self._send_with_itchat(receiver, content)
            else:
                logger.error("没有可用的微信库")
                return False
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
            
    def _send_with_wxpy(self, receiver: str, content: str) -> bool:
        """使用WXPY发送消息"""
        try:
            # 查找好友
            friend = self.bot.friends().search(receiver)
            if friend:
                friend[0].send(content)
                logger.info(f"WXPY消息发送成功: {receiver}")
                return True
            else:
                logger.error(f"WXPY未找到好友: {receiver}")
                return False
        except Exception as e:
            logger.error(f"WXPY发送消息出错: {e}")
            return False
            
    def _send_with_itchat(self, receiver: str, content: str) -> bool:
        """使用ITchat发送消息"""
        try:
            # 发送消息
            self.bot.send(content, toUserName=receiver)
            logger.info(f"ITchat消息发送成功: {receiver}")
            return True
        except Exception as e:
            logger.error(f"ITchat发送消息出错: {e}")
            return False
            
    def logout(self):
        """退出登录"""
        try:
            if self.bot:
                if WXPY_AVAILABLE:
                    self.bot.logout()
                elif ITCHAT_AVAILABLE:
                    self.bot.logout()
                    
            self.is_logged_in = False
            logger.info("微信已退出登录")
            
        except Exception as e:
            logger.error(f"退出登录时出错: {e}")
            
    def get_friends_list(self) -> list:
        """获取好友列表"""
        try:
            if not self.is_logged_in:
                logger.error("微信未登录，无法获取好友列表")
                return []
                
            if WXPY_AVAILABLE and self.bot:
                friends = self.bot.friends()
                return [friend.name for friend in friends]
            elif ITCHAT_AVAILABLE and self.bot:
                friends = self.bot.get_friends()
                return [friend['NickName'] for friend in friends]
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取好友列表失败: {e}")
            return [] 