from typing import Union, Sequence, Dict, Any, Tuple
from dataclasses import dataclass, field
from pprint import pprint


def get_dict(d: Dict[str, Any], key: str, default: Any = None):
    if not key:
        return default

    for k, v in d.items():
        if key.lower() in k.split():
            return v

    return default


@dataclass(order=True)
class Scalar:
    x_axis: int = 0
    y_axis: int = 0
    limit: tuple = (0, None)
    
    @staticmethod
    def _apply_lim(n, limit):
        if not limit:
            return
        a, b, *_ = limit
        a is not None and (n := min(a, n))
        b is not None and (n := max(b, n)) 
        return n

    def _limit(self):
        if not self.limit:
            return

        limit = zip((max, min), self.limit)
        
        for func, lim in limit:
            if lim is None:
                continue
            self.assign( map(func, zip(self, [lim]*2)) )
        
    def assign(self, other):
        self.x_axis, self.y_axis, *_ = other

    # arithmatic functions could be compacted;
    # using this for now to allow more flexibility when needed.

    def _self_arithmatic(self, other: Union[object, Sequence], operation: str):
        from operator import add, sub, mul, truediv, floordiv
        d = {
            '+ add a': add,
            '- sub s': sub,
            '* mul mult m': mul,
            '/ div d': truediv,
            '// fdiv floordiv': floordiv
        }

        op = get_dict(d, operation, add)

        if isinstance(other, Scalar):
            self.x_axis = op(self.x_axis, other.x_axis)
            self.y_axis = op(self.y_axis, other.y_axis)

            return self

        if isinstance(other, (int, float)):
            other = [other]*2

        if len(other) < 2:
            other = [*other, *[0] * (2 - len(other))]

        self.x_axis = op(self.x_axis, other[0])
        self.y_axis = op(self.y_axis, other[1])

        return self

    def _arithmatic(self, other: Union['Scalar', Sequence], operation: str):
        from operator import add, sub, mul, truediv, floordiv, pow

        d = {
            '+ add a': add,
            '- sub s': sub,
            '* mul mult m': mul,
            '/ div d': truediv,
            '// fdiv floordiv': floordiv,
            '** pow power': pow
        }

        op = get_dict(d, operation, add)

        if isinstance(other, Scalar):
            return Scalar(op(self.x_axis, other.x_axis), op(self.y_axis, other.y_axis))

        if isinstance(other, (int, float)):
            other = [other]*2

        if len(other) < 2:
            other = [*other, *[0] * (2 - len(other))]

        return Scalar(op(self.x_axis, other[0]), op(self.y_axis, other[1]))


    # Mathematical Operations

    def __add__(self, other: Union[object, Sequence]):
        return self._arithmatic(other, 'add')

    def __sub__(self, other: Union[object, Sequence]):
        return self._arithmatic(other, 'sub')

    def __mul__(self, other: Union[object, Sequence]):
        return self._arithmatic(other, 'mult')

    def __truediv__(self, other: Union[object, Sequence]):
        return self._arithmatic(other, 'div')

    def __floordiv__(self, other: Union[object, Sequence]):
        return self._arithmatic(other, 'fdiv')

    def __pow__(self, power, modulo=None):
        return self._arithmatic(power, 'pow')

    # i-Operations

    def __iadd__(self, other: Union[object, Sequence]):
        return self._self_arithmatic(other, 'add')

    def __isub__(self, other: Union[object, Sequence]):
        return self._self_arithmatic(other, 'sub')

    def __imul__(self, other: Union[object, Sequence]):
        return self._self_arithmatic(other, 'mult')

    def __itruediv__(self, other: Union[object, Sequence]):
        return self._self_arithmatic(other, 'div')

    def __ifloordiv__(self, other: Union[object, Sequence]):
        return self._self_arithmatic(other, 'fdiv')

    def __iter__(self):
        return iter((self.x_axis, self.y_axis))


@dataclass
class Vector:
    location: Scalar
    vel: Scalar
    acc: Scalar

    # _: KW_ONLY

    limit_mag: Scalar

    @staticmethod
    def calc_axes(mag: int, angle: float) -> Tuple[float, float]:
        from math import sin, cos
        return mag * sin(angle), mag * cos(angle)

    def _apply_limit(self):
        n = [self.location, self.vel, self.acc]
        [i._limit() for i in n]

    @property
    def magnitude(self):
        return sum(*self.acc ** 2) ** 0.5

    def apply_vector(self, x_mag: int, y_mag: int):
        pass

    def set_mag(self):
        pass

    def update(self, steps: int = 1):
        self.location += self.vel * steps
        self.vel += self.acc * steps

