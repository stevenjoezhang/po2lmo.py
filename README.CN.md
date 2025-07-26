# po2lmo

一个用于将 GNU gettext PO 文件转换为 Lua Machine Objects (LMO) 二进制格式的 Python 工具。

## 概述

po2lmo 是原始 C 版本 po2lmo 工具的 Python 实现，保持了相同的二进制格式兼容性。它可以将 GNU gettext PO 文件转换为 LMO 格式，该格式被各种 Lua 应用程序使用。

## 特性

- 完全兼容原始 C 版本的二进制格式
- 支持 Python 3.7+
- 提供命令行工具和 Python API
- 处理转义序列和多行字符串
- 重复键检测和错误处理
- 调试输出支持

## 安装

使用 pip 安装：

```bash
pip install po2lmo
```

## 使用方法

### 命令行工具

安装后，您可以使用 `po2lmo` 命令：

```bash
po2lmo input.po output.lmo
```

启用调试输出：

```bash
po2lmo --debug input.po output.lmo
```

### Python API

您也可以在 Python 代码中使用：

```python
from po2lmo import parse_po_file, write_lmo_file

# 解析 PO 文件
entries = parse_po_file('input.po')

# 写入 LMO 文件
write_lmo_file(entries, 'output.lmo')
```

## 开发

### 从源码安装

```bash
git clone https://github.com/stevenjoezhang/po2lmo.py.git
cd po2lmo
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 原始版本

原始 C 版本：
Copyright (C) 2009-2012 Jo-Philipp Wich <xm@subsignal.org>
