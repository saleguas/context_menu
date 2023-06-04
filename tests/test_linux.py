from context_menu import menus, linux_menus
# from context_menu import menus
#
# from context_menu import linux_menus


fc = menus.FastCommand('TestCommand', type='FILES',
                       command='echo hello > example.txt')


def test_command_func():
    nm = linux_menus.NautilusMenu(fc.name, [menus.ContextCommand(
        fc.name, command=fc.command, python=fc.python)], fc.type)
    lm = nm.generate_command_func(fc.command)
    valid_func = '''
\tdef method_handler0(self, menu, files):
\t\tfilepath = [unquote(subFile.get_uri()[7:]) for subFile in files][0]
\t\tos.system('echo hello > example.txt')\n
'''
    assert valid_func == lm.code


# getting rid of this after update
# def test_build_script_body():
#     nm = linux_menus.NautilusMenu(fc.name, [menus.ContextCommand(
#         fc.name, command=fc.command, python=fc.python)], fc.type)
#     nm.build_script()
#     valid_commands = ['menuitem0 = Nautilus.MenuItem(name = "ExampleMenuProvider::TestCommand", label="TestCommand", tip = "", icon = "")', 'submenu1 = Nautilus.Menu()', 'menuitem0.set_submenu(submenu1)',
#                       'menuitem2 = Nautilus.MenuItem(name = "ExampleMenuProvider::TestCommand", label="TestCommand", tip = "", icon = "")', 'menuitem2.connect("activate", self.method_handler3, files)', 'submenu1.append_item(menuitem2)', 'return menuitem0,']

#     print(nm.commands)
#     print()
#     print(valid_commands)
#     assert nm.commands == valid_commands
