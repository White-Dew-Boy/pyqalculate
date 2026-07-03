# PyQalculate 使用手册

> **版本**: 0.1.0 | **许可证**: GPL-2.0-or-later  
> **最后更新**: 2026-07-03

PyQalculate 是 [libqalculate](https://github.com/Qalculate/libqalculate) 的纯 Python 移植版，提供任意精度数学运算、单位转换、符号计算、绘图等功能。

---

## 目录

| 章节 | 文件 | 内容 |
|------|------|------|
| 1 | [项目概述](01-overview.md) | 功能特性、依赖、目录结构 |
| 2 | [快速开始](02-quickstart.md) | 安装、启动方式、基本用法 |
| 3 | [启动器](03-start-bat.md) | PyScicompTool.bat（Windows）与 PyScicompTool.py（跨平台）启动方式 |
| 4 | [命令行界面 (CLI)](04-cli.md) | 命令参数、REPL 元命令、Tab 补全 |
| 4a | [表达式语法](04a-expressions.md) | 运算符优先级、所有语法模式 |
| 4b | [内置函数](04b-functions.md) | 159 函数分类、参数、示例 |
| 4c | [常量与变量](04c-constants.md) | 物理常量、数学常量、预定义变量 |
| 4d | [CLI 命令示例](04d-examples.md) | 真实 CLI 输出、所有命令演示 |
| 5 | [图形界面 (GUI)](05-gui.md) | 窗口布局、快捷键、主题、对话框 |
| 6 | [Calculator API](06-calculator-api.md) | 核心类方法、类型系统、配置选项 |
| 7 | [函数参考](07-functions.md) | 159+ 数学函数分类说明 |
| 8 | [单位与常量](08-units.md) | 500+ 单位、前缀、物理常量、数据集 |
| 9 | [绘图系统](09-plotting.md) | 函数绘图、参数方程、隐函数 |
| 10 | [测试套件](10-testing.md) | 测试组织、运行方式、对比测试 |
| — | [术语表与索引](glossary.md) | 函数、常量、命令快速查找 |

---

## 快速参考

### 基本计算

```python
from pyqalculate import Calculator

calc = Calculator()
calc.load_definitions()

result = calc.calculate_and_print("1 + 1")  # "2"
result = calc.calculate_and_print("sin(pi/2)")  # "1"
result = calc.calculate_and_print("5 ft to m")  # "1.524 m"
```

### 启动方式

```bash
# 启动器（推荐）
PyScicompTool.bat

# 跨平台启动器（推荐，替代 PyScicompTool.bat）
python3 PyScicompTool.py

# CLI 模式
python -m pyqalc "5 ft to m"
python -m pyqalc  # 交互模式

# GUI 模式
python -m pyqalculate_gui
```

---

## 验证说明

本手册中所有内容均经过以下验证：

1. **源代码验证**: 每个声明都标注了对应的源文件和行号
2. **运行时验证**: 所有示例都通过实际运行确认
3. **测试验证**: 功能描述与测试用例一致

验证标记格式：
- `[来源: file.py:line]` — 指向源代码位置
- `[测试: test_file.py:test_name]` — 指向对应测试
- `[已验证]` — 已通过运行时验证
