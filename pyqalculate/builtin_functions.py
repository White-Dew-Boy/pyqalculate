"""Builtin function registry and all mathematical functions.

Mirrors libqalculate's BuiltinFunctions.h — provides the registry of all
built-in mathematical functions (trig, log, statistics, algebra, calculus,
matrix/vector, combinatorics, special functions, date/time, etc.).
"""

from __future__ import annotations

import datetime
import math
import random
from typing import TYPE_CHECKING

from pyqalculate.function import (
    Argument,
    BooleanArgument,
    DateArgument,
    IntegerArgument,
    MatrixArgument,
    MathFunction,
    NumberArgument,
    SymbolicArgument,
    TextArgument,
    VectorArgument,
)

if TYPE_CHECKING:
    from pyqalculate.math_structure import MathStructure
    from pyqalculate.types import EvaluationOptions


# ============================================================================
# Builtin function IDs (from libqalculate BuiltinFunctions.h)
# ============================================================================

FUNCTION_ID_SQRT = 1200
FUNCTION_ID_CBRT = 1201
FUNCTION_ID_ROOT = 1202
FUNCTION_ID_SQUARE = 1203
FUNCTION_ID_EXP = 1204
FUNCTION_ID_LOG = 1205
FUNCTION_ID_LOGN = 1206
FUNCTION_ID_LAMBERT_W = 1207
FUNCTION_ID_CIS = 1208
FUNCTION_ID_POWER_TOWER = 1209
FUNCTION_ID_ALL_ROOTS = 1210

FUNCTION_ID_SIN = 1300
FUNCTION_ID_COS = 1301
FUNCTION_ID_TAN = 1302
FUNCTION_ID_ASIN = 1303
FUNCTION_ID_ACOS = 1304
FUNCTION_ID_ATAN = 1305
FUNCTION_ID_SINH = 1306
FUNCTION_ID_COSH = 1307
FUNCTION_ID_TANH = 1308
FUNCTION_ID_ASINH = 1309
FUNCTION_ID_ACOSH = 1310
FUNCTION_ID_ATANH = 1311
FUNCTION_ID_SINC = 1312
FUNCTION_ID_ATAN2 = 1313
FUNCTION_ID_RADIANS_TO_DEFAULT_ANGLE_UNIT = 1314

FUNCTION_ID_ZETA = 1400
FUNCTION_ID_GAMMA = 1401
FUNCTION_ID_DIGAMMA = 1402
FUNCTION_ID_BETA = 1403
FUNCTION_ID_AIRY = 1404
FUNCTION_ID_BESSELJ = 1405
FUNCTION_ID_BESSELY = 1406
FUNCTION_ID_ERF = 1407
FUNCTION_ID_ERFI = 1408
FUNCTION_ID_ERFC = 1409
FUNCTION_ID_POLYLOG = 1410
FUNCTION_ID_HEAVISIDE = 1411
FUNCTION_ID_DIRAC = 1412
FUNCTION_ID_ERFINV = 1413

FUNCTION_ID_FACTORIAL = 1500
FUNCTION_ID_DOUBLE_FACTORIAL = 1501
FUNCTION_ID_MULTI_FACTORIAL = 1502
FUNCTION_ID_BINOMIAL = 1503

FUNCTION_ID_LOGINT = 1600
FUNCTION_ID_FRESNEL_S = 1601
FUNCTION_ID_FRESNEL_C = 1602
FUNCTION_ID_EXPINT = 1603
FUNCTION_ID_SININT = 1604
FUNCTION_ID_COSINT = 1605
FUNCTION_ID_SINHINT = 1606
FUNCTION_ID_COSHINT = 1607
FUNCTION_ID_I_GAMMA = 1608
FUNCTION_ID_INCOMPLETE_BETA = 1609
FUNCTION_ID_INVERSE_INCOMPLETE_BETA = 1610

FUNCTION_ID_ABS = 1700
FUNCTION_ID_GCD = 1701
FUNCTION_ID_LCM = 1702
FUNCTION_ID_DIVISORS = 1703
FUNCTION_ID_FACTORS = 1704
FUNCTION_ID_SIGNUM = 1710
FUNCTION_ID_ROUND = 1720
FUNCTION_ID_FLOOR = 1721
FUNCTION_ID_CEIL = 1722
FUNCTION_ID_TRUNC = 1723
FUNCTION_ID_NUMERATOR = 1730
FUNCTION_ID_DENOMINATOR = 1731
FUNCTION_ID_INT = 1732
FUNCTION_ID_FRAC = 1733
FUNCTION_ID_REM = 1734
FUNCTION_ID_MOD = 1735
FUNCTION_ID_PARALLEL = 1736
FUNCTION_ID_POWER_MOD = 1737
FUNCTION_ID_BERNOULLI = 1740
FUNCTION_ID_TOTIENT = 1745
FUNCTION_ID_RE = 1750
FUNCTION_ID_IM = 1751
FUNCTION_ID_ARG = 1752
FUNCTION_ID_PRIME_COUNT = 1760
FUNCTION_ID_NTH_PRIME = 1761
FUNCTION_ID_PREV_PRIME = 1762
FUNCTION_ID_NEXT_PRIME = 1763
FUNCTION_ID_PRIMES = 1764
FUNCTION_ID_IS_PRIME = 1765

FUNCTION_ID_DIFFERENTIATE = 1800
FUNCTION_ID_LIMIT = 1810
FUNCTION_ID_INTEGRATE = 1820
FUNCTION_ID_MONTE_CARLO = 1821
FUNCTION_ID_ROMBERG = 1822
FUNCTION_ID_SUM = 1830
FUNCTION_ID_PRODUCT = 1831
FUNCTION_ID_SOLVE = 1840
FUNCTION_ID_SOLVE_MULTIPLE = 1841
FUNCTION_ID_D_SOLVE = 1842
FUNCTION_ID_NEWTON_RAPHSON = 1850
FUNCTION_ID_SECANT_METHOD = 1851

FUNCTION_ID_BIN = 1900
FUNCTION_ID_OCT = 1901
FUNCTION_ID_DEC = 1902
FUNCTION_ID_HEX = 1903
FUNCTION_ID_BASE = 1904
FUNCTION_ID_ROMAN = 1905
FUNCTION_ID_BIJECTIVE = 1906
FUNCTION_ID_BINARY_DECIMAL = 1907
FUNCTION_ID_IEEE754_FLOAT = 1910
FUNCTION_ID_IEEE754_FLOAT_BITS = 1911
FUNCTION_ID_IEEE754_FLOAT_COMPONENTS = 1912
FUNCTION_ID_IEEE754_FLOAT_VALUE = 1913
FUNCTION_ID_IEEE754_FLOAT_ERROR = 1914
FUNCTION_ID_IS_NUMBER = 1920
FUNCTION_ID_IS_REAL = 1921
FUNCTION_ID_IS_RATIONAL = 1922
FUNCTION_ID_IS_INTEGER = 1923
FUNCTION_ID_ODD = 1924
FUNCTION_ID_EVEN = 1925
FUNCTION_ID_INTEGER_DIGITS = 1930
FUNCTION_ID_DIGIT_GET = 1931
FUNCTION_ID_DIGIT_SET = 1932

FUNCTION_ID_POLYNOMIAL_UNIT = 2000
FUNCTION_ID_POLYNOMIAL_PRIMPART = 2001
FUNCTION_ID_POLYNOMIAL_CONTENT = 2002
FUNCTION_ID_COEFF = 2003
FUNCTION_ID_L_COEFF = 2004
FUNCTION_ID_T_COEFF = 2005
FUNCTION_ID_DEGREE = 2006
FUNCTION_ID_L_DEGREE = 2007

FUNCTION_ID_BIT_XOR = 2100
FUNCTION_ID_XOR = 2101
FUNCTION_ID_BIT_CMP = 2102
FUNCTION_ID_SHIFT = 2103
FUNCTION_ID_CIRCULAR_SHIFT = 2104
FUNCTION_ID_BIT_SET = 2105
FUNCTION_ID_BIT_GET = 2106
FUNCTION_ID_SET_BITS = 2107
FUNCTION_ID_POP_COUNT = 2108

FUNCTION_ID_FOR = 2150
FUNCTION_ID_IF = 2151
FUNCTION_ID_FOREACH = 2152

FUNCTION_ID_TOTAL = 2200
FUNCTION_ID_PERCENTILE = 2201
FUNCTION_ID_MIN = 2202
FUNCTION_ID_MAX = 2203
FUNCTION_ID_MODE = 2204
FUNCTION_ID_RAND = 2220
FUNCTION_ID_RANDN = 2221
FUNCTION_ID_RAND_POISSON = 2222

FUNCTION_ID_DATE = 2300
FUNCTION_ID_DATE_TIME = 2301
FUNCTION_ID_TIME_VALUE = 2302
FUNCTION_ID_TIMESTAMP = 2303
FUNCTION_ID_TIMESTAMP_TO_DATE = 2304
FUNCTION_ID_DAYS = 2305
FUNCTION_ID_YEAR_FRAC = 2306
FUNCTION_ID_WEEK = 2307
FUNCTION_ID_WEEKDAY = 2308
FUNCTION_ID_MONTH = 2309
FUNCTION_ID_DAY = 2310
FUNCTION_ID_YEAR = 2311
FUNCTION_ID_YEARDAY = 2312
FUNCTION_ID_TIME = 2313
FUNCTION_ID_ADD_DAYS = 2320
FUNCTION_ID_ADD_MONTHS = 2321
FUNCTION_ID_ADD_YEARS = 2322
FUNCTION_ID_LUNAR_PHASE = 2350
FUNCTION_ID_NEXT_LUNAR_PHASE = 2351

FUNCTION_ID_INTERVAL = 2400
FUNCTION_ID_UNCERTAINTY = 2401
FUNCTION_ID_LOWER_END_POINT = 2402
FUNCTION_ID_UPPER_END_POINT = 2403
FUNCTION_ID_MID_POINT = 2404

FUNCTION_ID_ASCII = 2500
FUNCTION_ID_CHAR = 2501
FUNCTION_ID_LENGTH = 2502
FUNCTION_ID_CONCATENATE = 2503
FUNCTION_ID_STRING = 2504
FUNCTION_ID_CHARACTERS = 2505

FUNCTION_ID_REPRESENTS_NUMBER = 2600
FUNCTION_ID_REPRESENTS_REAL = 2601
FUNCTION_ID_REPRESENTS_RATIONAL = 2602
FUNCTION_ID_REPRESENTS_INTEGER = 2603
FUNCTION_ID_REPLACE = 2610
FUNCTION_ID_STRIP_UNITS = 2620
FUNCTION_ID_CUSTOM_SUM = 2630
FUNCTION_ID_FUNCTION = 2640
FUNCTION_ID_TITLE = 2650
FUNCTION_ID_ERROR = 2660
FUNCTION_ID_WARNING = 2661
FUNCTION_ID_MESSAGE = 2662
FUNCTION_ID_SAVE = 2670
FUNCTION_ID_REGISTER = 2680
FUNCTION_ID_STACK = 2681
FUNCTION_ID_PLOT = 2690
FUNCTION_ID_COMMAND = 2695

FUNCTION_ID_VECTOR = 1100
FUNCTION_ID_LIMITS = 1101
FUNCTION_ID_RANK = 1102
FUNCTION_ID_SORT = 1103
FUNCTION_ID_COMPONENT = 1104
FUNCTION_ID_DIMENSION = 1105
FUNCTION_ID_MATRIX = 1106
FUNCTION_ID_MERGE_VECTORS = 1107
FUNCTION_ID_MATRIX_TO_VECTOR = 1108
FUNCTION_ID_AREA = 1109
FUNCTION_ID_ROWS = 1110
FUNCTION_ID_COLUMNS = 1111
FUNCTION_ID_ROW = 1112
FUNCTION_ID_COLUMN = 1113
FUNCTION_ID_ELEMENTS = 1114
FUNCTION_ID_ELEMENT = 1115
FUNCTION_ID_TRANSPOSE = 1116
FUNCTION_ID_IDENTITY = 1117
FUNCTION_ID_DETERMINANT = 1118
FUNCTION_ID_PERMANENT = 1119
FUNCTION_ID_ADJOINT = 1120
FUNCTION_ID_COFACTOR = 1121
FUNCTION_ID_INVERSE = 1122
FUNCTION_ID_MAGNITUDE = 1123
FUNCTION_ID_ENTRYWISE = 1125
FUNCTION_ID_LOAD = 1126
FUNCTION_ID_EXPORT = 1127
FUNCTION_ID_GENERATE_VECTOR = 1128
FUNCTION_ID_SELECT = 1129
FUNCTION_ID_PROCESS = 1130
FUNCTION_ID_PROCESS_MATRIX = 1131
FUNCTION_ID_RREF = 1132
FUNCTION_ID_MATRIX_RANK = 1133
FUNCTION_ID_DOT_PRODUCT = 1134
FUNCTION_ID_ENTRYWISE_MULTIPLICATION = 1135
FUNCTION_ID_ENTRYWISE_DIVISION = 1136
FUNCTION_ID_ENTRYWISE_POWER = 1137
FUNCTION_ID_NORM = 1138
FUNCTION_ID_VERTCAT = 1139
FUNCTION_ID_HORZCAT = 1140
FUNCTION_ID_KRONECKER_PRODUCT = 1141
FUNCTION_ID_COLON = 1142
FUNCTION_ID_FLIP = 1143
FUNCTION_ID_REPLACE_PART = 1144
FUNCTION_ID_CIRCSHIFT = 1145
FUNCTION_ID_RESHAPE = 1146
FUNCTION_ID_FIND = 1147
FUNCTION_ID_INTERSECT = 1190
FUNCTION_ID_SET_DIFFERENCE = 1191
FUNCTION_ID_UNIQUE = 1192
FUNCTION_ID_COUNT = 1193
FUNCTION_ID_IS_MEMBER = 1194
FUNCTION_ID_UNION = 1195
FUNCTION_ID_IS_SUBSET = 1196

FUNCTION_ID_GEO_DISTANCE = 2700
FUNCTION_ID_LATEX = 2705

# Signal Processing
FUNCTION_ID_FFT = 2800
FUNCTION_ID_IFFT = 2801


# ============================================================================
# Helper utilities
# ============================================================================


def _ms(val) -> "MathStructure":
    """Shorthand to create a MathStructure from int/float/Number."""
    from pyqalculate.math_structure import MathStructure
    from pyqalculate.number import Number
    if isinstance(val, MathStructure):
        return val
    if isinstance(val, Number):
        return MathStructure.from_number(val)
    return MathStructure(val)


def _num(val) -> "Number":
    """Shorthand to create a Number."""
    from pyqalculate.number import Number
    if isinstance(val, Number):
        return val
    if isinstance(val, complex):
        return Number.complex(val.real, val.imag)
    return Number(val)


def _undef() -> "MathStructure":
    """Return undefined MathStructure."""
    from pyqalculate.math_structure import MathStructure
    return MathStructure.undefined()


def _is_num(s: "MathStructure") -> bool:
    return s.is_number()


def _float_val(s: "MathStructure") -> float:
    return s.float_value()


def _int_val(s: "MathStructure") -> int:
    if s.number is not None:
        return s.number.to_int()
    return int(s.float_value()) if s.is_number() else 0


def _try_sympy(func_name: str, vargs) -> "MathStructure | None":
    """Try to evaluate via SymPy function map. Returns MathStructure or None."""
    from pyqalculate.math_structure import MathStructure, _SYMPY_FUNC_MAP
    import sympy as sp
    try:
        sp_func = _SYMPY_FUNC_MAP.get(func_name)
        if sp_func is None:
            return None
        sympy_args = [v.to_sympy() for v in vargs]
        result = sp_func(*sympy_args)
        result = sp.N(result, 15)
        return MathStructure.from_sympy(result)
    except Exception:
        return None


