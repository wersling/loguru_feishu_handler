import json
import time
import hashlib
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
import requests
from loguru import logger


class LoguruFeishuSink:
    """Loguru 飞书消息推送 Sink
    
    通过飞书 webhook 接收日志消息并推送到飞书群聊
    """
    
    def __init__(
        self,
        webhook_url: str,
        keyword: str = "",
        cache_time: int = 60,
        filter_keys: Optional[List[str]] = None,
        simple_log_levelno: int = 30,  # WARNING级别以下使用简化格式
        simple_format: bool = True,
        timeout: int = 10
    ):
        """初始化飞书 Sink
        
        Args:
            webhook_url: 飞书机器人的 webhook 地址
            keyword: 飞书机器人的触发关键词
            cache_time: 缓存时间(秒)，相同消息在此时间内不重复发送，0为不启用缓存
            filter_keys: 需要过滤的字段列表
            simple_log_levelno: 简化输出的日志级别阈值
            simple_format: 是否启用简化格式
            timeout: 请求超时时间
        """
        self.webhook_url = webhook_url
        self.keyword = keyword
        self.cache_time = cache_time
        self.filter_keys = filter_keys or []
        self.simple_log_levelno = simple_log_levelno
        self.simple_format = simple_format
        self.timeout = timeout
        
        # 缓存相关
        self._cache: Dict[str, float] = {}
        self._cache_lock = threading.Lock()
        
    def __call__(self, message):
        """Loguru sink 的调用入口"""
        try:
            self._send_message(message)
        except Exception as e:
            # 避免日志发送失败影响主程序
            print(f"飞书消息发送失败: {e}")
    
    def _send_message(self, message):
        """发送消息到飞书"""
        # 格式化消息内容
        content = self._format_message(message)
        
        # 检查缓存
        if self.cache_time > 0 and self._should_skip_by_cache(content):
            return
            
        # 构造飞书消息格式
        feishu_message = self._build_feishu_message(content)
        
        # 发送消息
        self._send_to_feishu(feishu_message)
    
    def _format_message(self, message) -> str:
        """格式化日志消息"""
        record = message.record
        
        # 获取日志级别数值
        level_no = record["level"].no
        
        # 如果启用简化格式且级别低于阈值
        if self.simple_format and level_no < self.simple_log_levelno:
            return self._format_simple_message(record)
        else:
            return self._format_detailed_message(record)
    
    def _format_simple_message(self, record) -> str:
        """简化格式消息"""
        time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        level = record["level"].name
        message = record["message"]
        
        content = f"🕐 {time_str}\n📊 {level}\n📝 {message}"
        
        # 添加异常信息
        if record["exception"]:
            exc_info = record["exception"]
            content += f"\n❌ 异常类型: {exc_info.type.__name__}"
            content += f"\n💬 异常信息: {exc_info.value}"
        
        return content
    
    def _format_detailed_message(self, record) -> str:
        """详细格式消息"""
        time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        level = record["level"].name
        message = record["message"]
        file_info = f"{record['file'].path}:{record['line']}"
        function = record["function"]
        
        content = f"""🕐 时间: {time_str}
📊 级别: {level}
📁 文件: {file_info}
🔧 函数: {function}
📝 消息: {message}"""
        
        # 添加额外字段（过滤掉不需要的）
        extra_info = []
        for key, value in record["extra"].items():
            if key not in self.filter_keys:
                extra_info.append(f"{key}: {value}")
        
        if extra_info:
            content += f"\n📋 额外信息:\n" + "\n".join(extra_info)
        
        # 添加异常信息
        if record["exception"]:
            exc_info = record["exception"]
            content += f"\n❌ 异常类型: {exc_info.type.__name__}"
            content += f"\n💬 异常信息: {exc_info.value}"
            if exc_info.traceback:
                # 截取部分堆栈信息，避免消息过长
                traceback_lines = str(exc_info.traceback).split('\n')[:10]
                content += f"\n🔍 堆栈信息:\n```\n" + "\n".join(traceback_lines) + "\n```"
        
        return content
    
    def _build_feishu_message(self, content: str) -> Dict[str, Any]:
        """构造飞书消息格式"""
        # 添加关键词
        if self.keyword:
            content = f"{self.keyword}\n{content}"
            
        return {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
    
    def _should_skip_by_cache(self, content: str) -> bool:
        """检查是否应该跳过发送（基于缓存）"""
        if self.cache_time <= 0:
            return False
            
        # 生成内容哈希
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        current_time = time.time()
        
        with self._cache_lock:
            # 清理过期缓存
            expired_keys = [
                key for key, timestamp in self._cache.items()
                if current_time - timestamp > self.cache_time
            ]
            for key in expired_keys:
                del self._cache[key]
            
            # 检查是否在缓存中
            if content_hash in self._cache:
                return True
            
            # 添加到缓存
            self._cache[content_hash] = current_time
            return False
    
    def _send_to_feishu(self, message: Dict[str, Any]):
        """发送消息到飞书"""
        def _send():
            try:
                response = requests.post(
                    self.webhook_url,
                    json=message,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
            except Exception as e:
                print(f"飞书消息发送失败: {e}")
        
        # 使用线程发送，避免阻塞主程序
        thread = threading.Thread(target=_send, daemon=True)
        thread.start()


def add_feishu_sink(
    webhook_url: str,
    keyword: str = "",
    level: str = "INFO",
    cache_time: int = 60,
    filter_keys: Optional[List[str]] = None,
    simple_log_levelno: int = 30,
    simple_format: bool = True,
    **kwargs
) -> int:
    """便捷函数：为 loguru logger 添加飞书 sink
    
    Args:
        webhook_url: 飞书机器人的 webhook 地址
        keyword: 飞书机器人的触发关键词  
        level: 日志级别
        cache_time: 缓存时间(秒)
        filter_keys: 需要过滤的字段列表
        simple_log_levelno: 简化输出的日志级别阈值
        simple_format: 是否启用简化格式
        **kwargs: 其他传递给 logger.add 的参数
        
    Returns:
        sink_id: loguru sink 的 ID，可用于移除
        
    Example:
        >>> sink_id = add_feishu_sink(
        ...     "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
        ...     keyword="系统告警",
        ...     level="ERROR"
        ... )
    """
    sink = LoguruFeishuSink(
        webhook_url=webhook_url,
        keyword=keyword,
        cache_time=cache_time,
        filter_keys=filter_keys,
        simple_log_levelno=simple_log_levelno,
        simple_format=simple_format
    )
    
    return logger.add(sink, level=level, **kwargs) 