"""Number class - arbitrary precision numeric type for PyQalculate.

Mirrors libqalculate's Number class which supports rational, floating point,
complex, and infinite values with arbitrary precision (using gmpy2/mpmath).

Uses gmpy2.mpq for exact rationals and gmpy2.mpfr for high-precision floats,
providing the same functionality as the C++ GMP/MPFR implementation.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import gmpy2
from gmpy2 import mpz, mpq, mpfr

from pyqalculate.types import (
    NumberType,
    ParseOptions,
    DEFAULT_PRECISION,
    RoundingMode,
)

if TYPE_CHECKING:
    from pyqalculate.types import PrintOptions


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Working precision in bits for mpfr (≈ 53 bits for float64, but we use more)
_BIT_PRECISION = 256
# gmpy2 context for high-precision operations
_ctx = gmpy2.context()
_ctx.precision = _BIT_PRECISION


def _mpfr(val: object = 0) -> mpfr:
    """Create an mpfr with our working precision."""
    return mpfr(val, precision=_BIT_PRECISION)


def _is_perfect_square(n: mpz) -> bool:
    """Check if an mpz is a perfect square."""
    if n < 0:
        return False
    return gmpy2.isqrt(n) ** 2 == n


def _is_perfect_power(n: mpz, k: int) -> bool:
    """Check if an mpz is a perfect k-th power."""
    if n < 0:
        if k % 2 == 0:
            return False
        root = gmpy2.iroot(-n, k)
        return root[0] ** k == -n
    root = gmpy2.iroot(n, k)
    return root[0] ** k == n


def _mpz_root(n: mpz, k: int) -> tuple[mpz, bool]:
    """Return (root, is_exact) for the k-th root of n."""
    if n < 0:
        if k % 2 == 0:
            return mpz(0), False
        root, exact = gmpy2.iroot(-n, k)
        return -root, exact
    root, exact = gmpy2.iroot(n, k)
    return root, exact


def _gmpy2_gcd(a: mpz, b: mpz) -> mpz:
    """GCD for mpz values."""
    return gmpy2.gcd(a, b)


def _gmpy2_lcm(a: mpz, b:mpz) -> mpz:
    """LCM for mpz values."""
    if a == 0 and b == 0:
        return mpz(0)
    return abs(a * b) // gmpy2.gcd(a, b)


class Number:
    """Arbitrary precision number (rational, float, complex, or infinite).

    This is the Python port of libqalculate's Number class. It wraps gmpy2
    for exact rational arithmetic and mpmath for high-precision floating point.

    A Number can be:
    - Rational: stored as mpq (numerator/denominator)
    - Float: stored as mpfr (upper/lower bounds for interval support)
    - Complex: stored as a pair of Number (real + imaginary)
    - Infinite: positive or negative infinity
    """

    __slots__ = ("_rational", "_float_upper", "_float_lower", "_imag", "_type",
                 "_is_approx", "_precision", "_plusminus")

    def __init__(
        self,
        value: int | float | str | Number | None = None,
        denominator: int = 1,
        exp_10: int = 0,
    ) -> None:
        """Create a Number.

        Args:
            value: Initial value (int, float, string, or None for zero).
            denominator: Denominator when value is an int numerator.
            exp_10: Base-10 exponent multiplier.
        """
        self._rational = mpq(0)
        self._float_upper = _mpfr(0)
        self._float_lower = _mpfr(0)
        self._imag: Number | None = None
        self._type = NumberType.RATIONAL
        self._is_approx = False
        self._precision = DEFAULT_PRECISION
        self._plusminus = False

        if value is not None:
            if isinstance(value, (int, mpz)):
                self._rational = mpq(value, denominator)
                if exp_10 != 0:
                    self._rational *= mpq(10) ** exp_10
            elif isinstance(value, float):
                if math.isinf(value):
                    self._type = NumberType.PLUS_INFINITY if value > 0 else NumberType.MINUS_INFINITY
                elif math.isnan(value):
                    self._type = NumberType.FLOAT
                    self._float_upper = _mpfr("nan")
                    self._float_lower = _mpfr("nan")
                    self._is_approx = True
                else:
                    self._float_upper = _mpfr(value)
                    self._float_lower = _mpfr(value)
                    self._type = NumberType.FLOAT
                    self._is_approx = True
            elif isinstance(value, complex):
                r = Number(value.real)
                i = Number(value.imag)
                self.set(r)
                self.set_imaginary_part(i)
            elif isinstance(value, str):
                self.set(value)
            elif isinstance(value, Number):
                self.set(value)

    # -----------------------------------------------------------------------
    # Factory methods
    # -----------------------------------------------------------------------

    @classmethod
    def from_rational(cls, num: int, den: int = 1) -> Number:
        """Create an exact rational number."""
        n = cls()
        n._rational = mpq(num, den)
        n._type = NumberType.RATIONAL
        return n

    @classmethod
    def from_float(cls, value: float) -> Number:
        """Create an approximate floating-point number."""
        n = cls()
        if math.isinf(value):
            n._type = NumberType.PLUS_INFINITY if value > 0 else NumberType.MINUS_INFINITY
        else:
            n._float_upper = _mpfr(value)
            n._float_lower = _mpfr(value)
            n._type = NumberType.FLOAT
            n._is_approx = True
        return n

    @classmethod
    def from_mpfr(cls, value: mpfr) -> Number:
        """Create a Number from an mpfr value."""
        n = cls()
        n._float_upper = mpfr(value, precision=_BIT_PRECISION)
        n._float_lower = mpfr(value, precision=_BIT_PRECISION)
        n._type = NumberType.FLOAT
        n._is_approx = True
        return n

    @classmethod
    def plus_inf(cls) -> Number:
        """Create positive infinity."""
        n = cls()
        n._type = NumberType.PLUS_INFINITY
        return n

    @classmethod
    def minus_inf(cls) -> Number:
        """Create negative infinity."""
        n = cls()
        n._type = NumberType.MINUS_INFINITY
        return n

    @classmethod
    def complex(cls, real: Number | int | float = 0,
                imag: Number | int | float = 0) -> Number:
        """Create a complex number with given real and imaginary parts."""
        r = real if isinstance(real, Number) else Number(real)
        i = imag if isinstance(imag, Number) else Number(imag)
        n = cls()
        n.set(r)
        n.set_imaginary_part(i)
        return n

    # -----------------------------------------------------------------------
    # Properties / type queries
    # -----------------------------------------------------------------------

    @property
    def number_type(self) -> NumberType:
        """Return the type of this number."""
        return self._type

    def is_rational(self) -> bool:
        """True if the number is stored as an exact rational."""
        return self._type == NumberType.RATIONAL

    def is_floating_point(self) -> bool:
        """True if the number is stored as a floating-point value."""
        return self._type == NumberType.FLOAT

    is_float = is_floating_point

    def is_infinite(self, ignore_imag: bool = True) -> bool:
        """True if the number is ±∞."""
        if not ignore_imag and self._imag is not None and not self._imag.is_zero():
            return False
        return self._type in (NumberType.PLUS_INFINITY, NumberType.MINUS_INFINITY)

    def is_plus_infinity(self) -> bool:
        return self._type == NumberType.PLUS_INFINITY

    def is_minus_infinity(self) -> bool:
        return self._type == NumberType.MINUS_INFINITY

    def is_finite(self) -> bool:
        """True if the number is finite (not infinite)."""
        return not self.is_infinite()

    def is_zero(self) -> bool:
        if self._type != NumberType.RATIONAL:
            return False
        return self._rational == 0

    def is_non_zero(self) -> bool:
        return not self.is_zero()

    def is_one(self) -> bool:
        if self._type != NumberType.RATIONAL:
            return False
        return self._rational == 1

    def is_two(self) -> bool:
        if self._type != NumberType.RATIONAL:
            return False
        return self._rational == 2

    def is_minus_one(self) -> bool:
        if self._type != NumberType.RATIONAL:
            return False
        return self._rational == -1

    def is_negative(self) -> bool:
        if self._type == NumberType.MINUS_INFINITY:
            return True
        if self._type == NumberType.PLUS_INFINITY:
            return False
        if self._type == NumberType.RATIONAL:
            return self._rational < 0
        if self._type == NumberType.FLOAT:
            return self._float_upper < 0
        return False

    def is_non_negative(self) -> bool:
        return not self.is_negative()

    def is_positive(self) -> bool:
        if self._type == NumberType.PLUS_INFINITY:
            return True
        if self._type == NumberType.MINUS_INFINITY:
            return False
        if self._type == NumberType.RATIONAL:
            return self._rational > 0
        if self._type == NumberType.FLOAT:
            return self._float_lower > 0
        return False

    def is_non_positive(self) -> bool:
        return not self.is_positive()

    def is_integer(self, integer_type: int = 0) -> bool:
        """True if the number is an integer."""
        if self._type == NumberType.RATIONAL:
            return self._rational.denominator == 1
        if self._type == NumberType.FLOAT:
            # Check if both bounds are the same integer
            if self._float_upper == self._float_lower:
                return float(self._float_upper) == int(float(self._float_upper))
        return False

    def is_non_integer(self) -> bool:
        """True if the number is rational but not an integer."""
        return self._type == NumberType.RATIONAL and self._rational.denominator != 1

    def is_fraction(self) -> bool:
        """True if the number is a non-integer rational in (0,1)."""
        if self._type != NumberType.RATIONAL or self._rational.denominator == 1:
            return False
        return self._rational > 0 and self._rational < 1

    def is_even(self) -> bool:
        """True if the number is an even integer."""
        if not self.is_integer():
            return False
        return int(self._rational.numerator) % 2 == 0

    def is_odd(self) -> bool:
        """True if the number is an odd integer."""
        if not self.is_integer():
            return False
        return int(self._rational.numerator) % 2 != 0

    def is_complex(self) -> bool:
        """True if the number has a non-zero imaginary part."""
        return self._imag is not None and not self._imag.is_zero()

    def is_real(self) -> bool:
        """True if the number has no imaginary part."""
        return not self.is_complex()

    def has_real_part(self) -> bool:
        """True if the real part is non-zero."""
        if self._type == NumberType.RATIONAL:
            return self._rational != 0
        if self._type == NumberType.FLOAT:
            return self._float_upper != 0 or self._float_lower != 0
        return True  # infinity

    def has_imaginary_part(self) -> bool:
        """True if there is an imaginary component stored."""
        return self._imag is not None and not self._imag.is_zero()

    def is_interval(self, ignore_imag: bool = True) -> bool:
        """True if the number represents an interval (upper != lower)."""
        if not ignore_imag and self._imag is not None and self._imag.is_interval():
            return True
        if self._type == NumberType.FLOAT:
            return self._float_upper != self._float_lower
        return False

    def is_plusminus(self) -> bool:
        """True if this interval was created from ± (plusminus) notation.

        ±-intervals use variance formula arithmetic (error propagation)
        instead of strict interval arithmetic.
        """
        return self._plusminus and self.is_interval()

    def set_plusminus(self, value: bool = True) -> None:
        """Mark this interval as a ± (plusminus) interval."""
        self._plusminus = value

    def is_approximate(self) -> bool:
        return self._is_approx

    def precision(self, calculate_from_interval: int = 0) -> int:
        return self._precision

    # -----------------------------------------------------------------------
    # Value access
    # -----------------------------------------------------------------------

    def numerator(self) -> Number:
        """Return the numerator as a Number (for rational numbers)."""
        num = Number()
        if self._type == NumberType.RATIONAL:
            num._rational = mpq(self._rational.numerator)
        elif self._type == NumberType.FLOAT:
            # Approximate: just return the float
            num._float_upper = self._float_upper
            num._float_lower = self._float_lower
            num._type = NumberType.FLOAT
            num._is_approx = True
        return num

    def denominator(self) -> Number:
        """Return the denominator as a Number (for rational numbers)."""
        den = Number()
        if self._type == NumberType.RATIONAL:
            den._rational = mpq(self._rational.denominator)
        else:
            den._rational = mpq(1)
        return den

    def complex_numerator(self) -> Number:
        """Return the imaginary numerator."""
        if self._imag is not None and self._imag.is_rational():
            return self._imag.numerator()
        return Number(0)

    def complex_denominator(self) -> Number:
        """Return the imaginary denominator."""
        if self._imag is not None and self._imag.is_rational():
            return self._imag.denominator()
        return Number(1)

    def to_float(self) -> float:
        """Convert to Python float (may lose precision)."""
        if self._type == NumberType.PLUS_INFINITY:
            return float("inf")
        if self._type == NumberType.MINUS_INFINITY:
            return float("-inf")
        if self._type == NumberType.RATIONAL:
            return float(self._rational)
        return float(self._float_upper)

    def to_int(self) -> int:
        """Convert to Python int (rounds if needed)."""
        if self._type == NumberType.PLUS_INFINITY:
            raise OverflowError("Cannot convert +inf to int")
        if self._type == NumberType.MINUS_INFINITY:
            raise OverflowError("Cannot convert -inf to int")
        if self._type == NumberType.RATIONAL:
            if self._rational.denominator == 1:
                return int(self._rational.numerator)
            # Round to nearest integer
            return int(round(float(self._rational)))
        return int(round(float(self._float_upper)))

    def int_value(self, overflow: list | None = None) -> int:
        """Convert to int (C++ API compatibility)."""
        try:
            return self.to_int()
        except OverflowError:
            if overflow is not None:
                overflow[0] = True
            return 0

    def float_value(self) -> float:
        """C++ API compatibility alias."""
        return self.to_float()

    def integer_part(self) -> Number:
        """Return the integer part (truncation toward zero)."""
        n = Number(self)
        n.trunc()
        return n

    def to_string(self, base: int = 10) -> str:
        """Convert to string representation."""
        if self.is_complex():
            r = self.real_part()
            i = self.imaginary_part()
            i_val = i.to_float()
            r_str = r.to_string(base=base)
            i_str = i.to_string(base=base)
            if i_val < 0:
                return f"{r_str}{i_str}i"
            return f"{r_str}+{i_str}i"
        if self._type == NumberType.PLUS_INFINITY:
            return "inf"
        if self._type == NumberType.MINUS_INFINITY:
            return "-inf"
        if self._type == NumberType.RATIONAL:
            if self._rational.denominator == 1:
                if base != 10:
                    return mpz(self._rational.numerator).digits(base) if hasattr(mpz(self._rational.numerator), 'digits') else format(int(self._rational.numerator), f'0{base}'[-3:] if base in (2, 8, 16) else '')
                return str(int(self._rational.numerator))
            if base != 10:
                return f"{self.to_string(base)}/{self.to_string(base)}"
            return str(self._rational)
        # Float type
        if self._float_upper != self._float_lower:
            # Interval
            if self._plusminus:
                return self._format_plusminus()
            lo = float(self._float_lower)
            hi = float(self._float_upper)
            # Format with 8 decimal places for interval display
            return f"interval({lo:.8f}, {hi:.8f})"
        return str(float(self._float_upper))

    def _format_plusminus(self) -> str:
        """Format a ±-interval as 'value±uncertainty'."""
        mid = float((self._float_upper + self._float_lower) / 2)
        unc = float((self._float_upper - self._float_lower) / 2)

        if unc == 0:
            return self._format_float_value(mid)

        # Round uncertainty to 2 significant figures (round UP like qalculate)
        import math as _math
        magnitude = _math.floor(_math.log10(abs(unc)))
        # Use 2 significant figures
        factor = 10 ** (magnitude - 1)
        unc_rounded = _math.ceil(unc / factor) * factor

        # Determine the number of decimal places from the uncertainty
        if unc_rounded >= 1:
            if unc_rounded == int(unc_rounded):
                unc_str = str(int(unc_rounded))
                decimals = 0
            else:
                unc_str = f"{unc_rounded:.10g}"
                decimals = len(unc_str.split('.')[1]) if '.' in unc_str else 0
                unc_str = f"{unc_rounded:.{decimals}f}"
        else:
            # Number of decimal places = -magnitude + 1
            decimals = max(0, -magnitude + 1)
            unc_str = f"{unc_rounded:.{decimals}f}"

        # Format midpoint with same number of decimal places
        mid_str = f"{mid:.{decimals}f}"

        return f"{mid_str}\u00b1{unc_str}"

    def _format_uncertainty(self, unc: float) -> str:
        """Format uncertainty with 2 significant figures."""
        import math as _math
        if unc == 0:
            return "0"
        # Get 2 significant figures
        magnitude = _math.floor(_math.log10(abs(unc)))
        factor = 10 ** (magnitude - 1)  # 2 sig figs
        rounded = round(unc / factor) * factor
        # Format without floating-point artifacts
        if rounded >= 1:
            # Integer-like
            if rounded == int(rounded):
                return str(int(rounded))
            return f"{rounded:.10g}".rstrip('0').rstrip('.')
        else:
            # Small decimal
            s = f"{rounded:.10g}"
            # Remove trailing zeros
            if '.' in s:
                s = s.rstrip('0').rstrip('.')
            return s

    def _format_float_value(self, val: float) -> str:
        """Format a float value cleanly."""
        if val == int(val) and abs(val) < 1e15:
            return str(int(val))
        s = f"{val:.10g}"
        if '.' in s and 'e' not in s.lower():
            s = s.rstrip('0').rstrip('.')
        return s

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set(self, value: Number | str, po: ParseOptions | None = None,
            merge_precision: bool = False, keep_imag: bool = False) -> None:
        """Set the value from another Number or a string."""
        if isinstance(value, Number):
            old_imag = self._imag if keep_imag else None
            self._type = value._type
            self._rational = value._rational
            self._float_upper = value._float_upper
            self._float_lower = value._float_lower
            self._imag = value._imag
            self._is_approx = value._is_approx
            self._precision = value._precision
            self._plusminus = value._plusminus
            if keep_imag and old_imag is not None:
                self._imag = old_imag
        elif isinstance(value, str):
            self._parse_string(value)

    def _parse_string(self, s: str) -> None:
        """Parse a string into the number."""
        s = s.strip()
        if not s:
            self._rational = mpq(0)
            self._type = NumberType.RATIONAL
            return

        # Handle infinity
        if s.lower() in ("inf", "+inf", "infinity", "+infinity"):
            self._type = NumberType.PLUS_INFINITY
            return
        if s.lower() in ("-inf", "-infinity"):
            self._type = NumberType.MINUS_INFINITY
            return

        # Handle complex: "a+bi", "a-bi", "a+bj"
        # First try to detect complex numbers
        if 'i' in s.lower() or 'j' in s.lower():
            if self._try_parse_complex(s):
                return

        # Handle interval: "[a, b]"
        if s.startswith('[') and s.endswith(']'):
            if self._try_parse_interval(s):
                return

        # Handle "±" (plusminus) notation: "5±0.1"
        if '±' in s:
            parts = s.split('±')
            if len(parts) == 2:
                center = Number(parts[0].strip())
                delta = Number(parts[1].strip())
                self.set(center)
                lo = center - delta
                hi = center + delta
                self.set_interval(lo, hi)
                return

        # Handle rationals: "num/den"
        if '/' in s and 'e' not in s.lower().split('/')[-1]:
            parts = s.split('/')
            if len(parts) == 2:
                try:
                    num = int(parts[0].strip())
                    den = int(parts[1].strip())
                    self._rational = mpq(num, den)
                    self._type = NumberType.RATIONAL
                    return
                except ValueError:
                    pass

        # Handle floats (has '.' or 'e')
        if '.' in s or 'e' in s.lower():
            try:
                self._float_upper = _mpfr(s)
                self._float_lower = _mpfr(s)
                self._type = NumberType.FLOAT
                self._is_approx = True
                return
            except (ValueError, OverflowError):
                pass

        # Handle integers
        try:
            self._rational = mpq(int(s))
            self._type = NumberType.RATIONAL
            return
        except ValueError:
            pass

        raise ValueError(f"Cannot parse number: {s}")

    def _try_parse_complex(self, s: str) -> bool:
        """Try to parse a complex number string. Returns True on success."""
        import re
        # Normalize: replace j with i
        s = s.replace('j', 'i').replace('J', 'i')
        # Remove spaces
        s = s.replace(' ', '')

        # Handle pure imaginary: "i", "-i", "+i"
        if s == 'i':
            self._rational = mpq(0)
            self._type = NumberType.RATIONAL
            self._imag = Number(1)
            return True
        if s == '-i':
            self._rational = mpq(0)
            self._type = NumberType.RATIONAL
            self._imag = Number(-1)
            return True
        if s == '+i':
            self._rational = mpq(0)
            self._type = NumberType.RATIONAL
            self._imag = Number(1)
            return True

        # Handle pure imaginary with coefficient: "5i", "-3i", "+2.5i"
        m = re.match(r'^([+-]?\d*\.?\d+(?:e[+-]?\d+)?)i$', s, re.IGNORECASE)
        if m:
            imag_str = m.group(1)
            imag = Number(imag_str)
            self.clear()
            self._imag = imag
            return True

        # Handle mixed: "2+3i", "2-3i", "-2+3i", "-2-3i", "2+i", "2-i"
        # Split on the last + or - before the trailing i
        m = re.match(r'^(.+?)([+-])(\d*\.?\d*(?:e[+-]?\d+)?)i$', s, re.IGNORECASE)
        if m:
            real_str = m.group(1)
            sign = m.group(2)
            imag_coeff = m.group(3)

            real = Number(real_str)

            if imag_coeff in ('', '1'):
                imag_val = Number(1) if sign == '+' else Number(-1)
            else:
                imag_val = Number(imag_coeff)
                if sign == '-':
                    imag_val = -imag_val

            self.set(real)
            self._imag = imag_val
            return True

        return False

    def _try_parse_interval(self, s: str) -> bool:
        """Try to parse an interval string like '[1.5, 2.5]'."""
        inner = s[1:-1].strip()
        parts = inner.split(',')
        if len(parts) != 2:
            return False
        try:
            lo = Number(parts[0].strip())
            hi = Number(parts[1].strip())
            self.set_interval(lo, hi)
            return True
        except ValueError:
            return False

    def set_float(self, d_value: float) -> None:
        """Set to a floating-point value."""
        if math.isinf(d_value):
            self._type = NumberType.PLUS_INFINITY if d_value > 0 else NumberType.MINUS_INFINITY
        else:
            self._float_upper = _mpfr(d_value)
            self._float_lower = _mpfr(d_value)
            self._type = NumberType.FLOAT
            self._is_approx = True

    def set_plus_infinity(self, keep_precision: bool = False,
                          keep_imag: bool = False) -> None:
        """Set to positive infinity."""
        old_imag = self._imag if keep_imag else None
        self._type = NumberType.PLUS_INFINITY
        self._rational = mpq(0)
        self._float_upper = _mpfr(0)
        self._float_lower = _mpfr(0)
        self._is_approx = False
        if keep_imag:
            self._imag = old_imag
        else:
            self._imag = None

    def set_minus_infinity(self, keep_precision: bool = False,
                           keep_imag: bool = False) -> None:
        """Set to negative infinity."""
        old_imag = self._imag if keep_imag else None
        self._type = NumberType.MINUS_INFINITY
        self._rational = mpq(0)
        self._float_upper = _mpfr(0)
        self._float_lower = _mpfr(0)
        self._is_approx = False
        if keep_imag:
            self._imag = old_imag
        else:
            self._imag = None

    def set_imaginary_part(self, o: Number | int | float) -> None:
        """Set the imaginary part."""
        if not isinstance(o, Number):
            o = Number(o)
        self._imag = Number(o)

    setImaginaryPart = set_imaginary_part

    def set_interval(self, nr_lower: Number, nr_upper: Number,
                     keep_precision: bool = False) -> bool:
        """Set the number as an interval [lower, upper]."""
        if nr_lower.has_imaginary_part() or nr_upper.has_imaginary_part():
            return False
        if nr_lower > nr_upper:
            return False
        # Convert both to float
        self._float_lower = _mpfr(nr_lower.to_float())
        self._float_upper = _mpfr(nr_upper.to_float())
        self._type = NumberType.FLOAT
        self._is_approx = True
        if not keep_precision:
            self._precision = DEFAULT_PRECISION
        return True

    setInterval = set_interval

    def clear(self, keep_precision: bool = False) -> None:
        """Reset to zero."""
        self._rational = mpq(0)
        self._float_upper = _mpfr(0)
        self._float_lower = _mpfr(0)
        self._imag = None
        self._type = NumberType.RATIONAL
        self._is_approx = False
        if not keep_precision:
            self._precision = DEFAULT_PRECISION

    def clear_real(self) -> None:
        """Clear only the real part."""
        self._rational = mpq(0)
        self._float_upper = _mpfr(0)
        self._float_lower = _mpfr(0)
        self._type = NumberType.RATIONAL

    def clear_imaginary(self) -> None:
        """Clear only the imaginary part."""
        self._imag = None

    def mark_as_imaginary_part(self, is_imag: bool = True) -> None:
        """Mark this number as an imaginary part (internal use)."""
        pass  # Used in C++ for tracking; not strictly needed in Python

    # -----------------------------------------------------------------------
    # Precision helpers
    # -----------------------------------------------------------------------

    def set_to_floating_point(self) -> bool:
        """Convert rational to floating-point representation."""
        if self._type == NumberType.RATIONAL:
            val = float(self._rational)
            self._float_upper = _mpfr(val)
            self._float_lower = _mpfr(val)
            self._type = NumberType.FLOAT
            self._is_approx = True
        return True

    def set_precision_and_approximate_from(self, o: Number) -> None:
        """Inherit precision and approximation flag from another number."""
        if o._is_approx:
            self._is_approx = True
        if o._precision < self._precision:
            self._precision = o._precision

    setPrecisionAndApproximateFrom = set_precision_and_approximate_from

    def set_approximate(self, is_approximate: bool = True) -> None:
        self._is_approx = is_approximate

    def set_precision(self, prec: int) -> None:
        self._precision = prec

    # -----------------------------------------------------------------------
    # Conversion to float for internal operations
    # -----------------------------------------------------------------------

    def _to_mpfr(self) -> mpfr:
        """Convert to mpfr for float arithmetic."""
        if self._type == NumberType.RATIONAL:
            return _mpfr(float(self._rational))
        return self._float_upper

    # -----------------------------------------------------------------------
    # Real / imaginary parts
    # -----------------------------------------------------------------------

    def real_part(self) -> Number:
        """Return the real part of the number (without imaginary component)."""
        result = Number()
        result._type = self._type
        result._rational = self._rational
        result._float_upper = self._float_upper
        result._float_lower = self._float_lower
        result._is_approx = self._is_approx
        result._precision = self._precision
        result._imag = None  # Strip imaginary part
        return result

    realPart = real_part

    def imaginary_part(self) -> Number:
        """Return the imaginary part as a real number."""
        if self._imag is None:
            return Number(0)
        return Number(self._imag)

    imaginaryPart = imaginary_part

    def conj(self) -> Number:
        """Return the complex conjugate."""
        result = Number(self)
        if result._imag is not None:
            result._imag = -result._imag
        return result

    def lower_endpoint(self, include_imag: bool = False) -> Number:
        """Return the lower bound of an interval."""
        if self._type == NumberType.FLOAT and self._float_upper != self._float_lower:
            result = Number()
            result._float_lower = self._float_lower
            result._float_upper = self._float_lower
            result._type = NumberType.FLOAT
            result._is_approx = self._is_approx
            return result
        return Number(self)

    lowerEndPoint = lower_endpoint

    def upper_endpoint(self, include_imag: bool = False) -> Number:
        """Return the upper bound of an interval."""
        if self._type == NumberType.FLOAT and self._float_upper != self._float_lower:
            result = Number()
            result._float_lower = self._float_upper
            result._float_upper = self._float_upper
            result._type = NumberType.FLOAT
            result._is_approx = self._is_approx
            return result
        return Number(self)

    upperEndPoint = upper_endpoint

    def uncertainty(self) -> Number:
        """Return the uncertainty (half-width of interval)."""
        if not self.is_interval():
            return Number(0)
        diff = self._float_upper - self._float_lower
        return Number.from_mpfr(diff / 2)

    def relative_uncertainty(self) -> Number:
        """Return the relative uncertainty."""
        unc = self.uncertainty()
        mid = Number.from_mpfr((self._float_upper + self._float_lower) / 2)
        if mid.is_zero():
            return Number.plus_inf()
        return unc / mid

    def midpoint_value(self) -> float:
        """Return the midpoint of an interval as float."""
        if self._type == NumberType.FLOAT:
            return float((self._float_upper + self._float_lower) / 2)
        if self._type == NumberType.RATIONAL:
            return float(self._rational)
        return 0.0

    def uncertainty_value(self) -> float:
        """Return the uncertainty (half-width) as float."""
        if not self.is_interval():
            return 0.0
        return float((self._float_upper - self._float_lower) / 2)

    @classmethod
    def from_plusminus(cls, midpoint: float, uncertainty: float) -> Number:
        """Create a ±-interval number from midpoint and uncertainty.

        The resulting number stores [midpoint - |uncertainty|, midpoint + |uncertainty|]
        with the _plusminus flag set for variance formula arithmetic.
        """
        unc = abs(uncertainty)
        n = cls()
        n._float_lower = _mpfr(midpoint - unc)
        n._float_upper = _mpfr(midpoint + unc)
        n._type = NumberType.FLOAT
        n._is_approx = True
        n._plusminus = True
        return n

    # -----------------------------------------------------------------------
    # Arithmetic operations
    # -----------------------------------------------------------------------

    def __add__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented

        # Handle infinity cases
        if self.is_infinite() or other.is_infinite():
            return self._add_infinities(other)

        # Variance formula for ± intervals: uncertainties add in quadrature
        if (self.is_interval() or other.is_interval()) and (self.is_plusminus() or other.is_plusminus()):
            a_mid = self.midpoint_value()
            b_mid = other.midpoint_value()
            a_unc = self.uncertainty_value()
            b_unc = other.uncertainty_value()
            import math as _math
            new_mid = a_mid + b_mid
            new_unc = _math.sqrt(a_unc**2 + b_unc**2)
            result = Number.from_plusminus(new_mid, new_unc)
            # Preserve plusminus flag: if either operand is plusminus
            result._plusminus = self._plusminus or other._plusminus
            return result

        result = Number()
        # Complex addition
        if self.is_complex() or other.is_complex():
            r = self.real_part() + other.real_part()
            i = self.imaginary_part() + other.imaginary_part()
            result.set(r)
            if not i.is_zero():
                result._imag = i  # i IS the imaginary coefficient (a real number)
            return result

        if self._type == NumberType.RATIONAL and other._type == NumberType.RATIONAL:
            result._rational = self._rational + other._rational
            result._type = NumberType.RATIONAL
        else:
            a_lo, a_hi = self._get_bounds()
            b_lo, b_hi = other._get_bounds()
            result._float_lower = _mpfr(a_lo + b_lo)
            result._float_upper = _mpfr(a_hi + b_hi)
            result._type = NumberType.FLOAT
            result._is_approx = True
        result.set_precision_and_approximate_from(self)
        result.set_precision_and_approximate_from(other)
        return result

    def __radd__(self, other: int | float) -> Number:
        return self.__add__(other)

    def __sub__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented

        # Handle infinity
        if self.is_infinite() or other.is_infinite():
            return self._add_infinities(-other)

        # Variance formula for ± intervals: uncertainties add in quadrature
        if (self.is_interval() or other.is_interval()) and (self.is_plusminus() or other.is_plusminus()):
            a_mid = self.midpoint_value()
            b_mid = other.midpoint_value()
            a_unc = self.uncertainty_value()
            b_unc = other.uncertainty_value()
            import math as _math
            new_mid = a_mid - b_mid
            new_unc = _math.sqrt(a_unc**2 + b_unc**2)
            result = Number.from_plusminus(new_mid, new_unc)
            result._plusminus = self._plusminus or other._plusminus
            return result

        result = Number()
        # Complex subtraction
        if self.is_complex() or other.is_complex():
            r = self.real_part() - other.real_part()
            i = self.imaginary_part() - other.imaginary_part()
            result.set(r)
            if not i.is_zero():
                result._imag = i
            return result

        if self._type == NumberType.RATIONAL and other._type == NumberType.RATIONAL:
            result._rational = self._rational - other._rational
            result._type = NumberType.RATIONAL
        else:
            a_lo, a_hi = self._get_bounds()
            b_lo, b_hi = other._get_bounds()
            result._float_lower = _mpfr(a_lo - b_hi)
            result._float_upper = _mpfr(a_hi - b_lo)
            result._type = NumberType.FLOAT
            result._is_approx = True
        result.set_precision_and_approximate_from(self)
        result.set_precision_and_approximate_from(other)
        return result

    def __rsub__(self, other: int | float) -> Number:
        return Number(other).__sub__(self)

    def __mul__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented

        # Handle infinity
        if self.is_infinite() or other.is_infinite():
            return self._mul_infinities(other)

        # Variance formula for ± intervals: relative uncertainties add in quadrature
        if (self.is_interval() or other.is_interval()) and (self.is_plusminus() or other.is_plusminus()):
            a_mid = self.midpoint_value()
            b_mid = other.midpoint_value()
            a_unc = self.uncertainty_value()
            b_unc = other.uncertainty_value()
            import math as _math
            new_mid = a_mid * b_mid
            # Relative uncertainties in quadrature
            rel_a = a_unc / abs(a_mid) if a_mid != 0 else 0.0
            rel_b = b_unc / abs(b_mid) if b_mid != 0 else 0.0
            new_unc = abs(new_mid) * _math.sqrt(rel_a**2 + rel_b**2)
            result = Number.from_plusminus(new_mid, new_unc)
            result._plusminus = self._plusminus or other._plusminus
            return result

        result = Number()
        # Complex multiplication
        if self.is_complex() or other.is_complex():
            a = self.real_part()
            b = self.imaginary_part()
            c = other.real_part()
            d = other.imaginary_part()
            # (a+bi)(c+di) = (ac-bd) + (ad+bc)i
            real = a * c - b * d
            imag = a * d + b * c
            result.set(real)
            if not imag.is_zero():
                result._imag = imag
            return result

        if self._type == NumberType.RATIONAL and other._type == NumberType.RATIONAL:
            result._rational = self._rational * other._rational
            result._type = NumberType.RATIONAL
        else:
            a_lo, a_hi = self._get_bounds()
            b_lo, b_hi = other._get_bounds()
            # For general interval multiplication we need all 4 products
            products = [a_lo * b_lo, a_lo * b_hi, a_hi * b_lo, a_hi * b_hi]
            result._float_lower = _mpfr(min(products))
            result._float_upper = _mpfr(max(products))
            result._type = NumberType.FLOAT
            result._is_approx = True
        result.set_precision_and_approximate_from(self)
        result.set_precision_and_approximate_from(other)
        return result

    def __rmul__(self, other: int | float) -> Number:
        return self.__mul__(other)

    def __truediv__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented
        if other.is_zero():
            raise ZeroDivisionError("Division by zero")

        # Handle infinity
        if self.is_infinite() or other.is_infinite():
            return self._div_infinities(other)

        # Variance formula for ± intervals: relative uncertainties add in quadrature
        if (self.is_interval() or other.is_interval()) and (self.is_plusminus() or other.is_plusminus()):
            a_mid = self.midpoint_value()
            b_mid = other.midpoint_value()
            a_unc = self.uncertainty_value()
            b_unc = other.uncertainty_value()
            import math as _math
            if b_mid == 0:
                raise ZeroDivisionError("Division by zero midpoint")
            new_mid = a_mid / b_mid
            rel_a = a_unc / abs(a_mid) if a_mid != 0 else 0.0
            rel_b = b_unc / abs(b_mid) if b_mid != 0 else 0.0
            new_unc = abs(new_mid) * _math.sqrt(rel_a**2 + rel_b**2)
            result = Number.from_plusminus(new_mid, new_unc)
            result._plusminus = self._plusminus or other._plusminus
            return result

        result = Number()
        # Complex division
        if self.is_complex() or other.is_complex():
            a = self.real_part()
            b = self.imaginary_part()
            c = other.real_part()
            d = other.imaginary_part()
            denom = c * c + d * d
            if denom.is_zero():
                raise ZeroDivisionError("Division by zero complex")
            real = (a * c + b * d) / denom
            imag = (b * c - a * d) / denom
            result.set(real)
            if not imag.is_zero():
                result._imag = imag
            return result

        if self._type == NumberType.RATIONAL and other._type == NumberType.RATIONAL:
            result._rational = self._rational / other._rational
            result._type = NumberType.RATIONAL
        else:
            a_lo, a_hi = self._get_bounds()
            b_lo, b_hi = other._get_bounds()
            if b_lo <= 0 <= b_hi:
                # Division by interval containing zero is undefined
                raise ZeroDivisionError("Division by interval containing zero")
            products = [a_lo / b_lo, a_lo / b_hi, a_hi / b_lo, a_hi / b_hi]
            result._float_lower = _mpfr(min(products))
            result._float_upper = _mpfr(max(products))
            result._type = NumberType.FLOAT
            result._is_approx = True
        result.set_precision_and_approximate_from(self)
        result.set_precision_and_approximate_from(other)
        return result

    def __rtruediv__(self, other: int | float) -> Number:
        return Number(other).__truediv__(self)

    def __floordiv__(self, other: Number | int | float) -> Number:
        result = self / other
        result.floor()
        return result

    def __mod__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        result = Number(self)
        result.mod(other)
        return result

    def __pow__(self, other: Number | int | float) -> Number:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented

        # Variance formula for ± interval base with non-interval exponent:
        # (x ± δx)^n = x^n ± |n| * |x^(n-1)| * δx
        if self.is_interval() and not other.is_interval() and self.is_plusminus():
            a_mid = self.midpoint_value()
            a_unc = self.uncertainty_value()
            exp = other.to_float()
            import math as _math
            try:
                new_mid = a_mid ** exp
                # Derivative: d/dx (x^n) = n * x^(n-1)
                if a_mid != 0:
                    deriv = abs(exp * a_mid ** (exp - 1))
                    new_unc = deriv * a_unc
                else:
                    new_unc = 0.0
                result = Number.from_plusminus(new_mid, new_unc)
                result._plusminus = self._plusminus
                return result
            except (OverflowError, ValueError, ZeroDivisionError):
                pass

        result = Number()
        # Delegate to raise() method
        result.set(self)
        if not result.raise_(other):
            # Fallback to float computation
            try:
                base_f = self.to_float()
                exp_f = other.to_float()
                if base_f < 0 and exp_f != int(exp_f):
                    # Complex result
                    import cmath
                    val = cmath.exp(complex(exp_f) * cmath.log(complex(base_f)))
                    result = Number.complex(val.real, val.imag)
                else:
                    result = Number.from_float(base_f ** exp_f)
            except (OverflowError, ValueError, ZeroDivisionError):
                raise
        return result

    def __rpow__(self, other: int | float) -> Number:
        return Number(other) ** self

    def __neg__(self) -> Number:
        result = Number()
        if self._type == NumberType.RATIONAL:
            result._rational = -self._rational
            result._type = NumberType.RATIONAL
        elif self._type == NumberType.PLUS_INFINITY:
            result._type = NumberType.MINUS_INFINITY
        elif self._type == NumberType.MINUS_INFINITY:
            result._type = NumberType.PLUS_INFINITY
        elif self._type == NumberType.FLOAT:
            result._float_upper = -self._float_lower
            result._float_lower = -self._float_upper
            result._type = NumberType.FLOAT
            result._is_approx = True
        # Negate imaginary part too
        if self._imag is not None:
            result._imag = -self._imag
        return result

    def __abs__(self) -> Number:
        if self.is_negative():
            return -self
        return Number(self)

    def __iadd__(self, other: Number | int | float) -> Number:
        result = self + other
        self.set(result)
        return self

    def __isub__(self, other: Number | int | float) -> Number:
        result = self - other
        self.set(result)
        return self

    def __imul__(self, other: Number | int | float) -> Number:
        result = self * other
        self.set(result)
        return self

    def __itruediv__(self, other: Number | int | float) -> Number:
        result = self / other
        self.set(result)
        return self

    def __ipow__(self, other: Number | int | float) -> Number:
        result = self ** other
        self.set(result)
        return self

    # -----------------------------------------------------------------------
    # Infinity arithmetic helpers
    # -----------------------------------------------------------------------

    def _add_infinities(self, other: Number) -> Number:
        """Handle addition/subtraction with infinity."""
        s_inf = self.is_infinite()
        o_inf = other.is_infinite()

        if s_inf and o_inf:
            if self._type == other._type:
                return Number.plus_inf() if self._type == NumberType.PLUS_INFINITY else Number.minus_inf()
            # +inf + -inf is undefined
            raise ValueError("Indeterminate: inf - inf")

        if s_inf:
            return Number.plus_inf() if self._type == NumberType.PLUS_INFINITY else Number.minus_inf()
        return Number.plus_inf() if other._type == NumberType.PLUS_INFINITY else Number.minus_inf()

    def _mul_infinities(self, other: Number) -> Number:
        """Handle multiplication with infinity."""
        if self.is_zero() or other.is_zero():
            raise ValueError("Indeterminate: 0 * inf")
        s_neg = self.is_negative() or self._type == NumberType.MINUS_INFINITY
        o_neg = other.is_negative() or other._type == NumberType.MINUS_INFINITY
        if s_neg == o_neg:
            return Number.plus_inf()
        return Number.minus_inf()

    def _div_infinities(self, other: Number) -> Number:
        """Handle division with infinity."""
        if self.is_infinite() and other.is_infinite():
            raise ValueError("Indeterminate: inf / inf")
        if self.is_infinite():
            s_neg = self._type == NumberType.MINUS_INFINITY
            o_neg = other.is_negative()
            if s_neg == o_neg:
                return Number.plus_inf()
            return Number.minus_inf()
        # finite / inf = 0
        if other.is_infinite():
            return Number(0)
        return Number(0)

    def _get_bounds(self) -> tuple[float, float]:
        """Get (lower, upper) float bounds."""
        if self._type == NumberType.RATIONAL:
            v = float(self._rational)
            return (v, v)
        return (float(self._float_lower), float(self._float_upper))

    # -----------------------------------------------------------------------
    # In-place arithmetic methods (C++ API style)
    # -----------------------------------------------------------------------

    def add(self, other: Number | int | float) -> bool:
        """In-place addition. Returns True on success."""
        result = self + other
        self.set(result)
        return True

    def subtract(self, other: Number | int | float) -> bool:
        """In-place subtraction. Returns True on success."""
        result = self - other
        self.set(result)
        return True

    def multiply(self, other: Number | int | float) -> bool:
        """In-place multiplication. Returns True on success."""
        result = self * other
        self.set(result)
        return True

    def divide(self, other: Number | int | float) -> bool:
        """In-place division. Returns True on success."""
        try:
            result = self / other
            self.set(result)
            return True
        except (ZeroDivisionError, ValueError):
            return False

    def recip(self) -> bool:
        """In-place reciprocal (1/x)."""
        if self.is_zero():
            return False
        result = Number(1) / self
        self.set(result)
        return True

    def negate(self) -> bool:
        """In-place negation."""
        result = -self
        self.set(result)
        return True

    def abs(self) -> bool:
        """In-place absolute value."""
        if self.is_negative():
            self.negate()
        return True

    def signum(self) -> bool:
        """Set to sign: -1, 0, or 1."""
        if self.is_zero():
            return True
        if self.is_negative():
            self.set(Number(-1))
        else:
            self.set(Number(1))
        return True

    def square(self) -> bool:
        """In-place squaring (x^2)."""
        result = self * self
        self.set(result)
        return True

    # -----------------------------------------------------------------------
    # Power and root operations
    # -----------------------------------------------------------------------

    def raise_(self, o: Number, try_exact: bool = True,
               allow_complex: bool = False) -> bool:
        """Raise to power (in-place). Returns True on success.

        This mirrors the C++ Number::raise() method.

        Args:
            o: The exponent.
            try_exact: If True, try exact rational arithmetic first.
            allow_complex: If True, return the principal complex root for
                negative base with fractional exponent (odd denominator)
                instead of the real root.
        """
        if not isinstance(o, Number):
            o = Number(o)

        # x^0 = 1 (for non-zero x)
        if o.is_zero():
            if self.is_zero():
                return False  # 0^0 is undefined
            self.set(Number(1))
            self.set_precision_and_approximate_from(o)
            return True

        # x^1 = x
        if o.is_one():
            self.set_precision_and_approximate_from(o)
            return True

        # 0^n = 0 (for positive n)
        if self.is_zero():
            if o.is_negative():
                return False  # Division by zero
            return True

        # 1^n = 1
        if self.is_one():
            return True

        # Handle infinity
        if self.is_infinite() or o.is_infinite():
            return self._raise_infinity(o)

        # Handle complex base
        if self.is_complex():
            return self._raise_complex(o, try_exact)

        # Handle negative exponent: x^(-n) = 1/x^n
        if o.is_negative():
            if not self.recip():
                return False
            neg_o = -o
            return self.raise_(neg_o, try_exact, allow_complex=allow_complex)

        # Try exact rational power
        if (self._type == NumberType.RATIONAL and o._type == NumberType.RATIONAL
                and try_exact):
            if o.is_integer():
                # Integer power
                n = int(o._rational)
                if n >= 0:
                    self._rational = self._rational ** n
                    self.set_precision_and_approximate_from(o)
                    return True

            # Fractional power p/q: compute num^(p/q) and den^(p/q) separately
            if o._type == NumberType.RATIONAL and o._rational.denominator != 1:
                num = self._rational.numerator
                den = self._rational.denominator
                p = int(o._rational.numerator)
                q = int(o._rational.denominator)

                if self._rational < 0 and q % 2 == 0:
                    # Even root of negative → complex
                    if q == 2 and p == 1:
                        # sqrt of negative: i * sqrt(|x|)
                        abs_val = Number(abs(float(self._rational)))
                        if abs_val.sqrt():
                            self.clear()
                            self._imag = abs_val
                            return True
                    # Fall through to float
                elif self._rational < 0 and allow_complex:
                    # Negative base with odd denominator exponent and
                    # allow_complex=True: use the principal complex root
                    # instead of the real root.  Fall through to
                    # _raise_float() which uses cmath.
                    pass
                else:
                    # Try to compute exact root
                    if p < 0:
                        # Negative exponent
                        if not self.raise_(Number(mpq(-p, q)), try_exact,
                                           allow_complex=allow_complex):
                            return False
                        return self.recip()

                    # Positive fractional exponent: num^(p/q)
                    num_neg = num < 0
                    abs_num = abs(num)
                    abs_den = abs(den)

                    num_root, num_exact = _mpz_root(abs_num, q)
                    den_root, den_exact = _mpz_root(abs_den, q)

                    if num_exact and den_exact:
                        # Exact root found
                        result_num = mpz(num_root) ** p
                        result_den = mpz(den_root) ** p
                        if num_neg and q % 2 != 0:
                            result_num = -result_num
                        self._rational = mpq(result_num, result_den)
                        self.set_precision_and_approximate_from(o)
                        return True

        # Fall back to floating-point computation
        return self._raise_float(o)

    def _raise_float(self, o: Number) -> bool:
        """Compute power using floating-point arithmetic."""
        # Handle interval base: compute at both endpoints
        if self.is_interval():
            import math as _math
            lo = float(self._float_lower)
            hi = float(self._float_upper)
            exp = o.to_float()

            # Compute power at all 4 combinations and take min/max
            vals = []
            for base_val in (lo, hi):
                if base_val < 0 and exp != int(exp):
                    # Complex result for fractional power of negative
                    continue
                try:
                    vals.append(base_val ** exp)
                except (OverflowError, ValueError, ZeroDivisionError):
                    continue

            # Also check at 0 if interval crosses zero and exponent > 1
            if lo < 0 < hi and exp > 0:
                try:
                    vals.append(0.0 ** exp)
                except (ZeroDivisionError, ValueError):
                    pass

            if vals:
                min_val = min(vals)
                max_val = max(vals)
                self._float_lower = _mpfr(min_val)
                self._float_upper = _mpfr(max_val)
                self._type = NumberType.FLOAT
                self._is_approx = True
                self.set_precision_and_approximate_from(o)
                return True
            return False

        base = self.to_float()
        exp = o.to_float()

        if base < 0 and exp != int(exp):
            # Complex result
            import cmath
            val = cmath.exp(complex(exp) * cmath.log(complex(base)))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if val.imag != 0:
                self._imag = Number.from_float(val.imag)
            return True

        try:
            result = base ** exp
            if math.isinf(result):
                self._type = NumberType.PLUS_INFINITY if result > 0 else NumberType.MINUS_INFINITY
            else:
                self._float_upper = _mpfr(result)
                self._float_lower = _mpfr(result)
                self._type = NumberType.FLOAT
                self._is_approx = True
            self.set_precision_and_approximate_from(o)
            return True
        except (OverflowError, ValueError):
            return False

    def _raise_infinity(self, o: Number) -> bool:
        """Handle power with infinity."""
        if self.is_infinite() and o.is_infinite():
            return False  # Indeterminate
        if self.is_infinite():
            if o.is_zero():
                return False
            if o.is_negative():
                self.clear()
                return True
            if self._type == NumberType.MINUS_INFINITY:
                if o.is_even():
                    self._type = NumberType.PLUS_INFINITY
                elif not o.is_integer():
                    return False
            return True
        # self is finite, o is infinite
        if self.is_zero():
            return False
        if self.is_negative():
            return False
        if self > Number(1):
            self._type = NumberType.PLUS_INFINITY
        elif self.is_one():
            pass
        else:
            self.clear()
        return True

    def _raise_complex(self, o: Number, try_exact: bool) -> bool:
        """Raise a complex number to a power."""
        # For integer exponents, multiply repeatedly
        if o.is_integer() and o.is_positive():
            n = o.to_int()
            if n < 100:
                base = Number(self)
                for _ in range(n - 1):
                    result = self * base
                    self.set(result)
                self.set_precision_and_approximate_from(o)
                return True

        # General case: use polar form
        # z^n = |z|^n * e^(i*n*arg(z))
        import cmath
        r = self.real_part().to_float()
        im = self.imaginary_part().to_float() if self._imag is not None else 0.0
        z = complex(r, im)
        exp_val = o.to_float()
        try:
            result = z ** exp_val
            self.clear()
            self._float_upper = _mpfr(result.real)
            self._float_lower = _mpfr(result.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(result.imag) > 1e-15:
                self._imag = Number.from_float(result.imag)
            self.set_precision_and_approximate_from(o)
            return True
        except (OverflowError, ValueError, ZeroDivisionError):
            return False

    # -----------------------------------------------------------------------
    # Square root, cube root, nth root
    # -----------------------------------------------------------------------

    def sqrt(self) -> bool:
        """In-place square root. Returns True on success."""
        if self.is_complex():
            return self.raise_(Number(1, 2))

        if self._type == NumberType.MINUS_INFINITY:
            return False

        if self._type == NumberType.PLUS_INFINITY:
            return True

        if self.is_negative():
            # sqrt of negative → imaginary
            abs_val = Number(self)
            if not abs_val.negate() or not abs_val.sqrt():
                return False
            self.clear()
            self._imag = abs_val
            return True

        if self._type == NumberType.RATIONAL:
            num = self._rational.numerator
            den = self._rational.denominator
            if _is_perfect_square(num) and _is_perfect_square(den):
                self._rational = mpq(gmpy2.isqrt(num), gmpy2.isqrt(den))
                return True

        # Fall back to float
        val = self.to_float()
        result = math.sqrt(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def cbrt(self) -> bool:
        """In-place cube root. Returns True on success."""
        if self.is_complex():
            return self.raise_(Number(1, 3))

        if self._type == NumberType.PLUS_INFINITY:
            return True
        if self._type == NumberType.MINUS_INFINITY:
            return True  # cbrt(-inf) = -inf

        if self.is_one() or self.is_minus_one() or self.is_zero():
            return True

        if self._type == NumberType.RATIONAL:
            num = self._rational.numerator
            den = self._rational.denominator
            num_neg = num < 0
            abs_num = abs(num)
            num_root, num_exact = _mpz_root(abs_num, 3)
            den_root, den_exact = _mpz_root(den, 3)
            if num_exact and den_exact:
                result_num = num_root
                if num_neg:
                    result_num = -result_num
                self._rational = mpq(result_num, den_root)
                return True

        # Fall back to float
        val = self.to_float()
        if val < 0:
            result = -((-val) ** (1.0 / 3.0))
        else:
            result = val ** (1.0 / 3.0)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def root(self, o: Number) -> bool:
        """In-place nth root. Returns True on success."""
        if not o.is_integer() or not o.is_positive():
            return False
        if o.is_one():
            return True
        if o.is_two():
            return self.sqrt()
        if self.is_one() or self.is_zero():
            return True

        return self.raise_(Number(1) / o)

    # -----------------------------------------------------------------------
    # Exponential and logarithmic functions
    # -----------------------------------------------------------------------

    def exp(self) -> bool:
        """In-place exponential (e^x). Returns True on success."""
        if self._type == NumberType.PLUS_INFINITY:
            return True
        if self._type == NumberType.MINUS_INFINITY:
            self.clear()
            return True
        if self.is_complex():
            # e^(a+bi) = e^a * (cos(b) + i*sin(b))
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.exp(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True

        val = self.to_float()
        try:
            result = math.exp(val)
            if math.isinf(result):
                self._type = NumberType.PLUS_INFINITY
            else:
                self._float_upper = _mpfr(result)
                self._float_lower = _mpfr(result)
                self._type = NumberType.FLOAT
                self._is_approx = True
            return True
        except OverflowError:
            self._type = NumberType.PLUS_INFINITY
            return True

    def ln(self) -> bool:
        """In-place natural logarithm. Returns True on success."""
        if self._type == NumberType.PLUS_INFINITY:
            return True
        if self._type == NumberType.MINUS_INFINITY:
            # ln(-inf) = inf + i*pi
            self._type = NumberType.PLUS_INFINITY
            self._imag = Number()
            self._imag.pi()
            return True
        if self.is_zero():
            self._type = NumberType.MINUS_INFINITY
            return True
        if self.is_one():
            self.clear()
            return True

        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.log(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True

        if self.is_negative():
            # ln(-x) = ln(x) + i*pi
            abs_val = abs(self)
            if not abs_val.ln():
                return False
            self.set(abs_val)
            self._imag = Number()
            self._imag.pi()
            return True

        val = self.to_float()
        if val <= 0:
            return False
        result = math.log(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def log(self, base: Number | None = None) -> bool:
        """In-place logarithm. If base is None, computes ln."""
        if base is None:
            return self.ln()
        if not isinstance(base, Number):
            base = Number(base)
        # log_b(x) = ln(x) / ln(b)
        x_copy = Number(self)
        b_copy = Number(base)
        if not x_copy.ln() or not b_copy.ln():
            return False
        result = x_copy / b_copy
        self.set(result)
        return True

    def log2(self) -> bool:
        """In-place base-2 logarithm."""
        return self.log(Number(2))

    def log10(self) -> bool:
        """In-place base-10 logarithm."""
        return self.log(Number(10))

    def exp10(self) -> bool:
        """Set to 10^x (in-place)."""
        if self.is_zero():
            self.set(Number(1))
            return True
        ten = Number(10)
        result = ten ** self
        self.set(result)
        return True

    def exp2(self) -> bool:
        """Set to 2^x (in-place)."""
        if self.is_zero():
            self.set(Number(1))
            return True
        two = Number(2)
        result = two ** self
        self.set(result)
        return True

    # -----------------------------------------------------------------------
    # Rounding functions
    # -----------------------------------------------------------------------

    def floor(self) -> bool:
        """In-place floor. Returns True on success."""
        if self.is_infinite() or self.is_complex():
            return False
        if self._type == NumberType.RATIONAL:
            if not self.is_integer():
                n = int(self._rational.numerator)
                d = int(self._rational.denominator)
                # Floor division: floor(n/d)
                q = n // d  # Python's // does floor division
                self._rational = mpq(q)
            return True
        # Float
        val = float(self._float_lower)
        import math as _math
        self._float_lower = _mpfr(_math.floor(float(self._float_lower)))
        self._float_upper = _mpfr(_math.floor(float(self._float_upper)))
        if self._float_lower == self._float_upper:
            self._rational = mpq(int(self._float_lower))
            self._type = NumberType.RATIONAL
        return True

    def ceil(self) -> bool:
        """In-place ceiling. Returns True on success."""
        if self.is_infinite() or self.is_complex():
            return False
        if self._type == NumberType.RATIONAL:
            if not self.is_integer():
                n = int(self._rational.numerator)
                d = int(self._rational.denominator)
                # Ceiling division: ceil(n/d) = -floor(-n/d)
                q = -((-n) // d)
                self._rational = mpq(q)
            return True
        # Float
        import math as _math
        self._float_lower = _mpfr(_math.ceil(float(self._float_lower)))
        self._float_upper = _mpfr(_math.ceil(float(self._float_upper)))
        if self._float_lower == self._float_upper:
            self._rational = mpq(int(self._float_lower))
            self._type = NumberType.RATIONAL
        return True

    def trunc(self) -> bool:
        """In-place truncation toward zero. Returns True on success."""
        if self.is_infinite() or self.is_complex():
            return False
        if self._type == NumberType.RATIONAL:
            if not self.is_integer():
                n = int(self._rational.numerator)
                d = int(self._rational.denominator)
                q = int(n / d)  # truncation toward zero in Python
                self._rational = mpq(q)
            return True
        # Float
        import math as _math
        self._float_lower = _mpfr(_math.trunc(float(self._float_lower)))
        self._float_upper = _mpfr(_math.trunc(float(self._float_upper)))
        if self._float_lower == self._float_upper:
            self._rational = mpq(int(self._float_lower))
            self._type = NumberType.RATIONAL
        return True

    def round(self, halfway_to_even: bool = True) -> bool:
        """In-place rounding. Returns True on success."""
        if self.is_infinite() or self.is_complex():
            return False
        if self._type == NumberType.RATIONAL:
            if not self.is_integer():
                val = float(self._rational)
                if halfway_to_even:
                    rounded = round(val)
                else:
                    rounded = int(val + 0.5) if val >= 0 else int(val - 0.5)
                self._rational = mpq(rounded)
            return True
        # Float
        val = float(self._float_upper)
        if halfway_to_even:
            rounded = round(val)
        else:
            rounded = int(val + 0.5) if val >= 0 else int(val - 0.5)
        self._float_lower = _mpfr(rounded)
        self._float_upper = _mpfr(rounded)
        self._rational = mpq(rounded)
        self._type = NumberType.RATIONAL
        return True

    def mod(self, o: Number) -> bool:
        """In-place modulo (floored division remainder). Returns True on success."""
        if not isinstance(o, Number):
            o = Number(o)
        if self.is_infinite() or o.is_infinite():
            return False
        if self.is_complex() or o.is_complex():
            return False
        if o.is_zero():
            return False
        if self._type == NumberType.RATIONAL and o._type == NumberType.RATIONAL:
            if self.is_integer() and o.is_integer():
                n = int(self._rational.numerator)
                d = int(o._rational.numerator)
                self._rational = mpq(n % d)
            else:
                # a mod b = a - b * floor(a/b)
                q = self._rational / o._rational
                q_floor = mpq(int(q)) if q >= 0 or q == int(q) else mpq(int(q) - 1)
                self._rational = self._rational - o._rational * q_floor
        else:
            # Float mod
            a = self.to_float()
            b = o.to_float()
            result = a % b
            self._float_upper = _mpfr(result)
            self._float_lower = _mpfr(result)
            self._type = NumberType.FLOAT
            self._is_approx = True
        self.set_precision_and_approximate_from(o)
        return True

    def rem(self, o: Number) -> bool:
        """In-place remainder (truncated division). Returns True on success."""
        if not isinstance(o, Number):
            o = Number(o)
        if self.is_infinite() or o.is_infinite():
            return False
        if self.is_complex() or o.is_complex():
            return False
        if o.is_zero():
            return False
        if self._type == NumberType.RATIONAL and o._type == NumberType.RATIONAL:
            if self.is_integer() and o.is_integer():
                n = int(self._rational.numerator)
                d = int(o._rational.numerator)
                self._rational = mpq(int(n / d))  # truncated division
                self._rational = mpq(n - int(n / d) * d)
            else:
                q = self._rational / o._rational
                q_trunc = mpq(int(q))  # truncation
                self._rational = self._rational - o._rational * q_trunc
        else:
            a = self.to_float()
            b = o.to_float()
            result = math.fmod(a, b)
            self._float_upper = _mpfr(result)
            self._float_lower = _mpfr(result)
            self._type = NumberType.FLOAT
            self._is_approx = True
        self.set_precision_and_approximate_from(o)
        return True

    def frac(self) -> bool:
        """In-place fractional part. Returns True on success."""
        if self.is_infinite() or self.is_complex():
            return False
        if self._type == NumberType.RATIONAL:
            if self.is_integer():
                self.clear()
            else:
                n = int(self._rational.numerator)
                d = int(self._rational.denominator)
                self._rational = mpq(n % d, d)
        else:
            val = float(self._float_upper)
            self._float_upper = _mpfr(val - math.trunc(val))
            self._float_lower = self._float_upper
        return True

    # -----------------------------------------------------------------------
    # Number theory
    # -----------------------------------------------------------------------

    def factorial(self) -> bool:
        """In-place factorial. Returns True on success."""
        if not self.is_integer():
            return False
        if self.is_negative():
            return False
        if self.is_zero() or self.is_one():
            self.set(Number(1))
            return True
        n = int(self._rational.numerator)
        if n > 100000:
            return False  # Too large
        import math
        self._rational = mpq(math.factorial(n))
        return True

    def gcd(self, o: Number) -> bool:
        """In-place GCD. Returns True on success."""
        if not isinstance(o, Number):
            o = Number(o)
        if not self.is_rational() or not o.is_rational():
            return False
        if not self.is_integer() or not o.is_integer():
            # GCD for rationals: gcd(a/b, c/d) = gcd(a,c) / lcm(b,d)
            num_self = abs(int(self._rational.numerator))
            den_self = int(self._rational.denominator)
            num_other = abs(int(o._rational.numerator))
            den_other = int(o._rational.denominator)
            g_num = _gmpy2_gcd(mpz(num_self), mpz(num_other))
            l_den = _gmpy2_lcm(mpz(den_self), mpz(den_other))
            self._rational = mpq(g_num, l_den)
            return True
        if self.is_zero() and o.is_zero():
            self.clear()
            return True
        a = abs(int(self._rational.numerator))
        b = abs(int(o._rational.numerator))
        self._rational = mpq(int(_gmpy2_gcd(mpz(a), mpz(b))))
        self.set_precision_and_approximate_from(o)
        return True

    def lcm(self, o: Number) -> bool:
        """In-place LCM. Returns True on success."""
        if not isinstance(o, Number):
            o = Number(o)
        if not self.is_rational() or not o.is_rational():
            return False
        if not self.is_integer() or not o.is_integer():
            num_self = abs(int(self._rational.numerator))
            den_self = int(self._rational.denominator)
            num_other = abs(int(o._rational.numerator))
            den_other = int(o._rational.denominator)
            l_num = _gmpy2_lcm(mpz(num_self), mpz(num_other))
            g_den = _gmpy2_gcd(mpz(den_self), mpz(den_other))
            self._rational = mpq(l_num, g_den)
            return True
        a = abs(int(self._rational.numerator))
        b = abs(int(o._rational.numerator))
        self._rational = mpq(int(_gmpy2_lcm(mpz(a), mpz(b))))
        self.set_precision_and_approximate_from(o)
        return True

    def binomial(self, m: Number, k: Number) -> bool:
        """Set to binomial coefficient C(m, k). Returns True on success."""
        if not m.is_integer() or not k.is_integer():
            return False
        m_int = int(m._rational.numerator) if m._type == NumberType.RATIONAL else m.to_int()
        k_int = int(k._rational.numerator) if k._type == NumberType.RATIONAL else k.to_int()

        if m_int < 0:
            if k_int < 0:
                return False
            # Use identity: C(-m+k-1, k) * (-1)^k
            m2 = -m_int + k_int - 1
            result = self._compute_binomial(m2, k_int)
            if k_int % 2 != 0:
                result = -result
            self._rational = mpq(result)
            return True

        if k_int < 0 or k_int > m_int:
            self.clear()
            return True
        if m_int == k_int or k_int == 0:
            self.set(Number(1))
            return True

        result = self._compute_binomial(m_int, k_int)
        self._rational = mpq(result)
        return True

    @staticmethod
    def _compute_binomial(n: int, k: int) -> int:
        """Compute C(n, k) for non-negative integers."""
        import math
        return math.comb(n, k)

    # -----------------------------------------------------------------------
    # Trigonometric functions
    # -----------------------------------------------------------------------

    def sin(self) -> bool:
        """In-place sine. Returns True on success."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return False
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.sin(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.sin(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def cos(self) -> bool:
        """In-place cosine. Returns True on success."""
        if self.is_zero():
            self.set(Number(1))
            return True
        if self.is_infinite():
            return False
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.cos(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.cos(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def tan(self) -> bool:
        """In-place tangent. Returns True on success."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return False
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.tan(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.tan(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def asin(self) -> bool:
        """In-place arcsine. Returns True on success."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return False
        if self.is_complex() or abs(self.to_float()) > 1:
            import cmath
            val = cmath.asin(complex(self.to_float(),
                                     self._imag.to_float() if self._imag else 0))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        if abs(val) > 1:
            return False
        result = math.asin(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def acos(self) -> bool:
        """In-place arccosine. Returns True on success."""
        if self.is_one():
            self.clear()
            return True
        if self.is_infinite():
            return False
        if self.is_complex() or abs(self.to_float()) > 1:
            import cmath
            val = cmath.acos(complex(self.to_float(),
                                     self._imag.to_float() if self._imag else 0))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        if abs(val) > 1:
            return False
        result = math.acos(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def atan(self) -> bool:
        """In-place arctangent. Returns True on success."""
        if self.is_zero():
            return True
        if self.is_infinite():
            if self._type == NumberType.PLUS_INFINITY:
                self.clear()
                import math as _math
                self._float_upper = _mpfr(_math.pi / 2)
                self._float_lower = _mpfr(_math.pi / 2)
                self._type = NumberType.FLOAT
                self._is_approx = True
            else:
                self.clear()
                import math as _math
                self._float_upper = _mpfr(-_math.pi / 2)
                self._float_lower = _mpfr(-_math.pi / 2)
                self._type = NumberType.FLOAT
                self._is_approx = True
            return True
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag is not None else 0.0
            val = cmath.atan(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.atan(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def atan2(self, x: Number, allow_zero: bool = False) -> bool:
        """In-place atan2(self, x) = atan2(y, x). Returns True on success."""
        if self.is_complex() or x.is_complex():
            return False
        y_val = self.to_float()
        x_val = x.to_float()
        if y_val == 0 and x_val == 0 and not allow_zero:
            return False
        result = math.atan2(y_val, x_val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def arg(self) -> bool:
        """In-place argument (angle) of complex number."""
        if not self.is_complex():
            if self.is_negative():
                self.clear()
                import math as _math
                self._float_upper = _mpfr(_math.pi)
                self._float_lower = _mpfr(_math.pi)
                self._type = NumberType.FLOAT
                self._is_approx = True
            elif self.is_zero():
                return False  # arg(0) undefined
            # Positive real: arg = 0
            return True
        r = self.real_part().to_float()
        im = self.imaginary_part().to_float()
        result = math.atan2(im, r)
        self.clear()
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    # Hyperbolic functions

    def sinh(self) -> bool:
        """In-place hyperbolic sine."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return True  # sinh(±inf) = ±inf
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.sinh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.sinh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def cosh(self) -> bool:
        """In-place hyperbolic cosine."""
        if self.is_zero():
            self.set(Number(1))
            return True
        if self.is_infinite():
            self._type = NumberType.PLUS_INFINITY
            return True
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.cosh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.cosh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def tanh(self) -> bool:
        """In-place hyperbolic tangent."""
        if self.is_zero():
            return True
        if self.is_infinite():
            self.set(Number(1) if self._type == NumberType.PLUS_INFINITY else Number(-1))
            return True
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.tanh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.tanh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def asinh(self) -> bool:
        """In-place inverse hyperbolic sine."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return True
        if self.is_complex():
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.asinh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        result = math.asinh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def acosh(self) -> bool:
        """In-place inverse hyperbolic cosine."""
        if self.is_one():
            self.clear()
            return True
        if self.is_infinite():
            self._type = NumberType.PLUS_INFINITY
            return True
        if self.is_complex() or self.to_float() < 1:
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.acosh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        if val < 1:
            return False
        result = math.acosh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    def atanh(self) -> bool:
        """In-place inverse hyperbolic tangent."""
        if self.is_zero():
            return True
        if self.is_infinite():
            return False
        if self.is_complex() or abs(self.to_float()) >= 1:
            import cmath
            r = self.real_part().to_float()
            im = self.imaginary_part().to_float() if self._imag else 0.0
            val = cmath.atanh(complex(r, im))
            self.clear()
            self._float_upper = _mpfr(val.real)
            self._float_lower = _mpfr(val.real)
            self._type = NumberType.FLOAT
            self._is_approx = True
            if abs(val.imag) > 1e-15:
                self._imag = Number.from_float(val.imag)
            return True
        val = self.to_float()
        if abs(val) >= 1:
            return False
        result = math.atanh(val)
        self._float_upper = _mpfr(result)
        self._float_lower = _mpfr(result)
        self._type = NumberType.FLOAT
        self._is_approx = True
        return True

    # -----------------------------------------------------------------------
    # Constants
    # -----------------------------------------------------------------------

    def pi(self) -> None:
        """Set to π."""
        self.clear()
        self._float_upper = gmpy2.const_pi(precision=_BIT_PRECISION)
        self._float_lower = self._float_upper
        self._type = NumberType.FLOAT
        self._is_approx = True

    def e(self, use_cached: bool = True) -> None:
        """Set to e (Euler's number)."""
        self.clear()
        import math
        self._float_upper = _mpfr(math.e)
        self._float_lower = self._float_upper
        self._type = NumberType.FLOAT
        self._is_approx = True

    # -----------------------------------------------------------------------
    # Comparison
    # -----------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float)):
            other = Number(other)
        if not isinstance(other, Number):
            return NotImplemented

        # Both complex: compare real and imaginary
        if self.is_complex() or other.is_complex():
            sr = self.real_part()
            si = self.imaginary_part()
            or_ = other.real_part()
            oi = other.imaginary_part()
            return sr == or_ and si == oi

        # Both infinite
        if self.is_infinite() and other.is_infinite():
            return self._type == other._type

        # One infinite, one not
        if self.is_infinite() or other.is_infinite():
            return False

        # Mixed rational/float comparison
        if self._type == NumberType.RATIONAL and other._type == NumberType.RATIONAL:
            return self._rational == other._rational

        # Convert to float for comparison
        return abs(self.to_float() - other.to_float()) < 1e-10

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Number | int | float) -> bool:
        if isinstance(other, (int, float)):
            other = Number(other)
        if self._type == NumberType.MINUS_INFINITY:
            return other._type != NumberType.MINUS_INFINITY
        if self._type == NumberType.PLUS_INFINITY:
            return False
        if other._type == NumberType.PLUS_INFINITY:
            return True
        if other._type == NumberType.MINUS_INFINITY:
            return False
        if self.is_complex() or other.is_complex():
            raise TypeError("Cannot compare complex numbers with <")
        return self.to_float() < other.to_float()

    def __le__(self, other: Number | int | float) -> bool:
        return self == other or self < other

    def __gt__(self, other: Number | int | float) -> bool:
        if isinstance(other, (int, float)):
            other = Number(other)
        return not self.__le__(other)

    def __ge__(self, other: Number | int | float) -> bool:
        return not self.__lt__(other)

    def __hash__(self) -> int:
        if self._type == NumberType.RATIONAL:
            return hash(("Number", self._rational))
        if self._type == NumberType.FLOAT:
            return hash(("Number", float(self._float_upper)))
        return hash(("Number", self._type))

    # C++ API comparison aliases
    def equals(self, o: Number, allow_interval: bool = False,
               allow_infinite: bool = False) -> bool:
        """Check equality with options."""
        return self == o

    def is_greater_than(self, o: Number | int | float) -> bool:
        return self > o

    def is_less_than(self, o: Number | int | float) -> bool:
        return self < o

    def is_greater_than_or_equal_to(self, o: Number | int | float) -> bool:
        return self >= o

    def is_less_than_or_equal_to(self, o: Number | int | float) -> bool:
        return self <= o

    # -----------------------------------------------------------------------
    # Increment/decrement
    # -----------------------------------------------------------------------

    def __inc__(self) -> None:
        """Post-increment (x++)."""
        self.add(1)

    def __dec__(self) -> None:
        """Post-decrement (x--)."""
        self.subtract(1)

    # -----------------------------------------------------------------------
    # Boolean / logical
    # -----------------------------------------------------------------------

    def get_boolean(self) -> int:
        """Return 1 if truthy, 0 if falsy."""
        return 0 if self.is_zero() else 1

    def to_boolean(self) -> None:
        """Convert to boolean (0 or 1)."""
        if self.is_zero():
            self.set(Number(0))
        else:
            self.set(Number(1))

    # -----------------------------------------------------------------------
    # Representation
    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        if self.is_complex():
            r = self.real_part()
            i = self.imaginary_part()
            if i.is_negative():
                return f"Number({r.to_string()}{i.to_string()}i)"
            return f"Number({r.to_string()}+{i.to_string()}i)"
        return f"Number({self.to_string()})"

    def __str__(self) -> str:
        if self.is_complex():
            r = self.real_part()
            i = self.imaginary_part()
            i_val = i.to_float()
            r_val = r.to_string()
            if i_val < 0:
                return f"{r_val}{i.to_string()}i"
            return f"{r_val}+{i.to_string()}i"
        return self.to_string()

    def __bool__(self) -> bool:
        return not self.is_zero()

    def __int__(self) -> int:
        return self.to_int()

    def __float__(self) -> float:
        return self.to_float()
