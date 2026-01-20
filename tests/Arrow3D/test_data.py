import pytest
from src.qt_interface import Arrow3DData

def test_arrow3d_data_as_tuple():
    data = Arrow3DData(
        xs=[1, 2],
        ys=[3, 4],
        zs=[5, 6]
    )

    assert data.as_tuple() == ([1, 2], [3, 4], [5, 6])