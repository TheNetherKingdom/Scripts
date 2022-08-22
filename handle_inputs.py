def get_int(msg: str = "", reply: str = "", *args, **kwargs) -> Number:
   from re import match
   
   isnum = lambda x: match(r"^[+-]?\d+(.\d+)?$", x)

   if not reply:
      reply = "Invalid input. Please enter a number."

   while not isnum(k := input(msg, *args, **kwargs).strip()):
       print(reply)
   return [int, float]["." in k](k)
