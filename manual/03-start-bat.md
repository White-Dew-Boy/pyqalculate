# 第3章 启动器（start.bat / PyScicompTool.py）

> **验证状态**: ✅ 已验证  
> **来源**: `start.bat`, `scripts/test_runner.py`, `scripts/demo.py`

---

## 3.1 start.bat 概述

**适用平台**: Windows 专用

`start.bat` 是 Windows 启动器，提供图形化菜单访问所有功能。位于项目根目录。[来源: start.bat:1]

---

## 3.1a PyScicompTool.py 跨平台启动器

`PyScicompTool.py` 是跨平台 Python 启动器（替代 Windows-only 的 `start.bat`），支持 Windows、Linux、macOS。
位于项目根目录。[来源: PyScicompTool.py:1-5]

**启动方式**:

```bash
# Windows / Linux / macOS 通用
python3 PyScicompTool.py
```

**自动流程**:
1. 检查 Python >= 3.10 [来源: PyScicompTool.py:37-46]
2. 检查/创建虚拟环境 `.venv` [来源: PyScicompTool.py:49-65]
3. 安装核心依赖 (`pip install -e .`) [来源: PyScicompTool.py:68-81]
4. 安全重装可选依赖 (`matplotlib sympy gmpy2`) [来源: PyScicompTool.py:79-81]
5. 验证关键导入，损坏时自动 `--force-reinstall` [来源: PyScicompTool.py:84-101]
6. 进入交互菜单

**与 start.bat 的区别**:
| 特性 | start.bat | PyScicompTool.py |
|------|-----------|------------------|
| 平台 | Windows 专用 | Windows / Linux / macOS |
| 语言 | Batch | Python 3 |
| 清屏 | `cls` | `os.system("clear"/"cls")` |
| 暂停 | `pause` | `input("Press Enter...")` |

---

## 3.2 菜单选项

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

[来源: start.bat:94-102]

---

## 3.3 模式 1: CLI 模式

**功能**: 启动命令行计算器 [来源: start.bat:117-124]

**启动命令**: `%PY% scripts\cli.py` [来源: start.bat:122]

**退出方式**: 输入 `quit` 或 `exit` [来源: start.bat:120]

**详细说明**: 见 [第4章 命令行界面](04-cli.md)

---

## 3.4 模式 2: GUI 模式

**功能**: 启动图形界面计算器 [来源: start.bat:126-131]

**启动命令**: `%PY% scripts\gui.py` [来源: start.bat:129]

**详细说明**: 见 [第5章 图形界面](05-gui.md)

---

## 3.5 模式 3: 测试模式

**功能**: 运行所有测试套件 [来源: start.bat:133-137]

**启动命令**: `%PY% scripts\test_runner.py` [来源: start.bat:135]

### 测试套件组成

测试运行器执行三类测试 [来源: scripts/test_runner.py:78-100]:

| 序号 | 测试类型 | 脚本 | 输出文件 |
|------|----------|------|----------|
| 1 | 单元测试 | `pytest tests -v --tb=short` | `test_results/unit_tests.txt` |
| 2 | 对比测试 | `run_pyqalculate_tests.py` | `test_results/comparison.txt` |
| 3 | 绘图测试 | `run_plot_tests.py` | `test_results/plot_tests.txt` |

### 单元测试

运行 `tests/` 目录下所有 pytest 测试 [来源: test_runner.py:80-84]

**输出示例**:
```
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1
collected 1463 items
tests/test_basic.py::test_package_import PASSED
...
====== 1 failed, 1454 passed, 8 skipped in 165.21s =======
```

### 对比测试

将 pyqalculate 输出与原始 qalculate 输出对比 [来源: scripts/run_pyqalculate_tests.py:1-10]

**参考文件**: `D:\1\1tmp\qalculate_output\` 目录下 10 个文件 [来源: run_pyqalculate_tests.py:15-26]

**对比类别**:
- `[OK]` — 精确匹配
- `[FORMAT]` — 格式不同但数学等价
- `[DIFF]` — 值不同
- `[ERROR]` — 计算错误

**输出示例**:
```
Processing 01_basic_operations.txt...
  1.1 Nested roots... [OK]
  1.2 Sum of sin^2+cos^2... [DIFF]
  => 7/8 matches (87.5%) (1 diff)

