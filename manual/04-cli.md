# 第4章 命令行界面 (CLI) - 完整参考

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalc/cli.py` (960 行)

---

## 4.1 启动方式

```bash
# 直接启动
python -m pyqalc

# 通过启动器
PyScicompTool.bat → 选择 [1]
```

[来源: pyqalc/__main__.py:3]

---

## 4.2 命令行参数

| 参数 | 长参数 | 说明 | 来源 |
|------|--------|------|------|
| `expression` | — | 要计算的表达式（位置参数） | `cli.py:72-76` |
| `-t` | `--terse` | 只显示结果（不回显表达式） | `cli.py:77-83` |
| `-b` | `--base BASE` | 设置输出进制 (2, 8, 10, 16) | `cli.py:84-91` |
| `-s` | `--set OPTION` | 设置选项（如 `"precision 20"`） | `cli.py:92-99` |
| `-e` | `--exrates` | 启动时更新汇率 | `cli.py:100-106` |
| `-v` | `--version` | 显示版本 | `cli.py:107-112` |
| — | `--no-color` | 禁用彩色输出 | `cli.py:113-118` |
| `-h` | `--help` | 显示帮助信息 | argparse 自动提供 |

---

## 4.3 使用模式

### 单次计算模式

```bash
# 基本计算
python -m pyqalc "1 + 1"
# 输出: 1 + 1 = 2

# 简洁模式
python -m pyqalc -t "sin(pi/2)"
# 输出: 1

# 多表达式
python -m pyqalc "2+3" "4*5"
# 输出: 2+3 = 5
#        4*5 = 20
```

[来源: cli.py:940-952]

### 交互式 REPL

```bash
python -m pyqalc
> 2 + 3
  5
> sin(pi/2)
  1
> quit
```

[来源: cli.py:733-890]

**REPL 特性**:
- 命令历史（保存到 `~/.pyqalc_history`）[来源: cli.py:134]
- Tab 补全（函数、变量、单位）[来源: cli.py:155-239]
- `ans` 变量存储上次结果 [来源: cli.py:750-756]
- 彩色输出 [来源: cli.py:33-58]

---

## 4.4 REPL 元命令

### help

显示帮助信息 [来源: cli.py:246-266, 774-791]

```
> help
```

**新增功能**: `help <function>` 显示函数详细帮助 [来源: cli.py:453-470]

```
> help sin
  sin - Sine
  Category: Trigonometry
  Syntax: sin(x:number)

> help solve
  solve - Solve equation
  Category: Algebra
  Syntax: solve(equation:symbolic, [variable:symbolic])
```

### functions

列出所有可用函数 [来源: cli.py:473-475]

```
> functions
  Algebra:
    coeff, degree, dsolve, expand, factor, multisolve, roots, solve

  Base:
    base, bases, bin, float, floaterror, hex, oct, roman

  Bitwise:
    bitand, bitnot, bitor, bitxor, shift

  Calculus:
    diff, integrate, limit, product, sum

  Combinatorics:
    binomial, double_factorial, factorial, gamma, multinomial

  Date & Time:
    date, days, lunarphase, months, now, stamptodate, timestamp, today, weeks, years

  Exponents & Logarithms:
    cbrt, cis, exp, exp10, exp2, lambertw, ln, log10, log2, logn, root, sqrt, square

  Logical:
    and, not, or, xor

  Matrix:
    adj, cofactor, cross, det, dot, eigenvalues, hadamard, identity, inverse, magnitude, norm, rank, rref, trace, transpose

  Number Theory:
    abs, arg, bernoulli, ceil, denominator, floor, frac, gcd, im, int, interval, is_prime, lcm, mod, next_prime, nth_prime, numerator, parallel, powermod, prev_prime, prime_count, re, rem, round, signum, totient, trunc, uncertainty

  Special:
    airy, besselj, bessely, beta, digamma, dirac, erf, erfc, fresnelc, fresnels, heaviside, zeta

  Statistics:
    correlation, covariance, max, mean, median, min, mode, normdist, percentile, quartile, rand, stdev, variance

  Trigonometry:
    acos, acosh, asin, asinh, atan, atan2, atanh, cos, cosh, sin, sinc, sinh, tan, tanh

  Utility:
    concatenate, even, export, for, genvector, if, is_integer, is_number, is_rational, is_real, length, load, odd, plot, replace, tostring
