from dataclasses import dataclass, InitVar, field
from typing import Union, Sequence

ID = Union[int, str]

class Board:
   size: InitVar[ tuple[int, int] ] = (10, 10)
   players: dict[ ID, ID ] = field(default_factory=dict)
   win_length: int = 4

   _: KW_ONLY
   _board: list[list[ID]] = None
   default: ID = "~"
   x: int = 0
   y: int = 0

   def __post_init__(self, /, size):
      self.x, self.y = size
      if self.x < self.win_length or self.y < self.win_length:
        raise ValueError( (f"Board is incompatible with current configuration"
                           f" -- {size=}{self.win_length=}") )
      self._board = [ list([self._default]*self.x) for _ in range(self.y) ]

   
   def check_rows(self, board) -> bool:
      rows = ["".join(map(str, i)) for i in board]
      return [(k, any(str(v)*self.x in row for row in rows)
              for k, v in self.players.items()]
   
   def check_cols(self, board) -> bool:
     return self.check_rows( zip(board) )
   
   def get_right(self, board, x_offset: int = 0, y_offset: int = 0) -> list:
     """
     Gets all board diagonals, starting from position (x, y).
     """

     if y_offset < 0 or x_offset < 0:
       raise IndexError(f"Invalid Argument Caught. {(x_offset, y_offset)}")
     
     return [row[i] for i, row in zip(board[y_offset:], range(x_offset, len(board))))]
     
     
     
   def check_right(self, board) -> bool:
     """
     # Could be simplified to 2 list comprehensions,
     # used yield and an explicit for-loops for better readability.
     """

     # check lower diagonals (\)
     for i in range(len(board[0])): # range(self.x - self.win_length)
       a = self.get_right(board, i)
       #yield self.check_rows(a) if len(a) >= self.win_lengt else False
       yield len(a) >= self.win_length and self.check_rows(a)
     
     # check upper diagonals (/)
     for i in range(len(board)):
       a = self.get_right(board, 0, i)
       yield len(a) >= self.win_length and self.check_rows(a)
