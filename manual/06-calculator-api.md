# 第6章 Calculator API

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalculate/calculator.py` (2530 行), `pyqalculate/types.py` (783 行)

---

## 6.1 基本用法

```python
from pyqalculate import Calculator

calc = Calculator()
calc.load_definitions()           # 加载内置定义
calc.load_global_definitions()    # 加载全局定义

result = calc.calculate_and_print("1 + 1")  # "2"
```

[来源: calculator.py:39, 225-237]

---

## 6.2 Calculator 类

### 构造函数

```python
calc = Calculator()
```

[来源: calculator.py:52]

### 精度控制

| 方法 | 行号 | 说明 |
|------|------|------|
| `get_precision()` | 69 | 返回当前精度 |
| `set_precision(n)` | 73 | 设置精度（有效数字位数） |

[来源: calculator.py:69-73]

### 定义管理

| 方法 | 行号 | 说明 |
|------|------|------|
| `add_function(func)` | 79 | 注册数学函数 |
| `add_variable(var)` | 84 | 注册变量 |
| `add_unit(unit)` | 96 | 注册单位 |
| `add_prefix(prefix)` | 110 | 注册前缀 |
| `get_function(name)` | 114 | 查找函数（不区分大小写） |
| `get_variable(name)` | 118 | 查找变量（不区分大小写） |
| `get_unit(name)` | 122 | 查找单位（多优先级：精确→别名→前缀分解→不区分大小写） |
| `get_item(name)` | 182 | 统一查找（单位→变量→函数） |
| `has_function(name)` | 203 | 检查函数是否存在 |
| `has_variable(name)` | 206 | 检查变量是否存在 |
| `has_unit(name)` | 209 | 检查单位是否存在 |
| `count_functions()` | 214 | 统计函数数量 |
| `count_variables()` | 217 | 统计变量数量 |
| `count_units()` | 220 | 统计单位数量 |

[来源: calculator.py:79-220]

### 定义加载

| 方法 | 行号 | 说明 |
|------|------|------|
| `load_definitions()` | 225 | 加载所有内置函数、变量、单位、前缀 |
| `load_global_definitions()` | 237 | 从 JSON 加载：166+ 变量/常量、元素数据集、行星数据集 |
| `load_exchange_rates()` | 250 | 加载货币汇率（TODO） |

[来源: calculator.py:225-250]

---

## 6.3 核心计算方法

### parse — 解析表达式

```python
mstruct = calc.parse("1 + 1", po=None)
```

**参数**:
- `expression`: 表达式字符串
- `po`: ParseOptions（可选）

**返回**: MathStructure

[来源: calculator.py:643]

### calculate — 计算表达式

```python
mstruct = calc.calculate("1 + 1", timeout_ms=0, eo=None)
```

**参数**:
- `expression`: 表达式字符串
- `timeout_ms`: 超时（毫秒，0=无限制）
- `eo`: EvaluationOptions（可选）

**返回**: MathStructure

**特殊处理** [来源: calculator.py:653-907]:
- 单位转换: `"expr to unit"`
- WHERE 子句: `"expr where x > 0"`
- 日期运算: `"2024-01-01 + 100 days"`
- 进制转换: `"42 to hex"`, `"255 to bin"`
- 时间格式: `"10h31min to time"`
- 分数/因式分解/偏分数: `"to fraction"`, `"to factors"`, `"to partial fraction"`

### calculate_and_print — 计算并格式化

```python
result = calc.calculate_and_print("1 + 1", timeout_ms=0, eo=None, po=None)
```

**参数**:
- `expression`: 表达式字符串
- `timeout_ms`: 超时（毫秒）
- `eo`: EvaluationOptions（可选）
- `po`: PrintOptions（可选）

**返回**: 格式化的字符串

[来源: calculator.py:908]

### print_result — 格式化结果

```python
result = calc.print_result(mstruct, po=None)
```

**参数**:
- `mstruct`: MathStructure
- `po`: PrintOptions（可选）

**返回**: 格式化的字符串

[来源: calculator.py:950]

---

## 6.4 单位转换

### find_unit — 查找单位

```python
unit = calc.find_unit("meter")
```

[来源: calculator.py:978]

### convert — 转换值

```python
result = calc.convert(5.0, "ft", "m")  # 1.524
```

**参数**:
- `value`: 数值
- `from_unit`: 源单位
- `to_unit`: 目标单位
- `from_exp`: 源单位指数（默认 1）
- `to_exp`: 目标单位指数（默认 1）

**返回**: 转换后的数值，失败返回 None

[来源: calculator.py:1006]

---

## 6.5 CSV 导入/导出

### importCSV

```python
mstruct = calc.importCSV(filename, first_row=1, headers=True, 
                         delimiter=",", to_matrix=False, name="")
```

[来源: calculator.py:2368]

### exportCSV

```python
calc.exportCSV(mstruct, filename, delimiter=",")
```

[来源: calculator.py:2469]

---

## 6.5a XLSX 导入/导出

### importXLSX

```python
mstruct = calc.importXLSX(filename, sheet=0, headers=True, first_row=1,
                          to_matrix=False, name="")
