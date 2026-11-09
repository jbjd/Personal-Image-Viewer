"""Tests for base64 logic in C extensions."""

from tests.utils._c_bindings import base64_encode


def test_base64_encode():
    """Should return correct base64 values."""

    assert base64_encode("a") == "YQ=="
    assert base64_encode("ab") == "YWI="
    assert base64_encode("ab+") == "YWIr"
