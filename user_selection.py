

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
  def __init__(self, options: list, start: int = 0, 
                *, prefix: str = "\t", sep: str = ". "):
    self.options: dict = dict(enumerate(options, start=start))
    
    self.prefix = prefix
    self.sep = sep
  
  """
  @staticmethod
  def show(*args, *, prefix: str = "", **kwargs) -> None:
    print(prefix, *args, **kwargs)
  """
  
  def __repr__(self) -> str:
    string = (self.prefix + self.sep.join(map(str, item)) for item in self.options. items())
    return "\n".join(string)
  
  @staticmethod
  def quit(msg: Union[Exception, str] = "") -> None:
    if isinstance(msg, Exception):
      raise msg
    
    print(msg)
  
  def pick(self, msg: str = "", default = None, *, show: bool = True):
    if show:
       print('Choose one option -')
       print(self)
    
    return self.options.get(get_input(msg), default)
  
  def assert_pick(self, /, *args, **kwargs):
    k = self.pick()
    while k is None:
      print("Invalid Option. Try again.")
      k = self.pick(show=False)
    
    return k

def main():
  options = ['Exam', 'Monthly Test']
  marks = ["Maths", "Sst", "English", "Hindi", "Science"]

  subjects = HandleOptions(options, 1)
  user = subjects.assert_pick("Enter Answer: ")
  print(f"\nSelected \'{user}\'.")

  print()
  e = get_marks(pad_right(marks))
