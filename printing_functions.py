from time import sleep as wait
from typing import Sequence, Union

Animated = Union[str, Sequence[str]]

def animate_print(prefix: str = "", animated: Animated = None, suffix: str = "", /, repeat: int = 1, *, sep: str = "", delay: Union[int, float] = 0.1) -> None:
   if not animated:
      animated = (".", "..", "...")
  
   if isinstance(animated, str):
      animated = [animated[:i] for i in range(len(animated))]

   for _ in range(repeat):
      for x in animated:
         print(prefix, x, suffix, end="\r", sep=sep)
         wait(delay)

animated_print("hello")
