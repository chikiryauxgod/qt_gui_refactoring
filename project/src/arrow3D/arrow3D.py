from mpl_toolkits.mplot3d import proj3d
import numpy as np
from matplotlib.patches import FancyArrowPatch

# Класс для 3D стрелок
'''
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)
'''
class Arrow3DData:
    def __init__(self, xs, ys, zs):
        self.xs = xs
        self.ys = ys
        self.zs = zs

    def as_tuple(self):
        return self.xs, self.ys, self.zs

def matplotlib_project(xs, ys, zs, matrix):
    return proj3d.proj_transform(xs, ys, zs, matrix)

class Arrow3D(FancyArrowPatch):
    def __init__(self, data, project_fn, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._data = data
        self._project = project_fn

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._data.as_tuple()
        xs, ys, zs = self._project(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)
