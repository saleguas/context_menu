# Menus.py contextcommand
# from menus import *
#
# cc = ContextCommand('Directory\\Background\\shell\\test1', 'echo HELLO')
# cc.add_base_values({'Icon' : 'C:\\Users\\drale\\Pictures\\cmd.ico'})
# cc.compile()

# cc = ContextCommand('Test1', 'menus.py', preset='python')
# print(cc.command)

# ------------------------------------------------------------------


# Menus.py contextmenu
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

# ------------------------------------------------------------------

# Menus.py contextmenu order
# from menus import *
#
# menu = ContextMenu('DIRECTORY_BACKGROUND', 'Test Menu 1')
#
# for i in range(5):
#     submenu1 = SubMenu('Sub Menu {}'.format(i))
#     submenu1.add_items([
#         ContextCommand('Cool Command 1', 'echo hello'),
#     ])
#
#     if i != 4:
#         submenu1.add_items([
#             ContextCommand('Cool Command 3', 'echo hello'),
#             ContextCommand('Cool Command 2', 'echo hello2'),
#         ])
#
#     menu.add_items([submenu1])
#
# menu.compile()
# ------------------------------------------------------------------

# def lol():
#     print('hello')

# ------------------------------------------------------------------
# # registry_shortcuts.py
#
# from registry_shortcuts import *
#

# ------------------------------------------------------------------