OVERALL SUMMARY:
Total expressions: 69
  Exact matches (OK): 50
  Format matches (FORMAT): 3
  Total matches: 53
  Match rate: 76.8%
```

### 绘图测试

测试绘图功能 [来源: scripts/run_plot_tests.py:1-45]

**测试项目**:
- 二次函数 `x^2`
- 正弦函数 `sin(x)`
- 余弦函数 `cos(x)`

**输出示例**:
```
[PASS] 二次函数 -> 二次函数.png (40716 bytes)
[PASS] 正弦函数 -> 正弦函数.png (46543 bytes)
[PASS] 余弦函数 -> 余弦函数.png (47117 bytes)
绘图测试: 3/3 通过
```

### 测试结果摘要

```
==================================================
  Summary
==================================================
  unit            [PASS/FAIL]
  comparison      [PASS/FAIL]
  plot            [PASS/FAIL]
```

[来源: test_runner.py:102-118]

---

## 3.6 模式 4: 演示模式

**功能**: 运行所有演示 [来源: start.bat:139-143]

**启动命令**: `%PY% scripts\demo.py` [来源: start.bat:141]

### 演示命令列表

演示从 `scripts/demo_commands.txt` 读取命令 [来源: scripts/demo.py:41]

**命令类别**:

| 类别 | 命令示例 | 说明 |
|------|----------|------|
| 基本运算 | `2+3`, `sin(pi/2)` | 算术和三角函数 |
| 复杂公式 | `integrate(1/(1+x^5), x)` | 积分、求和 |
| 单位转换 | `5 ft to m` | 单位换算 |
| 物理常量 | `speed_of_light` | 内置常量 |
| 代数 | `factor(x^2-4)` | 因式分解 |
| 微积分 | `diff(sin(x^2)*exp(-x))` | 求导 |
| 统计 | `mean(1,2,3,4,5)` | 统计函数 |
| 设置 | `set precision 50` | 精度设置 |
| 帮助 | `help` | 显示帮助 |
| 绘图 | `plot(sin(x), sin.png)` | 函数绘图 |
| 参数方程 | `plot_parametric(...)` | 参数曲线 |
| 隐函数 | `plot_implicit(...)` | 隐函数绘图 |

### 演示输出

所有输出保存到 `scripts/demo_output/demo_results.txt` [来源: scripts/demo.py:44]

**输出示例**:
```
PyQalculate Demo Results
============================================================

>> 2+3
  5

>> set precision 50
  precision = 50

>> pi
  3.14159265358979311599796346854418516159057617187500

>> plot(sin(x), sin.png)
  [PLOT] sin.png (46543 bytes)

============================================================
Total commands: 50
Plots generated: 6
Errors: 0
```

### 元命令

演示支持以下元命令 [来源: scripts/demo.py:51-57]:

| 命令 | 语法 | 说明 |
|------|------|------|
| `set` | `set option value` | 设置选项 |
| `help` | `help` | 显示帮助 |
| `mode` | `mode mode_name` | 切换模式 |
| `base` | `base n` | 设置进制 |

**set 子选项** [来源: scripts/demo.py:149-186]:
- `set precision N` — 设置精度
- `set base N` — 设置进制 (2-36)
- `set angle degree|radian` — 设置角度单位
- `set approx exact|approximate|try_exact` — 设置近似模式

---

## 3.7 环境检查

启动器自动检查 [来源: start.bat:19-86]:

1. **Python 检查**: 验证 Python 已安装
2. **虚拟环境检查**: 检查 `.venv` 目录是否存在
3. **自动创建**: 如不存在，自动创建虚拟环境并安装依赖

---

## 3.8 输出目录

| 目录 | 内容 |
|------|------|
| `test_results/` | 测试输出文件 |
| `scripts/demo_output/` | 演示输出文件 |
| `scripts/demo_output/plots/` | 演示生成的图表 |
