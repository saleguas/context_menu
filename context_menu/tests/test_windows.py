import sys
import os

sys.path.append(os.path.abspath('..'))
import menus
import windows_menus

# ------------------------------------------------------------------------------
# Required files for setup
# ------------------------------------------------------------------------------


def foo2(filenames):
    print('foo2')
    print(filenames)
    input()


def foo3(filenames):
    print('foo3')
    print(filenames)
    input()


cm = menus.ContextMenu('Foo menu', type='FILES')
cm2 = menus.ContextMenu('Foo Menu 2')
cm3 = menus.ContextMenu('Foo Menu 3')
cm3.add_items([
    menus.ContextCommand('Foo One', command='echo hello > example.txt'),
])
cm2.add_items([
    menus.ContextCommand('Foo Two', python=foo2),
    cm3,
])
cm.add_items([
    cm2,
    menus.ContextCommand('Foo Three', python=foo3)
])

wm = windows_menus.RegistryMenu(cm.name, cm.sub_items, cm.type)


# ------------------------------------------------------------------------------
# End required files
# ------------------------------------------------------------------------------


def test_registry_menu_items():
    assert wm.sub_items[0].name == 'Foo Menu 2'


def test_registry_menu_path():
    assert wm.path == '*\\shell'


def test_file_select_command():
    func_name, func_file_name, func_dir_path = cm.sub_items[1].get_method_info(
    )

    reg_command = windows_menus.create_file_select_command(
        func_name, func_file_name, func_dir_path).replace('\\', '/')
    valid_command = f'''"{sys.executable}" -c "import sys; sys.path.insert(0, '{func_dir_path[2:]}'); import test_windows; test_windows.foo3([' '.join(sys.argv[1:]) ])" "%1""'''.replace(
        '\\', '/')

    print(reg_command)
    print(valid_command)
    assert reg_command == valid_command


test_file_select_command()
