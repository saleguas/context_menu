from code_preset import ExistingCode


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
