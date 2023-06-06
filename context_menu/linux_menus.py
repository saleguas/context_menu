# imports -------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING
import os
from enum import Enum

if TYPE_CHECKING:
    from context_menu.menus import ContextMenu, ItemType, ActivationType, CommandVar

# code_preset.py -------------------------------------


class ExistingCode(Enum):
    """
    Preset values important for metaprogramming.
    """

    CODE_HEAD = """
import gi
import sys
import os

try:
\tgi.require_version('Nautilus', '3.0')
except:
\tgi.require_version('Nautilus', '4.0')

from gi.repository import Nautilus, GObject

# -------------------------------------------- #

try:
\tfrom urllib import unquote
except ImportError:
\tfrom urllib.parse import unquote
    """

    CLASS_TEMPLATE = """
class {}MenuProvider(GObject.GObject, Nautilus.MenuProvider):
\tdef __init__(self):
\t\tpass
"""

    METHOD_HANDLER_TEMPLATE = """
\tdef {}(self, menu, files):
\t\tfilenames = [unquote(subFile.get_uri()[7:]) for subFile in files]
\t\t{}.{}({}, "{}")

"""

    COMMAND_HANDLER_TEMPLATE = """
\tdef {}(self, menu, files):
\t\tfilepath = [unquote(subFile.get_uri()[7:]) for subFile in files][0]
\t\tos.system('{}'{})

"""

    FILE_ITEMS = """\tdef get_file_items(self, *args):
\t\tfiles = args[-1]"""
    BACKGROUND_ITEMS = """\tdef get_background_items(self, *args):
\t\tfiles = args[-1]"""
    SUB_MENU = "submenu{} = Nautilus.Menu()"
    MENU_ITEM = 'menuitem{} = Nautilus.MenuItem(name = "ExampleMenuProvider::{}", label="{}", tip = "{}", icon = "{}")'


# code_builder.py ----------------------------------


class CodeBuilder:
    """
    The CodeBuilder class is used for generating the final python file for the Linux menus.
    """

    def __init__(
        self,
        name: str,
        body_commands: list[str],
        script_dirs: list[str],
        funcs: list[str],
        imports: list[str],
        type: ActivationType | str,
    ) -> None:
        """
        Pass the list of body_commands, the directories of all the scripts, the
        list of the function names, the list of the imports, and the type.
        """
        self.name = name
        self.body_commands = body_commands
        self.script_dirs = list(set(script_dirs))
        self.funcs = funcs
        self.imports = list(set(imports))
        self.type = type.upper()

    def build_script_dirs(self) -> str:
        """
        Creates the header of necessary path configurations.

        Adds all the 'sys.path.appends' in order to immport the classes and functions.

        Handled automatically by compile.
        """
        compiled_dirs = [f'sys.path.append("{x}")' for x in self.script_dirs]
        return "\n".join(compiled_dirs)

    def build_imports(self) -> str:
        """
        Creates the header of necessary imports.

        Handled automatically by compile.
        """
        compiled_imports = [f"import {x}" for x in self.imports]
        return "\n".join(compiled_imports)

    def compile(self) -> str:
        """
        Creates the code file.
        """
        code_head = ExistingCode.CODE_HEAD.value
        script_dirs_code = self.build_script_dirs()
        imports_code = self.build_imports()
        class_dec = ExistingCode.CLASS_TEMPLATE.value.format(self.name)
        class_funcs = "\n\n".join(self.funcs)
        class_type = ExistingCode.FILE_ITEMS.value
        if self.type in ["DIRECTORY_BACKGROUND", "DESKTOP_BACKGROUND"]:
            class_type = ExistingCode.BACKGROUND_ITEMS.value
        class_body = "\n".join(map(lambda x: "\t\t" + x, self.body_commands))

        code_skeleton = """
{}
{}
{}
{}
{}
{}
{}
    """.format(
            code_head,
            script_dirs_code,
            imports_code,
            class_dec,
            class_funcs,
            class_type,
            class_body,
        )

        return code_skeleton


COMMAND_VARS = {
    "FILENAME": "filepath",
    "DIR": "os.getcwd()",
    "DIRECTORY": "os.getcwd()",
    "PYTHONLOC": "sys.executable",
}


def command_var_format(item: str) -> str:
    """
    Converts a python string to a value for a command

    """
    return COMMAND_VARS[item.upper()]


# code_builder.py ----------------------------------


# Not necessary, but helps simplify the code.
class Variable:
    """
    Very simple class with no methods to help simplify the code.
    """

    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code


