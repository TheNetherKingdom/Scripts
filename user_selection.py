from typing import Union, List

class HandleOptions:
  def __init__(self, options: list, start: int = 0, 
                *, prefix: str = "\t", sep: str = ""):
    self.options: dict = dict(enumerate(options, start=start))
    
    self.prefix = prefix
    self.sep = sep
  
  
  @staticmethod
  def show(*args, *, prefix: str = "", **kwargs) -> None:
    print(prefix, *args, **kwargs)
  
  
  def __repr__(self) -> str:
    string = (self.prefix + self.sep.join(item) for item in self.options. items())
    return "\n".join(string)
  
  @staticmethod
  def quit(msg: Union[Exception, str] = "") -> None:
    if isinstance(msg, Exception):
      raise msg
    
    print(msg)
  
  def pick(self, msg: str = "", default = None):
    print('Choose one option -')
    print(self)
    
    clean_input = lambda x: get_input(x).strip().lower()
    
    return self.options.get(clean_input(msg), default)
  
  def assert_pick(self, /, *args, **kwargs):
    while (k := self.pick()) is None:
      print("Invalid Input. Enter an option")
    
    return k

if __name__ == "__main__":
   options = ['Exam', 'Monthly Test']
   marks = ["Maths", "Sst", "English", "Hindi", "Science"]

   subjects = HandleOptions(options, 1)
   user = subjects.assert_pick("Enter Answer: ")
