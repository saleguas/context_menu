import sys
import os


CONTEXT_SHORTCUTS = {
    'FILES': '*\\shell',
    'DIRECTORY': 'Directory\\shell',
    'DIRECTORY_BACKGROUND': 'Directory\\Background\\shell',
    'DESKTOP_BACKGROUND': 'DesktopBackground\\shell',
    'DRIVE': 'Drive\\shell'
}

COMMAND_PRESETS = {
    'python': sys.executable,
    'pythonw': os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
}


def context_registry_format(item):
    item = item.upper()
    if '.' in item:
        return item.lower()
    return CONTEXT_SHORTCUTS[item]


def command_preset_format(item):
    return COMMAND_PRESETS[item.lower()]
