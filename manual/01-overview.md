# 第1章 项目概述

> **验证状态**: ✅ 已验证  
> **来源**: `README.md`, `pyproject.toml`, 源代码目录结构

---

## 1.1 项目简介

PyQalculate 是 [libqalculate](https://github.com/Qalculate/libqalculate) 的纯 Python 移植版。[来源: README.md:1]

**核心能力**:
- 任意精度数学运算（通过 gmpy2/mpmath）[来源: pyproject.toml:30]
- 单位转换（500+ 单位，支持前缀、复合单位）[来源: pyqalculate_data/units.json]
- 符号计算（通过 SymPy）[来源: pyproject.toml:29]
- 159+ 内置数学函数 [来源: pyqalculate/builtin_functions.py:3487-3800]
- 进制转换（二进制/八进制/十六进制/任意进制/罗马数字）[来源: builtin_functions.py:2455-2676]
- 日期时间运算 [来源: builtin_functions.py:2684-2838]
- 函数绘图（通过 matplotlib）[来源: pyqalculate/plot.py]
- CLI 交互式命令行 [来源: pyqalc/cli.py]
- GUI 桌面计算器（实验性，tkinter）[来源: pyqalculate_gui/app.py]

---

## 1.2 版本信息

| 项目 | 值 | 来源 |
|------|-----|------|
| 版本号 | 0.1.0 (Pre-Alpha) | `pyproject.toml:4` |
| Python 要求 | >= 3.10 | `pyproject.toml:25` |
| 许可证 | GPL-2.0-or-later | `pyproject.toml:3` |
| qalculate 版本 | 5.11.0 | `pyqalculate/types.py:17` |

---

## 1.3 依赖项

**核心依赖** (`pyproject.toml:29-38`):

| 包 | 版本 | 用途 |
|----|------|------|
| sympy | >= 1.12 | 符号计算引擎 |
| gmpy2 | >= 2.1.5 | 任意精度算术 |
| mpmath | >= 1.3.0 | 多精度浮点 |
| pint | >= 0.22 | 单位转换 |
| convertdate | >= 2.4.0 | 日期转换 |
| matplotlib | >= 3.7.0 | 绘图 |
| scipy | >= 1.11.0 | 科学计算 |
| requests | >= 2.31.0 | HTTP 请求（汇率） |
| numpy | >= 1.24.0 | array computing |
| Pillow | >= 10.0.0 | image processing |
| python-dateutil | >= 2.8.0 | date utilities |
| pyreadline3 | >= 3.4.0 | readline for Windows |

---

## 1.4 目录结构

```
pyqalculate/
├── pyqalculate/           # 核心库（16 个 Python 模块）
│   ├── __init__.py         # 公共 API：导出 Calculator
│   ├── calculator.py       # 主 Calculator 类（2530 行）
│   ├── builtin_functions.py # 159 个内置数学函数（~4100 行）
│   ├── parser.py           # 表达式解析器（1118 行）
│   ├── math_structure.py   # MathStructure AST 节点（2600 行）
│   ├── number.py           # Number 类（有理数/浮点/复数）
│   ├── unit.py             # Unit 层次结构（779 行）
│   ├── variable.py         # Variable 类（347 行）
│   ├── function.py         # MathFunction 基类（413 行）
│   ├── prefix.py           # 前缀系统（240 行）
│   ├── definitions.py      # JSON 定义加载器（802 行）
│   ├── types.py            # 枚举、选项、常量（782 行）
│   ├── expression_item.py  # ExpressionItem 基类
│   ├── dataset.py          # DataSet 结构化数据（438 行）
│   ├── datetime_ext.py     # 日期时间扩展（232 行）
│   └── plot.py             # matplotlib 绘图器（543 行）
├── pyqalc/                 # CLI 包
│   ├── cli.py              # CLI 入口点（960 行）
│   └── __main__.py         # 模块运行器
├── pyqalculate_gui/        # GUI 包（实验性）
│   ├── app.py              # 应用程序控制器（652 行）
│   ├── calculator_service.py # GUI 计算器服务包装器
│   ├── event_bus.py        # 事件驱动通信
│   ├── expression_edit.py  # 表达式输入组件
│   ├── result_view.py      # 结果显示组件
│   ├── history_view.py     # 历史记录面板
│   ├── keypad.py           # 虚拟键盘
│   ├── menu_bar.py         # 菜单栏
│   ├── autocomplete.py     # 自动补全弹窗
│   ├── theme.py            # 亮色/暗色主题
│   ├── conversion_view.py  # 单位转换视图
│   ├── expression_status.py # 表达式状态显示
│   ├── i18n.py             # 国际化
│   ├── import_csv_dialog.py # CSV 导入对话框
│   ├── export_csv_dialog.py # CSV 导出对话框
│   ├── keyboard_shortcuts.py # 键盘快捷键
│   ├── math_renderer.py    # 数学公式渲染
│   ├── state.py            # 应用状态
│   ├── status_bar.py       # 状态栏
│   ├── plot_dialog.py      # 绘图配置对话框
│   ├── preferences_dialog.py # 设置对话框
│   └── dialogs/            # 数制转换、函数列表、帮助、基类对话框
├── pyqalculate_data/       # JSON 数据文件
│   ├── units.json          # 500+ 单位定义
│   ├── variables.json      # 166+ 常量/变量
│   ├── prefixes.json       # SI 和二进制前缀
│   ├── currencies.json     # 货币定义
│   ├── elements.json       # 118 种化学元素
│   ├── planets.json        # 10 个太阳系天体
│   ├── functions.json      # 函数定义
│   └── datasets.json       # 数据集定义
├── tests/                  # 38 个测试文件
├── scripts/                # 测试运行器、演示脚本
├── start.bat               # Windows 启动器
└── docs/                   # 文档
```

---

## 1.5 入口点

| 入口点 | 命令 | 来源 |
|--------|------|------|
| CLI | `python -m pyqalc` 或 `pyqalc` | `pyproject.toml:47` |
| GUI | `python -m pyqalculate_gui` | `pyqalculate_gui/__main__.py` |
| 启动器 | `start.bat` | `start.bat` |
