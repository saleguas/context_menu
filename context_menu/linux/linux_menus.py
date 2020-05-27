from code_preset import ExistingCode
from code_builder import CodeBuilder
import os



# Not necessary, but helps simplify the code.
class Variable:

    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code


class NautilusMenu:

    # Constructor, automatically handeled by menus.py
    def __init__(self, name: str, sub_items: list, type: str):
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
        return "{}.append_item({})".format(menu, item)

    def set_submenu(self, item: str, menu: str):
        return '{}.set_submenu({})'.format(item, menu)

    def connect(self, item: str, func: str):
        return '{}.connect("activate", {}, files)'.format(item, func)

# Methods to create variable declarations

    def generate_menu(self):
        base_menu = ExistingCode.SUB_MENU.value
        base_menu = base_menu.format(self.counter)
        self.counter += 1

        return Variable(base_menu.split(' = ')[0], base_menu)

    def generate_item(self, name: str):
        base_command = ExistingCode.MENU_ITEM.value
        formatted_item = base_command.format(self.counter, name, name, '', '')
        self.counter += 1

        return Variable(formatted_item.split(' = ')[0], formatted_item)

    def generate_python_func(self, class_origin: str, class_func: str):
        func_name = 'method_handler{}'.format(self.counter)
        created_func = ExistingCode.METHOD_HANDLER_TEMPLATE.value.format(
            func_name, class_origin, class_func, 'filenames')

        self.counter += 1

        return Variable(f'self.{func_name}', created_func)

    def generate_command_func(self, command: str):
        func_name = 'method_handler{}'.format(self.counter)
        created_func = ExistingCode.COMMAND_HANDLER_TEMPLATE.value.format(
            func_name, command)

        self.counter += 1

        return Variable(f'self.{func_name}', created_func)


# Other misc methods to help out

    def get_next_item(self):
        val = self.generate_item('')
        self.counter -= 1

        return val.name


# Building the script body

    def build_script_body(self, name: str, items: list):
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
        self.build_script_body(self.name, self.sub_items)
        self.commands.append('return menuitem0,')
        full_code = CodeBuilder(
            self.commands, self.script_dirs, self.funcs, self.imports, self.type).compile()

        return full_code

    def create_path(self, path: str, dir: str):
        new_dir = os.path.join(path, dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        return new_dir

    def compile(self):
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
#