def _propagate_plusminus(num, func, deriv_abs):
    """Propagate a ±-interval through a function using derivative-based error propagation.

    For f(x ± δx) ≈ f(x) ± |f'(x)| * δx.

    Args:
        num: Number with plusminus flag set.
        func: The function to apply (e.g., math.sin).
        deriv_abs: Function that returns |f'(x)| given x (e.g., lambda x: abs(math.cos(x))).

    Returns:
        MathStructure with the result as a ±-interval.
    """
    from pyqalculate.number import Number
    mid = num.midpoint_value()
    unc = num.uncertainty_value()
    import math as _math
    new_mid = func(mid)
    new_unc = deriv_abs(mid) * unc
    result_num = Number.from_plusminus(new_mid, new_unc)
    return _ms(result_num)


def _vector_to_list(m: "MathStructure") -> list:
    """Convert vector MathStructure to list of MathStructures."""
    if m.is_vector():
        return list(m)
    return [m]


def _to_sympy_symbol(m: "MathStructure"):
    """Convert a MathStructure to a SymPy Symbol, handling UNIT types.

    Units like 'N' (Newton) should be treated as symbolic variables
    when used as calculus variable arguments.
    """
    import sympy as sp
    from pyqalculate.types import StructureType as ST
    if m._type == ST.UNIT and m._unit is not None:
        return sp.Symbol(m._unit.name())
    if m._type == ST.VARIABLE and m._variable is not None:
        return sp.Symbol(m._variable.name())
    if m._type == ST.SYMBOLIC:
        return sp.Symbol(m._symbol)
    s = str(m)
    return sp.Symbol(s)


def _extract_float_list(m: "MathStructure") -> list[float]:
    """Extract a list of float values from a vector, column matrix, or single number."""
    if m.is_vector():
        return [_float_val(c) for c in m if _is_num(c)]
    if m.is_matrix():
        # Flatten column matrix to list (e.g. [1;2;3] → [1,2,3])
        vals = []
        for row in m:
            if row.is_vector():
                for c in row:
                    if _is_num(c):
                        vals.append(_float_val(c))
            elif _is_num(row):
                vals.append(_float_val(row))
        return vals
    if _is_num(m):
        return [_float_val(m)]
    return []


def _extract_complex_list(m: "MathStructure") -> list[complex]:
    """Extract list of complex values from a vector of NUMBER or Addition-tree (real+imag*i) children."""
    import math
    from pyqalculate.types import StructureType
    result: list[complex] = []
    children = list(m) if m.is_vector() else [m]
    for c in children:
        if c.is_number():
            result.append(complex(_float_val(c), 0))
        elif c.type == StructureType.ADDITION and len(c) == 2:
            real_child = c[0]
            mult_child = c[1]
            if (real_child.is_number() and
                mult_child.type == StructureType.MULTIPLICATION and
                len(mult_child) == 2 and
                mult_child[1].is_symbolic() and mult_child[1].symbol == "i"):
                real_val = _float_val(real_child)
                imag_val = _float_val(mult_child[0])
                result.append(complex(real_val, imag_val))
            else:
                continue
        else:
            continue
    return result


def _ndarray_to_mstruct(arr) -> "MathStructure":
    """Convert numpy array to MathStructure."""
    from pyqalculate.math_structure import MathStructure
    if arr.ndim == 1:
        return MathStructure.vector(*[MathStructure(float(x)) for x in arr])
    elif arr.ndim == 2:
        rows = []
        for row in arr:
            rows.append(MathStructure.vector(*[MathStructure(float(x)) for x in row]))
        return MathStructure.matrix(rows)
    return _undef()


def _ndarray_to_mstruct_complex(arr) -> "MathStructure":
    """Convert complex numpy array to MathStructure.

    For 1D arrays, each element becomes:
    - If imag part is ~0 (abs < 1e-15): plain real MathStructure
    - Otherwise: Addition(real, Multiplication(imag, Symbol('i')))

    For 2D+ arrays: returns undefined.
    """
    import numpy as np
    from pyqalculate.math_structure import MathStructure
    from pyqalculate.number import Number

    if arr.ndim == 1:
        elements: list[MathStructure] = []
        for val in arr:
            if abs(val.imag) < 1e-15:
                elements.append(MathStructure.from_number(Number.from_float(val.real)))
            else:
                real_part = MathStructure.from_number(Number.from_float(val.real))
                imag_part = MathStructure.from_number(Number.from_float(val.imag))
                imag_i = MathStructure.multiplication(imag_part, MathStructure.from_symbol("i"))
                elements.append(MathStructure.addition(real_part, imag_i))
        return MathStructure.vector(*elements)
    return _undef()


def _mstruct_to_ndarray(m: "MathStructure"):
    """Convert MathStructure matrix to numpy array."""
    import numpy as np
    if m.is_matrix():
        rows = []
        for row in m:
            if row.is_vector():
                rows.append([_float_val(c) for c in row])
            else:
                rows.append([_float_val(row)])
        return np.array(rows)
    if m.is_vector():
        # Check if it's a vector of vectors (matrix)
        if len(m) > 0 and all(c.is_vector() for c in m):
            rows = []
            for row in m:
                rows.append([_float_val(c) for c in row])
            return np.array(rows)
        return np.array([_float_val(c) for c in m])
    return np.array([[_float_val(m)]])


# ============================================================================
# 1. TRIGONOMETRIC FUNCTIONS
# ============================================================================


class SinFunction(MathFunction):
    """Sine: sin(x)."""
    def __init__(self):
        super().__init__("sin", 1, 1, "Trigonometry", "Sine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SIN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            num = vargs[0].number
            if num is not None and num.is_interval():
                return _propagate_plusminus(num, math.sin, lambda x: abs(math.cos(x)))
            return _ms(_num(math.sin(_float_val(vargs[0]))))
        return _try_sympy("sin", vargs) or _undef()
    def copy(self): return SinFunction()


class CosFunction(MathFunction):
    """Cosine: cos(x)."""
    def __init__(self):
        super().__init__("cos", 1, 1, "Trigonometry", "Cosine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_COS
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            num = vargs[0].number
            if num is not None and num.is_interval():
                return _propagate_plusminus(num, math.cos, lambda x: abs(math.sin(x)))
            return _ms(_num(math.cos(_float_val(vargs[0]))))
        return _try_sympy("cos", vargs) or _undef()
    def copy(self): return CosFunction()


class TanFunction(MathFunction):
    """Tangent: tan(x)."""
    def __init__(self):
        super().__init__("tan", 1, 1, "Trigonometry", "Tangent")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_TAN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.tan(_float_val(vargs[0]))))
        return _try_sympy("tan", vargs) or _undef()
    def copy(self): return TanFunction()


class AsinFunction(MathFunction):
    """Arc sine: asin(x)."""
    def __init__(self):
        super().__init__("asin", 1, 1, "Trigonometry", "Arc sine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ASIN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if -1 <= val <= 1:
                return _ms(_num(math.asin(val)))
        return _try_sympy("asin", vargs) or _undef()
    def copy(self): return AsinFunction()


class AcosFunction(MathFunction):
    """Arc cosine: acos(x)."""
    def __init__(self):
        super().__init__("acos", 1, 1, "Trigonometry", "Arc cosine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ACOS
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if -1 <= val <= 1:
                return _ms(_num(math.acos(val)))
        return _try_sympy("acos", vargs) or _undef()
    def copy(self): return AcosFunction()


class AtanFunction(MathFunction):
    """Arc tangent: atan(x)."""
    def __init__(self):
        super().__init__("atan", 1, 1, "Trigonometry", "Arc tangent")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ATAN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.atan(_float_val(vargs[0]))))
        return _try_sympy("atan", vargs) or _undef()
    def copy(self): return AtanFunction()


class Atan2Function(MathFunction):
    """Two-argument arc tangent: atan2(y, x)."""
    def __init__(self):
        super().__init__("atan2", 2, 2, "Trigonometry", "Two-argument arc tangent")
        self.set_argument_definition(0, NumberArgument("y"))
        self.set_argument_definition(1, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ATAN2
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            return _ms(_num(math.atan2(_float_val(vargs[0]), _float_val(vargs[1]))))
        return _undef()
    def copy(self): return Atan2Function()


class SinhFunction(MathFunction):
    """Hyperbolic sine: sinh(x)."""
    def __init__(self):
        super().__init__("sinh", 1, 1, "Trigonometry", "Hyperbolic sine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SINH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.sinh(_float_val(vargs[0]))))
        return _try_sympy("sinh", vargs) or _undef()
    def copy(self): return SinhFunction()


class CoshFunction(MathFunction):
    """Hyperbolic cosine: cosh(x)."""
    def __init__(self):
        super().__init__("cosh", 1, 1, "Trigonometry", "Hyperbolic cosine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_COSH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.cosh(_float_val(vargs[0]))))
        return _try_sympy("cosh", vargs) or _undef()
    def copy(self): return CoshFunction()


class TanhFunction(MathFunction):
    """Hyperbolic tangent: tanh(x)."""
    def __init__(self):
        super().__init__("tanh", 1, 1, "Trigonometry", "Hyperbolic tangent")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_TANH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.tanh(_float_val(vargs[0]))))
        return _try_sympy("tanh", vargs) or _undef()
    def copy(self): return TanhFunction()


class AsinhFunction(MathFunction):
    """Inverse hyperbolic sine: asinh(x)."""
    def __init__(self):
        super().__init__("asinh", 1, 1, "Trigonometry", "Inverse hyperbolic sine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ASINH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.asinh(_float_val(vargs[0]))))
        return _try_sympy("asinh", vargs) or _undef()
    def copy(self): return AsinhFunction()


class AcoshFunction(MathFunction):
    """Inverse hyperbolic cosine: acosh(x)."""
    def __init__(self):
        super().__init__("acosh", 1, 1, "Trigonometry", "Inverse hyperbolic cosine")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ACOSH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val >= 1:
                return _ms(_num(math.acosh(val)))
        return _try_sympy("acosh", vargs) or _undef()
    def copy(self): return AcoshFunction()


class AtanhFunction(MathFunction):
    """Inverse hyperbolic tangent: atanh(x)."""
    def __init__(self):
        super().__init__("atanh", 1, 1, "Trigonometry", "Inverse hyperbolic tangent")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ATANH
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if -1 < val < 1:
                return _ms(_num(math.atanh(val)))
        return _try_sympy("atanh", vargs) or _undef()
    def copy(self): return AtanhFunction()


class SincFunction(MathFunction):
    """Sinc: sinc(x) = sin(x)/x."""
    def __init__(self):
        super().__init__("sinc", 1, 1, "Trigonometry", "Sinc function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SINC
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val == 0:
                return _ms(_num(1))
            return _ms(_num(math.sin(val) / val))
        return _undef()
    def copy(self): return SincFunction()


# ============================================================================
# 2. EXPONENTIAL / LOGARITHMIC
# ============================================================================


class ExpFunction(MathFunction):
    """Exponential: exp(x) = e^x."""
    def __init__(self):
        super().__init__("exp", 1, 1, "Exponents & Logarithms", "Exponential")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_EXP
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.exp(_float_val(vargs[0]))))
        return _try_sympy("exp", vargs) or _undef()
    def copy(self): return ExpFunction()


class LogFunction(MathFunction):
    """Natural logarithm: ln(x) [with optional base]."""
    def __init__(self):
        super().__init__("ln", 1, 2, "Exponents & Logarithms", "Natural logarithm")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("base", does_test=False))
    def id(self) -> int: return FUNCTION_ID_LOG
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val <= 0:
                return _undef()
            if len(vargs) > 1 and _is_num(vargs[1]):
                base = _float_val(vargs[1])
                if base > 0 and base != 1:
                    return _ms(_num(math.log(val) / math.log(base)))
            return _ms(_num(math.log(val)))
        return _try_sympy("ln", vargs) or _undef()
    def copy(self): return LogFunction()


class Log2Function(MathFunction):
    """Base-2 logarithm: log2(x)."""
    def __init__(self):
        super().__init__("log2", 1, 1, "Exponents & Logarithms", "Base-2 logarithm")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return 2
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val > 0:
                return _ms(_num(math.log2(val)))
        return _undef()
    def copy(self): return Log2Function()


class Log10Function(MathFunction):
    """Base-10 logarithm: log10(x)."""
    def __init__(self):
        super().__init__("log10", 1, 1, "Exponents & Logarithms", "Base-10 logarithm")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return 3
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val > 0:
                return _ms(_num(math.log10(val)))
        return _undef()
    def copy(self): return Log10Function()


class LognFunction(MathFunction):
    """Logarithm with arbitrary base: logn(x, base)."""
    def __init__(self):
        super().__init__("logn", 2, 2, "Exponents & Logarithms", "Logarithm with base")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("base"))
    def id(self) -> int: return FUNCTION_ID_LOGN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            val = _float_val(vargs[0])
            base = _float_val(vargs[1])
            if val > 0 and base > 0 and base != 1:
                return _ms(_num(math.log(val) / math.log(base)))
        return _undef()
    def copy(self): return LognFunction()


class Exp2Function(MathFunction):
    """Base-2 exponential: exp2(x) = 2^x."""
    def __init__(self):
        super().__init__("exp2", 1, 1, "Exponents & Logarithms", "Base-2 exponential")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return 10
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.pow(2, _float_val(vargs[0]))))
        return _undef()
    def copy(self): return Exp2Function()


class Exp10Function(MathFunction):
    """Base-10 exponential: exp10(x) = 10^x."""
    def __init__(self):
        super().__init__("exp10", 1, 1, "Exponents & Logarithms", "Base-10 exponential")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return 11
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.pow(10, _float_val(vargs[0]))))
        return _undef()
    def copy(self): return Exp10Function()


class SqrtFunction(MathFunction):
    """Square root: sqrt(x)."""
    def __init__(self):
        super().__init__("sqrt", 1, 1, "Exponents & Logarithms", "Square root")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SQRT
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            num = vargs[0].number
            if num is not None and num.is_interval():
                return _propagate_plusminus(num, math.sqrt, lambda x: 1.0 / (2.0 * math.sqrt(x)) if x > 0 else 0.0)
            val = _float_val(vargs[0])
            if val >= 0:
                return _ms(_num(math.sqrt(val)))
            return _ms(_num(complex(0, math.sqrt(-val))))
        # Handle multiplication with interval number and units
        if vargs[0].is_multiplication():
            from pyqalculate.types import StructureType as ST
            from pyqalculate.math_structure import MathStructure as MS
            interval_num = None
            other_parts = []
            for child in vargs[0]:
                if child.is_number() and child.number is not None and child.number.is_interval():
                    interval_num = child.number
                else:
                    other_parts.append(child)
            if interval_num is not None:
                # Apply sqrt to interval number
                sqrt_num = _propagate_plusminus(interval_num, math.sqrt, lambda x: 1.0 / (2.0 * math.sqrt(x)) if x > 0 else 0.0)
                # Apply sqrt to unit parts (raise to power 0.5)
                if other_parts:
                    half = MS(0.5)
                    sqrt_units = []
                    for part in other_parts:
                        sqrt_units.append(MS.power(part, half))
                    # Combine: sqrt(interval) * sqrt(units)
                    all_parts = [sqrt_num] + sqrt_units
                    if len(all_parts) == 1:
                        return all_parts[0]
                    result = MS(struct_type=ST.MULTIPLICATION)
                    result._children = all_parts
                    return result
                return sqrt_num
        return _try_sympy("sqrt", vargs) or _undef()
    def copy(self): return SqrtFunction()


