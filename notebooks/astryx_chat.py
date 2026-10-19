# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Astryx chat

# %% [markdown]
# An echo bot built on `ax.Chat`. Python owns the message list: a submit
# appends the user message, then an asyncio task runs a tool-call row from
# running to complete and streams the reply into the last assistant message.
# The stop control cancels the task and marks the reply as stopped.

# %%
from __future__ import annotations

import asyncio

import anylumino.astryx as ax


chat = ax.Chat(
    [
        {"role": "system", "content": "Echo bot ready"},
        {"role": "assistant", "content": "Send a message and I will echo it **word by word**."},
    ],
    placeholder="Message the echo bot",
    width=560,
)
turn: asyncio.Task[None] | None = None


def update_last(**fields: object) -> None:
    chat.messages = [*chat.messages[:-1], {**chat.messages[-1], **fields}]


async def echo(text: str) -> None:
    update_last(tool_calls=[{"name": "Read", "target": "echo.txt", "status": "running"}])
    await asyncio.sleep(1.0)
    update_last(tool_calls=[{"name": "Read", "target": "echo.txt", "status": "complete"}])
    reply = ""
    for word in f"You said: *{text}*. Echoing it back one word at a time.".split():
        reply = f"{reply} {word}".strip()
        update_last(content=reply)
        await asyncio.sleep(0.25)

    update_last(status="sent")
    chat.is_streaming = False


def submit(widget: ax.Chat, text: str) -> None:
    global turn
    widget.messages = [
        *widget.messages,
        {"role": "user", "content": text, "status": "sent"},
        {"role": "assistant", "content": ""},
    ]
    widget.is_streaming = True
    turn = asyncio.get_running_loop().create_task(echo(text))


def stop(widget: ax.Chat) -> None:
    if turn is not None:
        turn.cancel()

    update_last(status="stopped")
    widget.is_streaming = False


chat.on_submit(submit)
chat.on_stop(stop)
chat
