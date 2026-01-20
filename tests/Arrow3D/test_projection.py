import pytest
import src.electoerosion

def stub_project(xs, ys, zs, matrix):
    return xs, ys, zs

def test_stub_projection_returns_input():
    xs, ys, zs = [1, 2], [3, 4], [5, 6]
    matrix = object()
    out_xs, out_ys, out_zs = stub_project(xs, ys, zs, matrix)

    assert out_xs == xs
    assert out_ys == ys
    assert out_zs == zs