```

导入 Excel `.xlsx` 文件。`sheet` 参数支持按索引（`0`）或名称（`"Sheet1"`）指定工作表。

[来源: calculator.py:2470]

### exportXLSX

```python
calc.exportXLSX(mstruct, filename, sheet_name="Sheet1")
```

导出 MathStructure 到 Excel `.xlsx` 文件。

[来源: calculator.py:2617]

---

## 6.6 类型系统

### EvaluationOptions — 评估选项

```python
@dataclass
class EvaluationOptions:
    approximation: ApproximationMode = ApproximationMode.TRY_EXACT
    sync_units: bool = True
    calculate_variables: bool = True
    calculate_functions: bool = True
    test_comparisons: bool = True
    isolate_x: bool = True
    allow_complex: bool = True
    allow_infinite: bool = True
    auto_post_conversion: AutoPostConversion = AutoPostConversion.OPTIMAL
    structuring: StructuringMode = StructuringMode.NONE
    parse_options: ParseOptions = field(default_factory=ParseOptions)
    complex_number_form: ComplexNumberForm = ComplexNumberForm.RECTANGULAR
    # ... (20 个字段)
```

[来源: types.py:710]

### PrintOptions — 打印选项

```python
@dataclass
class PrintOptions:
    min_exp: int = EXP_PRECISION
    base: int = BASE_DECIMAL
    base_display: BaseDisplay = BaseDisplay.NONE
    number_fraction_format: NumberFractionFormat = NumberFractionFormat.DECIMAL
    abbreviate_names: bool = True
    place_units_separately: bool = True
    use_unit_prefixes: bool = True
    short_multiplication: bool = True
    min_decimals: int = 0
    max_decimals: int = -1
    exact: bool = False
    approximate: bool = False
    # ... (45 个字段)
```

[来源: types.py:617]

### ParseOptions — 解析选项

```python
@dataclass
class ParseOptions:
    variables_enabled: bool = True
    functions_enabled: bool = True
    unknowns_enabled: bool = True
    units_enabled: bool = True
    rpn: bool = False
    base: int = BASE_DECIMAL
    angle_unit: AngleUnit = AngleUnit.NONE
    parsing_mode: ParsingMode = ParsingMode.ADAPTIVE
    # ... (14 个字段)
```

[来源: types.py:683]

---

## 6.7 枚举类型

### ApproximationMode — 近似模式

| 值 | 说明 |
|----|------|
| `EXACT` | 精确模式 |
| `TRY_EXACT` | 尝试精确 |
| `APPROXIMATE` | 近似模式 |
| `EXACT_VARIABLES` | 精确变量 |

[来源: types.py:289]

### AngleUnit — 角度单位

| 值 | 说明 |
|----|------|
| `NONE` | 无 |
| `RADIANS` | 弧度 |
| `DEGREES` | 度 |
| `GRADIANS` | 梯度 |
| `CUSTOM` | 自定义 |

[来源: types.py:330]

### StructureType — 结构类型

29 种类型 [来源: types.py:38]:
- NUMBER, SYMBOLIC, UNIT, VARIABLE, FUNCTION
- ADDITION, MULTIPLICATION, POWER
- VECTOR, MATRIX, COMPARISON
- UNIT_CONVERSION, FACTORIAL, WHERE, ASSIGNMENT
- 等等

---

## 6.8 MathStructure — 数学结构

表达式的 AST（抽象语法树）节点 [来源: math_structure.py:786]

### 工厂方法

| 方法 | 行号 | 说明 |
|------|------|------|
| `from_number(n)` | 853 | 从数字创建 |
| `from_variable(v)` | 860 | 从变量创建 |
| `from_unit(u)` | 867 | 从单位创建 |
| `from_symbol(s)` | 875 | 从符号创建 |
| `undefined()` | 882 | 创建未定义 |
| `addition(*children)` | 886 | 创建加法 |
| `multiplication(*children)` | 892 | 创建乘法 |
| `power(base, exp)` | 898 | 创建幂 |
| `vector(*elements)` | 916 | 创建向量 |
| `matrix(rows)` | 922 | 创建矩阵 |

[来源: math_structure.py:853-922]

### SymPy 桥接

```python
# MathStructure → SymPy
sympy_expr = mstruct.to_sympy()

# SymPy → MathStructure
mstruct = MathStructure.from_sympy(sympy_expr)
```

[来源: math_structure.py:956-1148]

### 属性检查

```python
mstruct.is_number()      # 是否为数字
mstruct.is_symbolic()    # 是否为符号
mstruct.is_variable()    # 是否为变量
mstruct.is_function()    # 是否为函数
mstruct.is_addition()    # 是否为加法
mstruct.is_multiplication()  # 是否为乘法
mstruct.is_power()       # 是否为幂
mstruct.is_vector()      # 是否为向量
mstruct.is_matrix()      # 是否为矩阵
mstruct.is_undefined()   # 是否未定义
```

[来源: math_structure.py:1274-1310]

---

## 6.9 全局实例

```python
from pyqalculate.calculator import get_calculator

calc = get_calculator()  # 返回全局单例
```

[来源: calculator.py:2525]
