from __future__ import annotations
from typing import TYPE_CHECKING
import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# from context_menu import menus
from context_menu import menus

if TYPE_CHECKING:
    from typing import Any

    from context_menu.menus import ActivationType


class MockedWinReg:
    """Mocks the calls to winreg in windows_menus.

    This class patches the functions in windows_menus that are used
    to modify the registry, in order to catch the keys created/deleted,
    and to allow checking from the tests if the expected keys exist.

    This also prevents that the tests really change the keys in the
    registry, and makes it possible to run the tests on non-Windows
    platforms.
    """

    def __init__(self) -> None:
        self._keys: dict[str, Any] = {}
        self._patches = [
            patch(f"context_menu.windows_menus.{fun}", getattr(self, fun))
            for fun in [
                "create_key",
                "set_key_value",
                "get_key_value",
                "list_keys",
                "delete_key",
            ]
        ]

    def __enter__(self) -> "MockedWinReg":
        for patch in self._patches:
            patch.__enter__()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        for patch in self._patches:
            patch.__exit__(*args, **kwargs)

    def create_key(self, path: str) -> None:
        """Mocks creating a key."""
        self._keys.setdefault(f"HKEY_CURRENT_USER\\{path}", {"": ""})

    def set_key_value(self, key_path: str, subkey_name: str, value: str | int) -> None:
        """Mocks changing the value of a key."""
        self._keys.setdefault(f"HKEY_CURRENT_USER\\{key_path}", {"": ""})[
            subkey_name
        ] = value

    def get_key_value(self, key_path: str, subkey_name: str) -> Any:
        """Mocks getting the value of a key."""
        return self._keys.get(f"HKEY_CURRENT_USER\\{key_path}", {}).get(
            subkey_name, None
        )

    def list_keys(self, path: str) -> list[str]:
        """Mocks listing the keys."""
        return self._keys.get(f"HKEY_CURRENT_USER\\{path}", {}).keys()

    def delete_key(self, path: str) -> None:
        """Mocks deleting a key."""
        path = f"HKEY_CURRENT_USER\\{path}"

        if path in self._keys:
            del self._keys[path]

    def assert_context_menu(self, parent: str, name: str) -> None:
        """Asserts that keys for a ContextMenu are correctly set.

        :param parent: parent \\shell key
        :param name: name of the key for the menu
        """
        for k, sk, v in (
            # Checks the key parent\\name
            ("", "", ""),
            ("", "MUIVerb", name),
            ("", "subcommands", ""),
            # Checks the key parent\\name\\shell
            ("\\shell", "", ""),
        ):
            assert self.get_key_value(f"{parent}\\{name}{k}", sk) == v

    def assert_context_command(self, parent: str, name: str, command: str) -> None:
        """Asserts that keys for a ContextCommand are correctly set.

        :param parent: parent \\shell key
        :param name: name of the key for the command
        :param command: expected command set in \\command
        """
        for k, v in (
            # Checks the key parent\\name
            ("", name),
            # Checks the key parent\\name\\command
            ("\\command", command),
        ):
            assert self.get_key_value(f"{parent}\\{name}{k}", "") == v

    def assert_fast_command(self, parent: str, name: str, command: str) -> None:
        """Asserts that keys for a FastCommand are correctly set.

        For some reasons, the name is no set when using FastCommand,
        while it is set for a ContextCommand.

        :param parent: parent \\shell key
        :param name: name of the key for the command
        :param command: expected command set in \\command
        """
        for k, v in (
            # Checks the key parent\\name
            ("", ""),
            # Checks the key parent\\name\\command
            ("\\command", command),
        ):
            assert self.get_key_value(f"{parent}\\{name}{k}", "") == v


def foo() -> None:
    pass


def test_context_menu(windows_platform: None) -> None:
    """Tests ContextMenu alone."""
    with MockedWinReg() as mocked_winreg:
        menus.ContextMenu("Test", "FILES").compile()

        mocked_winreg.assert_context_menu("Software\\Classes\\*\\shell", "Test")


def test_context_menu_nested(windows_platform: None) -> None:
    """Tests nested ContextMenu."""
    with MockedWinReg() as mocked_winreg:
        cm = menus.ContextMenu("Test", "FILES")
        cm2 = menus.ContextMenu("Test2")
        cm2.add_items([menus.ContextMenu("Test3")])
        cm.add_items([cm2])
        cm.compile()

        for parent, name in (
            # Checks shell\\Test
            ("", "Test"),
            # Checks shell\\Test\\shell\\Test2
            ("\\Test\\shell", "Test2"),
            # Checks shell\\Test\\shell\\Test2\\shell\\Test3
            ("\\Test\\shell\\Test2\\shell", "Test3"),
        ):
            mocked_winreg.assert_context_menu(
                f"Software\\Classes\\*\\shell{parent}", name
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
    ),
)
def test_context_command(
    activation_type: ActivationType,
    params: dict[str, Any],
    expected_parent: str,
    expected_command: str,
    windows_platform: None,
) -> None:
    """Tests ContextCommand with various options."""
    with MockedWinReg() as mocked_winreg:
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
) -> None:
    """Tests FastCommand with various options."""
    with MockedWinReg() as mocked_winreg:
        menus.FastCommand("Test", activation_type, **params).compile()

        mocked_winreg.assert_fast_command(expected_parent, "Test", expected_command)
