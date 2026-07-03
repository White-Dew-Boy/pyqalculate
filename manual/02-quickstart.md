# 第2章 快速开始

> **验证状态**: ✅ 已验证  
> **来源**: `README.md`, `PyScicompTool.bat`, `pyproject.toml`

---

## 2.1 安装

### 方式一：使用启动器（推荐）

双击 `PyScicompTool.bat`（Windows）或运行 `python3 PyScicompTool.py`（跨平台），选择菜单选项即可。启动器会自动：
1. 检查 Python 是否安装 [来源: PyScicompTool.bat:19-29]
2. 检查/创建虚拟环境 [来源: PyScicompTool.bat:34-86]
3. 安装依赖 [来源: PyScicompTool.bat:55-61]

### 方式二：手动安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装项目
pip install -e .

# 安装额外依赖
pip install matplotlib sympy gmpy2
```

[来源: README.md:Installation 部分]

---

## 2.2 启动方式

### 启动器菜单

运行 `PyScicompTool.bat` 后显示菜单：

运行 `python3 PyScicompTool.py` 显示相同菜单（跨平台）。

```
========================================
          Main Menu
========================================
  [1] CLI Mode     - Command line calculator
  [2] GUI Mode     - Graphical calculator
  [3] Run Tests    - Run all test suites
  [4] Run Demo     - Run all demos
  [0] Exit
========================================
```

[来源: PyScicompTool.bat:94-102]

| 选项 | 功能 | 来源 |
|------|------|------|
| 1 | 启动命令行计算器 | `PyScicompTool.bat:117-124` |
| 2 | 启动图形界面计算器 | `PyScicompTool.bat:126-131` |
| 3 | 运行所有测试套件 | `PyScicompTool.bat:133-137` |
| 4 | 运行演示模式 | `PyScicompTool.bat:139-143` |
| 0 | 退出 | `PyScicompTool.bat:151-157` |

---

## 2.3 基本用法

### CLI 单次计算

```bash
# 计算表达式
python -m pyqalc "1 + 1"
# 输出: 1 + 1 = 2

# 单位转换
python -m pyqalc "5 ft to m"
# 输出: 5 ft to m = 1.524 m

# 简洁模式（只显示结果）
python -m pyqalc -t "sin(pi/2)"
# 输出: 1
```

[来源: pyqalc/cli.py:583-595]

### CLI 交互模式

```bash
python -m pyqalc
> 2 + 3
  5
> sin(pi/2)
  1
> 5 ft to m
  1.524 m
> quit
```

[来源: pyqalc/cli.py:412-533]

### Python API

```python
from pyqalculate import Calculator

calc = Calculator()
calc.load_definitions()           # 加载内置定义
calc.load_global_definitions()    # 加载全局定义（元素、行星等）

# 基本计算
result = calc.calculate_and_print("1 + 1")  # "2"

# 单位转换
result = calc.calculate_and_print("5 ft to m")  # "1.524 m"

# 设置精度
calc.set_precision(20)
result = calc.calculate_and_print("pi")  # "3.1415926535897932385"

# 符号计算
result = calc.calculate_and_print("factor(x^2 - 4)")  # "(-2 + x) * (2 + x)"
```

[来源: README.md:Usage 部分, calculator.py:223-240]

---

## 2.4 验证清单

| 操作 | 预期结果 | 验证方式 |
|------|----------|----------|
| `PyScicompTool.bat` 启动 | 显示菜单 | 运行测试 |
| 选项 1 进入 CLI | 显示 `>` 提示符 | 运行测试 |
| 选项 2 启动 GUI | 打开窗口 | 运行测试 |
| 选项 3 运行测试 | 显示测试结果 | 运行测试 |
| `pyqalc "1+1"` | 输出 `2` | 运行测试 |
