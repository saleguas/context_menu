
# imports -------------------------------------------------
import os
from enum import Enum

# code_preset.py -------------------------------------


class ExistingCode(Enum):
    '''
    Preset values important for metaprogramming.
    '''

    CODE_HEAD = '''
import gi
import sys
import os

gi.require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject

# -------------------------------------------- #

try:
\tfrom urllib import unquote
except ImportError:
\tfrom urllib.parse import unquote
    '''

    CLASS_TEMPLATE = '''
class ExampleMenuProvider(GObject.GObject, Nautilus.MenuProvider):
\tdef __init__(self):
\t\tpass
'''

    METHOD_HANDLER_TEMPLATE = '''
\tdef {}(self, menu, files):
\t\tfilenames = [unquote(subFile.get_uri()[7:]) for subFile in files]
\t\t{}.{}({})

'''

    COMMAND_HANDLER_TEMPLATE = '''
\tdef {}(self, menu, files):
\t\tos.system('{}')

'''

    FILE_ITEMS = '\tdef get_file_items(self, window, files):'
    BACKGROUND_ITEMS = '\tdef get_background_items(self, window, files):'
    SUB_MENU = 'submenu{} = Nautilus.Menu()'
    MENU_ITEM = 'menuitem{} = Nautilus.MenuItem(name = "ExampleMenuProvider::{}", label="{}", tip = "{}", icon = "{}")'

# code_builder.py ----------------------------------


class CodeBuilder:
    '''
    The CodeBuilder class is used for generating the final python file for the Linux menus.
    '''

    def __init__(self, body_commands: list, script_dirs: list, funcs: list, imports: list, type: str):
        '''
        Pass the list of body_commands, the directories of all the scripts, the
        list of the function names, the list of the imports, and the type.
        '''
        self.body_commands = body_commands
        self.script_dirs = list(set(script_dirs))
        self.funcs = funcs
        self.imports = list(set(imports))
        self.type = type.upper()

    def build_script_dirs(self):
        '''
        Creates the header of necessary path configurations.

        Adds all the 'sys.path.appends' in order to immport the classes and functions.

        Handled automatically by compile.
        '''
        compiled_dirs = [f'sys.path.append("{x}")' for x in self.script_dirs]
        return '\n'.join(compiled_dirs)

    def build_imports(self):
        '''
        Creates the header of necessary imports.

        Handled automatically by compile.
        '''
        compiled_imports = [f'import {x}' for x in self.imports]
        return '\n'.join(compiled_imports)

    def compile(self):
        '''
        Creates the code file.
        '''
        code_head = ExistingCode.CODE_HEAD.value
        script_dirs_code = self.build_script_dirs()
        imports_code = self.build_imports()
        class_dec = ExistingCode.CLASS_TEMPLATE.value
        class_funcs = '\n\n'.join(self.funcs)
        class_type = ExistingCode.FILE_ITEMS.value
        if self.type in ['DIRECTORY_BACKGROUND', 'DESKTOP_BACKGROUND']:
            class_type = ExistingCode.BACKGROUND_ITEMS.value
        class_body = '\n'.join(map(lambda x: '\t\t' + x, self.body_commands))

        code_skeleton = '''
{}
{}
{}
{}
{}
{}
{}
    '''.format(code_head, script_dirs_code, imports_code, class_dec, class_funcs, class_type, class_body)

        return code_skeleton


# code_builder.py ----------------------------------

# Not necessary, but helps simplify the code.
class Variable:
    '''
    Very simple class with no methods to help simplify the code.
    '''

    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code


class NautilusMenu:

    # Constructor, automatically handeled by menus.py
    def __init__(self, name: str, sub_items: list, type: str):
        '''
        Items required are the name of the top menu, the sub items, and the type.
        '''
        self.name = name
        self.sub_items = sub_items
        self.type = type
        self.counter = 0

# Create all the necessary lists that will be used later on
        self.commands = []
        self.script_dirs = []
        self.funcs = []
        self.imports = []

