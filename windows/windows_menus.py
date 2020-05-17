import registry_shortcuts as reg
import advanced_reg_config as arc
import os

class RegistryCommand:
    '''
    Base class for a selectable command.
    '''

    def __init__(self, path, command, preset=None):
        self.path = path
        self.command = command
        if preset != None:
            self.command = arc.command_preset_format(preset) + ' ' + os.path.abspath(command)
            print(self.command)
        self.base_values = []

    def update_command_path(self):
        self.command_path = self.path + '\\command'

    def add_base_values(self, vals):
        for key in vals.keys():
            self.base_values.append((key, vals[key]))


    def compile(self):
        reg.run_admin()
        self.update_command_path()
        reg.create_key(self.path)
        reg.create_key(self.command_path)

        for val_pair in self.base_values:
            reg.set_key_value(self.path, val_pair[0], val_pair[1])

        reg.set_key_value(self.command_path, '', self.command)


class FastRegistryCommand(RegistryCommand):

    def __init__(self, name, command, preset=None):
        super().__init__('', command, preset)

    def update_path(self, path):
        self.path = path


# ------------------------------------------------------------------




class RegistryMenu:

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.items = []

    def add_items(self, items):
        for item in items:
            self.items.append(item)

    def compile(self):
        reg.run_admin()

        reg.create_key(self.path)
        reg.set_key_value(self.path, 'MUIVerb', self.name)
        reg.set_key_value(self.path, 'subcommands', '')
        self.path = self.path + '\\shell'
        reg.create_key(self.path)

        for item in self.items:
            item.update_path(self.path + '\\' + item.name)
            print(self.path + '\\' + item.name, item)
            item.compile()

class FastRegistryMenu(RegistryMenu):

    def __init__(self, type, name):
        self.path = arc.context_registry_format(type) + '\\' + name
        super().__init__(self.path, name)


class FastRegistrySubMenu(RegistryMenu):

    def __init__(self, name):
        super().__init__('', name)

    def update_path(self, path):
        self.path = path
