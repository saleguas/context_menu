import sys
sys.path.insert(0, "../linux")

try:
    import linux_menus
except ImportError:
    print('Import error')

import os
import inspect


class ContextMenu:

    def __init__(self, name, type=None):
        self.name = name
        self.sub_items = []
        self.type = type
        self.isMenu = True # Needed to avoid circular imports



    def add_items(self, items):
        for item in items:
            self.sub_items.append(item)

    def compile(self):
        linux_menus.NautilusMenu(self.name, self.sub_items, self.type).compile()



class ContextCommand:

    def __init__(self, name, command=None, python=None):
        self.name = name
        self.command = command
        self.isMenu = False
        self.python = python

    def get_method_info(self):
        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)







import test1
import test2

cm = ContextMenu('Foo', type='directory_background')

cm2 = ContextMenu('Foo2')
cm3 = ContextMenu('Foo3')
cm3.add_items([
    ContextCommand('foo1', python=test1.foo1)
])
cm2.add_items([
    cm3,
    ContextCommand('Command2', python=test1.foo2)
])
cm.add_items([
    cm2,
    ContextCommand('Command3', python=test2.foo3)
])

# cm = ContextMenu('Foo')
# cm3 = ContextMenu('Foo3')
# cm3.add_items([
#     ContextCommand('Command1', 'ex')
# ])
#
# cm.add_items([
#     cm3,
#     ContextCommand('Command3', 'ex')
# ])
#
print(cm.compile())

# top_command/
#     menu0/
#         menu1/
#               command1
#         command2
#     command3
#


# from menus import *
#
# menu = ContextMenu('DIRECTORY_BACKGROUND', 'Test Menu 1')
# submenu1 = SubMenu('Sub Menu 1')
# submenu1.add_items([
#     ContextCommand('Cool Command 1', 'echo hello'),
#     ContextCommand('Cool Command 2', 'echo hello2'),
#     ContextCommand('Cool Command 3', 'echo hello3')
# ])
#
# submenu2 = SubMenu('Sub Menu 2')
# submenu2.add_items([
#     submenu1,
#     ContextCommand('Cool Command 4', 'echo hello2'),
#     ContextCommand('Cool Command 5', 'echo hello3')
# ])
#
# menu.add_items([submenu2, submenu1])
# menu.compile()
