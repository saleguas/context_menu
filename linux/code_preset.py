from enum import Enum


class ExistingCode(Enum):
    CODE_HEAD = '''
import gi
gi.require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject
    '''

    CLASS_TEMPLATE = '''
class ExampleMenuProvider(GObject.GObject, Nautilus.MenuProvider):
\tdef __init__(self):
        \tpass
    '''

    FILE_ITEMS = 'def get_file_items(self, window, files):'
    BACKGROUND_ITEMS = 'sdef get_background_items(self, window, file):'
    SUB_MENU = 'submenu{} = Nautilus.Menu()'
    MENU_ITEM = 'menuitem{} = Nautilus.MenuItem(name = "ExampleMenuProvider::{}", label="{}", tip = "{}", icon = "{}")'
