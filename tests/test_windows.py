from __future__ import annotations
from typing import TYPE_CHECKING
import sys
from pathlib import Path
import pytest

# from context_menu import menus
from context_menu import menus

if TYPE_CHECKING:
    from typing import Any

    from context_menu.menus import ActivationType
    from context_menu.pytest_plugin import MockedWinReg


def foo() -> None:
    pass


def test_context_menu(windows_platform: None, mocked_winreg: MockedWinReg) -> None:
    """Tests ContextMenu alone."""
    menus.ContextMenu("Test", "FILES", "\\this\\is\\a\\placeholder").compile()

    mocked_winreg.assert_context_menu_with_icon("Software\\Classes\\*\\shell", "Test", "\\this\\is\\a\\placeholder.ico")


def test_context_menu_nested(
    windows_platform: None, mocked_winreg: MockedWinReg
) -> None:
    """Tests nested ContextMenu."""
    cm = menus.ContextMenu("Test", "FILES")
    cm2 = menus.ContextMenu("Test2")
    cm2.add_items([menus.ContextMenu("Test3")])
    cm.add_items([cm2])
    cm.compile()

    for parent, name, icon in (
        # Checks shell\\Test
        ("", "Test", "icon1.ico"),
        # Checks shell\\Test\\shell\\Test2
        ("\\Test\\shell", "Test2", "icon3.ico"),
        # Checks shell\\Test\\shell\\Test2\\shell\\Test3
        ("\\Test\\shell\\Test2\\shell", "Test3", "icon2.ico"),
    ):
        mocked_winreg.assert_context_menu_with_icon(f"Software\\Classes\\*\\shell{parent}", name, icon)


@pytest.mark.parametrize(
    "activation_type,params,expected_parent,expected_command",
    (
        # Test with a simple command
        (
            "FILES",
            {"command": "echo hello"},
            "Software\\Classes\\*\\shell",
            "echo hello",
        ),
        # Test with command variables
        (
            "FILES",
            {"command": "echo ?", "command_vars": ["FILENAME"]},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import os; import sys; os.system('echo ' + ' '.join(sys.argv[1:])  + '')" "%1"'''.format(
                sys.executable
            ),
        ),
        # Test with a python function
        (
            "FILES",
            {"python": foo},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import sys; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([' '.join(sys.argv[1:]) ],'')" "%1"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
        ),
        # Test with DIRECTORY_BACKGROUND
        (
            "DIRECTORY_BACKGROUND",
            {"python": foo},
            "Software\\Classes\\Directory\\Background\\shell",
            '''"{}" -c "import sys; import os; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([os.getcwd()],'')"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
        ),
    ),
)
def test_context_command(
    activation_type: ActivationType,
    params: dict[str, Any],
    expected_parent: str,
    expected_command: str,
    windows_platform: None,
    mocked_winreg: MockedWinReg,
) -> None:
    """Tests ContextCommand with various options."""
    cm = menus.ContextMenu("Test", activation_type)
    cm.add_items([menus.ContextCommand("Command", **params)])
    cm.compile()

    mocked_winreg.assert_context_menu(expected_parent, "Test")
    mocked_winreg.assert_context_command(
        f"{expected_parent}\\Test\\shell", "Command", expected_command
    )


@pytest.mark.parametrize(
    "activation_type,params,expected_parent,expected_command",
    (
        # Test with a simple command
        (
            "FILES",
            {"command": "echo hello"},
            "Software\\Classes\\*\\shell",
            "echo hello",
        ),
        # Test with command variables
        (
            "FILES",
            {"command": "echo ?", "command_vars": ["FILENAME"]},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import os; import sys; os.system('echo ' + ' '.join(sys.argv[1:])  + '')" "%1"'''.format(
                sys.executable
            ),
        ),
        # Test with a python function
        (
            "FILES",
            {"python": foo},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import sys; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([' '.join(sys.argv[1:]) ],'')" "%1"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
        ),
        # Test with DIRECTORY_BACKGROUND
        (
            "DIRECTORY_BACKGROUND",
            {"python": foo},
            "Software\\Classes\\Directory\\Background\\shell",
            '''"{}" -c "import sys; import os; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([os.getcwd()],'')"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
        ),
        # Test with file extension
        (
            ".txt",
            {"command": "echo hello"},
            "Software\\Classes\\.txt\\shell",
            "echo hello",
        ),
    ),
)
def test_fast_command(
    activation_type: ActivationType,
    params: dict[str, Any],
    expected_parent: str,
    expected_command: str,
    windows_platform: None,
    mocked_winreg: MockedWinReg,
) -> None:
    """Tests FastCommand with various options."""
    menus.FastCommand("Test", activation_type, **params).compile()

    mocked_winreg.assert_fast_command(expected_parent, "Test", expected_command)
