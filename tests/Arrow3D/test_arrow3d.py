import pytest
from src.arrow3D.arrow3D import Arrow3D, Arrow3DData

def stub_project(xs, ys, zs, matrix):
    return xs, ys, zs

class FakeAxes:
    def __init__(self):
        self.M = "test_matrix"

def test_arrow3d_returns_min_z():
    data = Arrow3DData(
        xs=[0, 1],
        ys=[0, 1],
        zs=[10, 5]
    )

    arrow = Arrow3D(
        data=data,
        project_fn=stub_project
    )

    arrow.axes = FakeAxes()
    z = arrow.do_3d_projection()

    assert z == 5