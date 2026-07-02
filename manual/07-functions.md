# 第7章 内置函数

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalculate/builtin_functions.py` (3817 行)

---

## 7.1 函数概览

PyQalculate 提供 **159+** 内置数学函数，注册在 `FunctionRegistry` 中 [来源: builtin_functions.py:3487-3800]

---

## 7.2 三角函数 (14 个)

[来源: builtin_functions.py:473-670]

| 函数 | 说明 | 示例 |
|------|------|------|
| `sin(x)` | 正弦 | `sin(pi/2)` → 1 |
| `cos(x)` | 余弦 | `cos(0)` → 1 |
| `tan(x)` | 正切 | `tan(pi/4)` → 1 |
| `asin(x)` | 反正弦 | `asin(1)` → π/2 |
| `acos(x)` | 反余弦 | `acos(1)` → 0 |
| `atan(x)` | 反正切 | `atan(1)` → π/4 |
| `atan2(y, x)` | 四象限反正切 | `atan2(1, 1)` → π/4 |
| `sinh(x)` | 双曲正弦 | `sinh(0)` → 0 |
| `cosh(x)` | 双曲余弦 | `cosh(0)` → 1 |
| `tanh(x)` | 双曲正切 | `tanh(0)` → 0 |
| `asinh(x)` | 反双曲正弦 | `asinh(0)` → 0 |
| `acosh(x)` | 反双曲余弦 | `acosh(1)` → 0 |
| `atanh(x)` | 反双曲正切 | `atanh(0)` → 0 |
| `sinc(x)` | sinc 函数 | `sinc(0)` → 1 |

---

## 7.3 指数/对数函数 (13 个)

[来源: builtin_functions.py:678-916]

| 函数 | 说明 | 示例 |
|------|------|------|
| `exp(x)` | 指数函数 e^x | `exp(1)` → e |
| `ln(x)` | 自然对数 | `ln(e)` → 1 |
| `log2(x)` | 以 2 为底的对数 | `log2(8)` → 3 |
| `log10(x)` | 以 10 为底的对数 | `log10(100)` → 2 |
| `logn(x, n)` | 以 n 为底的对数 | `logn(8, 2)` → 3 |
| `exp2(x)` | 2^x | `exp2(3)` → 8 |
| `exp10(x)` | 10^x | `exp10(2)` → 100 |
| `sqrt(x)` | 平方根 | `sqrt(4)` → 2 |
| `cbrt(x)` | 立方根 | `cbrt(8)` → 2 |
| `root(x, n)` | n 次根 | `root(8, 3)` → 2 |
| `square(x)` | 平方 | `square(3)` → 9 |
| `lambertw(x)` | Lambert W 函数 | `lambertw(0)` → 0 |
| `cis(x)` | cis 函数 | `cis(pi)` → -1 |

---

## 7.4 组合数学 (5 个)

[来源: builtin_functions.py:924-1016]

| 函数 | 说明 | 示例 |
|------|------|------|
| `factorial(n)` | 阶乘 | `factorial(5)` → 120 |
| `double_factorial(n)` | 双阶乘 | `double_factorial(5)` → 15 |
| `multinomial(...)` | 多项式系数 | `multinomial(6, 2, 4)` → 3150 |
| `binomial(n, k)` | 二项式系数 | `binomial(5, 2)` → 10 |
| `gamma(x)` | Gamma 函数 | `gamma(5)` → 24 |

---

## 7.5 数论函数 (27 个)

[来源: builtin_functions.py:1024-1477]

| 函数 | 说明 | 示例 |
|------|------|------|
| `abs(x)` | 绝对值 | `abs(-5)` → 5 |
| `signum(x)` | 符号函数 | `signum(-3)` → -1 |
| `round(x)` | 四舍五入 | `round(3.7)` → 4 |
| `floor(x)` | 向下取整 | `floor(3.7)` → 3 |
| `ceil(x)` | 向上取整 | `ceil(3.2)` → 4 |
| `trunc(x)` | 截断 | `trunc(3.7)` → 3 |
| `gcd(a, b)` | 最大公约数 | `gcd(12, 8)` → 4 |
| `lcm(a, b)` | 最小公倍数 | `lcm(12, 8)` → 24 |
| `mod(a, b)` | 取模 | `mod(7, 3)` → 1 |
| `rem(a, b)` | 取余 | `rem(7, 3)` → 1 |
| `is_prime(n)` | 是否为素数 | `is_prime(7)` → 1 |
| `next_prime(n)` | 下一个素数 | `next_prime(7)` → 11 |
| `prev_prime(n)` | 上一个素数 | `prev_prime(7)` → 5 |
| `nth_prime(n)` | 第 n 个素数 | `nth_prime(5)` → 11 |
| `prime_count(n)` | 不超过 n 的素数个数 | `prime_count(10)` → 4 |
| `numerator(x)` | 分子 | `numerator(3/4)` → 3 |
| `denominator(x)` | 分母 | `denominator(3/4)` → 4 |
| `int(x)` | 整数部分 | `int(3.7)` → 3 |
| `frac(x)` | 小数部分 | `frac(3.7)` → 0.7 |
| `totient(n)` | Euler totient 函数 | `totient(9)` → 6 |
| `bernoulli(n)` | Bernoulli 数 | `bernoulli(2)` → 1/6 |
| `re(z)` | 实部 | `re(3+4i)` → 3 |
| `im(z)` | 虚部 | `im(3+4i)` → 4 |
| `arg(z)` | 辐角 | `arg(1+i)` → π/4 |
| `powermod(a, b, m)` | 模幂 | `powermod(2, 10, 1000)` → 24 |
| `parallel(a, b)` | 并联电阻 | `parallel(4, 6)` → 2.4 |
| `interval(a, b)` | 区间 | `interval(1, 5)` |

---

## 7.6 代数函数 (8 个)

[来源: builtin_functions.py:1485-1705]

| 函数 | 说明 | 示例 |
|------|------|------|
| `solve(expr, var)` | 求解方程 | `solve(x^2 - 4, x)` → [-2, 2] |
| `multisolve(expr, vars)` | 多方程求解 | — |
| `dsolve(eq, init)` | 微分方程求解 | — |
| `factor(expr)` | 因式分解 | `factor(x^2 - 4)` → (x-2)(x+2) |
| `expand(expr)` | 展开 | `expand((x+1)^2)` → x²+2x+1 |
| `coeff(expr, var, n)` | 提取系数 | `coeff(x^2+2x+1, x, 1)` → 2 |
| `degree(expr, var)` | 多项式次数 | `degree(x^3+1, x)` → 3 |
| `roots(expr)` | 求根 | `roots(x^2 - 4)` → [-2, 2] |

---

## 7.7 微积分函数 (5 个)

[来源: builtin_functions.py:1713-1918]

| 函数 | 说明 | 示例 |
|------|------|------|
| `diff(expr, var)` | 求导 | `diff(x^2, x)` → 2x |
| `integrate(expr, var)` | 不定积分 | `integrate(x^2, x)` → x³/3 |
| `integrate(expr, var, a, b)` | 定积分 | `integrate(x^2, x, 0, 1)` → 1/3 |
| `limit(expr, var, val)` | 极限 | `limit(sin(x)/x, x, 0)` → 1 |
| `sum(expr, var, lo, hi)` | 求和 | `sum(x, x, 1, 10)` → 55 |
| `product(expr, var, lo, hi)` | 求积 | `product(x, x, 1, 5)` → 120 |

---

## 7.8 矩阵/向量函数 (15 个)

[来源: builtin_functions.py:1926-2187]

| 函数 | 说明 | 示例 |
|------|------|------|
| `det(M)` | 行列式 | `det([[1,2],[3,4]])` → -2 |
| `inverse(M)` | 逆矩阵 | — |
| `transpose(M)` | 转置 | — |
| `cross(a, b)` | 叉积 | `cross([1,0,0],[0,1,0])` → [0,0,1] |
| `dot(a, b)` | 点积 | `dot([1,2],[3,4])` → 11 |
| `hadamard(a, b)` | Hadamard 积 | — |
| `trace(M)` | 迹 | `trace([[1,2],[3,4]])` → 5 |
| `adj(M)` | 伴随矩阵 | — |
| `cofactor(M, i, j)` | 余子式 | — |
| `rref(M)` | 行最简形 | — |
| `rank(M)` | 秩 | — |
| `norm(v)` | 范数 | `norm([3,4])` → 5 |
| `eigenvalues(M)` | 特征值 | — |
| `identity(n)` | 单位矩阵 | `identity(3)` → 3×3 单位矩阵 |
| `magnitude(v)` | 模 | `magnitude([3,4])` → 5 |

---

## 7.9 统计函数 (13 个)

[来源: builtin_functions.py:2195-2447]

| 函数 | 说明 | 示例 |
|------|------|------|
| `mean(...)` | 平均值 | `mean(1,2,3,4,5)` → 3 |
| `stdev(...)` | 标准差 | — |
| `variance(...)` | 方差 | — |
| `median(...)` | 中位数 | `median(1,2,3,4,5)` → 3 |
| `mode(...)` | 众数 | — |
| `percentile(..., p)` | 百分位数 | — |
| `quartile(..., q)` | 四分位数 | — |
| `normdist(x, mu, sigma)` | 正态分布 | — |
| `min(...)` | 最小值 | `min(3,1,4)` → 1 |
| `max(...)` | 最大值 | `max(3,1,4)` → 4 |
| `rand()` | 随机数 | `rand()` → [0,1) |
| `correlation(x, y)` | 相关系数 | — |
| `covariance(x, y)` | 协方差 | — |

---

## 7.10 回归函数 (3 个)

[来源: builtin_functions.py:3700-3800]

`linearfit`、`quadraticfit`、`cubicfit` 提供最小二乘多项式曲线拟合。所有函数接受向量参数，返回以 x 表示的多项式。

| 函数 | 说明 | 示例 | 最少数据点 |
|------|------|------|------------|
| `linearfit(x, y)` | 线性回归 | `linearfit([1,2,3], [2,4,6])` → `2*x` | 2 |
| `quadraticfit(x, y)` | 二次回归 | `quadraticfit([5,3,4,5,6,7,13,24])` → `0.78*x² - 4.72*x + 9.73` | 3 |
| `cubicfit(x, y)` | 三次回归 | `cubicfit([5,3,4,5,6,7,13,24])` → `0.149*x³ - 1.23*x² + 2.95*x + 2.36` | 4 |

**使用方式**:
- 单参数：`linearfit([y1, y2, ...])` — x 自动取 1, 2, ..., n
- 双参数：`linearfit([x1, x2, ...], [y1, y2, ...])` — 显式指定 x 和 y
- 点数不足或不等长时返回 `undefined`

---

## 7.11 进制转换函数 (8 个)

[来源: builtin_functions.py:2455-2676]

| 函数 | 说明 | 示例 |
|------|------|------|
| `bin(x)` | 二进制 | `bin(255)` → "0b11111111" |
| `oct(x)` | 八进制 | `oct(255)` → "0o377" |
| `hex(x)` | 十六进制 | `hex(255)` → "0xFF" |
| `base(x, n)` | n 进制 | `base(255, 16)` → "FF" |
| `roman(x)` | 罗马数字 | `roman(2024)` → "MMXXIV" |
| `float(x)` | 浮点表示 | — |
| `floaterror(x)` | 浮点误差 | — |
| `bases(x)` | 所有进制 | — |

---

## 7.12 日期时间函数 (10 个)

[来源: builtin_functions.py:2684-2838]

| 函数 | 说明 | 示例 |
|------|------|------|
| `date(year, month, day)` | 创建日期 | `date(2024, 1, 1)` |
| `timestamp(date)` | 时间戳 | — |
| `stamptodate(ts)` | 时间戳转日期 | — |
| `days(date1, date2)` | 天数差 | — |
| `weeks(date1, date2)` | 周数差 | — |
| `months(date1, date2)` | 月数差 | — |
| `years(date1, date2)` | 年数差 | — |
| `now()` | 当前时间 | — |
| `today()` | 今天 | — |
| `lunarphase(date)` | 月相 | — |

---

## 7.13 特殊函数 (12 个)

[来源: builtin_functions.py:2840-3037]

| 函数 | 说明 | 示例 |
|------|------|------|
| `zeta(s)` | Riemann zeta 函数 | `zeta(2)` → π²/6 |
| `beta(a, b)` | Beta 函数 | — |
| `erf(x)` | 误差函数 | `erf(1)` → 0.8427... |
| `erfc(x)` | 互补误差函数 | — |
| `besselj(n, x)` | Bessel J 函数 | — |
| `bessely(n, x)` | Bessel Y 函数 | — |
| `airy(x)` | Airy 函数 | — |
| `fresnels(x)` | Fresnel S 函数 | — |
| `fresnelc(x)` | Fresnel C 函数 | — |
| `digamma(x)` | Digamma 函数 | — |
| `heaviside(x)` | 阶跃函数 | — |
| `dirac(x)` | Delta 函数 | — |

---

## 7.14 逻辑/位运算函数 (9 个)

[来源: builtin_functions.py:3040-3173]

| 函数 | 说明 | 示例 |
|------|------|------|
| `bitand(a, b)` | 按位与 | `bitand(0xFF, 0x0F)` → 15 |
| `bitor(a, b)` | 按位或 | — |
| `bitxor(a, b)` | 按位异或 | — |
| `bitnot(x)` | 按位取反 | — |
| `shift(x, n)` | 移位 | `shift(1, 8)` → 256 |
| `and(a, b)` | 逻辑与 | — |
| `or(a, b)` | 逻辑或 | — |
| `xor(a, b)` | 逻辑异或 | — |
| `not(x)` | 逻辑非 | — |

---

## 7.15 工具函数 (14 个)

[来源: builtin_functions.py:3176-3479]

| 函数 | 说明 | 示例 |
|------|------|------|
| `if(cond, then, else)` | 条件 | `if(1>0, 1, 0)` → 1 |
| `for(init, cond, step, expr)` | 循环 | — |
| `genvector(size, expr)` | 生成向量 | — |
| `load(file)` | 加载文件 | — |
| `export(expr, file)` | 导出 | — |
| `replace(str, old, new)` | 字符串替换 | — |
| `tostring(expr)` | 转字符串 | — |
| `length(str)` | 字符串长度 | — |
| `concatenate(...)` | 字符串连接 | — |
| `is_number(x)` | 是否为数字 | — |
| `is_real(x)` | 是否为实数 | — |
| `is_rational(x)` | 是否为有理数 | — |
| `is_integer(x)` | 是否为整数 | — |
| `odd(n)` / `even(n)` | 奇偶性 | — |
| `plot(expr, file)` | 绘图 | — |
