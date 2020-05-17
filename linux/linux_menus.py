from code_preset import ExistingCode

class Variable:

    def __init__(self, name, code):
        self.name = name
        self.code = code


class NautilusMenu:

    def __init__(self, name, sub_items, type):
        self.name = name
        self.sub_items = sub_items
        self.type = type
        self.counter = 0
        self.commands = []

    def connect(self, menu, item):
        return "{}.append_item({})".format(menu, item)

    def set_submenu(self, item, menu):
        return '{}.set_submenu({})'.format(item, menu)

    def generate_menu(self):
        base_menu = ExistingCode.SUB_MENU.value
        base_menu = base_menu.format(self.counter)
        self.counter += 1

        return Variable(base_menu.split(' = ')[0], base_menu)

    def generate_item(self, name, command):
        base_command = ExistingCode.MENU_ITEM.value
        formatted_item = base_command.format(self.counter, name, name, '', '')
        self.counter += 1

        return Variable(formatted_item.split(' = ')[0], formatted_item)

    def get_next_item(self):
        val = self.generate_item('', '')
        self.counter -= 1

        return val.name

    def build_script_body(self, name, items):
        top_item = self.generate_item(name, None)
        top_menu = self.generate_menu()
        submenu_com = self.set_submenu(top_item.name, top_menu.name)
        self.commands.append(top_item.code)
        self.commands.append(top_menu.code)
        self.commands.append(submenu_com)

        for item in items:
            if item.isMenu:
                subsubmenu_con = self.connect(top_menu.name, self.get_next_item())
                self.build_script_body(item.name, item.sub_items)
                self.commands.append(subsubmenu_con)
            else:
                formatted_command = self.generate_item(item.name, None)
                self.commands.append(formatted_command.code)
                formatted_command = self.connect(top_menu.name, formatted_command.name)
                self.commands.append(formatted_command)




    def compile(self):
        self.build_script_body(self.name, self.sub_items)
        code_body = '\n'.join(map(lambda x: '\t' + x, self.commands))
        print(code_body)
        full_code = '''
        {}
        {}
        {}
        {}
        '''.format(ExistingCode.CODE_HEAD.value, ExistingCode.CLASS_TEMPLATE.value, ExistingCode.FILE_ITEMS.value, code_body)

        return full_code





# top_command/
#     menu0/
#         menu1/
#               command1
#         command2
#     command3
#
