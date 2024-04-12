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
    # Assuming the icon path should include the .ico extension explicitly if required
    menus.ContextMenu("Test", "FILES", "\\this\\is\\a\\placeholder.ico").compile()

    # Corrected the assertion to match the expected call with the .ico extension
    mocked_winreg.assert_context_menu_with_icon("Software\\Classes\\*\\shell", "Test", "\\this\\is\\a\\placeholder.ico")



@pytest.mark.parametrize(
    "activation_type,params,expected_parent,expected_command,expected_icon",
    (
        # Test with a simple command
        (
            "FILES",
            {"command": "echo hello"},
            "Software\\Classes\\*\\shell",
            "echo hello",
            None,
        ),
        # Test with an icon
        (
            "FILES",
            {"command": "echo hello", "icon_path": "\\this\\is\\a\\placeholder.ico"},
            "Software\\Classes\\*\\shell",
            "echo hello",
            "\\this\\is\\a\\placeholder.ico"
        ),
        # Test with command variables
        (
            "FILES",
            {"command": "echo ?", "command_vars": ["FILENAME"]},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import os; import sys; os.system('echo ' + ' '.join(sys.argv[1:])  + '')" "%1"'''.format(
                sys.executable
            ),
            None,
        ),
        # Test with a python function
        (
            "FILES",
            {"python": foo},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import sys; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([' '.join(sys.argv[1:]) ],'')" "%1"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
            None,
        ),
        # Test with DIRECTORY_BACKGROUND
        (
            "DIRECTORY_BACKGROUND",
            {"python": foo},
            "Software\\Classes\\Directory\\Background\\shell",
            '''"{}" -c "import sys; import os; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([os.getcwd()],'')"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
            None,
        ),
        # Test with DESKTOP
        (
            "DESKTOP",
            {"python": foo},
            "Software\\Classes\\DesktopBackground\\shell",
            '''"{}" -c "import sys; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([' '.join(sys.argv[1:]) ],'')" "%1"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
            None,
        ),
    ),
)
def test_context_command(
    activation_type: ActivationType,
    params: dict[str, Any],
    expected_parent: str,
    expected_command: str,
    expected_icon: str,
    windows_platform: None,
    mocked_winreg: MockedWinReg,
) -> None:
    """Tests ContextCommand with various options."""
    cm = menus.ContextMenu("Test", activation_type)
    cm.add_items([menus.ContextCommand("Command", **params)])
    cm.compile()

    mocked_winreg.assert_context_menu(expected_parent, "Test")

    if expected_icon is not None:
        mocked_winreg.assert_context_command_with_icon(
            f"{expected_parent}\\Test\\shell", "Command", expected_command, expected_icon
        )
    else:
        mocked_winreg.assert_context_command(
            f"{expected_parent}\\Test\\shell", "Command", expected_command
        )


@pytest.mark.parametrize(
    "activation_type,params,expected_parent,expected_command,expected_icon",
    (
        # Test with a simple command
        (
            "FILES",
            {"command": "echo hello"},
            "Software\\Classes\\*\\shell",
            "echo hello",
            None,
        ),
        # Test with an icon
        (
            "FILES",
            {"command": "echo hello", "icon_path": "\\this\\is\\a\\placeholder.ico"},
            "Software\\Classes\\*\\shell",
            "echo hello",
            "\\this\\is\\a\\placeholder.ico",
        ),
        # Test with command variables
        (
            "FILES",
            {"command": "echo ?", "command_vars": ["FILENAME"]},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import os; import sys; os.system('echo ' + ' '.join(sys.argv[1:])  + '')" "%1"'''.format(
                sys.executable
            ),
            None,
        ),
        # Test with a python function
        (
            "FILES",
            {"python": foo},
            "Software\\Classes\\*\\shell",
            '''"{}" -c "import sys; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([' '.join(sys.argv[1:]) ],'')" "%1"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
            None,
        ),
        # Test with DIRECTORY_BACKGROUND
        (
            "DIRECTORY_BACKGROUND",
            {"python": foo},
            "Software\\Classes\\Directory\\Background\\shell",
            '''"{}" -c "import sys; import os; sys.path.insert(0, '{}'); import test_windows; test_windows.foo([os.getcwd()],'')"'''.format(
                sys.executable, Path(__file__).parent.as_posix()
            ),
            None,
        ),
        # Test with file extension
        (
            ".txt",
            {"command": "echo hello"},
            "Software\\Classes\\SystemFileAssociations\\.txt\\shell",
            "echo hello",
            None,
        ),
    ),
)
def test_fast_command(
    activation_type: ActivationType,
    params: dict[str, Any],
    expected_parent: str,
    expected_command: str,
    expected_icon: str | None,
    windows_platform: None,
    mocked_winreg: MockedWinReg,
) -> None:
    """Tests FastCommand with various options."""
    menus.FastCommand("Test", activation_type, **params).compile()

    if expected_icon is not None:
        mocked_winreg.assert_fast_command_with_icon(expected_parent, "Test", expected_command, expected_icon)
    else:
        mocked_winreg.assert_fast_command(expected_parent, "Test", expected_command)

