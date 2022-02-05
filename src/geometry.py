'''
The geometry.py module implements functionality for managing and
drawing shapes on the Tkinter canvas
'''

class Geometry:
    def __init__(self, shape, x, y):
        self._shape = shape
        self._x = x
        self._y = y
        # xf and yf for end points
        self._xf = None
        self._yf = None
        self._drawable = True

    def get_shape(self) -> 'Shape':
        return self._shape

    def get_x(self) -> int:
        return self._x

    def get_y(self) -> int:
        return self._y

    def get_end_x(self) -> int:
        return self._xf

    def get_end_y(self) -> int:
        return self._yf


    def set_end_x(self, x) -> None:
        self._xf = x

    def set_end_y(self, y) -> None:
        self._yf = y

    def is_drawable(self) -> bool:
        return self._drawable

    def set_drawable(self, value) -> None:
        self._drawable = value

