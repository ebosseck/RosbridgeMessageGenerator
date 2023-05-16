import os
import importlib

def loadModulesFromPath(path: str):
    '''
    Loads all Modules in all packages contained in the given path
    '''

    res = {}
    stack = []
    stack.append((path, ""))
    modules = []
    while len(stack) > 0:
        path, module = stack[0]
        stack.remove((path, module))
        lst = os.listdir(path)
        for d in lst:
            s = os.path.abspath(path) + os.sep + d

            if os.path.isdir(s):
                if os.path.exists(s + os.sep + "__init__.py"):
                    childmod = d if module == "" else module + "." + d
                    stack.append((s, childmod))
                    modules.append(childmod)
            elif d.endswith(".py") and "__init__" not in d:
                splitted = d.split('.')
                seperated = splitted[0] + "".join(("." + c) for c in splitted[1: -1])
                childmod = seperated if module == "" else module + "." + seperated
                modules.append(childmod)
    # load the modules
    for d in modules:
        res[d] = importlib.import_module(d)
    return res