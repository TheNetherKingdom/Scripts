from dataclasses import dataclass, KW_ONLY
from typing import Callable, Any, Union, Iterator


def is_seq(x) -> bool:
    return hasattr(x, "__getitem__")


def is_iter(x) -> bool:
    return hasattr(x, "__iter__")


def recur_hashable(a: Any):
    # is_seq = lambda x: hasattr(x, "__getitem__")
    bad_hash = lambda x: not isinstance(x, (str, int)) and is_seq(a)

    # if not bad_hash(a):
    #     yield hash(a)
    #     return

    for i in a:

        if not bad_hash(i):
            yield i
            continue

        if isinstance(i, dict):
            i = i.items()

        yield tuple(recur_hashable(tuple(i)))


def _hash(x: Any) -> tuple:
    return tuple(recur_hashable(x))


@dataclass(init=False, repr=False)
class IDict(dict):
    
    def __init__(self, *args, **kwargs):
        # _modify: bool = True
        #   self._modify = _modify
        #   self._d = dict(*args, **kwargs)
        self._hashable: bool | None = None  # Default Assumption
        super().__init__(dict(*args, **kwargs))

    def __hash__(self) -> int:
        """
        maybe too many conversions to 'tuple'. . .
        """
    
        if self._hashable is None:
            try:
                return setattr(self, "_hashable", True) or hash(tuple(self.items()))
            except TypeError:  # unable to hash
                # self._hashable = False
                return setattr(self, "_hashable", False) or hash(tuple((k, _hash(v)) for k, v in self.items()))

        if self._hashable:
            return hash(tuple(self.items()))

        return hash(tuple((k, recur_hashable(v)) for k, v in self.items()))  # keys are always hashable

    def __eq__(self, other) -> bool:
        if isinstance(other, dict):
            return hash(self) == hash(other)

        return tuple(self.items()) == tuple(other)


    def get_value(self, key: str, *, sep: str = None, default=None) -> str:
        key = key.lower().strip()

        """
        try:
            next(self.filter_type(str, items=False)) # O(1)
        except StopIteration:
            raise LookupError("No 'str' like key!")
        """

        if not any(map(lambda x: isinstance(x, str), self)):
            raise LookupError("No string like key found!")

        for k, v in self.filter_type(str):
            if key in k.lower().split(sep):
                return v
        return default

    def filter(self, func: Callable, *, items: bool = True) -> filter:
        """
        Only executes function on the keys,
        items - whether to return just the key, or the key-value pair.
        """

        if items:
            return filter(lambda x: func(x[0]), self.items())
            # return ((k, v) for k, v in self.items() if func(k))
        return filter(func, self)

    def filter_type(self, _type: type, *, items: bool = True):
        return self.filter(lambda x: isinstance(x, _type), items=items)

    def flip(self, in_place: bool = False):
        """
        Flips the key-value pairs; values becomes the keys, and vice-versa.
        Does not support hashable classes / frozen dictionaries.
        """

        hashable = lambda x: isinstance(x, (str, tuple, int))
        if not all(map(hashable, self.values())):
            raise TypeError("Unable to hash dictionary values.")

        if not in_place:
            return IDict(zip(self.values(), self.keys()))

        k, v = zip(*self.items())  # map(reversed, self.items())

        self.clear()
        for key, value in zip(v, k):
            self[key] = value

    def show(self, indent: int = 4, sort_keys: bool = False) -> str:
        from json import dumps

        return dumps(self, ensure_ascii=False, indent=indent, sort_keys=sort_keys, default=lambda: "-TypeError-")



class IterCache:
    """
    A cached iter object,
    Enabling iterating over an iterator without consuming it;

    this is done by capturing/caching the loaded elements,
    and re-iterating over them instead of where the iter stopped.

    Essentialy, allowing a dynamic loading of the object, and afterwards re-using it.
    
    
    Potential Edge Case: Has only one cache, cant "rollback" to multiple points.
        -- why would it need to rollback?! this is just an iterator.
    This (currently) doesn't work like a stack; rather, it's like a bucket - fill it, or spill it, no in-between.
    """

    def __init__(self, i: Iterator):
        self.i = i
        self._cache = False
        self._captured = []

    def __next__(self, *args, **kwargs):
        k = next(self.i, *args, **kwargs)

        self._cache and self._captured.append(k)
        return k

    def __iter__(self):
        if not self._cache:
            # self._captured and self._captured.clear()
            self._captured = []
            return self.i

        return Iterate.chain(self._captured, self.i)  # can prone elements of previous generators

    def __enter__(self, *, self_load: bool = True):
        self._cache = self_load

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.i = Iterate.chain(self._captured, self.i)
        self._cache = False


