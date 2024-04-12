from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from unittest.mock import patch

if TYPE_CHECKING:
    from typing import Any, Iterable


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

    def assert_context_menu_with_icon(self, parent: str, name: str, icon_path: str) -> None:
        """Asserts that keys for a ContextMenu with icon are correctly set.

        :param parent: parent \\shell key
        :param name: name of the key for the menu
        :param icon_path: path of the icon for the menu
        """
        for k, sk, v in (
            # Checks the key parent\\name
            ("", "", ""),
            ("", "MUIVerb", name),
            ("", "Icon", icon_path),
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

    def assert_context_command_with_icon(self, parent: str, name: str, command: str, icon_path: str) -> None:
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

        assert self.get_key_value(f"{parent}\\{name}", "Icon") == icon_path

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

    def assert_fast_command_with_icon(self, parent: str, name: str, command: str, icon_path: str) -> None:
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

        assert self.get_key_value(f"{parent}\\{name}", "Icon") == icon_path


@pytest.fixture
def mocked_winreg() -> Iterable[MockedWinReg]:
    """Mocks the calls to winreg in windows_menus."""
    with MockedWinReg() as winreg:
        yield winreg


class MockedPlatform:
    """Mocks the value returned by platform.system().

    This class can be used to change the return of platform.system()
    to run the tests as if we were on another platform.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._patches = [
            patch("context_menu.menus.platform", self),
        ]

    def system(self) -> str:
        return self._name

    def __enter__(self) -> "MockedPlatform":
        for patch in self._patches:
            patch.__enter__()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        for patch in self._patches:
            patch.__exit__(*args, **kwargs)


def mock_platform(name: str) -> MockedPlatform:
    """Mocks the value returned by platform.system().

    :param name: new returned value
    """
    return MockedPlatform(name)


@pytest.fixture
def linux_platform() -> Iterable[None]:
    """Makes the code think we are on Linux."""
    with mock_platform("Linux"):
        yield


@pytest.fixture
def windows_platform() -> Iterable[None]:
    """Makes the code think we are on Windows."""
    with mock_platform("Windows"):
        yield
