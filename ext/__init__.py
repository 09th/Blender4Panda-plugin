import os, sys, importlib, imp
extensions = []
ext_names = []
for f in os.listdir(__path__[0]):
    if not f.startswith('__') and f.endswith('.py'):
        module_name = os.path.splitext(f)[0]
        module = importlib.import_module('.'+module_name, __package__)
        imp.reload(module)
        if 'target' in dir(module) and 'order' in dir(module) and 'invoke' in dir(module):
            extensions.append(module)
            ext_names.append(module_name)
extensions.sort(key = lambda e: e.order)
del f, module, module_name
#print(dir())
