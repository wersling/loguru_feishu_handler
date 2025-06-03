#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loguru Feishu Handler 单元测试
"""

import unittest
import time
from unittest.mock import Mock, patch
from loguru import logger

from loguru_feishu_handler.handler import LoguruFeishuSink, add_feishu_sink


class TestLoguruFeishuSink(unittest.TestCase):
    """LoguruFeishuSink 测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/test"
        self.keyword = "测试"
        
    def test_init(self):
        """测试初始化"""
        sink = LoguruFeishuSink(
            webhook_url=self.webhook_url,
            keyword=self.keyword,
            cache_time=60
        )
        
        self.assertEqual(sink.webhook_url, self.webhook_url)
        self.assertEqual(sink.keyword, self.keyword)
        self.assertEqual(sink.cache_time, 60)
        self.assertIsInstance(sink._cache, dict)
    
    def test_format_simple_message(self):
        """测试简化格式消息"""
        sink = LoguruFeishuSink(self.webhook_url, keyword="告警")
        
        # 模拟 loguru record
        mock_level = Mock()
        mock_level.name = "INFO"
        mock_level.no = 20
        
        mock_time = Mock()
        mock_time.strftime.return_value = "2024-01-15 10:30:25"
        
        mock_record = {
            "time": mock_time,
            "level": mock_level,
            "message": "测试消息",
            "file": Mock(path="/test/file.py"),
            "line": 10,
            "function": "test_func",
            "extra": {},
            "exception": None
        }
        
        result = sink._format_simple_message(mock_record)
        
        # 检查富文本格式结构
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # 检查第一行包含关键词和消息（加粗格式）
        first_line = result[0]
        self.assertIsInstance(first_line, list)
        
        # 查找包含关键词的元素
        first_line_text = "".join(elem.get("text", "") for elem in first_line)
        self.assertIn("告警 | INFO | 测试消息", first_line_text)
    
    def test_format_simple_message_no_keyword(self):
        """测试无关键词的简化格式消息"""
        sink = LoguruFeishuSink(self.webhook_url, keyword="")
        
        # 模拟 loguru record
        mock_level = Mock()
        mock_level.name = "INFO"
        mock_level.no = 20
        
        mock_time = Mock()
        mock_time.strftime.return_value = "2024-01-15 10:30:25"
        
        mock_record = {
            "time": mock_time,
            "level": mock_level,
            "message": "测试消息",
            "file": Mock(path="/test/file.py"),
            "line": 10,
            "function": "test_func",
            "extra": {},
            "exception": None
        }
        
        result = sink._format_simple_message(mock_record)
        
        # 检查富文本格式结构
        self.assertIsInstance(result, list)
        
        # 检查第一行不包含关键词
        first_line = result[0]
        first_line_text = "".join(elem.get("text", "") for elem in first_line)
        self.assertNotIn("告警", first_line_text)
        self.assertIn("INFO | 测试消息", first_line_text)
    
    def test_format_detailed_message(self):
        """测试详细格式消息"""
        sink = LoguruFeishuSink(self.webhook_url, keyword="错误")
        
        # 模拟 loguru record
        mock_level = Mock()
        mock_level.name = "ERROR"
        mock_level.no = 40
        
        mock_time = Mock()
        mock_time.strftime.return_value = "2024-01-15 10:30:25"
        
        mock_record = {
            "time": mock_time,
            "level": mock_level,
            "message": "错误消息",
            "file": Mock(path="/test/file.py"),
            "line": 25,
            "function": "error_func",
            "extra": {"user_id": "12345"},
            "exception": None
        }
        
        result = sink._format_detailed_message(mock_record)
        
        # 检查富文本格式结构
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 4)  # 至少有标题、时间、文件、函数四行
        
        # 检查第一行包含关键词和消息
        first_line = result[0]
        first_line_text = "".join(elem.get("text", "") for elem in first_line)
        self.assertIn("错误 | ERROR | 错误消息", first_line_text)
    
    def test_format_detailed_message_no_keyword(self):
        """测试无关键词的详细格式消息"""
        sink = LoguruFeishuSink(self.webhook_url, keyword="")
        
        # 模拟 loguru record
        mock_level = Mock()
        mock_level.name = "ERROR"
        mock_level.no = 40
        
        mock_time = Mock()
        mock_time.strftime.return_value = "2024-01-15 10:30:25"
        
        mock_record = {
            "time": mock_time,
            "level": mock_level,
            "message": "错误消息",
            "file": Mock(path="/test/file.py"),
            "line": 25,
            "function": "error_func",
            "extra": {"user_id": "12345"},
            "exception": None
        }
        
        result = sink._format_detailed_message(mock_record)
        
        # 检查第一行不包含关键词
        first_line = result[0]
        first_line_text = "".join(elem.get("text", "") for elem in first_line)
        self.assertNotIn("错误 |", first_line_text)  # 确保不包含关键词
        self.assertIn("ERROR | 错误消息", first_line_text)
    
    def test_cache_mechanism(self):
        """测试缓存机制"""
        sink = LoguruFeishuSink(self.webhook_url, cache_time=1)
        
        content1 = "测试消息1"
        content2 = "测试消息2"
        
        # 第一次检查，应该不跳过
        self.assertFalse(sink._should_skip_by_cache(content1))
        
        # 立即再次检查相同内容，应该跳过
        self.assertTrue(sink._should_skip_by_cache(content1))
        
        # 检查不同内容，应该不跳过
        self.assertFalse(sink._should_skip_by_cache(content2))
        
        # 等待缓存过期
        time.sleep(1.1)
        
        # 缓存过期后，应该不跳过
        self.assertFalse(sink._should_skip_by_cache(content1))
    
    def test_build_feishu_message(self):
        """测试构造飞书消息格式"""
        sink = LoguruFeishuSink(self.webhook_url, keyword="告警")
        
        # 构造富文本内容元素
        content_elements = [
            [
                {"tag": "text", "text": "告警 | ERROR | 测试内容"}
            ],
            [{"tag": "text", "text": "🕐 时间: 2024-01-15 10:30:25"}]
        ]
        
        message = sink._build_feishu_message(content_elements)
        
        expected = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "日志消息",
                        "content": content_elements
                    }
                }
            }
        }
        
        self.assertEqual(message, expected)
    
    def test_build_feishu_message_no_keyword(self):
        """测试无关键词的飞书消息格式"""
        sink = LoguruFeishuSink(self.webhook_url)
        
        # 构造富文本内容元素
        content_elements = [
            [{"tag": "text", "text": "ERROR | 测试内容"}],
            [{"tag": "text", "text": "🕐 时间: 2024-01-15 10:30:25"}]
        ]
        
        message = sink._build_feishu_message(content_elements)
        
        expected = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "日志消息",
                        "content": content_elements
                    }
                }
            }
        }
        
        self.assertEqual(message, expected)
    
    @patch('requests.post')
    def test_send_to_feishu(self, mock_post):
        """测试发送到飞书"""
        mock_post.return_value.raise_for_status.return_value = None
        
        sink = LoguruFeishuSink(self.webhook_url)
        
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "日志消息",
                        "content": [[{"tag": "text", "text": "测试"}]]
                    }
                }
            }
        }
        
        sink._send_to_feishu(message)
        
        # 等待线程执行
        time.sleep(0.1)
        
        mock_post.assert_called_once_with(
            self.webhook_url,
            json=message,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )


class TestAddFeishuSink(unittest.TestCase):
    """add_feishu_sink 函数测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/test"
        
    def test_add_feishu_sink(self):
        """测试添加飞书 sink"""
        # 清除现有的handlers
        logger.remove()
        
        sink_id = add_feishu_sink(
            webhook_url=self.webhook_url,
            keyword="测试",
            level="INFO"
        )
        
        self.assertIsInstance(sink_id, int)
        
        # 清理
        logger.remove(sink_id)


if __name__ == "__main__":
    unittest.main() 