class NautilusMenu:
    # Constructor, automatically handeled by menus.py
    def __init__(
        self, name: str, sub_items: list[ItemType], type: ActivationType | str
    ) -> None:
        """
        Items required are the name of the top menu, the sub items, and the type.
        """
        # nautilus extensions doesn't work with filenames with spaces
        # Example menu item -> ExampleMenuItem
        self.name = (
            "".join([word.title() for word in name.split()])
            if len(name.split()) > 0
            else name
        )
        self.sub_items = sub_items
        self.type = type
        self.counter = 0

        # Create all the necessary lists that will be used later on
        self.commands: list[str] = []
        self.script_dirs: list[str] = []
        self.funcs: list[str] = []
        self.imports: list[str] = []

    # Methods to create action code
    def append_item(self, menu: str, item: str) -> str:
        """
        Creates a necessary body_command.
        """
        return "{}.append_item({})".format(menu, item)

    def set_submenu(self, item: str, menu: str) -> str:
        """
        Creates a necessary body_command.
        """
        return "{}.set_submenu({})".format(item, menu)

    def connect(self, item: str, func: str) -> str:
        """
        Creates a necessary body_command.
        """
        return '{}.connect("activate", {}, files)'.format(item, func)

    # Methods to create variable declarations

    def generate_menu(self) -> Variable:
        """
        Generates a nautilus menu variable.
        """
        base_menu = ExistingCode.SUB_MENU.value
        base_menu = base_menu.format(self.counter)
        self.counter += 1

        return Variable(base_menu.split(" = ")[0], base_menu)

    def generate_item(self, name: str) -> Variable:
        """
        Generates a nautilus command variable.
        """
        base_command = ExistingCode.MENU_ITEM.value
        formatted_item = base_command.format(self.counter, name, name, "", "")
        self.counter += 1

        return Variable(formatted_item.split(" = ")[0], formatted_item)

    def generate_python_func(
        self, class_origin: str, class_func: str, params: str
    ) -> Variable:
        """
        Generates a command attached to a python function
        """
        func_name = "method_handler{}".format(self.counter)
        created_func = ExistingCode.METHOD_HANDLER_TEMPLATE.value.format(
            func_name, class_origin, class_func, "filenames", params
        )

        self.counter += 1

        return Variable(f"self.{func_name}", created_func)

    def generate_command_func(self, command: str) -> Variable:
        """
        Generates a command attached to a python function
        """
        func_name = "method_handler{}".format(self.counter)
        created_func = ExistingCode.COMMAND_HANDLER_TEMPLATE.value.format(
            func_name, command, ""
        )

        self.counter += 1

        return Variable(f"self.{func_name}", created_func)

    def generate_mod_command_func(
        self, command: str, command_vars: list[CommandVar]
    ) -> Variable:
        """
        Generates a command attached to a python function that allows special variables.
        """
        new_command = command.replace("?", "{}")
        modified_vars = [command_var_format(item) for item in command_vars]
        final_str = ", ".join(modified_vars)
        func_name = "method_handler{}".format(self.counter)
        replace_func = """.format({})""".format(final_str)
        created_func = ExistingCode.COMMAND_HANDLER_TEMPLATE.value.format(
            func_name, new_command, replace_func
        )

        self.counter += 1

        return Variable(f"self.{func_name}", created_func)

    # Other misc methods to help out

    def get_next_item(self) -> str:
        """
        Very niche, required in other methods.
        """
        val = self.generate_item("")
        self.counter -= 1

        return val.name

    # Building the script body

    def build_script_body(self, name: str, items: list[ItemType]) -> None:
        """
        Builds the body commands of the script.
        """
        top_item = self.generate_item(name)
        top_menu = self.generate_menu()
        submenu_com = self.set_submenu(top_item.name, top_menu.name)
        self.commands.append(top_item.code)
        self.commands.append(top_menu.code)
        self.commands.append(submenu_com)

        for item in items:
            if item.isMenu:
                subsubmenu_con = self.append_item(top_menu.name, self.get_next_item())
                self.build_script_body(item.name, item.sub_items)
                self.commands.append(subsubmenu_con)
                continue

            # if the item is a command
            formatted_command = self.generate_item(item.name)
            self.commands.append(formatted_command.code)

            if item.python != None:
                # if there is a python function
                item_info = item.get_method_info()
                connected_func = self.generate_python_func(
                    item_info[1], item_info[0], item.params
                )
                self.script_dirs.append(item_info[2])
                self.imports.append(item_info[1])
            elif item.command_vars != None:
                # if the command requries parameters
                assert item.command is not None
                assert item.command_vars is not None
                connected_func = self.generate_mod_command_func(
                    item.command, item.command_vars
                )
            else:
                # if the command is simply normal
                assert item.command is not None
                connected_func = self.generate_command_func(item.command)
                # connected_func = self.generate_func('os', 'system')

            self.funcs.append(connected_func.code)

            connected_command = self.connect(
                formatted_command.name, connected_func.name
            )
            self.commands.append(connected_command)

            self.commands.append(
                self.append_item(top_menu.name, formatted_command.name)
            )

    def build_script(self) -> str:
        """
        Finishes and returns the full code.
        """
        self.build_script_body(self.name, self.sub_items)
        self.commands.append("return menuitem0,")
        full_code = CodeBuilder(
            self.name,
            self.commands,
            self.script_dirs,
            self.funcs,
            self.imports,
            self.type,
        ).compile()

        return full_code

    def create_path(self, path: str, dir: str) -> str:
        """
        Creates a path to directory. Creates all sub-directories
        """
        new_dir = os.path.join(path, dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        return new_dir

    def compile(self) -> None:
        """
        Creates the code, creates a file, and moves it to the correct location.
        """
        code = self.build_script()
        save_loc = os.path.join(os.path.expanduser("~"), ".local/share/")
        print(save_loc)
        save_loc = self.create_path(save_loc, "nautilus-python")
        save_loc = self.create_path(save_loc, "extensions")
        save_loc = os.path.join(save_loc, f"{self.name}.py")
        py_file = open(save_loc, "w")
        py_file.write(code)
        py_file.close()


# Testing section...

try:

    def remove_linux_menu(name) -> None:
        save_loc = os.path.join(
            os.path.expanduser("~"), ".local/share/nautilus-python/extensions", name
        )
        try:
            os.remove(save_loc + ".py")
            os.remove(save_loc + ".pyc")
        except Exception as e:
            print(e)

except Exception:
    pass
