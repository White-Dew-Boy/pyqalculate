# 第4b章 内置函数完整参考

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalculate/builtin_functions.py` (3817 行)

---

## 4b.1 三角函数 (14 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `sin(x)` | `sin(x)` | 正弦 | `sin(pi/2)` | `1` |
| `cos(x)` | `cos(x)` | 余弦 | `cos(0)` | `1` |
| `tan(x)` | `tan(x)` | 正切 | `tan(pi/4)` | `1` |
| `asin(x)` | `asin(x)` | 反正弦 | `asin(1)` | `1/2 * pi` |
| `acos(x)` | `acos(x)` | 反余弦 | `acos(1)` | `0` |
| `atan(x)` | `atan(x)` | 反正切 | `atan(1)` | `1/4 * pi` |
| `atan2(y, x)` | `atan2(y, x)` | 四象限反正切 | `atan2(1, 1)` | `1/4 * pi` |
| `sinh(x)` | `sinh(x)` | 双曲正弦 | `sinh(0)` | `0` |
| `cosh(x)` | `cosh(x)` | 双曲余弦 | `cosh(0)` | `1` |
| `tanh(x)` | `tanh(x)` | 双曲正切 | `tanh(0)` | `0` |
| `asinh(x)` | `asinh(x)` | 反双曲正弦 | `asinh(0)` | `0` |
| `acosh(x)` | `acosh(x)` | 反双曲余弦 | `acosh(1)` | `0` |
| `atanh(x)` | `atanh(x)` | 反双曲正切 | `atanh(0)` | `0` |
| `sinc(x)` | `sinc(x)` | sinc 函数 | `sinc(0)` | `1` |

[来源: builtin_functions.py:473-670]

---

## 4b.2 指数/对数函数 (13 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `exp(x)` | `exp(x)` | 指数函数 e^x | `exp(1)` | `e` |
| `ln(x)` | `ln(x)` | 自然对数 | `ln(e)` | `1` |
| `log2(x)` | `log2(x)` | 以 2 为底的对数 | `log2(8)` | `3` |
| `log10(x)` | `log10(x)` | 以 10 为底的对数 | `log10(100)` | `2` |
| `logn(x, n)` | `logn(x, n)` | 以 n 为底的对数 | `logn(8, 2)` | `3` |
| `exp2(x)` | `exp2(x)` | 2^x | `exp2(3)` | `8` |
| `exp10(x)` | `exp10(x)` | 10^x | `exp10(2)` | `100` |
| `sqrt(x)` | `sqrt(x)` | 平方根 | `sqrt(4)` | `2` |
| `cbrt(x)` | `cbrt(x)` | 立方根 | `cbrt(8)` | `2` |
| `root(x, n)` | `root(x, n)` | n 次根 | `root(8, 3)` | `2` |
| `square(x)` | `square(x)` | 平方 | `square(3)` | `9` |
| `lambertw(x)` | `lambertw(x)` | Lambert W 函数 | `lambertw(0)` | `0` |
| `cis(x)` | `cis(x)` | cis 函数 | `cis(pi)` | `-1` |

[来源: builtin_functions.py:678-916]

---

## 4b.3 组合数学 (5 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `factorial(n)` | `n!` 或 `factorial(n)` | 阶乘 | `5!` | `120` |
| `double_factorial(n)` | `double_factorial(n)` | 双阶乘 | `double_factorial(5)` | `15` |
| `multinomial(...)` | `multinomial(n1, n2, ...)` | 多项式系数 | `multinomial(6, 2, 4)` | `13860` |
| `binomial(n, k)` | `binomial(n, k)` | 二项式系数 | `binomial(5, 2)` | `10` |
| `gamma(x)` | `gamma(x)` | Gamma 函数 | `gamma(5)` | `24` |

[来源: builtin_functions.py:924-1016]

---

## 4b.4 数论函数 (28 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `abs(x)` | `abs(x)` | 绝对值 | `abs(-5)` | `5` |
| `signum(x)` | `signum(x)` | 符号函数 | `signum(-3)` | `-1` |
| `round(x)` | `round(x)` | 四舍五入（支持符号参数） | `round(3.7)` | `4` |
| `floor(x)` | `floor(x)` | 向下取整 | `floor(3.7)` | `3` |
| `ceil(x)` | `ceil(x)` | 向上取整 | `ceil(3.2)` | `4` |
| `trunc(x)` | `trunc(x)` | 截断（支持符号参数） | `trunc(3.7)` | `3` |
| `gcd(a, b)` | `gcd(a, b)` | 最大公约数 | `gcd(12, 8)` | `4` |
| `lcm(a, b)` | `lcm(a, b)` | 最小公倍数 | `lcm(12, 8)` | `24` |
| `mod(a, b)` | `mod(a, b)` | 取模 | `mod(7, 3)` | `1` |
| `rem(a, b)` | `rem(a, b)` | 取余 | `rem(7, 3)` | `1` |
| `is_prime(n)` | `is_prime(n)` | 是否为素数 | `is_prime(7)` | `1` |
| `next_prime(n)` | `next_prime(n)` | 下一个素数 | `next_prime(7)` | `11` |
| `prev_prime(n)` | `prev_prime(n)` | 上一个素数 | `prev_prime(7)` | `5` |
| `nth_prime(n)` | `nth_prime(n)` | 第 n 个素数 | `nth_prime(5)` | `11` |
| `prime_count(n)` | `prime_count(n)` | 不超过 n 的素数个数 | `prime_count(10)` | `4` |
| `numerator(x)` | `numerator(x)` | 分子 | `numerator(3/4)` | `3` |
| `denominator(x)` | `denominator(x)` | 分母 | `denominator(3/4)` | `4` |
| `int(x)` | `int(x)` | 整数部分 | `int(3.7)` | `3` |
| `frac(x)` | `frac(x)` | 小数部分 | `frac(3.7)` | `0.7` |
| `totient(n)` | `totient(n)` | Euler totient 函数 | `totient(9)` | `6` |
| `bernoulli(n)` | `bernoulli(n)` | Bernoulli 数 | `bernoulli(2)` | `1/6` |
| `re(z)` | `re(z)` | 实部 | `re(3+4i)` | `3` |
| `im(z)` | `im(z)` | 虚部 | `im(3+4i)` | `4` |
| `arg(z)` | `arg(z)` | 辐角 | `arg(1+i)` | `1/4 * pi` |
| `powermod(a, b, m)` | `powermod(a, b, m)` | 模幂 | `powermod(2, 10, 1000)` | `24` |
| `parallel(a, b)` | `parallel(a, b)` | 并联电阻（零值返回 infinity） | `parallel(4, 6)` | `12/5` |
| `interval(a, b)` | `interval(a, b)` | 区间 | `interval(1, 5)` | `[1, 5]` |
| `uncertainty(v, u)` | `uncertainty(v, u)` | 不确定度 | `uncertainty(5, 0.1)` | `5±0.1` |

[来源: builtin_functions.py:1024-1477]

---

## 4b.5 代数函数 (8 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `solve(expr, var)` | `solve(expr, var)` | 求解方程 | `solve(x^2 - 4, x)` | `(-2, 2)` |
| `multisolve(expr, vars)` | `multisolve(expr, vars)` | 多方程求解 | — | — |
| `dsolve(eq, init)` | `dsolve(eq, init)` | 微分方程求解 | — | — |
| `factor(expr)` | `factor(expr)` | 因式分解 | `factor(x^2 - 4)` | `(-2 + x) * (2 + x)` |
| `expand(expr)` | `expand(expr)` | 展开 | `expand((x+1)^2)` | `1 + 2*x + x^2` |
| `coeff(expr, var, n)` | `coeff(expr, var, n)` | 提取系数 | `coeff(x^2+2x+1, x, 1)` | `2` |
| `degree(expr, var)` | `degree(expr, var)` | 多项式次数 | `degree(x^3+1, x)` | `3` |
| `roots(expr)` | `roots(expr)` | 求根 | `roots(x^2 - 4)` | `(-2, 2)` |

[来源: builtin_functions.py:1485-1705]

---

## 4b.6 微积分函数 (6 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `diff(expr, var)` | `diff(expr, var)` | 求导 | `diff(x^2, x)` | `2 * x` |
| `integrate(expr, var)` | `integrate(expr, var)` | 不定积分 | `integrate(x^2, x)` | `1/3 * (x)^(3) + C` |
| `integrate(expr, var, a, b)` | `integrate(expr, var, a, b)` | 定积分 | `integrate(x^2, x, 0, 1)` | `1/3` |
| `limit(expr, var, val)` | `limit(expr, var, val)` | 极限 | `limit(sin(x)/x, x, 0)` | `1` |
| `sum(expr, var, lo, hi)` | `sum(expr, var, lo, hi)` | 求和 | `sum(x, x, 1, 10)` | `55` |
| `product(expr, var, lo, hi)` | `product(expr, var, lo, hi)` | 求积 | `product(x, x, 1, 5)` | `120` |

[来源: builtin_functions.py:1713-1918]

---

## 4b.7 矩阵/向量函数 (15 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `det(M)` | `det(M)` | 行列式 | `det([1,2;3,4])` | `-2` |
| `inverse(M)` | `inverse(M)` | 逆矩阵 | — | — |
| `transpose(M)` | `transpose(M)` | 转置 | — | — |
| `cross(a, b)` | `cross(a, b)` | 叉积 | `cross([1,0,0], [0,1,0])` | `[0, 0, 1]` |
| `dot(a, b)` | `dot(a, b)` | 点积 | `dot([1,2], [3,4])` | `11` |
| `hadamard(a, b)` | `hadamard(a, b)` | Hadamard 积 | — | — |
| `trace(M)` | `trace(M)` | 迹 | `trace([1,2;3,4])` | `5` |
| `adj(M)` | `adj(M)` | 伴随矩阵 | — | — |
| `cofactor(M, i, j)` | `cofactor(M, i, j)` | 余子式 | — | — |
| `rref(M)` | `rref(M)` | 行最简形 | — | — |
| `rank(M)` | `rank(M)` | 秩 | — | — |
| `norm(v)` | `norm(v)` | 范数 | `norm([3,4])` | `5` |
| `eigenvalues(M)` | `eigenvalues(M)` | 特征值 | — | — |
| `identity(n)` | `identity(n)` | 单位矩阵 | `identity(3)` | 3×3 单位矩阵 |
| `magnitude(v)` | `magnitude(v)` | 模 | `magnitude([3,4])` | `5` |

[来源: builtin_functions.py:1926-2187]

---

## 4b.8 统计函数 (13 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `mean(...)` | `mean(...)` | 平均值 | `mean(1,2,3,4,5)` | `3` |
| `stdev(...)` | `stdev(...)` | 标准差 | — | — |
| `variance(...)` | `variance(...)` | 方差 | — | — |
| `median(...)` | `median(...)` | 中位数 | `median(1,2,3,4,5)` | `3` |
| `mode(...)` | `mode(...)` | 众数 | — | — |
| `percentile(v, p)` | `percentile(v, p)` | 百分位数 | — | — |
| `quartile(v, q)` | `quartile(v, q)` | 四分位数 | — | — |
| `normdist(x, mu, sigma)` | `normdist(x, mu, sigma)` | 正态分布 | — | — |
| `min(...)` | `min(...)` | 最小值 | `min(3,1,4)` | `1` |
| `max(...)` | `max(...)` | 最大值 | `max(3,1,4)` | `4` |
| `rand()` | `rand()` | 随机数 | `rand()` | `[0,1)` |
| `correlation(x, y)` | `correlation(x, y)` | 相关系数 | — | — |
| `covariance(x, y)` | `covariance(x, y)` | 协方差 | — | — |

[来源: builtin_functions.py:2195-2447]

---

## 4b.9 进制转换函数 (8 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `bin(x)` | `bin(x)` | 二进制 | `bin(255)` | `1111 1111` |
| `oct(x)` | `oct(x)` | 八进制 | `oct(255)` | `0o377` |
| `hex(x)` | `hex(x)` | 十六进制 | `hex(255)` | `0xFF` |
| `base(x, n)` | `base(x, n)` | n 进制 | `base(255, 16)` | `ff` |
| `roman(x)` | `roman(x)` | 罗马数字 | `roman(1999)` | `MCMXCIX` |
| `float(x)` | `float(x)` | 浮点表示 | — | — |
| `floaterror(x)` | `floaterror(x)` | 浮点误差 | — | — |
| `bases(x)` | `bases(x)` | 所有进制 | `bases(42)` | `0010 1010 = 0o52 = 42 = 0x2A` |

[来源: builtin_functions.py:2455-2676]

---

## 4b.10 日期时间函数 (10 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `date(y, m, d)` | `date(y, m, d)` | 创建日期 | `date(2024, 1, 1)` | `2024-01-01` |
| `timestamp(date)` | `timestamp(date)` | 时间戳 | — | — |
| `stamptodate(ts)` | `stamptodate(ts)` | 时间戳转日期 | — | — |
| `days(d1, d2)` | `days(d1, d2)` | 天数差 | — | — |
| `weeks(d1, d2)` | `weeks(d1, d2)` | 周数差 | — | — |
| `months(d1, d2)` | `months(d1, d2)` | 月数差 | — | — |
| `years(d1, d2)` | `years(d1, d2)` | 年数差 | — | — |
| `now()` | `now` | 当前时间 | — | — |
| `today()` | `today` | 今天 | — | — |
| `lunarphase(date)` | `lunarphase(date)` | 月相 | — | — |

[来源: builtin_functions.py:2684-2838]

---

## 4b.11 特殊函数 (12 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `zeta(s)` | `zeta(s)` | Riemann zeta 函数 | `zeta(2)` | `1/6 * pi^2` |
| `beta(a, b)` | `beta(a, b)` | Beta 函数 | — | — |
| `erf(x)` | `erf(x)` | ⚠️ 误差函数（整数参数返回符号形式） | `erf(1.0)` | `0.8427...` |
| `erfc(x)` | `erfc(x)` | 互补误差函数 | — | — |
| `besselj(n, x)` | `besselj(n, x)` | Bessel J 函数 | — | — |
| `bessely(n, x)` | `bessely(n, x)` | Bessel Y 函数 | — | — |
| `airy(x)` | `airy(x)` | Airy 函数 | — | — |
| `fresnels(x)` | `fresnels(x)` | Fresnel S 函数 | — | — |
| `fresnelc(x)` | `fresnelc(x)` | Fresnel C 函数 | — | — |
| `digamma(x)` | `digamma(x)` | Digamma 函数 | — | — |
| `heaviside(x)` | `heaviside(x)` | 阶跃函数 | — | — |
| `dirac(x)` | `dirac(x)` | Delta 函数 | — | — |

[来源: builtin_functions.py:2840-3037]

---

## 4b.12 逻辑/位运算函数 (9 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `bitand(a, b)` | `bitand(a, b)` | 按位与 | `bitand(0xFF, 0x0F)` | `15` |
| `bitor(a, b)` | `bitor(a, b)` | 按位或 | — | — |
| `bitxor(a, b)` | `bitxor(a, b)` | 按位异或 | — | — |
| `bitnot(x)` | `bitnot(x)` | 按位取反 | — | — |
| `shift(x, n)` | `shift(x, n)` | 移位 | `shift(1, 8)` | `256` |
| `and(a, b)` | `and(a, b)` | 逻辑与 | — | — |
| `or(a, b)` | `or(a, b)` | 逻辑或 | — | — |
| `xor(a, b)` | `xor(a, b)` | 逻辑异或 | — | — |
| `not(x)` | `not(x)` | 逻辑非 | — | — |

[来源: builtin_functions.py:3040-3173]

---

## 4b.13 工具函数 (16 个)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `if(cond, then, else)` | `if(cond, then, else)` | 条件选择 | `if(1>0, 1, 0)` | `1` |
| `for(init, cond, step, expr)` | `for(init, cond, step, expr)` | 循环（支持符号边界） | `for(i:=1, i<=3, i:=i+1, i^2)` | `14` |
| `genvector(size, expr)` | `genvector(size, expr)` | 生成向量 | — | — |
| `load(file)` | `load(file)` | 加载文件 | — | — |
| `export(expr, file)` | `export(expr, file)` | 导出 | — | — |
| `replace(str, old, new)` | `replace(str, old, new)` | 字符串替换 | — | — |
| `tostring(expr)` | `tostring(expr)` | 转字符串 | — | — |
| `length(str)` | `length(str)` | 字符串长度 | — | — |
| `concatenate(...)` | `concatenate(...)` | 字符串连接 | — | — |
| `is_number(x)` | `is_number(x)` | 是否为数字 | — | — |
| `is_real(x)` | `is_real(x)` | 是否为实数 | — | — |
| `is_rational(x)` | `is_rational(x)` | 是否为有理数 | — | — |
| `is_integer(x)` | `is_integer(x)` | 是否为整数 | — | — |
| `odd(n)` / `even(n)` | `odd(n)` / `even(n)` | 奇偶性 | — | — |
| `plot(expr, file)` | `plot(expr, file)` | 绘图 | — | — |

[来源: builtin_functions.py:3176-3479]

---

## 4b.14 已知限制

> **重要**: 本节记录了 SymPy 引擎和内置函数的实际行为边界。

### 4b.14.1 积分限制

| 场景 | 状态 | 说明 |
|------|------|------|
| 多项式积分 | ✅ 完全支持 | `integrate(x^2, x)` → `x³/3 + C` |
| 三角函数积分 | ✅ 大部分支持 | `integrate(sin(x), x)` → `-cos(x)` |
| 有理函数积分 | ✅ 大部分支持 | 部分分式分解 |
| 含符号参数的积分 | ⚠️ 可能失败 | `integrate(x^a, x)` 当 `a` 为符号时 |
| 某些定积分 | ⚠️ 返回未求值 | 特殊函数相关的定积分 |
| 振荡积分 | ⚠️ 有限 | `integrate(sin(x^2), x)` 可能不完整 |

### 4b.14.2 求解器限制

| 场景 | 状态 | 说明 |
|------|------|------|
| 线性方程 | ✅ 完全支持 | 单变量或多变量 |
| 二次方程 | ✅ 完全支持 | 根式解 |
| 高次多项式 | ✅ 大部分支持 | 有解析解时 |
| 超越方程 | ⚠️ 有限 | `sin(x) = 0.5` 可能不完整 |
| 方程组 | ⚠️ 实验性 | `multisolve` 功能有限 |

### 4b.14.3 特殊函数限制

| 函数 | 状态 | 说明 |
|------|------|------|
| `beta(a, b)` | ⚠️ 部分支持 | 数值计算为主 |
| `besselj(n, x)` | ⚠️ 部分支持 | 特定参数有效 |
| `bessely(n, x)` | ⚠️ 部分支持 | 特定参数有效 |
| `airy(x)` | ⚠️ 部分支持 | 特定参数有效 |
| `fresnels(x)` / `fresnelc(x)` | ⚠️ 部分支持 | 数值计算为主 |
| `erf(x)` | ⚠️ 需浮点输入 | `erf(1)` 返回符号形式，需用 `erf(1.0)` 获取数值 |
| `digamma(x)` | ⚠️ 部分支持 | 特定参数有效 |
| `heaviside(x)` | ✅ 基本支持 | 阶跃函数 |
| `dirac(x)` | ⚠️ 有限 | 作为分布函数支持有限 |

### 4b.14.4 统计函数限制

| 函数 | 状态 | 说明 |
|------|------|------|
| `mean(...)` | ✅ 完全支持 | |
| `median(...)` | ✅ 完全支持 | |
| `min(...)` / `max(...)` | ✅ 完全支持 | |
| `stdev(...)` | ⚠️ 未测试 | 样本标准差 |
| `variance(...)` | ⚠️ 未测试 | 样本方差 |
| `mode(...)` | ⚠️ 未测试 | 众数 |
| `percentile(...)` | ⚠️ 未测试 | 百分位数 |
| `quartile(...)` | ⚠️ 未测试 | 四分位数 |
| `normdist(...)` | ⚠️ 未测试 | 正态分布 |
| `correlation(...)` | ⚠️ 未测试 | 相关系数 |
| `covariance(...)` | ⚠️ 未测试 | 协方差 |

### 4b.14.5 矩阵函数限制

| 函数 | 状态 | 说明 |
|------|------|------|
| `det(M)` | ✅ 完全支持 | 行列式 |
| `trace(M)` | ✅ 完全支持 | 迹 |
| `cross(a, b)` | ✅ 完全支持 | 叉积 |
| `dot(a, b)` | ✅ 完全支持 | 点积 |
| `norm(v)` | ✅ 完全支持 | 范数 |
| `magnitude(v)` | ✅ 完全支持 | 模 |
| `identity(n)` | ✅ 完全支持 | 单位矩阵 |
| `inverse(M)` | ⚠️ 未测试 | 逆矩阵 |
| `transpose(M)` | ⚠️ 未测试 | 转置 |
| `adj(M)` | ⚠️ 未测试 | 伴随矩阵 |
| `cofactor(M, i, j)` | ⚠️ 未测试 | 余子式 |
| `rref(M)` | ⚠️ 未测试 | 行最简形 |
| `rank(M)` | ⚠️ 未测试 | 秩 |
| `eigenvalues(M)` | ⚠️ 未测试 | 特征值 |
| `hadamard(a, b)` | ⚠️ 未测试 | Hadamard 积 |

### 4b.14.6 物理常量命名冲突

以下变量名在不同上下文中有不同含义：

| 变量名 | 物理常量含义 | 可能的冲突 |
|--------|-------------|-----------|
| `c` | 光速 (299792458 m/s) | 用户可能赋值为其他值 |
| `alpha` | 精细结构常数 (0.007297...) | 用户可能赋值为其他值 |
| `e` | 自然常数 (2.71828...) | 也可能解析为电荷 |
| `g` | 万有引力常数 (6.6743e-11) | 也可能表示标准重力 |
| `sigma` | 斯特藩-玻尔兹曼常数 | 用户可能赋值为其他值 |
| `R` | 气体常数 (8.314...) | 用户可能赋值为其他值 |

**建议**: 避免使用物理常量名称作为自定义变量名，或使用明确的别名（如 `speed_of_light` 代替 `c`）。

### 4b.14.7 工具函数限制

| 函数 | 状态 | 说明 |
|------|------|------|
| `if(cond, then, else)` | ✅ 支持 | 支持比较条件，如 `if(x>0, 1, 0)` |
| `for(init, cond, step, expr)` | ✅ 支持 | 支持符号边界，返回符号求和 |
| `round(x)` | ✅ 支持 | 支持符号参数 |
| `trunc(x)` | ✅ 支持 | 支持符号参数 |
| `parallel(a, b)` | ✅ 支持 | 零值返回 infinity |
| `genvector(size, expr)` | ⚠️ 未测试 | 生成向量 |
| `load(file)` | ⚠️ 未测试 | 加载文件 |
| `export(expr, file)` | ⚠️ 未测试 | 导出 |
| `replace(str, old, new)` | ⚠️ 未测试 | 字符串替换 |
| `tostring(expr)` | ⚠️ 未测试 | 转字符串 |
| `length(str)` | ⚠️ 未测试 | 字符串长度 |
| `concatenate(...)` | ⚠️ 未测试 | 字符串连接 |
| `is_number(x)` | ⚠️ 未测试 | 是否为数字 |
| `is_real(x)` | ⚠️ 未测试 | 是否为实数 |
| `is_rational(x)` | ⚠️ 未测试 | 是否为有理数 |
| `is_integer(x)` | ⚠️ 未测试 | 是否为整数 |
| `odd(n)` / `even(n)` | ⚠️ 未测试 | 奇偶性 |
| `plot(expr, file)` | ✅ 基本支持 | 绘图 |

---

## 4b.15 信号处理函数 (Signal Processing)

| 函数 | 语法 | 说明 | 示例 | 结果 |
|------|------|------|------|------|
| `fft(向量)` | `fft([x₁, x₂, ...])` | 一维快速傅里叶变换（正向）。输入实数或复数向量，返回复数值向量。长度保持不变。 | `fft([1, 0, 0, 0])` | `[1, 1, 1, 1]` |
| `ifft(向量)` | `ifft([X₁, X₂, ...])` | 一维快速傅里叶逆变换。输入频域复数向量，返回时域复数向量。`ifft(fft(x)) ≈ x`。 | `ifft(fft([1, 2, 3, 4]))` | `[1, 2, 3, 4]` |

**注意事项**:
- `fft` 和 `ifft` 是互逆操作：`ifft(fft(x))` 可精确还原原始信号
- 支持任意长度输入（不要求 2 的幂次），但 2 的幂次长度计算更快
- 输入为纯实数对称序列时，输出为纯实数
- 全零输入的 FFT 结果仍为全零