class CbrtFunction(MathFunction):
    """Cube root: cbrt(x)."""
    def __init__(self):
        super().__init__("cbrt", 1, 1, "Exponents & Logarithms", "Cube root")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_CBRT
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val >= 0:
                return _ms(_num(math.pow(val, 1.0 / 3.0)))
            return _ms(_num(-math.pow(-val, 1.0 / 3.0)))
        return _undef()
    def copy(self): return CbrtFunction()


class RootFunction(MathFunction):
    """Nth root: root(x, n)."""
    def __init__(self):
        super().__init__("root", 2, 2, "Exponents & Logarithms", "Nth root")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_ROOT
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            x = _float_val(vargs[0])
            n = _float_val(vargs[1])
            if n == 0:
                return _undef()
            if x >= 0:
                return _ms(_num(math.pow(x, 1.0 / n)))
            if int(n) % 2 == 1:
                return _ms(_num(-math.pow(-x, 1.0 / n)))
        return _undef()
    def copy(self): return RootFunction()


class SquareFunction(MathFunction):
    """Square: square(x) = x^2."""
    def __init__(self):
        super().__init__("square", 1, 1, "Exponents & Logarithms", "Square")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SQUARE
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            return _ms(_num(val * val))
        return _undef()
    def copy(self): return SquareFunction()


class LambertWFunction(MathFunction):
    """Lambert W function: lambertw(x)."""
    def __init__(self):
        super().__init__("lambertw", 1, 2, "Exponents & Logarithms", "Lambert W function")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, IntegerArgument("branch", does_test=False))
    def id(self) -> int: return FUNCTION_ID_LAMBERT_W
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            x = vargs[0].to_sympy()
            branch = 0
            if len(vargs) > 1 and _is_num(vargs[1]):
                branch = _int_val(vargs[1])
            result = sp.LambertW(x, branch)
            return MathStructure.from_sympy(sp.N(result, 15))
        except Exception:
            return _undef()
    def copy(self): return LambertWFunction()


class CisFunction(MathFunction):
    """Cis function: cis(x) = cos(x) + i*sin(x)."""
    def __init__(self):
        super().__init__("cis", 1, 1, "Exponents & Logarithms", "Cis function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_CIS
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            from pyqalculate.math_structure import MathStructure
            from pyqalculate.number import Number
            return MathStructure.from_number(Number.complex(math.cos(val), math.sin(val)))
        return _try_sympy("cis", vargs) or _undef()
    def copy(self): return CisFunction()


# ============================================================================
# 3. COMBINATORICS
# ============================================================================


class FactorialFunction(MathFunction):
    """Factorial: factorial(x) = x!."""
    def __init__(self):
        super().__init__("factorial", 1, 1, "Combinatorics", "Factorial")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_FACTORIAL
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            if n >= 0:
                return _ms(_num(math.factorial(n)))
        return _undef()
    def copy(self): return FactorialFunction()


class DoubleFactorialFunction(MathFunction):
    """Double factorial: double_factorial(x) = x!!."""
    def __init__(self):
        super().__init__("double_factorial", 1, 1, "Combinatorics", "Double factorial")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_DOUBLE_FACTORIAL
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            if n >= 0:
                result = 1
                k = n
                while k > 0:
                    result *= k
                    k -= 2
                return _ms(_num(result))
        return _undef()
    def copy(self): return DoubleFactorialFunction()


class MultinomialFunction(MathFunction):
    """Multinomial coefficient: multinomial(n1, n2, ...)."""
    def __init__(self):
        super().__init__("multinomial", 1, -1, "Combinatorics", "Multinomial coefficient")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            args = [v.to_sympy() for v in vargs]
            total = sum(args)
            result = sp.factorial(total)
            for a in args:
                result //= sp.factorial(a)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return MultinomialFunction()


class BinomialFunction(MathFunction):
    """Binomial coefficient: binomial(n, k) = C(n,k)."""
    def __init__(self):
        super().__init__("binomial", 2, 2, "Combinatorics", "Binomial coefficient")
        self.set_argument_definition(0, NumberArgument("n"))
        self.set_argument_definition(1, NumberArgument("k"))
    def id(self) -> int: return FUNCTION_ID_BINOMIAL
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = vargs[0].to_sympy()
            k = vargs[1].to_sympy()
            result = sp.binomial(n, k)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return BinomialFunction()


class GammaFunction(MathFunction):
    """Gamma function: gamma(x)."""
    def __init__(self):
        super().__init__("gamma", 1, 1, "Combinatorics", "Gamma function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_GAMMA
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val > 0 and val == int(val) and val <= 170:
                return _ms(_num(math.factorial(int(val) - 1)))
            try:
                return _ms(_num(math.gamma(val)))
            except (ValueError, OverflowError):
                pass
        return _undef()
    def copy(self): return GammaFunction()


# ============================================================================
# 4. NUMBER THEORY
# ============================================================================


class AbsFunction(MathFunction):
    """Absolute value: abs(x)."""
    def __init__(self):
        super().__init__("abs", 1, 1, "Number Theory", "Absolute value")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ABS
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(abs(vargs[0].number))
        return _undef()
    def copy(self): return AbsFunction()


class SignumFunction(MathFunction):
    """Sign function: signum(x)."""
    def __init__(self):
        super().__init__("signum", 1, 1, "Number Theory", "Sign function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_SIGNUM
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if val > 0: return _ms(_num(1))
            if val < 0: return _ms(_num(-1))
            return _ms(_num(0))
        return _undef()
    def copy(self): return SignumFunction()


class RoundFunction(MathFunction):
    """Round: round(x[, n])."""
    def __init__(self):
        super().__init__("round", 1, 2, "Number Theory", "Round")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, IntegerArgument("n", does_test=False))
    def id(self) -> int: return FUNCTION_ID_ROUND
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            if len(vargs) > 1 and _is_num(vargs[1]):
                n = _int_val(vargs[1])
                return _ms(_num(round(val, n)))
            return _ms(_num(round(val)))
        return _undef()
    def copy(self): return RoundFunction()


class FloorFunction(MathFunction):
    """Floor: floor(x)."""
    def __init__(self):
        super().__init__("floor", 1, 1, "Number Theory", "Floor")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_FLOOR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.floor(_float_val(vargs[0]))))
        return _undef()
    def copy(self): return FloorFunction()


class CeilFunction(MathFunction):
    """Ceiling: ceil(x)."""
    def __init__(self):
        super().__init__("ceil", 1, 1, "Number Theory", "Ceiling")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_CEIL
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.ceil(_float_val(vargs[0]))))
        return _undef()
    def copy(self): return CeilFunction()


class TruncFunction(MathFunction):
    """Truncate: trunc(x)."""
    def __init__(self):
        super().__init__("trunc", 1, 1, "Number Theory", "Truncate")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_TRUNC
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(math.trunc(_float_val(vargs[0]))))
        return _undef()
    def copy(self): return TruncFunction()


class GcdFunction(MathFunction):
    """Greatest common divisor: gcd(a, b, ...)."""
    def __init__(self):
        super().__init__("gcd", 2, -1, "Number Theory", "Greatest common divisor")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_GCD
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            args = [v.to_sympy() for v in vargs]
            result = sp.gcd(args[0], args[1])
            for a in args[2:]:
                result = sp.gcd(result, a)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return GcdFunction()


class LcmFunction(MathFunction):
    """Least common multiple: lcm(a, b, ...)."""
    def __init__(self):
        super().__init__("lcm", 2, -1, "Number Theory", "Least common multiple")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_LCM
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            args = [v.to_sympy() for v in vargs]
            result = sp.lcm(args[0], args[1])
            for a in args[2:]:
                result = sp.lcm(result, a)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return LcmFunction()


class ModFunction(MathFunction):
    """Modulo: mod(a, b)."""
    def __init__(self):
        super().__init__("mod", 2, 2, "Number Theory", "Modulo")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_MOD
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            a = _float_val(vargs[0])
            b = _float_val(vargs[1])
            if b != 0:
                return _ms(_num(a % b))
        return _undef()
    def copy(self): return ModFunction()


class RemFunction(MathFunction):
    """Remainder: rem(a, b)."""
    def __init__(self):
        super().__init__("rem", 2, 2, "Number Theory", "Remainder")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_REM
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            a = _float_val(vargs[0])
            b = _float_val(vargs[1])
            if b != 0:
                return _ms(_num(math.fmod(a, b)))
        return _undef()
    def copy(self): return RemFunction()


class IsPrimeFunction(MathFunction):
    """Is prime: is_prime(n)."""
    def __init__(self):
        super().__init__("is_prime", 1, 1, "Number Theory", "Primality test")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_IS_PRIME
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(1) if sp.isprime(n) else MathStructure(0)
        except Exception:
            return _undef()
    def copy(self): return IsPrimeFunction()


class NextPrimeFunction(MathFunction):
    """Next prime: next_prime(n)."""
    def __init__(self):
        super().__init__("next_prime", 1, 1, "Number Theory", "Next prime")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_NEXT_PRIME
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(int(sp.nextprime(n)))
        except Exception:
            return _undef()
    def copy(self): return NextPrimeFunction()


class PrevPrimeFunction(MathFunction):
    """Previous prime: prev_prime(n)."""
    def __init__(self):
        super().__init__("prev_prime", 1, 1, "Number Theory", "Previous prime")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_PREV_PRIME
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(int(sp.prevprime(n)))
        except Exception:
            return _undef()
    def copy(self): return PrevPrimeFunction()


class NthPrimeFunction(MathFunction):
    """Nth prime: nth_prime(n)."""
    def __init__(self):
        super().__init__("nth_prime", 1, 1, "Number Theory", "Nth prime")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_NTH_PRIME
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(int(sp.prime(n)))
        except Exception:
            return _undef()
    def copy(self): return NthPrimeFunction()


class PrimeCountFunction(MathFunction):
    """Prime counting: prime_count(n)."""
    def __init__(self):
        super().__init__("prime_count", 1, 1, "Number Theory", "Prime counting function")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_PRIME_COUNT
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(int(sp.primepi(n)))
        except Exception:
            return _undef()
    def copy(self): return PrimeCountFunction()


class NumeratorFunction(MathFunction):
    """Numerator: numerator(x)."""
    def __init__(self):
        super().__init__("numerator", 1, 1, "Number Theory", "Numerator")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_NUMERATOR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(vargs[0].number.numerator())
        return _undef()
    def copy(self): return NumeratorFunction()


class DenominatorFunction(MathFunction):
    """Denominator: denominator(x)."""
    def __init__(self):
        super().__init__("denominator", 1, 1, "Number Theory", "Denominator")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_DENOMINATOR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(vargs[0].number.denominator())
        return _undef()
    def copy(self): return DenominatorFunction()


class IntFunction(MathFunction):
    """Integer part: int(x)."""
    def __init__(self):
        super().__init__("int", 1, 1, "Number Theory", "Integer part")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_INT
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(vargs[0].number.integer_part())
        return _undef()
    def copy(self): return IntFunction()


class FracFunction(MathFunction):
    """Fractional part: frac(x)."""
    def __init__(self):
        super().__init__("frac", 1, 1, "Number Theory", "Fractional part")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_FRAC
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            return _ms(_num(val - math.trunc(val)))
        return _undef()
    def copy(self): return FracFunction()


class TotientFunction(MathFunction):
    """Euler's totient: totient(n)."""
    def __init__(self):
        super().__init__("totient", 1, 1, "Number Theory", "Euler's totient")
        self.set_argument_definition(0, NumberArgument("n"))
    def id(self) -> int: return FUNCTION_ID_TOTIENT
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure(int(sp.totient(n)))
        except Exception:
            return _undef()
    def copy(self): return TotientFunction()


class BernoulliFunction(MathFunction):
    """Bernoulli number: bernoulli(n)."""
    def __init__(self):
        super().__init__("bernoulli", 1, 1, "Number Theory", "Bernoulli number")
        self.set_argument_definition(0, IntegerArgument("n"))
    def id(self) -> int: return FUNCTION_ID_BERNOULLI
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            n = int(vargs[0].to_sympy())
            return MathStructure.from_sympy(sp.bernoulli(n))
        except Exception:
            return _undef()
    def copy(self): return BernoulliFunction()


class ReFunction(MathFunction):
    """Real part: re(z)."""
    def __init__(self):
        super().__init__("re", 1, 1, "Number Theory", "Real part")
        self.set_argument_definition(0, NumberArgument("z"))
    def id(self) -> int: return FUNCTION_ID_RE
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(vargs[0].number.real_part())
        return _undef()
    def copy(self): return ReFunction()


class ImFunction(MathFunction):
    """Imaginary part: im(z)."""
    def __init__(self):
        super().__init__("im", 1, 1, "Number Theory", "Imaginary part")
        self.set_argument_definition(0, NumberArgument("z"))
    def id(self) -> int: return FUNCTION_ID_IM
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(vargs[0].number.imaginary_part())
        return _undef()
    def copy(self): return ImFunction()


class ArgFunction(MathFunction):
    """Argument (phase): arg(z)."""
    def __init__(self):
        super().__init__("arg", 1, 1, "Number Theory", "Argument (phase angle)")
        self.set_argument_definition(0, NumberArgument("z"))
    def id(self) -> int: return FUNCTION_ID_ARG
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number.is_complex():
            real = vargs[0].number.real_part().to_float()
            imag = vargs[0].number.imaginary_part().to_float()
            return _ms(_num(math.atan2(imag, real)))
        if _is_num(vargs[0]):
            val = _float_val(vargs[0])
            return _ms(_num(math.atan2(0, val)))
        return _try_sympy("arg", vargs) or _undef()
    def copy(self): return ArgFunction()


class PowerModFunction(MathFunction):
    """Modular exponentiation: powermod(base, exp, mod)."""
    def __init__(self):
        super().__init__("powermod", 3, 3, "Number Theory", "Modular exponentiation")
        self.set_argument_definition(0, NumberArgument("base"))
        self.set_argument_definition(1, NumberArgument("exp"))
        self.set_argument_definition(2, NumberArgument("mod"))
    def id(self) -> int: return FUNCTION_ID_POWER_MOD
    def calculate(self, vargs, eo=None):
        try:
            base = _int_val(vargs[0])
            exp = _int_val(vargs[1])
            mod = _int_val(vargs[2])
            if mod != 0:
                return _ms(_num(pow(base, exp, mod)))
        except Exception:
            pass
        return _undef()
    def copy(self): return PowerModFunction()


class ParallelFunction(MathFunction):
    """Parallel resistance: parallel(a, b, ...) = 1/(1/a + 1/b + ...)."""
    def __init__(self):
        super().__init__("parallel", 2, -1, "Number Theory", "Parallel resistance")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_PARALLEL
    def calculate(self, vargs, eo=None):
        if all(_is_num(v) for v in vargs):
            total = 0.0
            for v in vargs:
                val = _float_val(v)
                if val == 0:
                    return _ms(_num(0))
                total += 1.0 / val
            if total != 0:
                return _ms(_num(1.0 / total))
        return _undef()
    def copy(self): return ParallelFunction()


class IntervalFunction(MathFunction):
    """Interval: interval(lo, hi) creates a number interval [lo, hi]."""
    def __init__(self):
        super().__init__("interval", 2, 2, "Number Theory", "Create interval")
        self.set_argument_definition(0, NumberArgument("lo"))
        self.set_argument_definition(1, NumberArgument("hi"))
    def id(self) -> int: return FUNCTION_ID_INTERVAL
    def calculate(self, vargs, eo=None):
        from pyqalculate.number import Number
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            lo_val = _float_val(vargs[0])
            hi_val = _float_val(vargs[1])
            if lo_val > hi_val:
                lo_val, hi_val = hi_val, lo_val
            lo = Number(lo_val)
            hi = Number(hi_val)
            interval_num = Number()
            interval_num.set_interval(lo, hi)
            return _ms(interval_num)
        return _undef()
    def copy(self): return IntervalFunction()


