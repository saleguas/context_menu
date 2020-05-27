import inspect
import sys
import os
import platform

# Need to append all the python subdirectories because Python doesn't recognize them
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
sys.path.append(os.path.join(file_dir, 'windows'))
sys.path.append(os.path.join(file_dir, 'linux'))

# Import the necessary library depending on the OS
if platform.system() == 'Linux':
    from linux import linux_menus
if platform.system() == 'Windows':
    from windows import windows_menus


class ContextMenu:

    def __init__(self, name: str, type: str = None):

        self.name = name
        self.sub_items = []
        self.type = type
        self.isMenu = True  # Needed to avoid circular imports

    def add_items(self, items: list):
        for item in items:
            self.sub_items.append(item)

    def compile(self):
        if platform.system() == 'Linux':
            linux_menus.NautilusMenu(
                self.name, self.sub_items, self.type).compile()
        if platform.system() == 'Windows':
            windows_menus.RegistryMenu(
                self.name, self.sub_items, self.type).compile()


class ContextCommand:

    def __init__(self, name: str, command: str = None, python: 'function' = None):
        self.name = name
        self.command = command
        self.isMenu = False
        self.python = python

        if command != None and python != None:
            raise ValueError('both command and python cannot be defined')

    def get_platform_command(self):
        return self.command[platform.system().lower()]

    def get_method_info(self):
        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)


class FastCommand:

    def __init__(self, name: str, type: str, command: str = None, python: 'function' = None):
        self.name = name
        self.type = type
        self.command = command
        self.python = python

        if command != None and python != None:
            raise ValueError('both command and python cannot be defined')

    def get_method_info(self):
        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)

    def compile(self):
        if platform.system() == 'Linux':
            linux_menus.NautilusMenu(self.name, [ContextCommand(
                self.name, command=self.command, python=self.python)], self.type).compile()
        if platform.system() == 'Windows':
            windows_menus.FastRegistryCommand(
                self.name, self.type, self.command, self.python).compile()
