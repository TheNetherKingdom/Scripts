from __future__ import annotations
from typing import Sequence, Union, List, Tuple, Callable, ClassVar
from dataclasses import dataclass

C = ClassVar['C']


def get(d: dict, value: str, default):
    value = value.strip().lower()

    if " " in value:
        raise NotImplemented

    for k, v in d.items():
        if value in k.split():
            return v

    return default


def map_operators(data: Union[str, Sequence[str]]) -> List[Tuple[Callable, Callable]]:
    # from operator import add, sub, mul, truediv, floordiv, lshift, rshift, and_, or_, xor, pow, \
    #                    iadd, isub, imul, itruediv, ifloordiv, ilshift, irshift, iand, ior, ixor, ipow

    import operator

    d = {"* m mul mult multiply": "mul",
         "/ // d div": "floordiv",
         "+ a add": "add",
         "- s sub minus": "sub",
         ">> > rshift r": "rshift",
         "<< < lshift l": "lshift",
         "** p pow power exp": "pow",

         "& && and": "and_",
         "| || or": "or_",
         "^ x xor": "xor"
         }

    convert = lambda x: (getattr(operator, x), getattr(operator, f"i{x.strip('_')}"))

    if data == "all":
        return list(map(convert, d.values()))

    # ---

    if isinstance(data, str):
        data = data.split()

    func_names = map(lambda x: get(d, x, "add"), data)
    return list(map(convert, func_names))


def set_funcs(cls, function, data: List[Tuple[Callable, Callable]], *, reverse: bool = True, self: bool = False):
    name = (i.__name__.strip("_") for i, _ in data)  # gets the function's name, to be allocated later.
    st = lambda *args: hasattr(*args[:2]) or setattr(*args)

    for i, (a, self_a) in zip(name, data):  # (FUNC_NAME, (FUNC, I_FUNC)) <- might want to refactor this (i, a, self_a).
        st(cls, f"__{i}__", function(a))
        reverse and st(cls, f"__r{i}__", function(a))
        self    and st(cls, f"__i{i}__", function(self_a))


def class_gen(actions: str | Sequence[str], self_actions: bool = False, *, callback_name: str = "_act") -> Callable:
    def setter(cls: C) -> C:
        callback = getattr(cls, callback_name, None)

        if callback is None:
            raise LookupError(f"{callback_name!r} function is missing")

        # generate functions -
        set_funcs(cls, callback, map_operators(actions), self=self_actions)

        # quit -
        return cls

    return setter



@class_gen("+ - / * < >", self_actions=True)
@dataclass
class Point:
    x: int = 0
    y: int = 0

    @staticmethod
    def _act(op: Callable) -> Callable:
        def i_math(self, other):
            self.x, self.y = math(self, other)
            return self

        def math(self, other):
            nonlocal op

            calc = lambda a, b: tuple(op(i, j) for i, j in zip(a, b))  # doesnt assign to 'self', due to arguments.
            # v = lambda x: self if op.__name__.startswith("i") else Point(*x)

            if isinstance(other, Point):
                return calc(self, other)

            if isinstance(other, (int, float)):
                other = [other] * 2

            elif len(other) < 2:
                other = [*other, *[0] * (2 - len(other))]

            return calc(self, other)

        return [math, i_math][op.__name__.startswith("i")]

    def __str__(self):
        return f"({','.join(map(str, self))})"

    def __iter__(self):
        return iter((self.x, self.y))

    def assign(self, other: Sequence):
        self.x, self.y, *_ = other

from pprint import pprint

a = Point()
pprint(dir(a))