```

### constants

列出所有物理常量 [来源: cli.py:477-479]

```
> constants
  Mathematical Constants:
    pi = 3.1415926...
    e = 2.7182818...
    euler = 0.5772156... (Euler-Mascheroni constant)
    catalan = 0.9159655... (Catalan's constant)
    golden = 1.6180339... (Golden ratio, also φ/phi)
    tau = 6.2831853... (2π)

  Physical Constants:
    alpha = 0.0072973526
    avogadro = 6.0221408e+23
    boltzmann = 1.380649e-23
    c = 299792458
    e_charge = 1.6021766e-19
    elementary_charge = 1.6021766e-19
    g = 6.6743e-11
    k_b = 1.380649e-23
    n_a = 6.0221408e+23
    ... and 54 more
```

### set

显示或设置选项 [来源: cli.py:208-257]

```
> set                    # 显示所有设置
> set precision 20       # 设置精度为 20 位
> set base 16            # 设置输出进制为十六进制
> set approx approximate # 设置近似模式
```

**set 子选项**:

| 选项 | 值 | 说明 |
|------|-----|------|
| `precision` | 整数 | 有效数字位数（内部精度） |
| `base` | 2-36 | 输出进制 |
| `approx` | `exact`, `approx`, `try_exact` | 近似模式 |

**⚠️ 注意**: `set precision` 影响的是**内部计算精度**，不会直接改变输出显示位数。输出格式由 `PrintOptions` 控制。

[来源: cli.py:228-257]

### base

改变输出进制 [来源: cli.py:260-287]

```
> base bin    # 二进制
> base oct    # 八进制
> base dec    # 十进制
> base hex    # 十六进制
> base 16     # 十六进制（数字形式）
```

### save

保存变量 [来源: cli.py:290-317]

```
> save x 42      # 保存 x = 42
> save result    # 保存上次结果为 result
```

### delete

删除用户变量 [来源: cli.py:320-335]

```
> delete x       # 删除变量 x
```

### assume

设置未知数假设 [来源: cli.py:338-347]

```
> assume x > 0
  Assumptions noted: x > 0
```

**注意**: 此命令目前是占位符，仅回显输入，不会实际应用假设。

### mode

显示或切换模式 [来源: cli.py:350-385]

```
> mode              # 显示当前模式
> mode exact        # 精确模式
> mode approx       # 近似模式
> mode fraction     # 分数显示
> mode decimal      # 小数显示
```

**模式说明**:

| 模式 | 效果 |
|------|------|
| `exact` | 精确模式，不近似 |
| `approx` | 近似模式，浮点计算 |
| `fraction` | 分数显示 |
| `decimal` | 小数显示 |

**⚠️ 注意**: `mode fraction` 不会将已有的小数结果转换为分数，它只影响后续计算结果的显示格式。

[来源: cli.py:365-385]

### factorize

因式分解上次结果 [来源: cli.py:497-511]

```
> 12
  12
> factorize
  2^2 * 3
```

### simplify

简化上次结果 [来源: cli.py:513-521]

```
> sin(x)^2 + cos(x)^2
  sin(x)^2 + cos(x)^2
> simplify
  1
```

**⚠️ 注意**: `simplify` 只应用基本代数恒等式（如 sin²+cos²=1），**不执行多项式除法**。例如 `(x²-4)/(x-2)` 不会被简化为 `x+2`。

### plot

打开交互式绘图窗口

```
> plot(sin(x))
> plot(x^2, -5, 5)
```

### plot_implicit

绘制隐函数 f(x,y)=0

```
> plot_implicit(x^2 + y^2 - 1)
```

### subplot

组合多个绘图为网格布局

```
> subplot(2, 2, 1, sin(x))
> subplot(2, 2, 2, cos(x))
```

### quit / exit / q

退出 REPL [来源: cli.py:450-451]

---

## 4.5 Tab 补全

支持补全的内容 [来源: cli.py:155-239]:

- 内置函数名（如 `sin`, `cos`, `sqrt`）
- 变量名（如 `pi`, `e`）
- 单位名（如 `m`, `kg`, `ft`）
- 元命令（如 `set`, `help`, `mode`）

**增强功能**: 当只有一个匹配项时，显示函数描述 [来源: cli.py:214-232]

```
> sin<TAB>
  sin - Sine
```

---

## 4.6 彩色输出

自动检测终端支持 [来源: cli.py:33-58]:

- 绿色：结果
- 青色：提示符
- 黄色：警告
- 禁用：`--no-color` 参数

---

## 4.7 已知限制与诚实说明

> **重要**: 本节记录了 CLI 和底层引擎的实际行为边界。遇到问题时请先查阅此节。

### 4.7.1 微分方程 (dsolve)

| 场景 | 状态 | 说明 |
|------|------|------|
| 一阶线性 ODE | ✅ 可用 | `dsolve(diff(y,x) - y, y)` 基本可用 |
| 高阶 ODE | ⚠️ 有限 | 二阶及以上可能返回未求值结果 |
| 边值问题 | ❌ 不支持 | 仅支持初值问题（部分） |

**正确格式**: 使用 `diff(y,x)` 格式，**不要**使用 `y'` prime notation。

```
# ✅ 正确
dsolve(diff(y,x) - y, y)

# ❌ 错误 - prime notation 不支持
dsolve(y' - y, y)
```

### 4.7.2 导数 (diff)

| 场景 | 状态 | 说明 |
|------|------|------|
| 多项式求导 | ✅ 完全支持 | `diff(x^2, x)` → `2*x` |
| 三角函数求导 | ✅ 完全支持 | `diff(sin(x), x)` → `cos(x)` |
| 复合函数求导 | ✅ 支持 | 链式法则自动应用 |
| prime notation `y'` | ❌ 不支持 | 必须使用 `diff(y,x)` 格式 |

### 4.7.3 极限 (limit)

| 场景 | 状态 | 说明 |
|------|------|------|
| 基本极限 | ✅ 可用 | `limit(sin(x)/x, x, 0)` → `1` |
| 多项式极限 | ✅ 可用 | `limit(1/x, x, inf)` → `0` |
| 1^∞ 类型 | ✅ 可用 | 通过 log 变换处理，如 `limit((1+1/x)^x, x, inf)` → `e` |
| 振荡极限 | ⚠️ 有限 | `limit(sin(x), x, inf)` 可能返回未求值 |

### 4.7.4 积分 (integrate)

| 场景 | 状态 | 说明 |
|------|------|------|
| 多项式积分 | ✅ 完全支持 | `integrate(x^2, x)` → `x³/3 + C` |
| 基本初等函数 | ✅ 大部分支持 | 三角、指数、对数等 |
| 经典积分 | ✅ 已验证 | `integrate(1/(1+x^5), x)` 等复杂积分可解 |
| 含符号参数的积分 | ⚠️ 有限 | `integrate(x^a, x)` 当 `a` 为符号时可能失败 |
| 某些定积分 | ⚠️ 可能返回未求值 | 特殊函数相关的定积分 |

### 4.7.5 物理常量命名冲突

| 变量名 | 作为物理常量 | 作为普通变量 | 说明 |
|--------|-------------|-------------|------|
| `c` | 光速 299792458 | 可能被用户赋值 | 优先作为光速常量 |
| `alpha` | 精细结构常数 0.007297... | 可能被用户赋值 | 优先作为精细结构常数 |
| `e` | 自然常数 2.71828... | 也可能被解析为电荷 | 上下文决定 |
| `g` | 万有引力常数 6.6743e-11 | 也可能表示标准重力 | 上下文决定 |

**建议**: 避免使用物理常量名称作为自定义变量名。

### 4.7.6 assume 命令

当前 `assume` 命令是**占位符**，仅回显输入，不会实际应用假设到计算中。

```
> assume x > 0
  Assumptions noted: x > 0
# 注意: 此假设不会影响后续计算
```

### 4.7.7 求解器 (solve)

| 场景 | 状态 | 说明 |
|------|------|------|
| 线性方程 | ✅ 完全支持 | `solve(2*x - 4, x)` → `2` |
| 二次方程 | ✅ 完全支持 | `solve(x^2 - 4, x)` → `(-2, 2)` |
| 高次多项式 | ✅ 大部分支持 | 有解析解的多项式 |
| 超越方程 | ⚠️ 有限 | `sin(x) = 0.5` 等可能不完整 |
| 方程组 | ⚠️ 实验性 | `multisolve` 功能有限 |

### 4.7.8 除零行为

除零现在返回清晰的错误信息，不再返回 `zoo` 或 `4*zoo`：

```
> 1/0
  Error: Division by zero
> 5/(x-1) where x=1
  Error: Division by zero
```

### 4.7.9 改进的函数行为

以下函数在最新版本中获得了改进：

| 函数 | 改进 | 说明 |
|------|------|------|
| `for(init, cond, step, expr)` | 符号边界支持 | 当边界为符号时返回符号求和，如 `for(i:=1, i<=n, i:=i+1, i)` → `1/2*n*(n+1)` |
| `round(x)` | 符号参数支持 | `round(x)` 对符号参数返回符号形式 |
| `trunc(x)` | 符号参数支持 | `trunc(x)` 对符号参数返回符号形式 |
| `parallel(a, b)` | 零值处理 | `parallel(0, 5)` → `infinity`（不再崩溃） |
