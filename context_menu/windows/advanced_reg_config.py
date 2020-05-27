import sys
import os


# These are the paths in the registry that correlate to when the context menu is fired.
# For example, FILES is when a file is right clicked
CONTEXT_SHORTCUTS = {
    'FILES': '*\\shell',
    'DIRECTORY': 'Directory\\shell',
    'DIRECTORY_BACKGROUND': 'Directory\\Background\\shell',
    'DESKTOP_BACKGROUND': 'DesktopBackground\\shell',
    'DRIVE': 'Drive\\shell'
}

# Not used yet, but could be useful in the future
COMMAND_PRESETS = {
    'python': sys.executable,
    'pythonw': os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
}


def context_registry_format(item: str) -> 'registry path to the desired type':
    '''
    Ensures the correct value is retrieved from the CONTEXT_SHORTCUTS dictionary.
    '''
    item = item.upper()
    if '.' in item:
        return item.lower()
    return CONTEXT_SHORTCUTS[item]


def command_preset_format(item: str) -> 'Path to desired python type':
    '''
    Used to get the path to a python executable
    '''
    return COMMAND_PRESETS[item.lower()]


def create_file_select_command(func_name: str, func_file_name: str, func_dir_path: str) -> 'Registry valid string to call python function':
    '''
    Creates a registry valid command to link a context menu entry to a funtion, specifically for FILES.
    '''
    python_loc = sys.executable
    sys_section = f'''import sys; sys.path.insert(0, '{func_dir_path[2:]}')'''.replace(
        '\\', '/')
    file_section = f'import {func_file_name}'
    dir_path = """' '.join(sys.argv[1:]) """
    func_section = f'{func_file_name}.{func_name}([{dir_path}])'
    python_portion = f'''"{python_loc}" -c "{sys_section}; {file_section}; {func_section}"'''
    full_command = '''{} \"%1\""'''.format(python_portion)

    return full_command


def create_directory_background_command(func_name: str, func_file_name: str, func_dir_path: str) -> 'Registry valid string to call python function':
    '''
    Creates a registry valid command to link a context menu entry to a funtion, specifically for BACKGROUNDS.

    '''
    python_loc = sys.executable
    sys_section = f'''import sys; import os; sys.path.insert(0, '{func_dir_path[2:]}')'''.replace(
        '\\', '/')
    file_section = f'import {func_file_name}'
    dir_path = 'os.getcwd()'
    func_section = f'{func_file_name}.{func_name}([{dir_path}])'
    full_command = f'''"{python_loc}" -c "{sys_section}; {file_section}; {func_section}"'''

    return full_command

# "C:\\Users\\drale\\AppData\\Local\\Programs\\Python\\Python37-32\\python.exe" -c "import sys; sys.path.insert(0, '/Users/drale/Documents/Programming/dumb programs'); import test; test.main()" \"%1\""
# "C:\\Users\\drale\\AppData\\Local\\Programs\\Python\\Python37-32\\python.exe" -c "import sys; sys.path.insert(0, '/Users/drale/Documents/Programming/dumb programs'); import test; test.main()" \"%1\""
