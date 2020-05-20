import code_preset

class CodeTemplate:


    def __init__(self, body_commands, sys_paths, imports):
        self.body_commands = body_commands
        self.sys_paths = sys_paths
        self.imports = imports




    def compile(self):
        head = code_preset.CODE_HEAD.value
