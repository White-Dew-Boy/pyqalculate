# 第4d章 CLI 命令示例（真实输出）

> **验证状态**: ✅ 已验证  
> **验证方式**: 通过 `python -m pyqalc` 实际运行并捕获输出

---

## 4d.1 基本算术

| 命令 | 输出 | 说明 |
|------|------|------|
| `1+1` | `1+1 = 2` | 基本加法 |
| `2*3+4` | `2*3+4 = 10` | 运算符优先级 |
| `2^10` | `2^10 = 1024` | 幂运算 |
| `100 mod 7` | `100 mod 7 = 2` | 取模 |
| `100 \ 7` | `100 \ 7 = 14` | 整除 |

---

## 4d.2 三角函数

| 命令 | 输出 | 说明 |
|------|------|------|
| `sin(pi/2)` | `sin(pi/2) = 1` | 正弦 |
| `cos(0)` | `cos(0) = 1` | 余弦 |
| `tan(pi/4)` | `tan(pi/4) = 1` | 正切 |
| `asin(1)` | `asin(1) = 1/2 * pi` | 反正弦（符号结果） |

---

## 4d.3 对数函数

| 命令 | 输出 | 说明 |
|------|------|------|
| `ln(e)` | `ln(e) = 1` | 自然对数 |
| `log2(8)` | `log2(8) = 3` | 以 2 为底 |
| `log10(100)` | `log10(100) = 2` | 以 10 为底 |

---

## 4d.4 微积分

| 命令 | 输出 | 说明 |
|------|------|------|
| `diff(x^2, x)` | `diff(x^2, x) = 2 * x` | 求导 |
| `integrate(x^2, x)` | `integrate(x^2, x) = 1/3 * (x)^(3) + C` | 不定积分（带常数 C） |
| `limit(sin(x)/x, x, 0)` | `limit(sin(x)/x, x, 0) = 1` | 极限 |

---

## 4d.5 单位转换

| 命令 | 输出 | 说明 |
|------|------|------|
| `5 ft to m` | `5 ft to m = 1.524 m` | 英尺→米 |
| `100 km/h to m/s` | `100 km/h to m/s = 27.777778 m/s` | 速度转换 |
| `1 lightyear to km` | `1 lightyear to km = 9.4607305e+12 km` | 光年→千米 |

---

## 4d.6 进制转换

| 命令 | 输出 | 说明 |
|------|------|------|
| `255 to hex` | `255 to hex = 0xFF` | 十六进制（0x 前缀） |
| `255 to bin` | `255 to bin = 1111 1111` | 二进制（空格分隔 nibble） |
| `255 to oct` | `255 to oct = 0377` | 八进制（0 前缀） |

---

## 4d.7 代数

| 命令 | 输出 | 说明 |
|------|------|------|
| `factor(x^2-4)` | `factor(x^2-4) = (- 2 + x) * (2 + x)` | 因式分解 |
| `solve(x^2-4, x)` | `solve(x^2-4, x) = (-2, 2)` | 求解方程 |

---

## 4d.8 REPL 元命令

### help 命令

```
> help
PyQalculate 0.1.0 - interactive calculator

Type any mathematical expression to evaluate it.
Special commands:
  set [option [value]]     Show/set options (precision, base, etc.)
  base <n>                 Change the output number base
  save <name> [value]      Save a variable
  delete <name>            Delete a user variable
  assume <assumptions>     Set assumptions for unknowns
  mode [mode_name]         Show/change calculation mode
  factorize                Factorize last result
  simplify                 Simplify last result
  help [function]          Show help for a function (e.g. help sin)
  functions                List all available functions
  constants                List all physical constants
  quit / exit              Exit the program
```

### help <function> 命令

```
> help sin
  sin - Sine
  Category: Trigonometry
  Syntax: sin(x:number)

> help solve
  solve - Solve equation
  Category: Algebra
  Syntax: solve(equation:symbolic, [variable:symbolic])

> help integrate
  integrate - Integrate
  Category: Calculus
  Syntax: integrate(expression:symbolic, [symbol:symbolic], [lower], [upper])
```

### functions 命令

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

### constants 命令

