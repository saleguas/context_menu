from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import patch
import pytest


if TYPE_CHECKING:
    from typing import Iterable


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
def windows_platform() -> Iterable[None]:
    """Makes the code think we are on Windows."""
    with mock_platform("Windows"):
        yield
