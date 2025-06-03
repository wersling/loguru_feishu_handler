#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loguru Feishu Handler 真实飞书测试
使用真实的飞书webhook地址进行功能验证
"""

import time
from loguru import logger
from loguru_feishu_handler import add_feishu_sink, LoguruFeishuSink

def test_basic_functionality():
    """测试基础功能"""
    print("=== 基础功能测试 ===")
    
    # 真实的飞书webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/35df1ece-7bef-42dc-9894-ecd824ec56f5"
    
    # 清除所有现有的logger handlers
    logger.remove()
    
    # 添加控制台输出（便于本地查看）
    logger.add(lambda msg: print(f"[本地日志] {msg}", end=""), level="DEBUG")
    
    # 添加飞书 sink
    sink_id = add_feishu_sink(
        webhook_url=webhook_url,
        keyword="loguru测试",
        level="INFO",
        cache_time=5  # 5秒缓存，便于测试
    )
    
    print(f"✅ 已添加飞书 sink，ID: {sink_id}")
    
    # 测试不同级别的日志
    logger.info("🚀 Loguru Feishu Handler 测试开始")
    time.sleep(1)
    
    logger.warning("⚠️ 这是一条警告消息")
    time.sleep(1)
    
    logger.error("❌ 这是一条错误消息")
    time.sleep(1)
    
    # 测试异常日志
    try:
        result = 10 / 0
    except Exception as e:
        logger.exception("💥 捕获到除零异常")
    
    time.sleep(1)
    
    # 测试缓存机制
    logger.error("🔄 重复消息测试 - 第1次")
    logger.error("🔄 重复消息测试 - 第1次")  # 这条应该被缓存跳过
    
    time.sleep(1)
    
    logger.critical("🔥 系统严重错误！需要立即处理！")
    
    print("✅ 基础功能测试完成")
    return sink_id

def test_advanced_features():
    """测试高级功能"""
    print("\n=== 高级功能测试 ===")
    
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/35df1ece-7bef-42dc-9894-ecd824ec56f5"
    
    # 创建自定义配置的sink
    custom_sink = LoguruFeishuSink(
        webhook_url=webhook_url,
        keyword="高级测试",
        cache_time=10,
        filter_keys=["process", "thread"],  # 过滤掉进程和线程信息
        simple_log_levelno=20,  # INFO级别以下使用简化格式
        simple_format=True,
        timeout=15
    )
    
    # 添加自定义sink
    custom_sink_id = logger.add(custom_sink, level="DEBUG")
    print(f"✅ 已添加自定义飞书 sink，ID: {custom_sink_id}")
    
    # 添加额外的上下文信息
    logger.configure(extra={"app_name": "测试应用", "version": "1.0.0", "env": "test"})
    
    # 测试简化格式 (DEBUG/INFO)
    logger.debug("🔍 调试信息 - 使用简化格式")
    time.sleep(1)
    
    logger.info("ℹ️ 应用信息 - 使用简化格式", extra={"user_id": "12345", "action": "login"})
    time.sleep(1)
    
    # 测试详细格式 (WARNING及以上)
    logger.warning("⚠️ 内存使用率过高", extra={"memory_usage": "85%", "threshold": "80%"})
    time.sleep(1)
    
    logger.error("💾 数据库连接失败", extra={
        "db_host": "localhost:3306", 
        "error_code": 1045,
        "retry_count": 3
    })
    time.sleep(1)
    
    # 测试复杂异常
    try:
        import json
        json.loads('{"invalid": json}')  # 故意的JSON错误
    except Exception as e:
        logger.exception("📄 JSON解析失败", extra={
            "input_data": '{"invalid": json}',
            "parser": "json.loads"
        })
    
    print("✅ 高级功能测试完成")
    return custom_sink_id

def test_message_formats():
    """测试消息格式"""
    print("\n=== 消息格式测试 ===")
    
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/35df1ece-7bef-42dc-9894-ecd824ec56f5"
    
    # 创建用于格式测试的sink
    format_sink = LoguruFeishuSink(
        webhook_url=webhook_url,
        keyword="格式测试",
        cache_time=0,  # 禁用缓存以便测试所有消息
        simple_log_levelno=25,  # 设置为WARNING级别
        simple_format=True
    )
    
    format_sink_id = logger.add(format_sink, level="DEBUG")
    print(f"✅ 已添加格式测试 sink，ID: {format_sink_id}")
    
    # 测试简化格式消息
    logger.info("📝 这是简化格式的消息")
    time.sleep(1)
    
    # 测试详细格式消息
    logger.warning("📋 这是详细格式的消息")
    time.sleep(1)
    
    # 测试带emoji的消息
    logger.error("🎯 测试各种emoji表情 🚀 🔥 ⭐ 💡 🎉")
    time.sleep(1)
    
    # 测试长消息
    long_message = "这是一条很长的消息，" * 20 + "用于测试消息长度处理。"
    logger.error(f"📏 长消息测试: {long_message}")
    
    print("✅ 消息格式测试完成")
    return format_sink_id

def main():
    """主测试函数"""
    print("🎯 开始 Loguru Feishu Handler 真实测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        basic_sink_id = test_basic_functionality()
        advanced_sink_id = test_advanced_features()
        format_sink_id = test_message_formats()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        print("📱 请检查飞书群聊中是否收到了测试消息")
        print(f"🔧 添加的sink ID: {basic_sink_id}, {advanced_sink_id}, {format_sink_id}")
        
        # 清理sink
        logger.remove(basic_sink_id)
        logger.remove(advanced_sink_id)
        logger.remove(format_sink_id)
        print("🧹 已清理所有测试sink")
        
    except Exception as e:
        logger.exception(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main() 