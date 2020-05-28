import winreg

import ctypes
import sys
from enum import Enum


# ------------------------------------------------------------------

def is_admin():
    '''
    Returns True if the current python instance has admin, and false otherwise.
    '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_admin():
    '''
    If the python instance does not have admin priviledges, it stops the current execution and runs the program as admin.
    '''
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, sys.argv[0], None, 1)
        sys.exit()

# ------------------------------------------------------------------


def create_key(path: str, hive=winreg.HKEY_CLASSES_ROOT):
    '''
    Creates a key at the desired path.
    '''
    winreg.CreateKey(hive, path)


def set_key_value(key_path: str, subkey_name: str, value: 'Value', hive=winreg.HKEY_CLASSES_ROOT):
    '''
    Changes the value of a subkey. Creates the subkey if it doesn't exist.
    '''

    registry_key = winreg.OpenKey(hive, key_path, 0,
                                  winreg.KEY_WRITE)
    winreg.SetValueEx(registry_key, subkey_name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(registry_key)


def list_keys(path: str, hive=winreg.HKEY_CLASSES_ROOT) -> 'List of keys':
    '''
    Returns a list of all the keys at a given registry path.
    '''

    open_key = winreg.OpenKey(hive, path)
    key_amt = winreg.QueryInfoKey(open_key)[0]
    keys = []

    for count in range(key_amt):
        subkey = winreg.EnumKey(open_key, count)
        keys.append(subkey)

    return keys


def delete_key(path: str, hive=winreg.HKEY_CLASSES_ROOT):
    '''
    Deletes the desired key and all other subkeys at the given path.
    '''
    open_key = winreg.OpenKey(hive, path)
    subkeys = list_keys(path)

    if len(subkeys) > 0:
        for key in subkeys:
            delete_key(path + '\\' + key)
    winreg.DeleteKey(open_key, "")


# ------------------------------------------------------------------


# run_admin()
# print(list_keys('Directory\\Background\\shell\\AnyCode'))
# input()
