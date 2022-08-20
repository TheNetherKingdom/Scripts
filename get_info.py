
def const_print(a, sep: str = ' '):
    cols = zip(*a)
    a = map(lambda x: map(str, x), a)
    get_max = lambda x: max(x, key=len)
    amount = list(map(len, map(get_max, map(lambda x: map(str, x), cols))))

    new = [sep.join([v.ljust(amount[i % len(amount)]) for i, v in enumerate(j)]) for j in a]
    for i in new:
        print(i)

def show_func(k: object) -> str:
        try:
            *name, _, t = str(k).split()[:5]
            return f"{' '.join(name)}; is {t}" + '>' if name[0].startswith('<') else ''
        except (IndexError, ValueError):
            return k

def show_attrs(a: object, ignore=('builtins', "doc")):
    print(a, type(a), sep=' | ')

    fix_attr = lambda x: f"{x:_^{len(x) + 4}}"

    
    
    # can be reduced to a single 'list comprehension'
    c = []
    for i in sorted(filter(lambda x: x not in map(fix_attr, ignore), a.__dir__())):
        c.append((i, show_func(getattr(a, i)), type(getattr(a, i))))
    const_print(c, sep=" = ")
