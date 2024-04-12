# all imports ---------------
from __future__ import annotations
from typing import TYPE_CHECKING
import os
import ctypes
import sys

if TYPE_CHECKING:
    from typing import Any
    from types import FunctionType
    from context_menu.menus import (
        ItemType,
        MethodInfo,
        ActivationType,
        CommandVar,
        ContextMenu,
    )


# registry_shortcuts.py ----------------------------------------------------------------------------------------

try:
    import winreg

    # ------------------------------------------------------------------

    def is_admin() -> bool:
        """
        Returns True if the current python instance has admin, and false otherwise.
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_admin(params: str = sys.argv[0], force: bool = False) -> None:
        """
        If the python instance does not have admin priviledges, it stops the current execution and runs the program as admin.

        You can customize where it runs/Force it to run regardless.
        """
        if not is_admin() or force:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            sys.exit()

    # ------------------------------------------------------------------

    def create_key(path: str, hive: int = winreg.HKEY_CURRENT_USER) -> None:
        """
        Creates a key at the desired path.
        """
        winreg.CreateKey(hive, path)

    def set_key_value(
        key_path: str,
        subkey_name: str,
        value: str | int,
        hive: int = winreg.HKEY_CURRENT_USER,
    ) -> None:
        """
        Changes the value of a subkey. Creates the subkey if it doesn't exist.
        """

        registry_key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, subkey_name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)

    def get_key_value(
        key_path: str,
        subkey_name: str,
        hive: int = winreg.HKEY_CURRENT_USER,
    ) -> Any:
        """
        Gets the value of a subkey.
        """
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as open_key:
            return winreg.QueryValueEx(open_key, subkey_name)[0]

    def list_keys(path: str, hive: int = winreg.HKEY_CURRENT_USER) -> list[str]:
        """
        Returns a list of all the keys at a given registry path.
        """

        open_key = winreg.OpenKey(hive, path)
        key_amt = winreg.QueryInfoKey(open_key)[0]
        keys = []

        for count in range(key_amt):
            subkey = winreg.EnumKey(open_key, count)
            keys.append(subkey)

        return keys

    def delete_key(path: str, hive: int = winreg.HKEY_CURRENT_USER) -> None:
        """
        Deletes the desired key and all other subkeys at the given path.
        """
        open_key = winreg.OpenKey(hive, path)
        subkeys = list_keys(path)

        if len(subkeys) > 0:
            for key in subkeys:
                delete_key(path + "\\" + key)
        winreg.DeleteKey(open_key, "")

except:

    def create_key(path: str, hive: int = 0) -> None:
        """
        Creates a key at the desired path.
        """
        raise NotImplementedError("winreg is not available on this platform")

    def set_key_value(
        key_path: str, subkey_name: str, value: str | int, hive: int = 0
    ) -> None:
        """
        Changes the value of a subkey. Creates the subkey if it doesn't exist.
        """
        raise NotImplementedError("winreg is not available on this platform")

    def get_key_value(key_path: str, subkey_name: str, hive: int = 0) -> Any:
        """
        Gets the value of a subkey.
        """
        raise NotImplementedError("winreg is not available on this platform")

    def list_keys(path: str, hive: int = 0) -> list[str]:
        """
        Returns a list of all the keys at a given registry path.
        """
        raise NotImplementedError("winreg is not available on this platform")

    def delete_key(path: str, hive: int = 0) -> None:
        """
        Deletes the desired key and all other subkeys at the given path.
        """
        raise NotImplementedError("winreg is not available on this platform")

    print("Not windows")


# advanced_reg_config.py ----------------------------------------------------------------------------------------


# These are the paths in the registry that correlate to when the context menu is fired.
# For example, FILES is when a file is right clicked
CONTEXT_SHORTCUTS = {
    "FILELOC": "Software\\Classes\\SystemFileAssociations",
    "FILES": "Software\\Classes\\*\\shell",
    "DIRECTORY": "Software\\Classes\\Directory\\shell",
    "DIRECTORY_BACKGROUND": "Software\\Classes\\Directory\\Background\\shell",
    "DRIVE": "Software\\Classes\\Drive\\shell",
    "DESKTOP": "Software\\Classes\\DesktopBackground\\shell",
}

# Not used yet, but could be useful in the future
COMMAND_PRESETS = {
    "python": sys.executable,
    "pythonw": os.path.join(os.path.dirname(sys.executable), "pythonw.exe"),
}

COMMAND_VARS = {
    "FILENAME": "' '.join(sys.argv[1:]) ",
    "DIR": "os.getcwd()",
    "DIRECTORY": "os.getcwd()",
    "PYTHONLOC": "sys.executable",
}


def join_keys(*keys: str) -> str:
    """Joins parts of a registry path.

    This joins the parts with \\ unlike os.path.join that would
    use / on Linux and break tests.

    :param keys: parts of the registry path
    :return: complete registry path
    """
    return "\\".join(keys)


def context_registry_format(item: str) -> str:
    """
    Converts a verbose type into a registry path.

    For example, 'FILES' -> 'Software\\Classes\\*\\shell'
    """
    item = item.upper()
    if "." in item:
        return join_keys(CONTEXT_SHORTCUTS["FILELOC"], item.lower(), "shell")
    return CONTEXT_SHORTCUTS[item]


def command_preset_format(item: str) -> str:
    """
    Converts a python string to an executable location.

    For example, 'python' -> sys.executable
    """
    return COMMAND_PRESETS[item.lower()]


def command_var_format(item: str) -> str:
    """
    Converts a python string to a value for a command

    """
    return COMMAND_VARS[item.upper()]


def create_file_select_command(
    func_name: str, func_file_name: str, func_dir_path: str, params: str
) -> str:
    """
    Creates a registry valid command to link a context menu entry to a funtion, specifically for file selection(FILES, DIRECTORY, DRIVE).

    Requires the name of the function, the name of the file, and the path to the directory of the file.
    """
    python_loc = sys.executable
    sys_section = f"""import sys; sys.path.insert(0, '{func_dir_path}')""".replace(
        "\\", "/"
    )
    file_section = f"import {func_file_name}"
    dir_path = """' '.join(sys.argv[1:]) """
    func_section = f"""{func_file_name}.{func_name}([{dir_path}],'{params}')"""
    python_portion = (
        f'''"{python_loc}" -c "{sys_section}; {file_section}; {func_section}"'''
    )
    full_command = f'''{python_portion} \"%1\"'''

    return full_command


def create_directory_background_command(
    func_name: str, func_file_name: str, func_dir_path: str, params: str
) -> str:
    """
    Creates a registry valid command to link a context menu entry to a funtion, specifically for backgrounds(DIRECTORY_BACKGROUND, DESKTOP_BACKGROUND).

    Requires the name of the function, the name of the file, and the path to the directory of the file.
    """
    python_loc = sys.executable
    sys_section = (
        f"""import sys; import os; sys.path.insert(0, '{func_dir_path}')""".replace(
            "\\", "/"
        )
    )
    file_section = f"import {func_file_name}"
    dir_path = "os.getcwd()"
    func_section = f"""{func_file_name}.{func_name}([{dir_path}],'{params}')"""
    full_command = (
        f'''"{python_loc}" -c "{sys_section}; {file_section}; {func_section}"'''
    )

    return full_command


def create_shell_command(command: str, command_vars: list[CommandVar]) -> str:
    """
    Creates a shell command and replaces '?' with the command_vars list
    """

    transformed_vars = [
        "' + " + command_var_format(item) + " + '" for item in command_vars
    ]
    new_command = command.replace("?", "{}").format(*transformed_vars)
    python_section = """import os; import sys; os.system('{}')""".format(new_command)
    full_command = '"{}" -c "{}" "%1"'.format(sys.executable, python_section)
    return full_command


# windows_menus.py ----------------------------------------------------------------------------------------


# Used to create a Registry entry
class RegistryMenu:
    """
    Class to convert the general menu from menus.py to a Windows-specific menu.
    """

    def __init__(self, name: str, sub_items: list[ItemType], type: str, icon_path: str = None) -> None:
        """
        Handled automatically by menus.py, but requires a name, all the sub items, and a type
        """
        self.name = name
        self.sub_items = sub_items
        self.type = type.upper()
        self.icon_path = icon_path
        self.path = context_registry_format(type)

    def create_menu(self, name: str, path: str, icon_path: str = None) -> str:
        """
        Creates a menu with the given name and path.

        Used in the compile method.
        """
        key_path = join_keys(path, name)
        create_key(key_path)

        set_key_value(key_path, "MUIVerb", name)
        set_key_value(key_path, "subcommands", "")
        if icon_path is not None:
            set_key_value(key_path, 'Icon', icon_path)

        key_shell_path = join_keys(key_path, "shell")
        create_key(key_shell_path)

        return key_shell_path

    def create_command(self, name: str, path: str, command: str, icon_path: str = None) -> None:
        """
        Creates a key with a command subkey with the 'name' and 'command', at path 'path'.
        """
        key_path = join_keys(path, name)
        create_key(key_path)
        set_key_value(key_path, "", name)

        command_path = join_keys(key_path, "command")
        create_key(command_path)
        set_key_value(command_path, "", command)

        if icon_path is not None:
            set_key_value(key_path, 'Icon', icon_path)

    def compile(
        self, items: list[ItemType] | None = None, path: str | None = None
    ) -> None:
        """
        Used to create the menu. Recursively iterates through each element in the top level menu.
        """
        if items == None:
            # run_admin()
            items = self.sub_items
            path = self.create_menu(self.name, self.path, self.icon_path)

        assert items is not None
        assert path is not None
        for item in items:
            if item.isMenu:
                # if the item is a menu
                submenu_path = self.create_menu(item.name, path, self.icon_path)
                self.compile(items=item.sub_items, path=submenu_path)
                continue

            # Otherwise the item is  a command
            if item.command == None:
                # If a Python function is defined
                func_name, func_file_name, func_dir_path = item.get_method_info()
                new_command = None
                if self.type in ["DIRECTORY_BACKGROUND", "DESKTOP_BACKGROUND"]:
                    # If it requires a background command
                    new_command = create_directory_background_command(
                        func_name, func_file_name, func_dir_path, item.params
                    )
                else:
                    # If it requires a file command
                    new_command = create_file_select_command(
                        func_name, func_file_name, func_dir_path, item.params
                    )
                self.create_command(item.name, path, new_command, item.icon_path)
            elif item.command_vars != None:
                # If the item has to be ran from os.system
                assert item.command is not None
                assert item.command_vars is not None
                new_command = create_shell_command(item.command, item.command_vars)
                self.create_command(item.name, path, new_command, item.icon_path)
            else:
                # The item is just a plain old command
                assert item.command is not None
                self.create_command(item.name, path, item.command, item.icon_path)


# Fast command class
# Everything is identical to either the RegistryMenu class or code in the menus file
class FastRegistryCommand:
    """
    Fast command class.

    Everything is identical to either the RegistryMenu class or code in the menus file
    """

    def __init__(
        self,
        name: str,
        type: ActivationType | str,
        command: str,
        python: FunctionType,
        params: str,
        command_vars: list[CommandVar],
        icon_path: str = None,
    ) -> None:
        self.name = name
        self.type = type
        self.path = context_registry_format(type)
        self.command = command
        self.python = python
        self.params = params
        self.command_vars = command_vars
        self.icon_path = icon_path

    def get_method_info(self) -> MethodInfo:
        import inspect

        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)

    def compile(self) -> None:
        # run_admin()

        key_path = join_keys(self.path, self.name)
        create_key(key_path)

        command_path = join_keys(key_path, "command")
        create_key(command_path)

        new_command = self.command

        if self.command == None:
            # If a python function is defined
            func_name, func_file_name, func_dir_path = self.get_method_info()
            if self.type in ["DIRECTORY_BACKGROUND", "DESKTOP_BACKGROUND"]:
                # If it requires a background selection
                new_command = create_directory_background_command(
                    func_name, func_file_name, func_dir_path, self.params
                )
            else:
                # If it requires a file selection
                new_command = create_file_select_command(
                    func_name, func_file_name, func_dir_path, self.params
                )
        elif self.command_vars != None:
            # If it has command_vars
            new_command = create_shell_command(self.command, self.command_vars)

        set_key_value(command_path, "", new_command)

        if self.icon_path is not None:
            set_key_value(key_path, 'Icon', self.icon_path)


# Testing section...

try:

    def remove_windows_menu(name: str, type: ActivationType | str) -> None:
        """
        Removes a context menu from the windows registry.
        """
        # run_admin()
        menu_path = join_keys(context_registry_format(type), name)
        delete_key(menu_path)

except Exception:
    pass
    # for testing
