import winreg
import ctypes
import sys
from enum import Enum



# ------------------------------------------------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, sys.argv[0], None, 1)
        sys.exit()

# ------------------------------------------------------------------

def create_key(path, hive = winreg.HKEY_CLASSES_ROOT):
    winreg.CreateKey(hive, path)

def set_key_value(key_path, subkey_name, value, hive=winreg.HKEY_CLASSES_ROOT):
    '''
    Changes the value of a subkey.

    Args: Path to key, name of subkey, and value
    '''

    registry_key = winreg.OpenKey(hive, key_path, 0,
                                  winreg.KEY_WRITE)
    winreg.SetValueEx(registry_key, subkey_name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(registry_key)


def list_keys(path, hive = winreg.HKEY_CLASSES_ROOT):

    open_key = winreg.OpenKey(hive, path)
    key_amt = winreg.QueryInfoKey(open_key)[0]
    keys = []

    for count in range(key_amt):
        subkey = winreg.EnumKey(open_key, count)
        keys.append(subkey)

    return keys

def delete_key(path, hive = winreg.HKEY_CLASSES_ROOT):
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