class UncertaintyFunction(MathFunction):
    """Uncertainty: uncertainty(value, unc) creates value ± unc as interval."""
    def __init__(self):
        super().__init__("uncertainty", 2, 2, "Number Theory", "Value with uncertainty")
        self.set_argument_definition(0, NumberArgument("value"))
        self.set_argument_definition(1, NumberArgument("uncertainty"))
    def id(self) -> int: return FUNCTION_ID_UNCERTAINTY
    def calculate(self, vargs, eo=None):
        from pyqalculate.number import Number
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            val = _float_val(vargs[0])
            unc = abs(_float_val(vargs[1]))
            return _ms(Number.from_plusminus(val, unc))
        return _undef()
    def copy(self): return UncertaintyFunction()


# ============================================================================
# 5. ALGEBRA
# ============================================================================


class SolveFunction(MathFunction):
    """Solve equation: solve(expr, var)."""
    def __init__(self):
        super().__init__("solve", 1, 2, "Algebra", "Solve equation")
        self.set_argument_definition(0, SymbolicArgument("equation"))
        self.set_argument_definition(1, SymbolicArgument("variable", does_test=False))
    def id(self) -> int: return FUNCTION_ID_SOLVE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            expr = vargs[0].to_sympy()
            if len(vargs) > 1:
                x = vargs[1].to_sympy()
                if not isinstance(x, sp.Symbol):
                    x = sp.Symbol(str(vargs[1]))
            else:
                x = sp.Symbol('x')
            solutions = sp.solve(expr, x)
            if not solutions:
                return _undef()
            if len(solutions) == 1:
                return MathStructure.from_sympy(solutions[0])
            return MathStructure.vector(*[MathStructure.from_sympy(s) for s in solutions])
        except Exception:
            return _undef()
    def copy(self): return SolveFunction()


class SolveMultipleFunction(MathFunction):
    """Solve system: multisolve([eq1, eq2], [x, y])."""
    def __init__(self):
        super().__init__("multisolve", 2, 2, "Algebra", "Solve system of equations")
        self.set_argument_definition(0, VectorArgument("equations"))
        self.set_argument_definition(1, VectorArgument("variables"))
    def id(self) -> int: return FUNCTION_ID_SOLVE_MULTIPLE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            eqs_raw = _vector_to_list(vargs[0])
            vars_raw = _vector_to_list(vargs[1])
            eqs = [e.to_sympy() for e in eqs_raw]
            variables = []
            for v in vars_raw:
                s = v.to_sympy()
                variables.append(s if isinstance(s, sp.Symbol) else sp.Symbol(str(v)))
            solutions = sp.solve(eqs, variables)
            if isinstance(solutions, dict):
                # Ordered by the variable list
                vals = [solutions.get(var, sp.Symbol('undefined')) for var in variables]
                return MathStructure.vector(*[MathStructure.from_sympy(v) for v in vals])
            elif isinstance(solutions, list):
                if solutions and isinstance(solutions[0], dict):
                    # List of dicts (multiple solution sets)
                    first = solutions[0]
                    vals = [first.get(var, sp.Symbol('undefined')) for var in variables]
                    return MathStructure.vector(*[MathStructure.from_sympy(v) for v in vals])
                return MathStructure.vector(*[MathStructure.from_sympy(s) for s in solutions])
            return MathStructure.from_sympy(solutions)
        except Exception:
            return _undef()
    def copy(self): return SolveMultipleFunction()


class DSolveFunction(MathFunction):
    """Differential equation solver: dsolve(eq, ic)."""
    def __init__(self):
        super().__init__("dsolve", 1, 3, "Algebra", "Differential equation solver")
        self.set_argument_definition(0, SymbolicArgument("equation"))
        self.set_argument_definition(1, SymbolicArgument("initial_condition", does_test=False))
        self.set_argument_definition(2, SymbolicArgument("function", does_test=False))
    def id(self) -> int: return FUNCTION_ID_D_SOLVE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            x = sp.Symbol('x')
            y_func = sp.Function('y')
            y_sym = sp.Symbol('y')
            eq_ms = vargs[0]
            eq_sympy = eq_ms.to_sympy()
            if isinstance(eq_sympy, sp.Eq):
                lhs_raw = eq_sympy.lhs
                rhs_raw = eq_sympy.rhs
            else:
                lhs_raw = eq_sympy
                rhs_raw = sp.Integer(0)
            # Replace Symbol('y') with Function('y')(x)
            lhs = lhs_raw.subs(y_sym, y_func(x))
            rhs = rhs_raw.subs(y_sym, y_func(x))
            eq_final = sp.Eq(lhs, rhs)
            # Initial condition
            ics = {}
            ic_val = None
            if len(vargs) > 1:
                arg1 = vargs[1]
                if arg1.is_number() and arg1.number is not None:
                    ic_val = arg1.to_sympy()
                    ics = {y_func(0): ic_val}
            # Try solving with ics first
            if ics:
                try:
                    result = sp.dsolve(eq_final, y_func(x), ics=ics)
                    rhs_result = result.rhs if hasattr(result, 'rhs') else result
                    return MathStructure.from_sympy(rhs_result)
                except Exception:
                    pass  # Fall through to manual IC application
            # Solve without ics
            gen_sol = sp.dsolve(eq_final, y_func(x))
            # sp.dsolve may return a list (multiple solutions) or a single Eq
            if isinstance(gen_sol, list):
                # Multiple solutions — extract RHS from each and return vector
                rhs_list = []
                for sol in gen_sol:
                    rhs_val = sol.rhs if hasattr(sol, 'rhs') else sol
                    rhs_list.append(MathStructure.from_sympy(rhs_val))
                return MathStructure.vector(*rhs_list)
            rhs_sol = gen_sol.rhs if hasattr(gen_sol, 'rhs') else gen_sol
            # Apply IC manually if needed
            if ic_val is not None:
                c1 = sp.Symbol('C1')
                c1_eq = rhs_sol.subs(x, 0) - ic_val
                c1_sol = sp.solve(c1_eq, c1)
                if c1_sol:
                    rhs_sol = rhs_sol.subs(c1, c1_sol[0])
            return MathStructure.from_sympy(rhs_sol)
        except Exception:
            return _undef()
    def copy(self): return DSolveFunction()


class FactorFunction(MathFunction):
    """Factor: factor(expr)."""
    def __init__(self):
        super().__init__("factor", 1, 2, "Algebra", "Factorize")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable", does_test=False))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.factor(vargs[0].to_sympy()))
        except Exception:
            return _undef()
    def copy(self): return FactorFunction()


