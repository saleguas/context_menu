import sys
sys.path.insert(0, "../linux")

try:
    import linux_menus
except ImportError:
    print('Import error')

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

    def __init__(self, name, command):
        self.name = name
        self.command = command
        self.isMenu = False




cm = ContextMenu('Foo')

cm2 = ContextMenu('Foo2')
cm3 = ContextMenu('Foo3')
cm3.add_items([
    ContextCommand('Command1', 'ex')
])
cm2.add_items([
    cm3,
    ContextCommand('Command2', 'ex')
])
cm.add_items([
    cm2,
    ContextCommand('Command3', 'ex')
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
