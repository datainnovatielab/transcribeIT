# -*- coding: utf-8 -*-

"""Tests for the example module."""

import pytest
from nota_bene import app


def test_something():
    assert example


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise (ValueError)


# Fixture example
@pytest.fixture
def an_object():
    return {}


def test_example(an_object):
    assert an_object == {}
