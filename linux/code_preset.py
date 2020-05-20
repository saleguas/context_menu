from enum import Enum


class ExistingCode(Enum):
    CODE_HEAD = '''
import gi
import sys
import os

gi.require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject

# -------------------------------------------- #

try:
\tfrom urllib import unquote
except ImportError:
\tfrom urllib.parse import unquote
    '''

    CLASS_TEMPLATE = '''
class ExampleMenuProvider(GObject.GObject, Nautilus.MenuProvider):
\tdef __init__(self):
\t\tpass
'''

    METHOD_HANDLER_TEMPLATE = '''
\tdef {}(self, menu, files):
\t\tfilenames = [unquote(subFile.get_uri()[7:]) for subFile in files]
\t\t{}.{}(filenames)

'''

    FILE_ITEMS = '\tdef get_file_items(self, window, files):'
    BACKGROUND_ITEMS = '\tdef get_background_items(self, window, file):'
    SUB_MENU = 'submenu{} = Nautilus.Menu()'
    MENU_ITEM = 'menuitem{} = Nautilus.MenuItem(name = "ExampleMenuProvider::{}", label="{}", tip = "{}", icon = "{}")'
