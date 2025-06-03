# 发布指南

## 准备工作

### 1. 安装发布工具

```bash
pip install build twine
```

### 2. 配置PyPI凭据

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-你的令牌
```

## 发布步骤

### 1. 清理旧文件

```bash
rm -rf build/ dist/ *.egg-info/
```

### 2. 构建包

```bash
python -m build
```

### 3. 检查包

```bash
twine check dist/*
```

### 4. 上传到PyPI

#### 测试环境（可选）

```bash
twine upload --repository testpypi dist/*
```

#### 正式环境

```bash
twine upload dist/*
```

### 5. 验证安装

```bash
pip install loguru-feishu-handler
```

## 版本管理

### 更新版本号

需要同时更新以下文件中的版本号：

1. `setup.py` 中的 `version`
2. `loguru_feishu_handler/__init__.py` 中的 `__version__`

### 创建Git标签

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 发布检查清单

- [ ] 所有测试通过
- [ ] 文档更新完整
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 许可证信息正确
- [ ] 包可以正常构建
- [ ] 包可以正常安装和导入

## 故障排除

### 常见问题

1. **上传失败：文件已存在**
   - 确保版本号是唯一的
   - PyPI不允许重复上传相同版本

2. **导入失败**
   - 检查包结构
   - 确保 `__init__.py` 文件正确

3. **依赖问题**
   - 检查 `setup.py` 中的依赖版本
   - 确保依赖包在PyPI中可用 