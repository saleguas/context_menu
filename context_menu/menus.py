import inspect
import sys
import os
import platform

# Need to append all the python subdirectories because Python doesn't recognize them

# Import the necessary library depending on the OS
if platform.system() == 'Linux':
    from context_menu import linux_menus
if platform.system() == 'Windows':
    from context_menu import windows_menus


class ContextMenu:
    '''
    The general menu class. This class generalizes the menus and eventually passes the correct values to the platform-specifically menus.
    '''

    def __init__(self, name: str, type: str = None):
        '''
        Only specify type if it's the root menu.
        '''

        self.name = name
        self.sub_items = []
        self.type = type
        self.isMenu = True  # Needed to avoid circular imports

    def add_items(self, items: list):
        '''
        Adds a list of items to the current menu.
        '''
        for item in items:
            self.sub_items.append(item)

    def compile(self):
        '''
        Recognizes the current platform and passes information to the respective menu. Creates the actual menu.
        '''
        if platform.system() == 'Linux':
            linux_menus.NautilusMenu(
                self.name, self.sub_items, self.type).compile()
        if platform.system() == 'Windows':
            windows_menus.RegistryMenu(
                self.name, self.sub_items, self.type).compile()


class ContextCommand:
    '''
    The general command class.

     A command is an executable entry in a context-menu, where menus hold other commands.
    '''

    def __init__(self, name: str, command: str = None, python: 'function' = None):
        '''
        Do not specify both 'python' and 'command', either pass a python function or a command but not both.
        '''
        self.name = name
        self.command = command
        self.isMenu = False
        self.python = python

        if command != None and python != None:
            raise ValueError('both command and python cannot be defined')

    def get_platform_command(self):
        '''
        Will be used in future changes.
        '''
        return self.command[platform.system().lower()]

    def get_method_info(self) -> "('function name', 'function file name', 'path to function directory')":
        '''
        Extremely important for making shell commands to run python code.

        Returns a tuple.
        '''
        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)


class FastCommand:
    '''
    Used for fast creation of a command. Good if you don't want to get too involved and just jump start a program.

    Extremely similar methods to other classes, only slightly modified. View the documentation of the above classes for info on these methods.
    '''

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
