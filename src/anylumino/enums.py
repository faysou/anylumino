"""Enums for the fixed option values of anylumino layout widgets.

Each enum is a `StrEnum`, so a member compares equal to its string value and
syncs as that string. Keywords that take one accept the member or its value,
such as ``Orientation.VERTICAL`` or ``"vertical"``, and reject any other value.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TypeVar

E = TypeVar("E", bound=StrEnum)


class Orientation(StrEnum):
    """Whether children run side by side or stacked."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Direction(StrEnum):
    """The order in which a box panel lays out its children."""

    LEFT_TO_RIGHT = "left-to-right"
    RIGHT_TO_LEFT = "right-to-left"
    TOP_TO_BOTTOM = "top-to-bottom"
    BOTTOM_TO_TOP = "bottom-to-top"


class TabPlacement(StrEnum):
    """Which side of a tab panel its tab bar sits on."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class DockMode(StrEnum):
    """Where a dock panel inserts a new widget relative to the existing ones."""

    TAB_AFTER = "tab-after"
    SPLIT_RIGHT = "split-right"
    SPLIT_LEFT = "split-left"
    SPLIT_TOP = "split-top"
    SPLIT_BOTTOM = "split-bottom"


def choice(value: E | str, enum: type[E], name: str) -> E:
    """Return ``value`` as a member of ``enum``.

    Raises
    ------
    ValueError
        If ``value`` is not a value of ``enum``; the message names the
        keyword ``name`` and lists the allowed values.
    """
    try:
        return enum(value)
    except ValueError:
        allowed = ", ".join(repr(member.value) for member in enum)
        raise ValueError(f"{name}={value!r} is not a valid {enum.__name__}; use one of {allowed}") from None


def optional_choice(value: E | str | None, enum: type[E], name: str) -> E | None:
    """Return ``value`` as a member of ``enum``, or `None` when it is `None`."""

    return None if value is None else choice(value, enum, name)
