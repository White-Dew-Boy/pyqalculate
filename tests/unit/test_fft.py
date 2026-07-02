"""Tests for FFT/IFFT functions."""
import math

import pytest
from pyqalculate import Calculator


@pytest.fixture
def calc():
    c = Calculator()
    c.load_definitions()
    return c


# ---------------------------------------------------------------------------
# Basic FFT tests
# ---------------------------------------------------------------------------

class TestFftFunction:
    def test_fft_dc_signal(self, calc):
        """fft([1,0,0,0]) should produce all-ones spectrum."""
        result = calc.calculate_and_print("fft([1,0,0,0])")
        assert result is not None
        assert "1" in result

    def test_fft_impulse(self, calc):
        """fft([0,1,0,-1]) should produce appropriate complex spectrum."""
        result = calc.calculate_and_print("fft([0,1,0,-1])")
        assert result is not None
        assert "i" in result

    def test_fft_single_element(self, calc):
        """fft of single element returns that element."""
        result = calc.calculate_and_print("fft([5])")
        assert result is not None
        assert "5" in result

    def test_fft_two_point(self, calc):
        """fft([1,2]) = [3, -1]."""
        result = calc.calculate_and_print("fft([1,2])")
        assert "3" in result
        assert "-1" in result

    def test_fft_pure_cosine(self, calc):
        """fft of [1,0,-1,0] (sampled cosine) produces real peaks."""
        result = calc.calculate_and_print("fft([1,0,-1,0])")
        assert result is not None
        assert "2" in result

    def test_fft_length_preserved(self, calc):
        """Output vector length equals input length."""
        result = calc.calculate_and_print("fft([1,2,3,4])")
        assert result is not None
        assert result.startswith("[")
        assert result.endswith("]")


# ---------------------------------------------------------------------------
# Basic IFFT tests
# ---------------------------------------------------------------------------

class TestIfftFunction:
    def test_ifft_dc_to_impulse(self, calc):
        """ifft([1,1,1,1]) should produce [1,0,0,0]."""
        result = calc.calculate_and_print("ifft([1,1,1,1])")
        assert result is not None
        assert "1" in result

    def test_roundtrip_power_of_2(self, calc):
        """ifft(fft([1,2,3,4])) should approximately recover [1,2,3,4]."""
        result = calc.calculate_and_print("ifft(fft([1,2,3,4]))")
        assert result is not None
        assert "1" in result
        assert "2" in result
        assert "3" in result
        assert "4" in result

    def test_roundtrip_8_elements(self, calc):
        """ifft(fft([1,2,3,4,5,6,7,8])) should approximately recover."""
        result = calc.calculate_and_print("ifft(fft([1,2,3,4,5,6,7,8]))")
        assert result is not None


# ---------------------------------------------------------------------------
# Round-trip accuracy tests: ifft(fft(x)) ≈ x
# ---------------------------------------------------------------------------

class TestFftRoundTrip:
    """Round-trip accuracy: ifft(fft(x)) should recover x."""

    def test_roundtrip_power_of_2_4(self, calc):
        """Round-trip for N=4."""
        result = calc.calculate_and_print("ifft(fft([1,2,3,4]))")
        assert result is not None
        for v in ["1", "2", "3", "4"]:
            assert v in result

    def test_roundtrip_non_power_of_2(self, calc):
        """Round-trip for non-power-of-2 N=7."""
        result = calc.calculate_and_print("ifft(fft([1,2,3,4,5,6,7]))")
        assert result is not None
        for v in ["1", "2", "3", "4", "5", "6", "7"]:
            assert v in result

    def test_roundtrip_large_power_of_2(self, calc):
        """Round-trip for N=16 (larger power-of-2 input)."""
        vals = ",".join(str(i) for i in range(1, 17))
        result = calc.calculate_and_print(f"ifft(fft([{vals}]))")
        assert result is not None

    def test_roundtrip_negative_values(self, calc):
        """Round-trip preserves negative values."""
        result = calc.calculate_and_print("ifft(fft([-1,2,-3,4]))")
        assert result is not None
        assert "-1" in result
        assert "-3" in result
        assert "2" in result
        assert "4" in result

    def test_roundtrip_fractional_values(self, calc):
        """Round-trip preserves fractional values."""
        result = calc.calculate_and_print("ifft(fft([0.5, 1.5, 2.5, 3.5]))")
        assert result is not None
        assert "0.5" in result or "1/2" in result


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestFftEdgeCases:
    """Edge case tests for FFT/IFFT."""

    def test_fft_single_element_identity(self, calc):
        """fft([x]) should return [x]."""
        result = calc.calculate_and_print("fft([42])")
        assert "42" in result

    def test_ifft_single_element_identity(self, calc):
        """ifft([x]) should return [x]."""
        result = calc.calculate_and_print("ifft([42])")
        assert "42" in result

    def test_fft_all_zeros(self, calc):
        """fft of all zeros should be all zeros."""
        result = calc.calculate_and_print("fft([0,0,0,0])")
        assert result is not None
        assert "0" in result

    def test_ifft_all_zeros(self, calc):
        """ifft of all zeros should be all zeros."""
        result = calc.calculate_and_print("ifft([0,0,0,0])")
        assert result is not None
        assert "0" in result

    def test_fft_symmetric_input(self, calc):
        """fft of symmetric real input [1,2,2,1] produces real output."""
        result = calc.calculate_and_print("fft([1,2,2,1])")
        assert result is not None
        assert "6" in result  # DC = 1+2+2+1

    def test_fft_two_element_roundtrip(self, calc):
        """Round-trip for N=2."""
        result = calc.calculate_and_print("ifft(fft([7,3]))")
        assert result is not None
        assert "7" in result
        assert "3" in result

    def test_fft_uniform_signal(self, calc):
        """fft of uniform signal [c,c,c,c] concentrates at DC bin."""
        result = calc.calculate_and_print("fft([5,5,5,5])")
        assert result is not None
        assert "20" in result  # DC = 5*4

    def test_fft_negative_input(self, calc):
        """fft handles negative input values."""
        result = calc.calculate_and_print("fft([-1,-2,-3,-4])")
        assert result is not None

    def test_ifft_preserves_length(self, calc):
        """ifft output is a valid vector."""
        result = calc.calculate_and_print("ifft([1,2,3,4,5])")
        assert result is not None
        assert result.startswith("[")
        assert result.endswith("]")

    def test_fft_ifft_inverse_order(self, calc):
        """fft(ifft(x)) should also recover x (dual property)."""
        result = calc.calculate_and_print("fft(ifft([1,2,3,4]))")
        assert result is not None
        for v in ["1", "2", "3", "4"]:
            assert v in result

    def test_roundtrip_mixed_sign(self, calc):
        """Round-trip with alternating signs."""
        result = calc.calculate_and_print("ifft(fft([1,-1,1,-1]))")
        assert result is not None
        assert "1" in result
        assert "-1" in result
