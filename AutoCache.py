import pathlib
from pathlib import Path
import inspect
import pickle
import yaml

import io
import zlib
import functools
import typing

_k = Path("../Bin")
binpath = lambda x: _k / x  # to be modified later (refer to _TODO_).


def gen_path(func, *args, **kwargs) -> Path:
    pass


def chain(*iters):
    for i in iters:
        yield from i


def gen_name(func, args, kwargs, *, sep="_*_") -> tuple[str, str]:
    return func.__name__, \
        sep.join(chain(map(str, args),
                       (f"{k}={v.__name__ if hasattr(v, '__call__') else str(v)}" for k, v in kwargs.items())))


def _cache(m: int = 255, file: str | Path = "DefaultCache.yaml",
           *, load: bool = True, cache: bool = True, compress: bool | int = True):
    def handler(func):
        def wrapper(*args, **kwargs):
            nonlocal load, cache, file, m, compress

            if not isinstance(file, (str, Path)):
                raise ValueError(f"Invalid File Path {file} ({type(file)})")

            a = file.suffix.strip(".") if isinstance(file, Path) else file.rsplit(".", 1)[-1]
            # can be combined into one sentence
            if a != "yaml":
                raise NotImplementedError("File isn't in YAML format.")

            if not hasattr(func, "__call__") or func.__name__ == "<lambda>":
                raise ValueError(f"'func' argument isn't callable.")

            path = binpath(file)
            compress = [compress, 6][compress is True]
            if compress < 0 or compress > 9:
                raise zlib.error("Invalid Compression lvl. Please Enter a number between 0-9")

            if not path.exists():
                flush_cache(path)

            with path.open("r") as f:
                data = yaml.load(f.read(), yaml.Loader)

            default = {}
            a, b = gen_name(func, args, kwargs)

            if load:
                if (v := data.get(a, default).get(b, default)) is not default:
                    v = compress and zlib.decompress(v)
                    return pickle.loads(v)

            if cache:
                if a not in data:
                    data[a] = {}

                convert = pickle.dumps

                if compress:
                    convert = lambda x: zlib.compress(pickle.dumps(x), compress)

                # if isinstance(k := func(*args, **kwargs), (map, filter)) or \
                #         (hasattr(k, "__iter__") and not hasattr("__len__")):
                #     raise ValueError(f"Cant Cache Iterators ; <{type(k)}")
                if isinstance(k := func(*args, **kwargs), typing.Iterator):
                    raise ValueError(f"Cant Cache Iterators ; {type(k)}")
                data[a] |= {b: convert(k)}

                if (length := len(data[a])) > m:
                    print(f"Warning: Removing {length - m} elements from the cache!")
                    data[a] = dict(tuple(data[a].items())[length - m:])

                with path.open("w") as f:
                    yaml.dump(data, f)

                return k

            return func(*args, **kwargs)
        return wrapper
    return handler


@functools.wraps(_cache)
def cache(*args, **kwargs):
    if len(args) == 1 and hasattr(func := args[0], "__call__"):
        return _cache()(func)
    return _cache(*args, **kwargs)


def flush_cache(file: str | Path = "default_cache.yaml") -> None:
    if isinstance(file, str):
        file = binpath(file)

    with file.open("w") as f:
        f.write("None: None")


def main():
    flush_cache()


if __name__ == "__main__":
    (_k := main()) and print(_k)

# TODO: add a cache directory in 'bin' - and have a separate cache-file for every different file.
#  *(files may share the same functions' names)
# TODO: add a run-time cache, reduce accesing the file;
#  then, cache all the changes after the program ends (possible optimization, especially if the file gets larger).
