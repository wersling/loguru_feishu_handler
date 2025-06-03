#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loguru Feishu Handler 高级使用示例
"""

from loguru import logger
from loguru_feishu_handler import LoguruFeishuSink

def main():
    """高级使用示例"""
    
    # 替换为你的飞书机器人 webhook 地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
    
    # 创建自定义 sink 配置
    feishu_sink = LoguruFeishuSink(
        webhook_url=webhook_url,
        keyword="系统监控",
        cache_time=300,  # 5分钟内相同消息不重复发送
        filter_keys=["process", "thread", "elapsed"],  # 过滤掉进程、线程和耗时信息
        simple_log_levelno=20,  # INFO级别(20)以下使用简化格式
        simple_format=True,     # 启用简化格式
        timeout=15             # 请求超时时间15秒
    )
    
    # 添加到 logger，设置为 DEBUG 级别
    sink_id = logger.add(feishu_sink, level="DEBUG")
    print(f"已添加自定义飞书 sink，ID: {sink_id}")
    
    # 添加额外信息到日志上下文
    logger.configure(extra={"app_name": "示例应用", "version": "1.0.0"})
    
    # 测试不同级别的日志
    print("\n=== 测试不同级别的日志 ===")
    
    # DEBUG 级别 - 使用简化格式
    logger.debug("应用启动中...")
    
    # INFO 级别 - 使用简化格式  
    logger.info("用户登录成功", extra={"user_id": "12345", "ip": "192.168.1.100"})
    
    # WARNING 级别 - 使用详细格式
    logger.warning("磁盘空间不足", extra={"disk_usage": "85%", "available": "2GB"})
    
    # ERROR 级别 - 使用详细格式
    logger.error("数据库连接失败", extra={"db_host": "localhost", "error_code": 1045})
    
    # 测试异常日志
    print("\n=== 测试异常日志 ===")
    
    try:
        # 模拟文件操作错误
        with open("/nonexistent/file.txt", "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        logger.exception("文件读取失败", extra={"file_path": "/nonexistent/file.txt"})
    
    try:
        # 模拟网络请求错误
        import requests
        response = requests.get("http://nonexistent-domain.com", timeout=1)
    except Exception as e:
        logger.exception("网络请求失败", extra={"url": "http://nonexistent-domain.com"})
    
    # 测试缓存机制
    print("\n=== 测试缓存机制 ===")
    
    # 发送相同消息多次，只有第一次会发送到飞书
    for i in range(3):
        logger.error("重复的错误消息用于测试缓存")
        print(f"第 {i+1} 次发送相同消息")
    
    # 发送不同消息
    logger.error("这是一条不同的错误消息")
    
    print("\n示例运行完成，请检查飞书群聊接收到的消息格式")
    print("注意观察：")
    print("1. DEBUG/INFO 级别使用简化格式")
    print("2. WARNING/ERROR 级别使用详细格式") 
    print("3. 异常日志包含堆栈信息")
    print("4. 重复消息只发送一次")
    print("5. 过滤掉了 process、thread、elapsed 字段")

if __name__ == "__main__":
    main() 