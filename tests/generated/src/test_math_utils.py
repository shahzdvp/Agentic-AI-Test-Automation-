from src.math_utils import multiply
import pytest

def test_multiply_positive_numbers():
    assert multiply(2, 3) == 6
    assert multiply(10, 5) == 50

def test_multiply_negative_numbers():
    assert multiply(-2, -3) == 6
    assert multiply(-4, 5) == -20
    assert multiply(4, -5) == -20

def test_multiply_by_zero():
    assert multiply(5, 0) == 0
    assert multiply(0, -5) == 0
    assert multiply(0, 0) == 0

def test_multiply_floating_point():
    assert multiply(2.5, 4.0) == 10.0
    assert multiply(0.1, 0.2) == pytest.approx(0.02)

def test_multiply_sequence_repetition():
    assert multiply("abc", 3) == "abcabcabc"
    assert multiply([1, 2], 2) == [1, 2, 1, 2]
