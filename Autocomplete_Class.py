from typing import Dict, Sequence, Union, List, Tuple, Callable
from dataclasses import dataclass, field
from operator import add, sub, mul, truediv, floordiv, lshift, rshift, and_, or_, xor, pow

Ingredients = Union[Dict[str, int], Sequence[Tuple[str, int]]]

def get(d: dict, value: str, default):
    value = value.strip().lower()
    
    if " " in value:
        raise NotImplemented
    
    for k, v in d.items():
        if value in k.split():
            return v
    
    return default


def set_funcs(cls, function, data: List[Callable]):
    name = (i.__name__.strip("_") for i in data)
 
    for i, a in zip(name, data):
        setattr(cls, f"__{i}__", function(a))
        setattr(cls, f"__r{i}__", function(a))


def map_operators(data: Union[str, Sequence[str]]) -> List[Callable]:
    d = {"* m mul mult multiply": mul,
            "/ // d div": floordiv,
            "+ a add": add,
            "- s sub minus": sub,
            ">> > rshift r": rshift,
            "<< < lshift l": lshift,
            "** p pow power exp": pow,
            
            "& && and": and_,
            "| || or": or_,
            "^ x xor": xor
    }
    
    if isinstance(data, str):
        data = data.split()
    
    convert = lambda x: get(d, x, add)
    return list(map(convert, data))


def class_gen(actions: str):
    def setter(cls: object):
        callback = cls._act if "_act" in dir(cls) else None
        
        if not callback:
            raise ArgumentError(" '_act' function is missing")
            
        set_funcs(cls, callback, map_operators(actions))
        
        return cls
    return setter


@dataclass
@class_gen("+ - * / > < and or")
class Recipe:
    req: Ingredients = field(default_factory=dict)
    result: Ingredients = field(default_factory=dict) # length of 1 for simplicity
    
    
    def _act(op: Callable):
        
        def logic_handler(self, other):
            nonlocal op
            if not isinstance(other, set):
                return op( set(self.result), set(other.result) )
            return op( set(self.result), other)
        
        def math_handler(self, other):
            nonlocal op
            if isinstance(other, int) and other > 0:
               op = lambda d: {k: op(v, other) for k, v in d.items()}
               return Recipe( *map(op, self) )
            
            raise NotImplemented(f"{op.__name__} with {type(other)}")     
         
        part = [math_handler, logic_handler][op in (or_, and_ xor)]
        return part
