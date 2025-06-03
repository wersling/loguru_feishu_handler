#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化的富文本格式发送
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from loguru_feishu_handler import add_feishu_sink

# 飞书 webhook 地址
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/35df1ece-7bef-42dc-9894-ecd824ec56f5"

def test_simple_rich_text():
    """测试简化富文本格式消息"""
    
    # 添加飞书 sink
    sink_id = add_feishu_sink(
        webhook_url=WEBHOOK_URL,
        keyword="测试",
        level="INFO",
        cache_time=0   # 禁用缓存，方便测试
    )
    
    try:
        logger.info("这是一条基础的富文本测试消息")
        # logger.error("这是一条错误消息测试")
        
        print("简化富文本格式测试消息已发送!")
        
    finally:
        # 移除 sink
        logger.remove(sink_id)


if __name__ == "__main__":
    test_simple_rich_text() 