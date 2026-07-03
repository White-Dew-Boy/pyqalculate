# 第10章 测试套件

> **验证状态**: ✅ 已验证  
> **来源**: `tests/` 目录 (39 个测试文件), `scripts/test_runner.py`

---

## 10.1 测试概述

**测试文件数量**: 39 个 [来源: tests/ 目录]  
**测试框架**: pytest [来源: pyproject.toml:60-62]  
**运行命令**: `pytest tests/ -v` [来源: pyproject.toml:62]

---

## 10.2 测试组织

### 核心模块测试

| 测试文件 | 测试内容 | 来源 |
|----------|----------|------|
| `test_calculator.py` | Calculator API | `tests/test_calculator.py` |
| `test_parser.py` | 表达式解析 | `tests/test_parser.py` |
| `test_basic.py` | 基本算术 | `tests/test_basic.py` |
| `test_number.py` | Number 类 | `tests/test_number.py` |
| `test_functions.py` | 内置函数 | `tests/test_functions.py` |
| `test_units.py` | 单位系统 | `tests/test_units.py` |
| `test_constants.py` | 物理常量 | `tests/test_constants.py` |
| `test_phase8_constants.py` | 高级常量 | `tests/test_phase8_constants.py` |
| `test_datasets.py` | 元素/行星数据集 | `tests/test_datasets.py` |
| `test_plot.py` | 绘图 | `tests/test_plot.py` |
| `test_csv.py` | CSV 导入/导出 | `tests/test_csv.py` |
| `test_integration.py` | 集成测试 | `tests/test_integration.py` |
| `test_qalculate_reference.py` | 参考测试用例 | `tests/test_qalculate_reference.py` |
| `test_cli.py` | CLI 测试 | `tests/test_cli.py` |

### GUI 测试

| 测试文件 | 测试内容 | 来源 |
|----------|----------|------|
| `test_gui.py` | GUI 冒烟测试 | `tests/test_gui.py` |
| `test_gui_integration.py` | GUI 集成测试 | `tests/test_gui_integration.py` |
| `test_autocomplete.py` | 自动补全 | `tests/test_autocomplete.py` |
| `test_keyboard_shortcuts.py` | 键盘快捷键 | `tests/test_keyboard_shortcuts.py` |
| `test_event_bus.py` | 事件总线 | `tests/test_event_bus.py` |
| `test_theme.py` | 主题系统 | `tests/test_theme.py` |
| `test_math_renderer.py` | 数学渲染 | `tests/test_math_renderer.py` |
| `test_expression_edit.py` | 表达式编辑器 | `tests/test_expression_edit.py` |
| `test_expression_status.py` | 表达式状态栏 | `tests/test_expression_status.py` |
| `test_result_view.py` | 结果显示 | `tests/test_result_view.py` |
| `test_history_view.py` | 历史记录面板 | `tests/test_history_view.py` |
| `test_keypad.py` | 虚拟键盘 | `tests/test_keypad.py` |
| `test_menu_bar.py` | 菜单栏 | `tests/test_menu_bar.py` |
| `test_status_bar.py` | 状态栏 | `tests/test_status_bar.py` |
| `test_conversion_view.py` | 转换面板 | `tests/test_conversion_view.py` |
| `test_state.py` | 应用状态 | `tests/test_state.py` |
| `test_calculator_service.py` | GUI 计算器服务 | `tests/test_calculator_service.py` |

### 对话框测试

| 测试文件 | 测试内容 | 来源 |
|----------|----------|------|
| `test_dialog_base.py` | 对话框基类 | `tests/test_dialog_base.py` |
| `test_plot_dialog.py` | 绘图对话框 | `tests/test_plot_dialog.py` |
| `test_preferences_dialog.py` | 设置对话框 | `tests/test_preferences_dialog.py` |
| `test_number_bases_dialog.py` | 进制转换对话框 | `tests/test_number_bases_dialog.py` |
| `test_functions_list_dialog.py` | 函数列表对话框 | `tests/test_functions_list_dialog.py` |
| `test_import_csv_dialog.py` | CSV 导入对话框 | `tests/test_import_csv_dialog.py` |
| `test_export_csv_dialog.py` | CSV 导出对话框 | `tests/test_export_csv_dialog.py` |

---

## 10.3 运行测试

### 方式一：通过启动器

```
PyScicompTool.bat → 选择 [3]
```

[来源: PyScicompTool.bat:106-111]

### 方式二：直接运行 pytest

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_calculator.py -v

# 运行特定测试
pytest tests/test_calculator.py::test_basic_calculation -v

# 显示简短回溯
pytest tests/ -v --tb=short
```

[来源: pyproject.toml:60-62]

### 方式三：通过测试运行器

```bash
python scripts/test_runner.py
```

[来源: scripts/test_runner.py]

---

## 10.4 测试套件详解

### 单元测试

运行 `tests/` 目录下所有 pytest 测试 [来源: test_runner.py:80-84]

**输出示例**:
```
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1
collected 1463 items
tests/test_basic.py::test_package_import PASSED
tests/test_basic.py::test_types_import PASSED
...
====== 1 failed, 1454 passed, 8 skipped in 165.21s =======
```

**结果说明**:
- `PASSED` — 测试通过
- `FAILED` — 测试失败
- `SKIPPED` — 测试跳过
- `ERROR` — 测试错误

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

---

## 10.5 测试结果摘要

运行模式 3 后显示摘要 [来源: test_runner.py:102-118]:

```
==================================================
  Summary
==================================================
  unit            [PASS/FAIL]
  comparison      [PASS/FAIL]
  plot            [PASS/FAIL]

Some tests failed. Check test_results/ for details.

Results saved to: test_results/
```

---

## 10.6 测试输出文件

| 文件 | 内容 |
|------|------|
| `test_results/unit_tests.txt` | 单元测试详细输出 |
| `test_results/comparison.txt` | 对比测试详细输出 |
| `test_results/plot_tests.txt` | 绘图测试详细输出 |

---

## 10.7 参考测试

`test_qalculate_reference.py` 包含从原始 libqalculate 提取的测试用例 [来源: tests/test_qalculate_reference.py]

**测试数据来源**: `D:\1\1tmp\qalculate_output\` 目录下 10 个文件

**测试类别**:
1. 基本运算
2. 单位转换
3. 物理常量
4. 不确定性/区间
5. 代数方程
6. 微积分
7. 矩阵/向量
8. 统计
9. 日期时间
10. 进制转换

---

## 10.8 编写测试

### 测试文件命名

- 文件名: `test_*.py`
- 函数名: `test_*`
- 类名: `Test*`

### 示例测试

```python
import pytest
from pyqalculate import Calculator

@pytest.fixture
def calc():
    calc = Calculator()
    calc.load_definitions()
    return calc

def test_basic_calculation(calc):
    result = calc.calculate_and_print("1 + 1")
    assert result == "2"

def test_trig_function(calc):
    result = calc.calculate_and_print("sin(pi/2)")
    assert result == "1"
```

[来源: tests/test_calculator.py]
