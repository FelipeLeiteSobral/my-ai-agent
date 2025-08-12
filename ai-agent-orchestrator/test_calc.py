import pytest
from calc import soma, subtrai

def test_soma():
    assert soma(2, 3) == 5
    assert soma(-1, 1) == 0

def test_subtrai():
    assert subtrai(5, 3) == 2
    assert subtrai(0, 1) == -1
