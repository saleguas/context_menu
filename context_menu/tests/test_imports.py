import os
import sys

def test_importing():
    from context_menu import menus
    c = menus.ContextCommand("test")
    assert c.name == "test"



