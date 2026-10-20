"""Astryx chat widget."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from enum import StrEnum
from typing import Any

import traitlets as t

from .base import Widget
from .base import _clean_props


class ChatRole(StrEnum):
    """Who wrote a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    """A notice from the application, shown between the turns."""


class MessageStatus(StrEnum):
    """The delivery status of a chat message."""

    SENDING = "sending"
    SENT = "sent"
    ERROR = "error"
    STOPPED = "stopped"


class ToolCallStatus(StrEnum):
    """The status of a tool call shown under a chat message."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class Chat(Widget):
    """Render a chat thread and composer from a Python-owned message list.

    Parameters
    ----------
    messages : Iterable[Mapping[str, Any]], default ()
        Messages in display order. Each message has a `ChatRole` ``role``,
        Markdown ``content``, an optional `MessageStatus` ``status``, and
        optional ``tool_calls``. Each tool call has a ``name``, an optional
        ``target``, and a `ToolCallStatus` ``status``. The enum members are
        strings, so plain strings such as ``"user"`` work too.
    is_streaming : bool, default False
        Whether an assistant turn is in progress. While it is, the composer
        shows a stop control instead of the send button, and the last
        assistant message renders in streaming mode.
    placeholder : str, default ''
        Composer placeholder. Empty uses the Astryx default.
    disabled : bool, default False
        Whether the composer is disabled. A disabled chat ignores submits.
    width : int | float | str | None, default None
        CSS width. Numbers are normalized by anylumino where supported.
    height : int | float | str | None, default 480
        CSS height. The thread scrolls inside this height, so it needs a
        definite value. Numbers are normalized by anylumino where supported.
    **props : Any
        JSON-safe ``ChatLayout`` props forwarded to Astryx, such as
        ``density`` (``"compact"``, ``"balanced"``, or ``"spacious"``).

    Notes
    -----
    Assigning ``messages`` replaces the list; mutating it in place does not
    sync. To stream a reply, replace the last message with its longer
    content::

        chat.messages = [*chat.messages[:-1], {"role": "assistant", "content": text}]

    Submitting does not append the user message. Submit callbacks decide what
    the thread shows.

    See Astryx component docs: <https://astryx.atmeta.com/components/ChatLayout>.
    """

    messages = t.List(t.Dict(), default_value=[]).tag(sync=True)
    is_streaming = t.Bool(False).tag(sync=True)
    placeholder = t.Unicode("").tag(sync=True)

    def __init__(
        self,
        messages: Iterable[Mapping[str, Any]] = (),
        *,
        is_streaming: bool = False,
        placeholder: str = "",
        disabled: bool = False,
        width: int | float | str | None = None,
        height: int | float | str | None = 480,
        **props: Any,
    ) -> None:
        super().__init__(
            "Chat",
            props=_clean_props(props),
            disabled=disabled,
            width=width,
            height=height,
            messages=[dict(message) for message in messages],
            is_streaming=is_streaming,
            placeholder=placeholder,
        )
        self._submit_callbacks: list[Callable[[Chat, str], None]] = []
        self._stop_callbacks: list[Callable[[Chat], None]] = []

    def on_submit(
        self,
        callback: Callable[[Chat, str], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback receiving the chat and the submitted text."""
        if remove:
            self._submit_callbacks = [
                item for item in self._submit_callbacks if item is not callback
            ]

            return

        self._submit_callbacks.append(callback)

    def on_stop(
        self,
        callback: Callable[[Chat], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for the composer stop control."""
        if remove:
            self._stop_callbacks = [
                item for item in self._stop_callbacks if item is not callback
            ]

            return

        self._stop_callbacks.append(callback)

    def _handle_frontend_message(
        self, _widget: object, content: dict[str, Any], _buffers: object
    ) -> None:
        msg_type = content.get("type")
        if msg_type == "submit":
            if self.disabled:
                return

            text = str(content.get("value", ""))
            for callback in list(self._submit_callbacks):
                callback(self, text)

            return

        if msg_type == "stop":
            for callback in list(self._stop_callbacks):
                callback(self)

            return

        super()._handle_frontend_message(_widget, content, _buffers)


__all__ = ["Chat"]
