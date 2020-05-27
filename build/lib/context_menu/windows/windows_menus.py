import registry_shortcuts as reg
import advanced_reg_config as arc
import os


# ------------------------------------------------------------------


# Used to create a Registry entry
class RegistryMenu:

    def __init__(self, name: str, sub_items: list, type: str):
        self.name = name
        self.sub_items = sub_items
        self.type = type.upper()
        self.path = arc.context_registry_format(type)

    def create_menu(self, name: str, path: str) -> 'Path to shell key of new menu':
        '''
        Used in the compile method. Makes creating menus easier.
        '''
        key_path = os.path.join(path, name)
        reg.create_key(key_path)

        reg.set_key_value(key_path, 'MUIVerb', name)
        reg.set_key_value(key_path, 'subcommands', '')

        key_shell_path = os.path.join(key_path, 'shell')
        reg.create_key(key_shell_path)

        return key_shell_path

    def create_command(self, name: str, path: str, command: str):
        key_path = os.path.join(path, name)
        reg.create_key(key_path)
        reg.set_key_value(key_path, '', name)

        command_path = os.path.join(key_path, 'command')
        reg.create_key(command_path)
        reg.set_key_value(command_path, '', command)

    def compile(self, items: list = None, path: str = None):
        '''
        Used to create the meun. Recursively iterates through each element in the top level menu.
        '''
        if items == None:
            reg.run_admin()
            items = self.sub_items
            path = self.create_menu(self.name, self.path)

        for item in items:
            if item.isMenu:
                submenu_path = self.create_menu(item.name, path)
                self.compile(items=item.sub_items, path=submenu_path)
            else:
                if item.command == None:
                    func_name, func_file_name, func_dir_path = item.get_method_info()
                    new_command = None
                    if self.type in ['DIRECTORY_BACKGROUND', 'DESKTOP_BACKGROUND']:
                        new_command = arc.create_directory_background_command(
                            func_name, func_file_name, func_dir_path)
                    else:
                        new_command = arc.create_file_select_command(
                            func_name, func_file_name, func_dir_path)
                    self.create_command(item.name, path, new_command)
                else:
                    self.create_command(item.name, path, item.command)


# Fast command class
# Everything is identical to either the RegistryMenu class or code in the menus file
class FastRegistryCommand:

    def __init__(self, name: str, type: str, command: str, python: 'function'):
        self.name = name
        self.type = type
        self.path = arc.context_registry_format(type)
        self.command = command
        self.python = python

    def get_method_info(self):
        import inspect

        func_file_path = os.path.abspath(inspect.getfile(self.python))

        func_dir_path = os.path.dirname(func_file_path)
        func_name = self.python.__name__
        func_file_name = os.path.splitext(os.path.basename(func_file_path))[0]

        return (func_name, func_file_name, func_dir_path)

    def compile(self):
        reg.run_admin()

        key_path = os.path.join(self.path, self.name)
        reg.create_key(key_path)

        command_path = os.path.join(key_path, 'command')
        reg.create_key(command_path)

        new_command = None

        if self.command == None:
            func_name, func_file_name, func_dir_path = self.get_method_info()
            if self.type in ['DIRECTORY_BACKGROUND', 'DESKTOP_BACKGROUND']:
                new_command = arc.create_directory_background_command(
                    func_name, func_file_name, func_dir_path)
            else:
                new_command = arc.create_file_select_command(
                    func_name, func_file_name, func_dir_path)
        else:
            new_command = self.command

        reg.set_key_value(command_path, '', new_command)