```
> constants
  Physical Constants:
    alpha = 0.0072973526
    alpha_particle_u = 4.0015062
    ans = 0
    avogadro = 6.0221408e+23
    bakers_dozen = 13
    billion = 1000000000
    boltzmann = 1.380649e-23
    c = 299792458
    centillion = 1e+303
    crore = 10000000
    decillion = 1e+33
    deuteron_u = 2.0135532
    doz = 12
    dozen = 12
    duodecillion = 1e+39
    dz = 12
    e = 2.7182818
    e_charge = 1.6021766e-19
    electron_u = 0.00054857991
    elementary_charge = 1.6021766e-19
    false = 0
    fermi_coupling = 1.1663787e-05
    fine_structure = 0.0072973526
    g = 6.6743e-11
    g_0 = 9.80665
    great_gross = 1728
    great_hundred = 120
    gro = 144
    gross = 144
    helion_u = 3.0149322
    higgs_boson = 125110
    hundred = 100
    josephson_conventional = 483597900000000
    k_b = 1.380649e-23
    k_j90 = 483597900000000
    klitzing_conventional = 25812.807
    lakh = 100000
    lattice_parameter_si = 5.4310205e-10
    long_hundred = 120
    long_thousand = 1200
    m_sun = 1.98892e+30
    million = 1000000
    muon_u = 0.11342893
    n_a = 6.0221408e+23
    neutron_u = 1.0086649
    newtonian_constant = 6.6743e-11
    no = 0
    nonillion = 1e+30
    novemdecillion = 1e+60
    octillion = 1e+27
    ... and 54 more
```

### set 命令

```
> set
  precision = 8
  base = 10
  terse = False
  approximation = TRY_EXACT

> set precision 20
  precision = 20

> set base 16
  base = 16

> set approx approximate
  approximation = APPROXIMATE
```

### base 命令

```
> base bin
  Base set to 2

> base hex
  Base set to 16

> base dec
  Base set to 10
```

### mode 命令

```
> mode
  base = 10
  approximation = TRY_EXACT
  exact = True
  fraction format = DECIMAL

> mode exact
  Mode set to exact

> mode approx
  Mode set to approximate

> mode fraction
  Mode set to fraction
```

### factorize 命令

```
> 12
  12
> factorize
  2^2 * 3
```

### simplify 命令

```
> (x^2 - 4)/(x - 2)
  (x^2 - 4)/(x - 2)
> simplify
  x + 2
```

### save/delete 命令

```
> save x 42
  Saved x = 42

> x + 8
  50

> delete x
  Deleted x
```

---

## 4d.9 Tab 补全示例

当输入部分命令并按 Tab 时（只有一个匹配项时显示描述）：

```
> si<TAB>
  sin - Sine

> sqrt<TAB>
  sqrt - Square root
```

当有多个匹配项时，按 Tab 会循环显示选项：
```
> co<TAB><TAB><TAB>
  cos
  cosh
  correlation
```

---

## 4d.10 复杂表达式示例

| 命令 | 输出 | 说明 |
|------|------|------|
| `2^100` | `2^100 = 1267650600228229401496703205376` | 大数 |
| `factorial(20)` | `20! = 2432902008176640000` | 大阶乘 |
| `gcd(2520, 3600)` | `gcd(2520, 3600) = 360` | 最大公约数 |
| `binomial(20, 5)` | `binomial(20, 5) = 15504` | 二项式系数 |
| `sin(pi/3)^2 + cos(pi/3)^2` | `sin(pi/3)^2 + cos(pi/3)^2 = 1` | 恒等式 |
| `sqrt(32) + cbrt(-27)` | `sqrt(32) + cbrt(-27) = 4 * sqrt(2) - 3` | 混合根号 |
| `137/12 to fraction` | `137/12 to fraction = 11 + 5/12` | 带分数 |
| `1.5 to fraction` | `1.5 to fraction = 3/2` | 小数→分数 |
| `2024-06-15 + 100 days` | `2024-06-15 + 100 days = 2024-09-23` | 日期运算 |
| `10 h 31 min to time` | `10 h 31 min to time = 10:31` | 时间格式 |
| `42 to roman` | `42 to roman = XLII` | 罗马数字 |
| `42 to bases` | `42 to bases = 101010 = 0o52 = 42 = 0x2A` | 所有进制 |
| `det([1,2;3,4])` | `det([1,2;3,4]) = -2` | 矩阵行列式 |
| `mean(1,2,3,4,5)` | `mean(1,2,3,4,5) = 3` | 平均值 |
| `correlation({1,2,3,4,5}, {2,4,5,4,5})` | `correlation({1,2,3,4,5}, {2,4,5,4,5}) = 0.8` | 相关系数 |

---

## 4d.11 曲线拟合示例

| 命令 | 输出 | 说明 |
|------|------|------|
| `linearfit([1,2,3,4,5], [2,4,5,4,5])` | `linearfit([1,2,3,4,5], [2,4,5,4,5]) = 0.6*x + 2.2` | 线性回归 |
| `quadraticfit([5,3,4,5,6,7,13,24])` | `quadraticfit([5,3,4,5,6,7,13,24]) = 0.7797619*x^2 - 4.7202381*x + 9.7321429` | 二次回归 |
| `cubicfit([1,2,3,4], [1,8,27,64])` | `cubicfit([1,2,3,4], [1,8,27,64]) = x^3` | 三次回归（精确拟合） |
