# Loguru Feishu Handler

基于 [loguru](https://github.com/Delgan/loguru) 的飞书消息推送处理器，通过飞书机器人 webhook 将日志消息推送到飞书群聊。

## 特点

- 🚀 **简单易用** - 一行代码即可接入飞书日志推送
- 🎨 **富文本格式** - 支持飞书富文本消息，更好的格式化效果
- 🔒 **缓存机制** - 支持相同消息缓存，避免重复发送
- 🎯 **格式灵活** - 支持简化和详细两种消息格式
- 🔧 **字段过滤** - 可配置过滤不需要的日志字段
- ⚡ **异步发送** - 多线程发送，不阻塞主程序
- 🛡️ **异常安全** - 发送失败不影响主程序运行

## 安装

```bash
pip install loguru-feishu-handler
```

## 快速开始

### 1. 创建飞书机器人

1. 在飞书群聊中，点击群设置
2. 选择"机器人" -> "添加机器人" -> "自定义机器人"
3. 设置机器人名称和描述
4. 复制生成的 Webhook 地址
5. （可选）设置关键词触发

### 2. 基础使用

```python
from loguru import logger
from loguru_feishu_handler import add_feishu_sink

# 添加飞书 sink
sink_id = add_feishu_sink(
    webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx",
    keyword="系统告警",  # 飞书机器人关键词
    level="ERROR"       # 只发送 ERROR 级别以上的日志
)

# 发送日志
logger.error("这是一条错误日志")
logger.critical("系统发生严重错误！")

# 带异常信息的日志
try:
    1 / 0
except Exception as e:
    logger.exception("发生了除零错误")
```

### 3. 高级配置

```python
from loguru import logger
from loguru_feishu_handler import LoguruFeishuSink

# 创建自定义 sink
sink = LoguruFeishuSink(
    webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx",
    keyword="系统监控",
    cache_time=300,  # 5分钟内相同消息不重复发送
    filter_keys=["process", "thread"],  # 过滤掉进程和线程信息
    simple_log_levelno=20,  # INFO级别以下使用简化格式
    simple_format=True,     # 启用简化格式
    timeout=15             # 请求超时时间
)

# 添加到 logger
sink_id = logger.add(sink, level="INFO")

# 使用示例
logger.info("这是一条信息日志")  # 简化格式
logger.error("这是一条错误日志")  # 详细格式
```

### 4. 消息格式示例

**富文本格式特性：**
- 支持飞书原生富文本格式（post 类型）
- 第一行关键信息**加粗显示**
- 更好的可读性和视觉效果
- 兼容飞书移动端和桌面端

**简化格式** (级别低于 WARNING):
```
富文本消息，第一行加粗：
**系统告警 | INFO | 应用启动成功**
🕐 时间: 2024-01-15 10:30:25
```

**详细格式** (级别 WARNING 及以上):
```
富文本消息，第一行加粗：
**系统告警 | ERROR | 数据处理失败**
🕐 时间: 2024-01-15 10:30:25
📁 文件: /app/main.py:25
🔧 函数: process_data
📋 额外信息:
user_id: 12345
request_id: req_001
❌ 异常类型: ValueError
💬 异常信息: 无效的数据格式
🔍 堆栈信息:
ValueError: 无效的数据格式
  File "/app/main.py", line 25, in process_data
    return parse_data(raw_data)
```

**无关键词格式**:
```
富文本消息，第一行加粗：
**ERROR | 系统错误**
🕐 时间: 2024-01-15 10:30:25
📁 文件: /app/main.py:25
🔧 函数: error_handler
```

## API 参考

### add_feishu_sink()

便捷函数，快速添加飞书 sink。

**参数:**
- `webhook_url` (str): 飞书机器人 webhook 地址
- `keyword` (str, optional): 机器人触发关键词
- `level` (str, optional): 日志级别，默认 "INFO"
- `cache_time` (int, optional): 缓存时间(秒)，默认 60
- `filter_keys` (List[str], optional): 需要过滤的字段列表
- `simple_log_levelno` (int, optional): 简化格式阈值，默认 30 (WARNING)
- `simple_format` (bool, optional): 是否启用简化格式，默认 True
- `**kwargs`: 传递给 `logger.add()` 的其他参数

**返回:**
- `int`: sink ID，可用于移除 sink

### LoguruFeishuSink

飞书 Sink 类，提供更多自定义选项。

**方法:**
- `__init__(webhook_url, ...)`: 初始化 sink
- `__call__(message)`: 处理日志消息（loguru 自动调用）

## 注意事项

1. **网络要求**: 需要能够访问飞书 API
2. **消息格式**: 使用飞书富文本格式（post），更好的显示效果
3. **消息限制**: 单条消息不超过 30KB
4. **频率限制**: 建议设置合适的缓存时间，避免频繁发送
5. **异常处理**: 发送失败会打印错误信息，但不影响主程序
6. **兼容性**: 富文本格式兼容飞书移动端和桌面端

## 更新日志

### v1.1.0
- 升级为飞书富文本格式（post 类型）
- 支持第一行加粗显示关键信息
- 优化消息结构和可读性
- 更好的飞书客户端兼容性

### v1.0.0
- 初始版本发布
- 支持基础的日志消息推送
- 支持缓存机制
- 支持简化和详细格式
- 支持字段过滤

## 许可证

Apache License 2.0 