# Methods to create action code
    def append_item(self, menu: str, item: str):
        '''
        Creates a necssary body_command.
        '''
        return "{}.append_item({})".format(menu, item)

    def set_submenu(self, item: str, menu: str):
        '''
        Creates a necssary body_command.
        '''
        return '{}.set_submenu({})'.format(item, menu)

    def connect(self, item: str, func: str):
        '''
        Creates a necssary body_command.
        '''
        return '{}.connect("activate", {}, files)'.format(item, func)

# Methods to create variable declarations

    def generate_menu(self):
        '''
        Generates a nautilus menu variable.
        '''
        base_menu = ExistingCode.SUB_MENU.value
        base_menu = base_menu.format(self.counter)
        self.counter += 1

        return Variable(base_menu.split(' = ')[0], base_menu)

    def generate_item(self, name: str):
        '''
        Generates a nautilus command variable.
        '''
        base_command = ExistingCode.MENU_ITEM.value
        formatted_item = base_command.format(self.counter, name, name, '', '')
        self.counter += 1

        return Variable(formatted_item.split(' = ')[0], formatted_item)

    def generate_python_func(self, class_origin: str, class_func: str):
        '''
        Generates a command attached to a python function
        '''
        func_name = 'method_handler{}'.format(self.counter)
        created_func = ExistingCode.METHOD_HANDLER_TEMPLATE.value.format(
            func_name, class_origin, class_func, 'filenames')

        self.counter += 1

        return Variable(f'self.{func_name}', created_func)

    def generate_command_func(self, command: str):
        '''
        Generates a command attached to a python function
        '''
        func_name = 'method_handler{}'.format(self.counter)
        created_func = ExistingCode.COMMAND_HANDLER_TEMPLATE.value.format(
            func_name, command)

        self.counter += 1

        return Variable(f'self.{func_name}', created_func)


# Other misc methods to help out


    def get_next_item(self):
        '''
        Very niche, required in other methods.
        '''
        val = self.generate_item('')
        self.counter -= 1

        return val.name


# Building the script body


    def build_script_body(self, name: str, items: list):
        '''
        Builds the body commands of the script.
        '''
        top_item = self.generate_item(name)
        top_menu = self.generate_menu()
        submenu_com = self.set_submenu(top_item.name, top_menu.name)
        self.commands.append(top_item.code)
        self.commands.append(top_menu.code)
        self.commands.append(submenu_com)

        for item in items:
            if item.isMenu:
                subsubmenu_con = self.append_item(
                    top_menu.name, self.get_next_item())
                self.build_script_body(item.name, item.sub_items)
                self.commands.append(subsubmenu_con)
            else:
                formatted_command = self.generate_item(item.name)
                self.commands.append(formatted_command.code)

                connected_func = None

                if item.python != None:
                    item_info = item.get_method_info()
                    connected_func = self.generate_python_func(
                        item_info[1], item_info[0])
                    self.script_dirs.append(item_info[2])
                    self.imports.append(item_info[1])
                else:
                    connected_func = self.generate_command_func(item.command)
                    # connected_func = self.generate_func('os', 'system')

                self.funcs.append(connected_func.code)

                connected_command = self.connect(
                    formatted_command.name, connected_func.name)
                self.commands.append(connected_command)

                formatted_command = self.append_item(
                    top_menu.name, formatted_command.name)
                self.commands.append(formatted_command)

    def build_script(self):
        '''
        Finishes and returns the full code.
        '''
        self.build_script_body(self.name, self.sub_items)
        self.commands.append('return menuitem0,')
        full_code = CodeBuilder(
            self.commands, self.script_dirs, self.funcs, self.imports, self.type).compile()

        return full_code

    def create_path(self, path: str, dir: str):
        '''
        Creates a path to directory. Creates all sub-directories
        '''
        new_dir = os.path.join(path, dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        return new_dir

    def compile(self):
        '''
        Creates the code, creates a file, and moves it to the correct location.
        '''
        code = self.build_script()
        save_loc = os.path.join(os.path.expanduser('~'), '.local/share/')
        print(save_loc)
        save_loc = self.create_path(save_loc, 'nautilus-python')
        save_loc = self.create_path(save_loc, 'extensions')
        save_loc = os.path.join(save_loc, f'{self.name}.py')
        py_file = open(save_loc, 'w')
        py_file.write(code)
        py_file.close()


# top_command/
#     menu0/
#         menu1/
#               command1
#         command2
#     command3