class Iterate:
    """
    A class to extend/build on 'iterator's behavior.
    Note; Any changes done to the original iterator would be reflected, and vice versa.
    """
    
    def __init__(self, *args, **kwargs):
        self.feedback: list = []

        self._cache = False
        self._captured = []

        if len(args) == 1 and not kwargs:
            a = args[0]

            if is_seq(a):
                raise ValueError(f"\'{a}\' is a sequence, no need to cast it.")  # could use '!r'; not consistent.

            if is_iter(a):
                self.i = a  # 'iter(a)' doesnt duplicate ;-;
                return

            raise ValueError(f"\'{a}\' is not an iterable.")

        self.i = iter(*args, **kwargs)

    def __next__(self, *args, **kwargs):
        self.feedback.append(k := next(self.i, *args, **kwargs))
        self._cache and self._captured.append(k)
        return k

    def __iter__(self):
        if not self._cache:
            # self._captured and self._captured.clear()
            # self._captured = []
            return self.i

        return Iterate.chain(self._captured, self.i)  # can prone elements of previous generators
        # return Iterate.chain(self.feedback, self.i)

    def __enter__(self, *, load_self: bool = False):
        self._cache = not load_self

    def __exit__(self, *args):
        # exc_type, exc_val, exc_tb = args
        self.i = Iterate.chain(self._captured, self.i)
        # self.restore()
        self._cache = False
        if self._captured:
            self._captured = []

    def __contains__(self, item):
        # LOADS TILL ELEMENT IS REACHED! (cant rollback)
        return item in self.i

    def _force_enter(self, *args, **kwargs):
        return self.__enter__(*args, **kwargs)

    def _force_exit(self, *args):
        return self.__exit__(*args)

    def restore(self, *, cache: bool = True, clear: bool = False, check: bool = True):
        
        # check if there's anying cached / was consumed -
        if check and ((cache and not self._cache) or (not cache and not self.feedback)):
            raise LookupError("No Cache was Found!")

        is_cached = (self.feedback, self._captured)[cache]
        self.i = Iterate.chain(is_cached, self.i)
        
        # keep the saved cache -
        if not clear:
            return

        #   d = [([], self._captured), (self.feedback, [])]
        #   self.feedback, self._captured = d[cache]

        if not cache:
            self.feedback = []
            return

        self._captured = []

    def apply(self, func: Callable) -> None:
        self.i = map(func, self.i)

    def load(self, amount: int, *, load_self: bool = True):
        # for _ in range(amount):
        #     yield next(self)
        # return [k for _ in range(amount) if (k := next(self, self)) is not self]
        return list(self.iter(amount, load_self=load_self))

    def filter(self, func: Callable) -> None:
        self.i = filter(func, self)

    def chunks(self, size: int, *, overflow: bool = True, cast: type = tuple):
        if not overflow:
            return cast([*zip(*[self] * size)])

        j = list(self)
        n = len(j) % size
        return cast(list(zip(*[iter(j)] * size)) + [tuple(j[-n:])] * bool(n))

    def iter(self, amount: int = -1, *, load_self: bool = True):
        """
        amount: amount of elements to load.
        load_self: whether ot not it should modify the iterator.
        """

        if amount < 0:
            return

        with self:
            not load_self or self._force_exit()

            for _ in range(amount):
                if (j := next(self, self)) is self:
                    return
                yield j

    def safe_iter(self, amount: int = -1, yield_cond: Callable = None, apply_cond: int = -1,
                  *, _op: Callable = any, load_self: bool = True):
        """

        :param amount:
        :param yield_cond:
        :param apply_cond: which part to call it on; [-1] Index and Elem, [0] Index,
                -- Removed due to complexity and redundancy; could simply call filter() or enumerate() on the iterator.
        :param _op: Given sequence of boolean values; [<INDEX>, <ITER_ELEM>]
        :param load_self: whether to modify original iterator or not.
        :return:
        """

        raise NotImplemented("Function implementation is not complete.")
        # DOESN'T WORK YET

        # if amount < 0:
        #     return
        #
        # def cond(*args):
        #     nonlocal yield_cond, apply_cond
        #
        #     if not yield_cond:
        #         return True
        #
        #     # noinspection PyBroadException
        #     def safe_cond(func, *args, **kwargs) -> bool:
        #         try:
        #             return bool(func(*args, **kwargs))
        #         except Exception:
        #             return False
        #
        #     if apply_cond not in range(-1, 2):
        #         raise ValueError(f"Cant Apply function; Given {apply_cond}\tAll[-1] Index[0] Value[1]")
        #
        #     safe = lambda *x, **kx: bool(safe_cond(yield_cond, *x, **kx))
        #     args = [(args, args[apply_cond])[apply_cond != -1]]
        #     if len(args) == 1:
        #         return safe(*args)
        #
        #     return _op(map(safe, args))
        #
        # if not load_self:
        #     self._force_enter(load_self=load_self)
        #
        # for i in range(amount):
        #     j = next(self, self)
        #
        #     if j is self:
        #         self._force_exit()
        #         return
        #
        #     if cond(i, j):
        #         yield j
        #
        # self._force_exit()

    def slice(self, s: slice, *, load_self: bool = True):
        default = (0, 0, 1)
        setd = lambda a: [*a][a[0] is None]
        start, stop, step = map(setd, zip((s.start, s.stop, s.step), default))

        if start > stop and step > 0:
            return

        if step < 1:
            # this would mean - to load the entire iterator;
            # then, why is an iterator needed anyway?
            raise NotImplementedError

        not load_self and self._force_enter(load_self=load_self)

        if start:
            [next(self, None) for _ in range(start)]  # loads and skips N elements.

        for n in range(0, stop - start):
            j = next(self, self)

            if j is self:
                self._force_exit()
                return

            if n % step == 0:
                yield j

        self._force_exit()

        # self.load(start, load_self=load_self)
        # yield from (j for n, j in enumerate(self.iter(stop - start)) if not n % step)

    def reverse(self):
        self.i = reversed(self)

    @property
    def full(self):
        return Iterate(Iterate.chain(self.feedback, self.i))

    @staticmethod
    def chain(*iterables):
        for i in iterables:
            yield from i

    @staticmethod
    def chain_elem(*iterables):
        """
        Equivelent to 'itertools.chain.from_iterable()'
        """

        # is_iter = lambda x: hasattr(x, "__iter__")
        can_iter = lambda x: not isinstance(x, (str, int)) and is_iter(x)

        if len(iterables) == 1:
            iterables = iterables[0]

            if not can_iter(iterables):
                yield iterables
                return

        for i in iterables:
            if can_iter(i):
                yield from Iterate.chain_elem(tuple(i))
            else:
                yield i

    def __radd__(self, other):
        self.i = Iterate.chain(other, self.i)
        return self

    def __add__(self, other):
        self.i = Iterate.chain(self.i, other)
        return self

    def __and__(self, other):
        return self + other

    def __floordiv__(self, other: int):
        return self.chunks(other)

    def __mul__(self, other: int):
        return self.load(other)

    def __rshift__(self, other: int):
        self.load(other)
        return self

    def __rrshift__(self, other):
        return Iterate(Iterate.chain(other, self))

    def __format__(self, format_spec):
        print(format_spec)
        return "Iter(...)"

    def __len__(self):
        return 0

    def __getitem__(self, item: Union[int, slice]):
        if isinstance(item, slice):
            return self.slice(item)

        if isinstance(item, int):
            return list(self.slice(slice(item, item + 1, 1)))

        raise NotImplementedError(f"Unsupported type. Given {type(item)}.")

    # Might want to rework the operators actions
    # changing the shift methods and the math operators.
    #
    # TODO:
    # -
    # -


@dataclass(init=False, repr=False)
class IEnumerate:
    def __init__(self, *args, max_load: int = 10, **kwargs):
        self.e = enumerate(*args, **kwargs)

    # def __str__(self):
    #     return repr(self)

    def __repr__(self):
        pass



def main():

  p = IDict(a=("hello", [123, [23]]), b=12)
  b = IEnumerate("ABC")
  c = Iterate(enumerate("ABC"))

  k = Iterate(iter(range(28)))

  chunks = p["a"]
  print(chunks)
  

if __name__ == "__main__":
  main()