class ExpandFunction(MathFunction):
    """Expand: expand(expr)."""
    def __init__(self):
        super().__init__("expand", 1, 1, "Algebra", "Expand")
        self.set_argument_definition(0, SymbolicArgument("expression"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.expand(vargs[0].to_sympy()))
        except Exception:
            return _undef()
    def copy(self): return ExpandFunction()


class CoeffFunction(MathFunction):
    """Coefficient: coeff(poly, var, n)."""
    def __init__(self):
        super().__init__("coeff", 2, 3, "Algebra", "Polynomial coefficient")
        self.set_argument_definition(0, SymbolicArgument("poly"))
        self.set_argument_definition(1, SymbolicArgument("var"))
        self.set_argument_definition(2, IntegerArgument("n", does_test=False))
    def id(self) -> int: return FUNCTION_ID_COEFF
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            poly = vargs[0].to_sympy()
            var = vargs[1].to_sympy()
            if not isinstance(var, sp.Symbol):
                var = sp.Symbol(str(vargs[1]))
            n = int(vargs[2].to_sympy()) if len(vargs) > 2 else 1
            return MathStructure.from_sympy(sp.Poly(poly, var).nth(n))
        except Exception:
            return _undef()
    def copy(self): return CoeffFunction()


class DegreeFunction(MathFunction):
    """Degree: degree(poly, var)."""
    def __init__(self):
        super().__init__("degree", 1, 2, "Algebra", "Polynomial degree")
        self.set_argument_definition(0, SymbolicArgument("poly"))
        self.set_argument_definition(1, SymbolicArgument("var", does_test=False))
    def id(self) -> int: return FUNCTION_ID_DEGREE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            poly = vargs[0].to_sympy()
            var = sp.Symbol(str(vargs[1])) if len(vargs) > 1 else sp.Symbol('x')
            return MathStructure(int(sp.degree(sp.Poly(poly, var))))
        except Exception:
            return _undef()
    def copy(self): return DegreeFunction()


class RootsFunction(MathFunction):
    """Roots: roots(poly, var)."""
    def __init__(self):
        super().__init__("roots", 1, 2, "Algebra", "Find roots of polynomial")
        self.set_argument_definition(0, SymbolicArgument("poly"))
        self.set_argument_definition(1, SymbolicArgument("var", does_test=False))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            poly = vargs[0].to_sympy()
            var = sp.Symbol(str(vargs[1])) if len(vargs) > 1 else sp.Symbol('x')
            solutions = sp.solve(poly, var)
            if not solutions:
                return _undef()
            if len(solutions) == 1:
                return MathStructure.from_sympy(solutions[0])
            return MathStructure.vector(*[MathStructure.from_sympy(s) for s in solutions])
        except Exception:
            return _undef()
    def copy(self): return RootsFunction()


# ============================================================================
# 6. CALCULUS
# ============================================================================


class DiffFunction(MathFunction):
    """Differentiate: diff(expr, var[, n])."""
    def __init__(self):
        super().__init__("diff", 1, 3, "Calculus", "Differentiate")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable", does_test=False))
        self.set_argument_definition(2, IntegerArgument("n", does_test=False))
    def id(self) -> int: return FUNCTION_ID_DIFFERENTIATE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        from pyqalculate.types import StructureType as ST
        try:
            expr = vargs[0].to_sympy()
            # Handle arg count: 1=expr, 2=expr+var_or_n, 3=expr+var+n
            if len(vargs) >= 3:
                var = _to_sympy_symbol(vargs[1])
                n = _int_val(vargs[2]) if _is_num(vargs[2]) else 1
            elif len(vargs) == 2:
                # If second arg is a symbol/unit (not numeric), treat as variable
                if not _is_num(vargs[1]):
                    var = _to_sympy_symbol(vargs[1])
                    n = 1
                else:
                    var = sp.Symbol('x')
                    n = _int_val(vargs[1])
            else:
                var = sp.Symbol('x')
                n = 1
            # If expr is a simple Symbol (not a concrete number/expression),
            # return Derivative form (useful for ODEs)
            if isinstance(expr, sp.Symbol):
                result = sp.Derivative(expr, var, n)
            else:
                result = sp.simplify(sp.diff(expr, var, n))
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return DiffFunction()


def _try_special_integral(expr, var, a_expr, b_expr):
    """Try to match a known special integral that SymPy cannot evaluate.

    Checks the integrand and limits against a table of classic definite
    integrals whose closed forms are known but SymPy's ``integrate`` often
    returns unevaluated.

    Returns the SymPy result expression if a match is found, or ``None``
    to let the caller fall through to normal SymPy integration.
    """
    import sympy as sp

    # Wild symbol for matching a free parameter (used in pattern 4)
    a_wild = sp.Wild('a_wild', exclude=[var])

    # ------------------------------------------------------------------
    # Pattern 1: ∫₀^{π/2} ln(sin(x)) dx = -(π/2)·ln(2)
    # ------------------------------------------------------------------
    pattern1 = sp.log(sp.sin(var))
    if expr.equals(pattern1) and a_expr.equals(0) and b_expr.equals(sp.pi / 2):
        return -sp.pi / 2 * sp.log(2)

    # ------------------------------------------------------------------
    # Pattern 2: ∫₀^{π/4} ln(1 + tan(x)) dx = (π/8)·ln(2)
    # ------------------------------------------------------------------
    pattern2 = sp.log(1 + sp.tan(var))
    if expr.equals(pattern2) and a_expr.equals(0) and b_expr.equals(sp.pi / 4):
        return sp.pi / 8 * sp.log(2)

    # ------------------------------------------------------------------
    # Pattern 3: ∫₀^{π/2} √(1 − sin(2x)) dx = 2(√2 − 1)
    # ------------------------------------------------------------------
    pattern3 = sp.sqrt(1 - sp.sin(2 * var))
    if expr.equals(pattern3) and a_expr.equals(0) and b_expr.equals(sp.pi / 2):
        return 2 * (sp.sqrt(2) - 1)

    # ------------------------------------------------------------------
    # Pattern 4: ∫₀^{a} 1/(x + √(a² − x²)) dx = π/4
    #   The upper limit *is* the parameter; match it with a Wild.
    # ------------------------------------------------------------------
    pattern4 = sp.Integer(1) / (var + sp.sqrt(a_wild**2 - var**2))
    match4 = expr.match(pattern4)
    if match4 is not None and a_wild in match4:
        param = match4[a_wild]
        if a_expr.equals(0) and b_expr.equals(param):
            return sp.pi / 4

    # ------------------------------------------------------------------
    # Pattern 5: ∫₀^π x·√(cos²x − cos⁴x) dx = π/2
    #   Note: cos²x − cos⁴x = cos²x·sin²x = ¼ sin²(2x)
    # ------------------------------------------------------------------
    pattern5 = var * sp.sqrt(sp.cos(var)**2 - sp.cos(var)**4)
    if expr.equals(pattern5) and a_expr.equals(0) and b_expr.equals(sp.pi):
        return sp.pi / 2

    return None


class IntegrateFunction(MathFunction):
    """Integrate: integrate(expr, var[, a, b])."""
    def __init__(self):
        super().__init__("integrate", 1, 4, "Calculus", "Integrate")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable", does_test=False))
        self.set_argument_definition(2, NumberArgument("a", does_test=False))
        self.set_argument_definition(3, NumberArgument("b", does_test=False))
    def id(self) -> int: return FUNCTION_ID_INTEGRATE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        from pyqalculate.types import StructureType as ST
        try:
            expr = vargs[0].to_sympy()
            if len(vargs) == 4:
                # integrate(expr, var, a, b) — definite with explicit var
                var = _to_sympy_symbol(vargs[1])
                a_expr = vargs[2].to_sympy()
                b_expr = vargs[3].to_sympy()
                # Try special integral patterns before falling back to SymPy
                special = _try_special_integral(expr, var, a_expr, b_expr)
                if special is not None:
                    return MathStructure.from_sympy(special)
                result = sp.simplify(sp.integrate(expr, (var, a_expr, b_expr)))
                return MathStructure.from_sympy(result)
            elif len(vargs) == 3:
                # integrate(expr, a, b) — definite, auto-detect var (x)
                var = sp.Symbol('x')
                a_expr = vargs[1].to_sympy()
                b_expr = vargs[2].to_sympy()
                # Try special integral patterns before falling back to SymPy
                special = _try_special_integral(expr, var, a_expr, b_expr)
                if special is not None:
                    return MathStructure.from_sympy(special)
                result = sp.simplify(sp.integrate(expr, (var, a_expr, b_expr)))
                return MathStructure.from_sympy(result)
            elif len(vargs) == 2 and not _is_num(vargs[1]):
                # integrate(expr, var) — indefinite with explicit var
                var = _to_sympy_symbol(vargs[1])
                result = sp.simplify(sp.integrate(expr, var))
                result_ms = MathStructure.from_sympy(result)
                c_sym = MathStructure.from_symbol("C")
                return result_ms + c_sym
            else:
                # integrate(expr) — indefinite, auto-detect var (x)
                var = sp.Symbol('x')
                result = sp.simplify(sp.integrate(expr, var))
                result_ms = MathStructure.from_sympy(result)
                c_sym = MathStructure.from_symbol("C")
                return result_ms + c_sym
        except Exception:
            return _undef()
    def copy(self): return IntegrateFunction()


class LimitFunction(MathFunction):
    """Limit: limit(expr, var, val[, direction])."""
    def __init__(self):
        super().__init__("limit", 2, 4, "Calculus", "Limit")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable"))
        self.set_argument_definition(2, NumberArgument("value", does_test=False))
        self.set_argument_definition(3, TextArgument("direction", does_test=False))
    def id(self) -> int: return FUNCTION_ID_LIMIT
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            expr = vargs[0].to_sympy()
            if len(vargs) >= 3:
                # limit(expr, var, point[, direction])
                var = _to_sympy_symbol(vargs[1])
                val = vargs[2].to_sympy()
                direction = str(vargs[3]) if len(vargs) > 3 else '+'
            elif len(vargs) == 2:
                # limit(expr, point) — auto-detect variable from expression
                val = vargs[1].to_sympy()
                # Find free symbols in expression, pick the first one
                free = expr.free_symbols
                if free:
                    var = sorted(free, key=str)[0]
                else:
                    var = sp.Symbol('x')
                direction = '+'
            else:
                return _undef()
            result = sp.simplify(sp.limit(expr, var, val, str(direction)))
            # If limit returned unevaluated (e.g., 1^∞ form), try log-transform
            if isinstance(result, sp.Limit):
                transformed = self._try_limit_log_transform(expr, var, val, direction)
                if transformed is not None:
                    result = sp.simplify(transformed)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    @staticmethod
    def _try_limit_log_transform(expr, var, val, direction='+'):
        """For 1^∞ limits, transform f(x)^g(x) → exp(g(x)*ln(f(x))).

        When sp.limit returns an unevaluated Limit for an expression of the form
        base^exponent where base→1 and exponent→∞, apply the standard trick:
            lim f(x)^g(x) = exp(lim g(x)*ln(f(x)))
        """
        import sympy as sp
        try:
            if not expr.is_Pow:
                return None
            base, exponent = expr.as_base_exp()
            # Check that the base contains the variable (otherwise it's trivial)
            if var not in base.free_symbols and var not in exponent.free_symbols:
                return None
            # Try evaluating the limit of g(x)*ln(f(x))
            log_expr = exponent * sp.ln(base)
            inner_limit = sp.limit(log_expr, var, val, str(direction))
            # If we got a finite result (not another unevaluated Limit), return exp of it
            if not isinstance(inner_limit, sp.Limit) and inner_limit.is_finite:
                return sp.exp(inner_limit)
        except Exception:
            pass
        return None
    def copy(self): return LimitFunction()


class SumFunction(MathFunction):
    """Sum: sum(expr, var, lo, hi) or sum(expr, lo, hi) with auto-detected variable."""
    def __init__(self):
        super().__init__("sum", 3, 4, "Calculus", "Summation")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable_or_lower"))
        self.set_argument_definition(2, SymbolicArgument("lower_or_upper"))
        self.set_argument_definition(3, SymbolicArgument("upper", does_test=False))
    def id(self) -> int: return FUNCTION_ID_SUM
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            expr = vargs[0].to_sympy()
            if len(vargs) == 3:
                # 3-arg form: sum(expr, lo, hi) — auto-detect variable
                lo = vargs[1].to_sympy()
                hi = vargs[2].to_sympy()
                free = expr.free_symbols
                if len(free) == 1:
                    var = free.pop()
                elif len(free) > 1:
                    # Prefer 'n' if present, otherwise pick first alphabetically
                    n_sym = sp.Symbol('n')
                    var = n_sym if n_sym in free else sorted(free, key=str)[0]
                else:
                    return _undef()
            else:
                # 4-arg form: sum(expr, var, lo, hi)
                var = vargs[1].to_sympy()
                if not isinstance(var, sp.Symbol):
                    var = sp.Symbol(str(vargs[1]))
                lo = vargs[2].to_sympy()
                hi = vargs[3].to_sympy()
            result = sp.summation(expr, (var, lo, hi))
            # Simplify the result (e.g., cos²+sin²=1 sums)
            result = sp.simplify(result)
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return SumFunction()


class ProductFunction(MathFunction):
    """Product: product(expr, var, lo, hi) or product(expr, lo, hi) with auto-detected variable."""
    def __init__(self):
        super().__init__("product", 3, 4, "Calculus", "Product")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable_or_lower"))
        self.set_argument_definition(2, SymbolicArgument("lower_or_upper"))
        self.set_argument_definition(3, SymbolicArgument("upper", does_test=False))
    def id(self) -> int: return FUNCTION_ID_PRODUCT
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            expr = vargs[0].to_sympy()
            if len(vargs) == 3:
                lo = vargs[1].to_sympy()
                hi = vargs[2].to_sympy()
                free = expr.free_symbols
                if len(free) == 1:
                    var = free.pop()
                elif len(free) > 1:
                    n_sym = sp.Symbol('n')
                    var = n_sym if n_sym in free else sorted(free, key=str)[0]
                else:
                    return _undef()
            else:
                var = vargs[1].to_sympy()
                if not isinstance(var, sp.Symbol):
                    var = sp.Symbol(str(vargs[1]))
                lo = vargs[2].to_sympy()
                hi = vargs[3].to_sympy()
            result = sp.product(expr, (var, lo, hi))
            return MathStructure.from_sympy(result)
        except Exception:
            return _undef()
    def copy(self): return ProductFunction()


# ============================================================================
# 7. MATRIX / VECTOR
# ============================================================================


class DetFunction(MathFunction):
    """Determinant: det(matrix)."""
    def __init__(self):
        super().__init__("det", 1, 1, "Matrix", "Determinant")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_DETERMINANT
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            if arr.ndim == 2:
                return _ms(_num(float(np.linalg.det(arr))))
        except Exception:
            pass
        return _undef()
    def copy(self): return DetFunction()


class InverseMatrixFunction(MathFunction):
    """Matrix inverse: inverse(matrix)."""
    def __init__(self):
        super().__init__("inverse", 1, 1, "Matrix", "Matrix inverse")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_INVERSE
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            if arr.ndim == 2:
                return _ndarray_to_mstruct(np.linalg.inv(arr))
        except Exception:
            pass
        return _undef()
    def copy(self): return InverseMatrixFunction()


class TransposeFunction(MathFunction):
    """Transpose: transpose(matrix)."""
    def __init__(self):
        super().__init__("transpose", 1, 1, "Matrix", "Transpose")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_TRANSPOSE
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            return _ndarray_to_mstruct(_mstruct_to_ndarray(vargs[0]).T)
        except Exception:
            pass
        return _undef()
    def copy(self): return TransposeFunction()


class CrossFunction(MathFunction):
    """Cross product: cross(a, b)."""
    def __init__(self):
        super().__init__("cross", 2, 2, "Matrix", "Cross product")
        self.set_argument_definition(0, VectorArgument("a"))
        self.set_argument_definition(1, VectorArgument("b"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            return _ndarray_to_mstruct(np.cross(_mstruct_to_ndarray(vargs[0]), _mstruct_to_ndarray(vargs[1])))
        except Exception:
            pass
        return _undef()
    def copy(self): return CrossFunction()


class DotFunction(MathFunction):
    """Dot product: dot(a, b)."""
    def __init__(self):
        super().__init__("dot", 2, 2, "Matrix", "Dot product")
        self.set_argument_definition(0, VectorArgument("a"))
        self.set_argument_definition(1, VectorArgument("b"))
    def id(self) -> int: return FUNCTION_ID_DOT_PRODUCT
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            result = np.dot(_mstruct_to_ndarray(vargs[0]), _mstruct_to_ndarray(vargs[1]))
            return _ms(_num(float(result))) if result.ndim == 0 else _ndarray_to_mstruct(result)
        except Exception:
            pass
        return _undef()
    def copy(self): return DotFunction()


class HadamardFunction(MathFunction):
    """Entrywise multiplication: hadamard(a, b)."""
    def __init__(self):
        super().__init__("hadamard", 2, 2, "Matrix", "Entrywise multiplication")
        self.set_argument_definition(0, MatrixArgument("a"))
        self.set_argument_definition(1, MatrixArgument("b"))
    def id(self) -> int: return FUNCTION_ID_ENTRYWISE_MULTIPLICATION
    def calculate(self, vargs, eo=None):
        try:
            return _ndarray_to_mstruct(_mstruct_to_ndarray(vargs[0]) * _mstruct_to_ndarray(vargs[1]))
        except Exception:
            pass
        return _undef()
    def copy(self): return HadamardFunction()


class TraceFunction(MathFunction):
    """Matrix trace: trace(matrix)."""
    def __init__(self):
        super().__init__("trace", 1, 1, "Matrix", "Matrix trace")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            if arr.ndim == 2:
                return _ms(_num(float(np.trace(arr))))
        except Exception:
            pass
        return _undef()
    def copy(self): return TraceFunction()


class AdjointFunction(MathFunction):
    """Adjoint (conjugate transpose): adj(matrix)."""
    def __init__(self):
        super().__init__("adj", 1, 1, "Matrix", "Adjoint (conjugate transpose)")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_ADJOINT
    def calculate(self, vargs, eo=None):
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            if arr.ndim == 2:
                return _ndarray_to_mstruct(arr.conj().T)
        except Exception:
            pass
        return _undef()
    def copy(self): return AdjointFunction()


class CofactorFunction(MathFunction):
    """Matrix cofactor: cofactor(matrix, i, j)."""
    def __init__(self):
        super().__init__("cofactor", 3, 3, "Matrix", "Matrix cofactor")
        self.set_argument_definition(0, MatrixArgument("matrix"))
        self.set_argument_definition(1, IntegerArgument("row"))
        self.set_argument_definition(2, IntegerArgument("col"))
    def id(self) -> int: return FUNCTION_ID_COFACTOR
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            i, j = _int_val(vargs[1]) - 1, _int_val(vargs[2]) - 1
            minor = np.delete(np.delete(arr, i, axis=0), j, axis=1)
            return _ms(_num(float((-1) ** (i + j) * np.linalg.det(minor))))
        except Exception:
            pass
        return _undef()
    def copy(self): return CofactorFunction()


class RrefFunction(MathFunction):
    """Reduced row echelon form: rref(matrix)."""
    def __init__(self):
        super().__init__("rref", 1, 1, "Matrix", "Reduced row echelon form")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_RREF
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            sp_matrix = sp.Matrix(_mstruct_to_ndarray(vargs[0]).tolist())
            rref_matrix, _ = sp_matrix.rref()
            rows = [MathStructure.vector(*[MathStructure(float(x)) for x in row]) for row in rref_matrix.tolist()]
            return MathStructure.matrix(rows)
        except Exception:
            return _undef()
    def copy(self): return RrefFunction()


class MatrixRankFunction(MathFunction):
    """Matrix rank: rank(matrix)."""
    def __init__(self):
        super().__init__("rank", 1, 1, "Matrix", "Matrix rank")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return FUNCTION_ID_MATRIX_RANK
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            return _ms(_num(int(np.linalg.matrix_rank(_mstruct_to_ndarray(vargs[0])))))
        except Exception:
            pass
        return _undef()
    def copy(self): return MatrixRankFunction()


class NormFunction(MathFunction):
    """Vector/matrix norm: norm(v[, p])."""
    def __init__(self):
        super().__init__("norm", 1, 2, "Matrix", "Vector/matrix norm")
        self.set_argument_definition(0, NumberArgument("v"))
        self.set_argument_definition(1, NumberArgument("p", does_test=False))
    def id(self) -> int: return FUNCTION_ID_NORM
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            p = _float_val(vargs[1]) if len(vargs) > 1 and _is_num(vargs[1]) else 2
            return _ms(_num(float(np.linalg.norm(_mstruct_to_ndarray(vargs[0]), ord=p))))
        except Exception:
            pass
        return _undef()
    def copy(self): return NormFunction()


class EigenvaluesFunction(MathFunction):
    """Eigenvalues: eigenvalues(matrix)."""
    def __init__(self):
        super().__init__("eigenvalues", 1, 1, "Matrix", "Eigenvalues")
        self.set_argument_definition(0, MatrixArgument("matrix"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            arr = _mstruct_to_ndarray(vargs[0])
            if arr.ndim == 2:
                return _ndarray_to_mstruct(np.linalg.eigvals(arr))
        except Exception:
            pass
        return _undef()
    def copy(self): return EigenvaluesFunction()


class IdentityMatrixFunction(MathFunction):
    """Identity matrix: identity(n)."""
    def __init__(self):
        super().__init__("identity", 1, 1, "Matrix", "Identity matrix")
        self.set_argument_definition(0, IntegerArgument("n"))
    def id(self) -> int: return FUNCTION_ID_IDENTITY
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            n = _int_val(vargs[0])
            if n > 0:
                return _ndarray_to_mstruct(np.eye(n))
        except Exception:
            pass
        return _undef()
    def copy(self): return IdentityMatrixFunction()


class MagnitudeFunction(MathFunction):
    """Magnitude (Euclidean norm): magnitude(v)."""
    def __init__(self):
        super().__init__("magnitude", 1, 1, "Matrix", "Euclidean magnitude")
        self.set_argument_definition(0, VectorArgument("v"))
    def id(self) -> int: return FUNCTION_ID_MAGNITUDE
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            return _ms(_num(float(np.linalg.norm(_mstruct_to_ndarray(vargs[0])))))
        except Exception:
            pass
        return _undef()
    def copy(self): return MagnitudeFunction()


# ============================================================================
# 8. STATISTICS
# ============================================================================


class MeanFunction(MathFunction):
    """Mean: mean(v)."""
    def __init__(self):
        super().__init__("mean", 1, -1, "Statistics", "Mean")
        self.set_argument_definition(0, NumberArgument("v"))
    def id(self) -> int: return FUNCTION_ID_TOTAL
    def calculate(self, vargs, eo=None):
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if vals:
            return _ms(_num(sum(vals) / len(vals)))
        return _undef()
    def copy(self): return MeanFunction()


class StdevFunction(MathFunction):
    """Standard deviation: stdev(v)."""
    def __init__(self):
        super().__init__("stdev", 1, -1, "Statistics", "Standard deviation")
        self.set_argument_definition(0, NumberArgument("v"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import statistics
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if len(vals) >= 2:
            return _ms(_num(statistics.stdev(vals)))
        return _undef()
    def copy(self): return StdevFunction()


class VarianceFunction(MathFunction):
    """Variance: variance(v)."""
    def __init__(self):
        super().__init__("variance", 1, -1, "Statistics", "Variance")
        self.set_argument_definition(0, NumberArgument("v"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import statistics
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if len(vals) >= 2:
            return _ms(_num(statistics.variance(vals)))
        return _undef()
    def copy(self): return VarianceFunction()


class MedianFunction(MathFunction):
    """Median: median(v)."""
    def __init__(self):
        super().__init__("median", 1, -1, "Statistics", "Median")
        self.set_argument_definition(0, NumberArgument("v"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import statistics
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if vals:
            return _ms(_num(statistics.median(vals)))
        return _undef()
    def copy(self): return MedianFunction()


class ModeFunction(MathFunction):
    """Mode: mode(v)."""
    def __init__(self):
        super().__init__("mode", 1, -1, "Statistics", "Mode")
        self.set_argument_definition(0, NumberArgument("v"))
    def id(self) -> int: return FUNCTION_ID_MODE
    def calculate(self, vargs, eo=None):
        import statistics
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if vals:
            try:
                return _ms(_num(statistics.mode(vals)))
            except statistics.StatisticsError:
                return _undef()
        return _undef()
    def copy(self): return ModeFunction()


class PercentileFunction(MathFunction):
    """Percentile: percentile(v, p)."""
    def __init__(self):
        super().__init__("percentile", 2, 2, "Statistics", "Percentile")
        self.set_argument_definition(0, VectorArgument("v"))
        self.set_argument_definition(1, NumberArgument("p"))
    def id(self) -> int: return FUNCTION_ID_PERCENTILE
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            vals = _extract_float_list(vargs[0])
            p = _float_val(vargs[1])
            if vals:
                return _ms(_num(float(np.percentile(vals, p))))
        except Exception:
            pass
        return _undef()
    def copy(self): return PercentileFunction()


class QuartileFunction(MathFunction):
    """Quartile: quartile(v, q)."""
    def __init__(self):
        super().__init__("quartile", 2, 2, "Statistics", "Quartile")
        self.set_argument_definition(0, VectorArgument("v"))
        self.set_argument_definition(1, IntegerArgument("q"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            vals = _extract_float_list(vargs[0])
            q = _int_val(vargs[1])
            if vals and 0 <= q <= 4:
                return _ms(_num(float(np.percentile(vals, q * 25))))
        except Exception:
            pass
        return _undef()
    def copy(self): return QuartileFunction()


class NormDistFunction(MathFunction):
    """Normal distribution PDF: normdist(x, mean, stddev)."""
    def __init__(self):
        super().__init__("normdist", 3, 3, "Statistics", "Normal distribution")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("mean"))
        self.set_argument_definition(2, NumberArgument("stddev"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        try:
            from scipy.stats import norm
            x = _float_val(vargs[0])
            mean = _float_val(vargs[1])
            stddev = _float_val(vargs[2])
            if stddev > 0:
                return _ms(_num(float(norm.pdf(x, mean, stddev))))
        except Exception:
            pass
        return _undef()
    def copy(self): return NormDistFunction()


class MinFunction(MathFunction):
    """Minimum: min(a, b, ...) or min(vector)."""
    def __init__(self):
        super().__init__("min", 1, -1, "Statistics", "Minimum")
        self.set_argument_definition(0, NumberArgument("a"))
    def id(self) -> int: return FUNCTION_ID_MIN
    def calculate(self, vargs, eo=None):
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if vals:
            return _ms(_num(min(vals)))
        return _undef()
    def copy(self): return MinFunction()


class MaxFunction(MathFunction):
    """Maximum: max(a, b, ...) or max(vector)."""
    def __init__(self):
        super().__init__("max", 1, -1, "Statistics", "Maximum")
        self.set_argument_definition(0, NumberArgument("a"))
    def id(self) -> int: return FUNCTION_ID_MAX
    def calculate(self, vargs, eo=None):
        vals = []
        for v in vargs:
            if v.is_vector():
                vals.extend(_extract_float_list(v))
            elif _is_num(v):
                vals.append(_float_val(v))
        if vals:
            return _ms(_num(max(vals)))
        return _undef()
    def copy(self): return MaxFunction()


class RandFunction(MathFunction):
    """Random number: rand([max])."""
    def __init__(self):
        super().__init__("rand", 0, 1, "Statistics", "Random number")
        self.set_argument_definition(0, NumberArgument("max", does_test=False))
    def id(self) -> int: return FUNCTION_ID_RAND
    def calculate(self, vargs, eo=None):
        if vargs and _is_num(vargs[0]):
            return _ms(_num(random.uniform(0, _float_val(vargs[0]))))
        return _ms(_num(random.random()))
    def copy(self): return RandFunction()


class CorrelationFunction(MathFunction):
    """Correlation: correlation(x, y)."""
    def __init__(self):
        super().__init__("correlation", 2, 2, "Statistics", "Pearson correlation")
        self.set_argument_definition(0, Argument("x"))
        self.set_argument_definition(1, Argument("y"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            x = _extract_float_list(vargs[0])
            y = _extract_float_list(vargs[1])
            if len(x) == len(y) and len(x) >= 2:
                return _ms(_num(float(np.corrcoef(x, y)[0, 1])))
        except Exception:
            pass
        return _undef()
    def copy(self): return CorrelationFunction()


class CovarianceFunction(MathFunction):
    """Covariance: covariance(x, y)."""
    def __init__(self):
        super().__init__("covariance", 2, 2, "Statistics", "Covariance")
        self.set_argument_definition(0, Argument("x"))
        self.set_argument_definition(1, Argument("y"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        import numpy as np
        try:
            x = _extract_float_list(vargs[0])
            y = _extract_float_list(vargs[1])
            if len(x) == len(y) and len(x) >= 2:
                return _ms(_num(float(np.cov(x, y)[0, 1])))
        except Exception:
            pass
        return _undef()
    def copy(self): return CovarianceFunction()


# ============================================================================
# 9. BASE CONVERSION
# ============================================================================


class BinFunction(MathFunction):
    """Binary representation: bin(x) or bin(x, width).

    Returns nibble-aligned binary.  When *width* is given, zero-pads
    to at least that many bits (e.g., bin(42, 16) → 0000 0000 0010 1010).
    """
    def __init__(self):
        super().__init__("bin", 1, 2, "Base", "Binary representation")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("width"))
    def id(self) -> int: return FUNCTION_ID_BIN
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            # Determine minimum bit width
            width = 0
            if len(vargs) > 1 and _is_num(vargs[1]):
                width = _int_val(vargs[1])
            bits = format(abs(n), 'b')
            # Pad to specified width or at least nibble-aligned
            min_bits = max(width, ((len(bits) + 3) // 4) * 4)
            bits = bits.zfill(min_bits)
            # Space-separate nibbles
            formatted = ' '.join(bits[i:i+4] for i in range(0, len(bits), 4))
            sign = '-' if n < 0 else ''
            return MathStructure.from_symbol(sign + formatted)
        return _undef()
    def copy(self): return BinFunction()


class OctFunction(MathFunction):
    """Octal representation: oct(x)."""
    def __init__(self):
        super().__init__("oct", 1, 1, "Base", "Octal representation")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_OCT
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            sign = '-' if n < 0 else ''
            return MathStructure.from_symbol(sign + '0' + format(abs(n), 'o'))
        return _undef()
    def copy(self): return OctFunction()


class HexFunction(MathFunction):
    """Hexadecimal representation: hex(x)."""
    def __init__(self):
        super().__init__("hex", 1, 1, "Base", "Hexadecimal representation")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_HEX
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            sign = '-' if n < 0 else ''
            return MathStructure.from_symbol(sign + '0x' + format(abs(n), 'X'))
        return _undef()
    def copy(self): return HexFunction()


class BaseFunction(MathFunction):
    """Base conversion: base(x, b).

    Supports integer bases 2-36 with alphanumeric digits, and non-integer
    bases (e.g., sqrt(2)) with greedy digit selection using digits 0..floor(b).
    """
    def __init__(self):
        super().__init__("base", 2, 2, "Base", "Base conversion")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, NumberArgument("base"))
    def id(self) -> int: return FUNCTION_ID_BASE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            n = _int_val(vargs[0])
            b_num = vargs[1]
            # Get base as float for non-integer bases
            try:
                b_val = b_num.number.to_float() if hasattr(b_num, 'number') and b_num.number is not None else float(_float_val(b_num))
            except Exception:
                b_val = _float_val(b_num)
            # Integer base 2-36: use alphanumeric digits
            if b_val == int(b_val) and 2 <= int(b_val) <= 36:
                b = int(b_val)
                import string
                digits = string.digits + string.ascii_lowercase
                if n == 0:
                    return MathStructure.from_symbol("0")
                result = ""
                neg = n < 0
                n = abs(n)
                while n:
                    result = digits[n % b] + result
                    n //= b
                return MathStructure.from_symbol(("-" + result) if neg else result)
            # Non-integer base: greedy algorithm with digits 0..floor(b)
            if b_val > 1:
                max_digit = int(b_val)  # floor(base)
                val = float(abs(n))
                if val == 0:
                    return MathStructure.from_symbol("0")
                # Find highest power
                import math
                p = int(math.log(val) / math.log(b_val))
                # Ensure p is high enough (handle floating-point rounding)
                while b_val ** (p + 1) <= val * (1 + 1e-12):
                    p += 1
                result = ""
                for exp in range(p, -1, -1):
                    power = b_val ** exp
                    digit = min(max_digit, int(val / power + 1e-12))
                    val -= digit * power
                    # Clamp negative residuals from floating-point error
                    if val < 0 and val > -1e-10:
                        val = 0.0
                    result += str(digit)
                # Trim leading zeros but keep at least one digit
                result = result.lstrip('0') or '0'
                sign = '-' if n < 0 else ''
                return MathStructure.from_symbol(sign + result)
        return _undef()
    def copy(self): return BaseFunction()


class RomanFunction(MathFunction):
    """Roman numeral: roman(x)."""
    def __init__(self):
        super().__init__("roman", 1, 1, "Base", "Roman numeral")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ROMAN
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            if 1 <= n <= 3999:
                val_map = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),
                           (100,'C'),(90,'XC'),(50,'L'),(40,'XL'),
                           (10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
                result = ''
                for val, sym in val_map:
                    while n >= val:
                        result += sym
                        n -= val
                return MathStructure.from_symbol(result)
        return _undef()
    def copy(self): return RomanFunction()


class FloatFunction(MathFunction):
    """IEEE 754 float: float(x).

    Returns the IEEE 754 single-precision (32-bit) binary representation
    with nibble spacing, e.g. '0100 0000 0100 1001 0000 1111 1101 0000'.
    """
    def __init__(self):
        super().__init__("float", 1, 1, "Base", "IEEE 754 float")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_IEEE754_FLOAT
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            import struct
            val = _float_val(vargs[0])
            raw = struct.pack('>f', val)
            bits = ''.join(format(b, '08b') for b in raw)
            formatted = ' '.join(bits[i:i+4] for i in range(0, len(bits), 4))
            return MathStructure.from_symbol(formatted)
        return _undef()
    def copy(self): return FloatFunction()


class FloatErrorFunction(MathFunction):
    """IEEE 754 float error: floatError(x)."""
    def __init__(self):
        super().__init__("floatError", 1, 1, "Base", "IEEE 754 float error")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_IEEE754_FLOAT_ERROR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            import struct
            val = _float_val(vargs[0])
            recovered = struct.unpack('>d', struct.pack('>d', val))[0]
            return _ms(_num(abs(val - recovered)))
        return _undef()
    def copy(self): return FloatErrorFunction()


class BasesFunction(MathFunction):
    """Show number in multiple bases: bases(x).

    Returns a single string: 'bin = oct = dec = hex' with nibble-aligned
    binary, leading-zero octal, plain decimal, and 0x-prefixed hex.
    """
    def __init__(self):
        super().__init__("bases", 1, 1, "Base", "Multiple base representations")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            abs_n = abs(n)
            sign = '-' if n < 0 else ''
            # Binary: nibble-aligned, space-separated (16-bit minimum)
            bits = format(abs_n, 'b')
            min_bits = max(16, ((len(bits) + 3) // 4) * 4)
            bits = bits.zfill(min_bits)
            bin_str = sign + ' '.join(bits[i:i+4] for i in range(0, len(bits), 4))
            # Octal: leading zero
            oct_str = sign + '0' + format(abs_n, 'o')
            # Decimal
            dec_str = str(n)
            # Hex: 0x prefix, uppercase
            hex_str = sign + '0x' + format(abs_n, 'X')
            return MathStructure.from_symbol(
                f"{bin_str} = {oct_str} = {dec_str} = {hex_str}"
            )
        return _undef()
    def copy(self): return BasesFunction()


# ============================================================================
# 10. DATE/TIME
# ============================================================================


class DateFunction(MathFunction):
    """Date: date(y, m, d)."""
    def __init__(self):
        super().__init__("date", 3, 3, "Date & Time", "Create date")
        self.set_argument_definition(0, IntegerArgument("year"))
        self.set_argument_definition(1, IntegerArgument("month"))
        self.set_argument_definition(2, IntegerArgument("day"))
    def id(self) -> int: return FUNCTION_ID_DATE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_symbol(str(datetime.date(_int_val(vargs[0]), _int_val(vargs[1]), _int_val(vargs[2]))))
        except Exception:
            return _undef()
    def copy(self): return DateFunction()


class TimestampFunction(MathFunction):
    """Timestamp: timestamp([date])."""
    def __init__(self):
        super().__init__("timestamp", 0, 1, "Date & Time", "Unix timestamp")
        self.set_argument_definition(0, TextArgument("date", does_test=False))
    def id(self) -> int: return FUNCTION_ID_TIMESTAMP
    def calculate(self, vargs, eo=None):
        if vargs and vargs[0].is_symbolic():
            try:
                return _ms(_num(int(datetime.datetime.fromisoformat(str(vargs[0])).timestamp())))
            except Exception:
                pass
        return _ms(_num(int(datetime.datetime.now().timestamp())))
    def copy(self): return TimestampFunction()


class StampToDateFunction(MathFunction):
    """Stamp to date: stamptodate(timestamp)."""
    def __init__(self):
        super().__init__("stamptodate", 1, 1, "Date & Time", "Timestamp to date")
        self.set_argument_definition(0, NumberArgument("timestamp"))
    def id(self) -> int: return FUNCTION_ID_TIMESTAMP_TO_DATE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        if _is_num(vargs[0]):
            return MathStructure.from_symbol(datetime.datetime.fromtimestamp(_float_val(vargs[0])).isoformat())
        return _undef()
    def copy(self): return StampToDateFunction()


class DaysFunction(MathFunction):
    """Days between dates: days(date1, date2)."""
    def __init__(self):
        super().__init__("days", 2, 2, "Date & Time", "Days between dates")
        self.set_argument_definition(0, TextArgument("date1"))
        self.set_argument_definition(1, TextArgument("date2"))
    def id(self) -> int: return FUNCTION_ID_DAYS
    def calculate(self, vargs, eo=None):
        try:
            return _ms(_num((datetime.date.fromisoformat(str(vargs[1])) - datetime.date.fromisoformat(str(vargs[0]))).days))
        except Exception:
            return _undef()
    def copy(self): return DaysFunction()


class WeeksFunction(MathFunction):
    """Weeks between dates: weeks(date1, date2)."""
    def __init__(self):
        super().__init__("weeks", 2, 2, "Date & Time", "Weeks between dates")
        self.set_argument_definition(0, TextArgument("date1"))
        self.set_argument_definition(1, TextArgument("date2"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        try:
            return _ms(_num((datetime.date.fromisoformat(str(vargs[1])) - datetime.date.fromisoformat(str(vargs[0]))).days // 7))
        except Exception:
            return _undef()
    def copy(self): return WeeksFunction()


class MonthsFunction(MathFunction):
    """Months between dates: months(date1, date2)."""
    def __init__(self):
        super().__init__("months", 2, 2, "Date & Time", "Months between dates")
        self.set_argument_definition(0, TextArgument("date1"))
        self.set_argument_definition(1, TextArgument("date2"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        try:
            d1 = datetime.date.fromisoformat(str(vargs[0]))
            d2 = datetime.date.fromisoformat(str(vargs[1]))
            return _ms(_num((d2.year - d1.year) * 12 + d2.month - d1.month))
        except Exception:
            return _undef()
    def copy(self): return MonthsFunction()


class YearsFunction(MathFunction):
    """Years between dates: years(date1, date2)."""
    def __init__(self):
        super().__init__("years", 2, 2, "Date & Time", "Years between dates")
        self.set_argument_definition(0, TextArgument("date1"))
        self.set_argument_definition(1, TextArgument("date2"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        try:
            return _ms(_num(datetime.date.fromisoformat(str(vargs[1])).year - datetime.date.fromisoformat(str(vargs[0])).year))
        except Exception:
            return _undef()
    def copy(self): return YearsFunction()


class NowFunction(MathFunction):
    """Current date/time: now()."""
    def __init__(self):
        super().__init__("now", 0, 0, "Date & Time", "Current date/time")
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        return MathStructure.from_symbol(datetime.datetime.now().isoformat())
    def copy(self): return NowFunction()


class TodayFunction(MathFunction):
    """Today's date: today()."""
    def __init__(self):
        super().__init__("today", 0, 0, "Date & Time", "Today's date")
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        return MathStructure.from_symbol(str(datetime.date.today()))
    def copy(self): return TodayFunction()


class LunarPhaseFunction(MathFunction):
    """Lunar phase: lunarphase([date])."""
    def __init__(self):
        super().__init__("lunarphase", 0, 1, "Date & Time", "Lunar phase")
        self.set_argument_definition(0, TextArgument("date", does_test=False))
    def id(self) -> int: return FUNCTION_ID_LUNAR_PHASE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        try:
            d = datetime.date.fromisoformat(str(vargs[0])) if vargs and vargs[0].is_symbolic() else datetime.date.today()
            days_since = (d - datetime.date(2000, 1, 6)).days
            phase = (days_since % 29.53059) / 29.53059
            names = ["New Moon","Waxing Crescent","First Quarter","Waxing Gibbous",
                     "Full Moon","Waning Gibbous","Last Quarter","Waning Crescent"]
            return MathStructure.from_symbol(f"{names[int(phase * 8) % 8]} ({phase:.1%})")
        except Exception:
            return _undef()
    def copy(self): return LunarPhaseFunction()


# ============================================================================
# 11. SPECIAL FUNCTIONS
# ============================================================================


class ZetaFunction(MathFunction):
    """Riemann zeta: zeta(s)."""
    def __init__(self):
        super().__init__("zeta", 1, 1, "Special", "Riemann zeta function")
        self.set_argument_definition(0, NumberArgument("s"))
    def id(self) -> int: return FUNCTION_ID_ZETA
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.zeta(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return ZetaFunction()


class BetaFunction(MathFunction):
    """Beta function: beta(a, b)."""
    def __init__(self):
        super().__init__("beta", 2, 2, "Special", "Beta function")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_BETA
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.beta(vargs[0].to_sympy(), vargs[1].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return BetaFunction()


class ErfFunction(MathFunction):
    """Error function: erf(x)."""
    def __init__(self):
        super().__init__("erf", 1, 1, "Special", "Error function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ERF
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.erf(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return ErfFunction()


class ErfcFunction(MathFunction):
    """Complementary error function: erfc(x)."""
    def __init__(self):
        super().__init__("erfc", 1, 1, "Special", "Complementary error function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ERFC
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.erfc(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return ErfcFunction()


class BesseljFunction(MathFunction):
    """Bessel J: besselj(n, x)."""
    def __init__(self):
        super().__init__("besselj", 2, 2, "Special", "Bessel J")
        self.set_argument_definition(0, NumberArgument("n"))
        self.set_argument_definition(1, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_BESSELJ
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.besselj(vargs[0].to_sympy(), vargs[1].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return BesseljFunction()


class BesselyFunction(MathFunction):
    """Bessel Y: bessely(n, x)."""
    def __init__(self):
        super().__init__("bessely", 2, 2, "Special", "Bessel Y")
        self.set_argument_definition(0, NumberArgument("n"))
        self.set_argument_definition(1, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_BESSELY
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.bessely(vargs[0].to_sympy(), vargs[1].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return BesselyFunction()


class AiryFunction(MathFunction):
    """Airy function: airy(x)."""
    def __init__(self):
        super().__init__("airy", 1, 1, "Special", "Airy function Ai")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_AIRY
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.airyai(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return AiryFunction()


class FresnelSFunction(MathFunction):
    """Fresnel S: fresnels(x)."""
    def __init__(self):
        super().__init__("fresnels", 1, 1, "Special", "Fresnel S integral")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_FRESNEL_S
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.fresnels(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return FresnelSFunction()


class FresnelCFunction(MathFunction):
    """Fresnel C: fresnelc(x)."""
    def __init__(self):
        super().__init__("fresnelc", 1, 1, "Special", "Fresnel C integral")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_FRESNEL_C
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.fresnelc(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return FresnelCFunction()


class DigammaFunction(MathFunction):
    """Digamma function: digamma(x)."""
    def __init__(self):
        super().__init__("digamma", 1, 1, "Special", "Digamma function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_DIGAMMA
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.digamma(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return DigammaFunction()


class HeavisideFunction(MathFunction):
    """Heaviside step function: heaviside(x)."""
    def __init__(self):
        super().__init__("heaviside", 1, 1, "Special", "Heaviside step function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_HEAVISIDE
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.N(sp.Heaviside(vargs[0].to_sympy()), 15))
        except Exception:
            return _undef()
    def copy(self): return HeavisideFunction()


class DiracFunction(MathFunction):
    """Dirac delta: dirac(x)."""
    def __init__(self):
        super().__init__("dirac", 1, 1, "Special", "Dirac delta function")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_DIRAC
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            return MathStructure.from_sympy(sp.DiracDelta(vargs[0].to_sympy()))
        except Exception:
            return _undef()
    def copy(self): return DiracFunction()


# ============================================================================
# 12. LOGICAL / BITWISE
# ============================================================================


class BitAndFunction(MathFunction):
    """Bitwise AND: bitand(a, b)."""
    def __init__(self):
        super().__init__("bitand", 2, 2, "Bitwise", "Bitwise AND")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            return _ms(_num(_int_val(vargs[0]) & _int_val(vargs[1])))
        return _undef()
    def copy(self): return BitAndFunction()


class BitOrFunction(MathFunction):
    """Bitwise OR: bitor(a, b)."""
    def __init__(self):
        super().__init__("bitor", 2, 2, "Bitwise", "Bitwise OR")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            return _ms(_num(_int_val(vargs[0]) | _int_val(vargs[1])))
        return _undef()
    def copy(self): return BitOrFunction()


class BitXorFunction(MathFunction):
    """Bitwise XOR: bitxor(a, b)."""
    def __init__(self):
        super().__init__("bitxor", 2, 2, "Bitwise", "Bitwise XOR")
        self.set_argument_definition(0, NumberArgument("a"))
        self.set_argument_definition(1, NumberArgument("b"))
    def id(self) -> int: return FUNCTION_ID_BIT_XOR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            return _ms(_num(_int_val(vargs[0]) ^ _int_val(vargs[1])))
        return _undef()
    def copy(self): return BitXorFunction()


class BitNotFunction(MathFunction):
    """Bitwise NOT: bitnot(x[, bits])."""
    def __init__(self):
        super().__init__("bitnot", 1, 2, "Bitwise", "Bitwise NOT")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, IntegerArgument("bits", does_test=False))
    def id(self) -> int: return FUNCTION_ID_BIT_CMP
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            x = _int_val(vargs[0])
            bits = _int_val(vargs[1]) if len(vargs) > 1 and _is_num(vargs[1]) else 32
            return _ms(_num(~x & ((1 << bits) - 1)))
        return _undef()
    def copy(self): return BitNotFunction()


class ShiftFunction(MathFunction):
    """Bit shift: shift(x, n)."""
    def __init__(self):
        super().__init__("shift", 2, 2, "Bitwise", "Bit shift")
        self.set_argument_definition(0, NumberArgument("x"))
        self.set_argument_definition(1, IntegerArgument("n"))
    def id(self) -> int: return FUNCTION_ID_SHIFT
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            x = _int_val(vargs[0])
            n = _int_val(vargs[1])
            return _ms(_num(x << n if n >= 0 else x >> (-n)))
        return _undef()
    def copy(self): return ShiftFunction()


class LogicalAndFunction(MathFunction):
    """Logical AND: and(a, b)."""
    def __init__(self):
        super().__init__("and", 2, -1, "Logical", "Logical AND")
        self.set_argument_definition(0, BooleanArgument("a"))
        self.set_argument_definition(1, BooleanArgument("b"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        if all(_is_num(v) for v in vargs):
            return _ms(_num(1 if all(_float_val(v) != 0 for v in vargs) else 0))
        return _undef()
    def copy(self): return LogicalAndFunction()


class LogicalOrFunction(MathFunction):
    """Logical OR: or(a, b)."""
    def __init__(self):
        super().__init__("or", 2, -1, "Logical", "Logical OR")
        self.set_argument_definition(0, BooleanArgument("a"))
        self.set_argument_definition(1, BooleanArgument("b"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        if all(_is_num(v) for v in vargs):
            return _ms(_num(1 if any(_float_val(v) != 0 for v in vargs) else 0))
        return _undef()
    def copy(self): return LogicalOrFunction()


class LogicalXorFunction(MathFunction):
    """Logical XOR: xor(a, b)."""
    def __init__(self):
        super().__init__("xor", 2, 2, "Logical", "Logical XOR")
        self.set_argument_definition(0, BooleanArgument("a"))
        self.set_argument_definition(1, BooleanArgument("b"))
    def id(self) -> int: return FUNCTION_ID_XOR
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and _is_num(vargs[1]):
            a = _float_val(vargs[0]) != 0
            b = _float_val(vargs[1]) != 0
            return _ms(_num(1 if (a ^ b) else 0))
        return _undef()
    def copy(self): return LogicalXorFunction()


class LogicalNotFunction(MathFunction):
    """Logical NOT: not(x)."""
    def __init__(self):
        super().__init__("not", 1, 1, "Logical", "Logical NOT")
        self.set_argument_definition(0, BooleanArgument("x"))
    def id(self) -> int: return 0
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return _ms(_num(0 if _float_val(vargs[0]) != 0 else 1))
        return _undef()
    def copy(self): return LogicalNotFunction()


# ============================================================================
# 13. UTILITY FUNCTIONS
# ============================================================================


class IfFunction(MathFunction):
    """Conditional: if(condition, then, else)."""
    def __init__(self):
        super().__init__("if", 2, 3, "Utility", "Conditional")
        self.set_argument_definition(0, BooleanArgument("condition"))
        self.set_argument_definition(1, Argument("then"))
        self.set_argument_definition(2, Argument("else", does_test=False))
    def id(self) -> int: return FUNCTION_ID_IF
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            return vargs[1] if _float_val(vargs[0]) != 0 else (vargs[2] if len(vargs) > 2 else _undef())
        return _undef()
    def copy(self): return IfFunction()


class ForFunction(MathFunction):
    """For loop: for(var, start, end, expr)."""
    def __init__(self):
        super().__init__("for", 4, 4, "Utility", "For loop")
        self.set_argument_definition(0, SymbolicArgument("variable"))
        self.set_argument_definition(1, NumberArgument("start"))
        self.set_argument_definition(2, NumberArgument("end"))
        self.set_argument_definition(3, SymbolicArgument("expression"))
    def id(self) -> int: return FUNCTION_ID_FOR
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            var = sp.Symbol(str(vargs[0]))
            start = int(vargs[1].to_sympy())
            end = int(vargs[2].to_sympy())
            expr = vargs[3].to_sympy()
            total = sp.Integer(0)
            for i in range(start, end + 1):
                total += expr.subs(var, i)
            return MathStructure.from_sympy(total)
        except Exception:
            return _undef()
    def copy(self): return ForFunction()


class GenVectorFunction(MathFunction):
    """Generate vector: genvector(expr, var, n)."""
    def __init__(self):
        super().__init__("genvector", 3, 3, "Utility", "Generate vector")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, SymbolicArgument("variable"))
        self.set_argument_definition(2, IntegerArgument("n"))
    def id(self) -> int: return FUNCTION_ID_GENERATE_VECTOR
    def calculate(self, vargs, eo=None):
        import sympy as sp
        from pyqalculate.math_structure import MathStructure
        try:
            expr = vargs[0].to_sympy()
            var = sp.Symbol(str(vargs[1]))
            n = _int_val(vargs[2])
            return MathStructure.vector(*[MathStructure.from_sympy(expr.subs(var, i)) for i in range(1, n + 1)])
        except Exception:
            return _undef()
    def copy(self): return GenVectorFunction()


class LoadFunction(MathFunction):
    """Load CSV file: load(filename[, delimiter]).

    Imports a CSV file and returns the data as a matrix.
    Also registers each column as a variable.

    Examples:
        load("data.csv")
        load("data.csv", ";")
    """
    def __init__(self):
        super().__init__("load", 1, 2, "Utility", "Load CSV file")
        self.set_argument_definition(0, TextArgument("filename"))
        self.set_argument_definition(1, TextArgument("delimiter", does_test=False))
    def id(self) -> int: return FUNCTION_ID_LOAD
    def calculate(self, vargs, eo=None):
        from pyqalculate.calculator import get_calculator
        filename = str(vargs[0])
        delimiter = str(vargs[1]) if len(vargs) > 1 else ","
        calc = get_calculator()
        result = calc.importCSV(filename, delimiter=delimiter, to_matrix=True)
        return result
    def copy(self): return LoadFunction()


class ExportFunction(MathFunction):
    """Export to CSV file: export(data, filename[, delimiter]).

    Exports a matrix or vector to a CSV file.

    Examples:
        export(mydata, "output.csv")
        export(mydata, "output.csv", ";")
    """
    def __init__(self):
        super().__init__("export", 2, 3, "Utility", "Export to CSV file")
        self.set_argument_definition(0, Argument("data"))
        self.set_argument_definition(1, TextArgument("filename"))
        self.set_argument_definition(2, TextArgument("delimiter", does_test=False))
    def id(self) -> int: return FUNCTION_ID_EXPORT
    def calculate(self, vargs, eo=None):
        from pyqalculate.calculator import get_calculator
        data = vargs[0]
        filename = str(vargs[1])
        delimiter = str(vargs[2]) if len(vargs) > 2 else ","
        calc = get_calculator()
        success = calc.exportCSV(data, filename, delimiter=delimiter)
        if success:
            return _ms(_num(1))
        return _undef()
    def copy(self): return ExportFunction()


class ReplaceFunction(MathFunction):
    """Replace: replace(expr, old, new)."""
    def __init__(self):
        super().__init__("replace", 3, 3, "Utility", "String/expression replace")
        self.set_argument_definition(0, TextArgument("text"))
        self.set_argument_definition(1, TextArgument("old"))
        self.set_argument_definition(2, TextArgument("new"))
    def id(self) -> int: return FUNCTION_ID_REPLACE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        return MathStructure.from_symbol(str(vargs[0]).replace(str(vargs[1]), str(vargs[2])))
    def copy(self): return ReplaceFunction()


class ToStringFunction(MathFunction):
    """To string: tostring(x)."""
    def __init__(self):
        super().__init__("tostring", 1, 1, "Utility", "Convert to string")
        self.set_argument_definition(0, Argument("x"))
    def id(self) -> int: return FUNCTION_ID_STRING
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        return MathStructure.from_symbol(str(vargs[0]))
    def copy(self): return ToStringFunction()


class LengthFunction(MathFunction):
    """String/vector length: length(s)."""
    def __init__(self):
        super().__init__("length", 1, 1, "Utility", "String/vector length")
        self.set_argument_definition(0, Argument("s"))
    def id(self) -> int: return FUNCTION_ID_LENGTH
    def calculate(self, vargs, eo=None):
        if vargs[0].is_vector():
            return _ms(_num(len(vargs[0])))
        if vargs[0].is_symbolic():
            return _ms(_num(len(str(vargs[0]))))
        return _ms(_num(1))
    def copy(self): return LengthFunction()


class ConcatenateFunction(MathFunction):
    """Concatenate: concatenate(a, b, ...)."""
    def __init__(self):
        super().__init__("concatenate", 2, -1, "Utility", "Concatenate strings")
        self.set_argument_definition(0, Argument("a"))
        self.set_argument_definition(1, Argument("b"))
    def id(self) -> int: return FUNCTION_ID_CONCATENATE
    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure
        return MathStructure.from_symbol(''.join(str(v) for v in vargs))
    def copy(self): return ConcatenateFunction()


class IsNumberFunction(MathFunction):
    """Is number: is_number(x)."""
    def __init__(self):
        super().__init__("is_number", 1, 1, "Utility", "Is number test")
        self.set_argument_definition(0, Argument("x"))
    def id(self) -> int: return FUNCTION_ID_IS_NUMBER
    def calculate(self, vargs, eo=None):
        return _ms(_num(1 if _is_num(vargs[0]) else 0))
    def copy(self): return IsNumberFunction()


class IsRealFunction(MathFunction):
    """Is real: is_real(x)."""
    def __init__(self):
        super().__init__("is_real", 1, 1, "Utility", "Is real test")
        self.set_argument_definition(0, Argument("x"))
    def id(self) -> int: return FUNCTION_ID_IS_REAL
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(_num(1 if vargs[0].number.is_real() else 0))
        return _ms(_num(0))
    def copy(self): return IsRealFunction()


class IsRationalFunction(MathFunction):
    """Is rational: is_rational(x)."""
    def __init__(self):
        super().__init__("is_rational", 1, 1, "Utility", "Is rational test")
        self.set_argument_definition(0, Argument("x"))
    def id(self) -> int: return FUNCTION_ID_IS_RATIONAL
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(_num(1 if vargs[0].number.is_rational() else 0))
        return _ms(_num(0))
    def copy(self): return IsRationalFunction()


class IsIntegerFunction(MathFunction):
    """Is integer: is_integer(x)."""
    def __init__(self):
        super().__init__("is_integer", 1, 1, "Utility", "Is integer test")
        self.set_argument_definition(0, Argument("x"))
    def id(self) -> int: return FUNCTION_ID_IS_INTEGER
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]) and vargs[0].number is not None:
            return _ms(_num(1 if vargs[0].number.is_integer() else 0))
        return _ms(_num(0))
    def copy(self): return IsIntegerFunction()


class OddFunction(MathFunction):
    """Is odd: odd(x)."""
    def __init__(self):
        super().__init__("odd", 1, 1, "Utility", "Is odd test")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_ODD
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            return _ms(_num(1 if n % 2 != 0 else 0))
        return _undef()
    def copy(self): return OddFunction()


class EvenFunction(MathFunction):
    """Is even: even(x)."""
    def __init__(self):
        super().__init__("even", 1, 1, "Utility", "Is even test")
        self.set_argument_definition(0, NumberArgument("x"))
    def id(self) -> int: return FUNCTION_ID_EVEN
    def calculate(self, vargs, eo=None):
        if _is_num(vargs[0]):
            n = _int_val(vargs[0])
            return _ms(_num(1 if n % 2 == 0 else 0))
        return _undef()
    def copy(self): return EvenFunction()


class PlotFunction(MathFunction):
    """Plot a mathematical expression.

    Usage: plot(expression, x_min, x_max[, filename])

    Plots the given expression over the range [x_min, x_max].
    If filename is provided, saves to file; otherwise displays interactively.

    Examples:
        plot(x^2, -5, 5)
        plot(sin(x), 0, 2*pi, "sine.png")
    """

    def __init__(self):
        super().__init__("plot", 1, 4, "Utility", "Plot function")
        self.set_argument_definition(0, SymbolicArgument("expression"))
        self.set_argument_definition(1, NumberArgument("x_min", does_test=False))
        self.set_argument_definition(2, NumberArgument("x_max", does_test=False))
        self.set_argument_definition(3, TextArgument("filename", does_test=False))

    def id(self) -> int:
        return FUNCTION_ID_PLOT

    def calculate(self, vargs, eo=None):
        from pyqalculate.math_structure import MathStructure

        # Extract expression as string
        expr_str = str(vargs[0]) if len(vargs) > 0 else "x"
        # Convert MathStructure notation to Python math notation
        expr_str = expr_str.replace("^", "**")

        # Extract x range
        x_min = _float_val(vargs[1]) if len(vargs) > 1 and _is_num(vargs[1]) else -10.0
        x_max = _float_val(vargs[2]) if len(vargs) > 2 and _is_num(vargs[2]) else 10.0

        # Extract filename
        filename = str(vargs[3]) if len(vargs) > 3 else ""

        try:
            from pyqalculate.plot import Plotter
            plotter = Plotter()
            result_path = plotter.plot(expr_str, x_min=x_min, x_max=x_max, filename=filename)

            if result_path:
                return MathStructure.from_symbol(result_path)
            else:
                return MathStructure.from_symbol("Plot displayed")
        except ImportError:
            return MathStructure.from_symbol(
                "Error: matplotlib is required for plotting. "
                "Install with: pip install matplotlib"
            )
        except Exception as e:
            return MathStructure.from_symbol(f"Plot error: {e}")

    def copy(self):
        return PlotFunction()


# ============================================================================
# Signal Processing Functions
# ============================================================================


class FftFunction(MathFunction):
    def __init__(self):
        super().__init__("fft", 1, 1, "Signal Processing", "Fast Fourier Transform")
        self.set_argument_definition(0, VectorArgument("signal"))

    def id(self) -> int:
        return FUNCTION_ID_FFT

    def calculate(self, vargs, eo=None):
        import numpy as np
        import math
        try:
            vals = _extract_complex_list(vargs[0])
            if not vals:
                return _undef()
            if any(math.isnan(v.real) or math.isnan(v.imag) or math.isinf(v.real) or math.isinf(v.imag) for v in vals):
                return _undef()
            result = np.fft.fft(vals)
            return _ndarray_to_mstruct_complex(result)
        except Exception:
            return _undef()

    def copy(self):
        return FftFunction()


class IfftFunction(MathFunction):
    """Inverse Fast Fourier Transform: ifft(vector)."""

    def __init__(self):
        super().__init__("ifft", 1, 1, "Signal Processing", "Inverse Fast Fourier Transform")
        self.set_argument_definition(0, VectorArgument("signal"))

    def id(self) -> int:
        return FUNCTION_ID_IFFT

    def calculate(self, vargs, eo=None):
        import numpy as np
        import math
        try:
            vals = _extract_complex_list(vargs[0])
            if not vals:
                return _undef()
            if any(math.isnan(v.real) or math.isnan(v.imag) or math.isinf(v.real) or math.isinf(v.imag) for v in vals):
                return _undef()
            result = np.fft.ifft(vals)
            return _ndarray_to_mstruct_complex(result)
        except Exception:
            return _undef()

    def copy(self):
        return IfftFunction()


# ============================================================================
# FunctionRegistry
# ============================================================================


class FunctionRegistry:
    """Registry of all builtin mathematical functions.

    Functions are registered by name and can be looked up by name or ID.
    """

    def __init__(self) -> None:
        self._by_name: dict[str, MathFunction] = {}
        self._by_id: dict[int, MathFunction] = {}

    def register(self, func: MathFunction) -> None:
        """Register a function."""
        self._by_name[func.name().lower()] = func
        if func.id() != 0:
            self._by_id[func.id()] = func

    def get_by_name(self, name: str) -> MathFunction | None:
        """Look up a function by name (case-insensitive)."""
        return self._by_name.get(name.lower())

    def get_by_id(self, func_id: int) -> MathFunction | None:
        """Look up a function by ID."""
        return self._by_id.get(func_id)

    def count(self) -> int:
        return len(self._by_name)

    def names(self) -> list[str]:
        return sorted(self._by_name.keys())


# ============================================================================
# Default registry with ALL builtin functions
# ============================================================================

_default_registry: FunctionRegistry | None = None


def get_default_registry() -> FunctionRegistry:
    """Return the default function registry with all builtin functions."""
    global _default_registry
    if _default_registry is None:
        _default_registry = FunctionRegistry()

        # Trigonometric (14)
        _default_registry.register(SinFunction())
        _default_registry.register(CosFunction())
        _default_registry.register(TanFunction())
        _default_registry.register(AsinFunction())
        _default_registry.register(AcosFunction())
        _default_registry.register(AtanFunction())
        _default_registry.register(Atan2Function())
        _default_registry.register(SinhFunction())
        _default_registry.register(CoshFunction())
        _default_registry.register(TanhFunction())
        _default_registry.register(AsinhFunction())
        _default_registry.register(AcoshFunction())
        _default_registry.register(AtanhFunction())
        _default_registry.register(SincFunction())

        # Exponential/Logarithmic (11)
        _default_registry.register(ExpFunction())
        _default_registry.register(LogFunction())
        _default_registry.register(Log2Function())
        _default_registry.register(Log10Function())
        _default_registry.register(LognFunction())
        _default_registry.register(Exp2Function())
        _default_registry.register(Exp10Function())
        _default_registry.register(SqrtFunction())
        _default_registry.register(CbrtFunction())
        _default_registry.register(RootFunction())
        _default_registry.register(SquareFunction())
        _default_registry.register(LambertWFunction())
        _default_registry.register(CisFunction())

        # Combinatorics (6)
        _default_registry.register(FactorialFunction())
        _default_registry.register(DoubleFactorialFunction())
        _default_registry.register(MultinomialFunction())
        _default_registry.register(BinomialFunction())
        _default_registry.register(GammaFunction())

        # Number Theory (24)
        _default_registry.register(AbsFunction())
        _default_registry.register(SignumFunction())
        _default_registry.register(RoundFunction())
        _default_registry.register(FloorFunction())
        _default_registry.register(CeilFunction())
        _default_registry.register(TruncFunction())
        _default_registry.register(GcdFunction())
        _default_registry.register(LcmFunction())
        _default_registry.register(ModFunction())
        _default_registry.register(RemFunction())
        _default_registry.register(IsPrimeFunction())
        _default_registry.register(NextPrimeFunction())
        _default_registry.register(PrevPrimeFunction())
        _default_registry.register(NthPrimeFunction())
        _default_registry.register(PrimeCountFunction())
        _default_registry.register(NumeratorFunction())
        _default_registry.register(DenominatorFunction())
        _default_registry.register(IntFunction())
        _default_registry.register(FracFunction())
        _default_registry.register(TotientFunction())
        _default_registry.register(BernoulliFunction())
        _default_registry.register(ReFunction())
        _default_registry.register(ImFunction())
        _default_registry.register(ArgFunction())
        _default_registry.register(PowerModFunction())
        _default_registry.register(ParallelFunction())
        _default_registry.register(IntervalFunction())
        _default_registry.register(UncertaintyFunction())

        # Algebra (8)
        _default_registry.register(SolveFunction())
        _default_registry.register(SolveMultipleFunction())
        _default_registry.register(DSolveFunction())
        _default_registry.register(FactorFunction())
        _default_registry.register(ExpandFunction())
        _default_registry.register(CoeffFunction())
        _default_registry.register(DegreeFunction())
        _default_registry.register(RootsFunction())

        # Calculus (5)
        _default_registry.register(DiffFunction())
        _default_registry.register(IntegrateFunction())
        _default_registry.register(LimitFunction())
        _default_registry.register(SumFunction())
        _default_registry.register(ProductFunction())

        # Matrix/Vector (15)
        _default_registry.register(DetFunction())
        _default_registry.register(InverseMatrixFunction())
        _default_registry.register(TransposeFunction())
        _default_registry.register(CrossFunction())
        _default_registry.register(DotFunction())
        _default_registry.register(HadamardFunction())
        _default_registry.register(TraceFunction())
        _default_registry.register(AdjointFunction())
        _default_registry.register(CofactorFunction())
        _default_registry.register(RrefFunction())
        _default_registry.register(MatrixRankFunction())
        _default_registry.register(NormFunction())
        _default_registry.register(EigenvaluesFunction())
        _default_registry.register(IdentityMatrixFunction())
        _default_registry.register(MagnitudeFunction())

        # Statistics (13)
        _default_registry.register(MeanFunction())
        _default_registry.register(StdevFunction())
        _default_registry.register(VarianceFunction())
        _default_registry.register(MedianFunction())
        _default_registry.register(ModeFunction())
        _default_registry.register(PercentileFunction())
        _default_registry.register(QuartileFunction())
        _default_registry.register(NormDistFunction())
        _default_registry.register(MinFunction())
        _default_registry.register(MaxFunction())
        _default_registry.register(RandFunction())
        _default_registry.register(CorrelationFunction())
        _default_registry.register(CovarianceFunction())

        # Base Conversion (8)
        _default_registry.register(BinFunction())
        _default_registry.register(OctFunction())
        _default_registry.register(HexFunction())
        _default_registry.register(BaseFunction())
        _default_registry.register(RomanFunction())
        _default_registry.register(FloatFunction())
        _default_registry.register(FloatErrorFunction())
        _default_registry.register(BasesFunction())

        # Date/Time (10)
        _default_registry.register(DateFunction())
        _default_registry.register(TimestampFunction())
        _default_registry.register(StampToDateFunction())
        _default_registry.register(DaysFunction())
        _default_registry.register(WeeksFunction())
        _default_registry.register(MonthsFunction())
        _default_registry.register(YearsFunction())
        _default_registry.register(NowFunction())
        _default_registry.register(TodayFunction())
        _default_registry.register(LunarPhaseFunction())

        # Special Functions (13)
        _default_registry.register(ZetaFunction())
        _default_registry.register(BetaFunction())
        _default_registry.register(ErfFunction())
        _default_registry.register(ErfcFunction())
        _default_registry.register(BesseljFunction())
        _default_registry.register(BesselyFunction())
        _default_registry.register(AiryFunction())
        _default_registry.register(FresnelSFunction())
        _default_registry.register(FresnelCFunction())
        _default_registry.register(DigammaFunction())
        _default_registry.register(HeavisideFunction())
        _default_registry.register(DiracFunction())

        # Logical/Bitwise (10)
        _default_registry.register(BitAndFunction())
        _default_registry.register(BitOrFunction())
        _default_registry.register(BitXorFunction())
        _default_registry.register(BitNotFunction())
        _default_registry.register(ShiftFunction())
        _default_registry.register(LogicalAndFunction())
        _default_registry.register(LogicalOrFunction())
        _default_registry.register(LogicalXorFunction())
        _default_registry.register(LogicalNotFunction())

        # Utility (14)
        _default_registry.register(IfFunction())
        _default_registry.register(ForFunction())
        _default_registry.register(GenVectorFunction())
        _default_registry.register(LoadFunction())
        _default_registry.register(ExportFunction())
        _default_registry.register(ReplaceFunction())
        _default_registry.register(ToStringFunction())
        _default_registry.register(LengthFunction())
        _default_registry.register(ConcatenateFunction())
        _default_registry.register(IsNumberFunction())
        _default_registry.register(IsRealFunction())
        _default_registry.register(IsRationalFunction())
        _default_registry.register(IsIntegerFunction())
        _default_registry.register(OddFunction())
        _default_registry.register(EvenFunction())
        _default_registry.register(PlotFunction())

        # Signal Processing
        _default_registry.register(FftFunction())
        _default_registry.register(IfftFunction())

    return _default_registry
