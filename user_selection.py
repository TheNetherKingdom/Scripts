

def get_input(msg: str = "") -> int:
  while not (k := input(msg).strip()).isnumeric():
    print("Invalid Input, Enter a number.")
  return int(k)
  
def get_marks(subjects: list) -> dict:
  question = 'Enter your {} Marks: '
  ask_with = lambda x: get_input(question.format(x))
  
  return {name: ask_with(name) for name in subjects}
  
def pad_right(a: list) -> list:
  k = max(map(len, a))
  return [i.ljust(k) for i in a]

"""
def get_marks_alternative(subjects: list) -> list:
  question = 'Enter your {} Marks: '
  
  answers = []
  for i in subjects:
    ans
"""
from typing import Union, List

class HandleOptions:
  def __init__(self, options: list, title: str = "", start: int = 1, 
                *, prefix: str = "\t", sep: str = ". "):
    self.options: dict = dict(enumerate(options, start=start))
    
    self.prefix = prefix
    self.title = title or 'Choose one option -'
    self.sep = sep
  
  """
  @staticmethod
  def show(*args, *, prefix: str = "", **kwargs) -> None:
    print(prefix, *args, **kwargs)
  """

  def __repr__(self) -> str:
    string = (self.prefix + self.sep.join(map(str, item)) for item in self.options.items())
    return "\n".join(string)
  
  @staticmethod
  def quit(msg: Union[Exception, str] = "") -> None:
    if isinstance(msg, Exception):
      raise msg
    
    raise NotImplementedError
  
  def show(self) -> None:
    print(f"{self.title}\n{self!r}")

  def pick(self, msg: str = "", default = None, *, topic: bool = True, exit_code: int = -1:
    show() if topic else print(self)
    k = get_input(msg)
    if k != exit_code:
       return self.options.get(g
K, default)
    return k  # self.quit()
  
  def assert_pick(self, /, *args, **kwargs):
    print(self.title)

    while (k := self.pick(*args, topic=False, **kwargs)) is None:
      print("Invalid Option. Try again.")
    
    return k

def main():
  options = ['Exam', 'Monthly Test']
  marks = ["Maths", "Sst", "English", "Hindi", "Science"]

  subjects = HandleOptions(options)
  user = subjects.assert_pick("Enter Answer: ", exit_code = 0)
  print(f"\nSelected {user!r}.")

  print()
  e = get_marks(pad_right(marks))
