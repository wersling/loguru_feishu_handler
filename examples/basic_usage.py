#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loguru Feishu Handler 基础使用示例
"""

from loguru import logger
from loguru_feishu_handler import add_feishu_sink

def main():
    """基础使用示例"""
    
    # 替换为你的飞书机器人 webhook 地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
    
    # 添加飞书 sink - 只发送 ERROR 级别以上的日志
    sink_id = add_feishu_sink(
        webhook_url=webhook_url,
        keyword="系统告警",  # 飞书机器人关键词
        level="ERROR",       # 只发送 ERROR 级别以上的日志
        cache_time=60       # 60秒内相同消息不重复发送
    )
    
    print(f"已添加飞书 sink，ID: {sink_id}")
    
    # 发送不同级别的日志
    logger.debug("这是调试信息")      # 不会发送到飞书
    logger.info("这是普通信息")       # 不会发送到飞书
    logger.warning("这是警告信息")    # 不会发送到飞书
    logger.error("这是错误信息")      # 会发送到飞书
    logger.critical("这是严重错误")   # 会发送到飞书
    
    # 带异常信息的日志
    try:
        result = 10 / 0  # 故意制造除零错误
    except Exception as e:
        logger.exception("发生了除零错误")  # 会发送到飞书，包含堆栈信息
    
    # 测试缓存机制 - 相同消息在缓存时间内不会重复发送
    logger.error("重复的错误消息")
    logger.error("重复的错误消息")  # 这条不会发送
    
    print("示例运行完成，请检查飞书群聊是否收到消息")

if __name__ == "__main__":
    main() 