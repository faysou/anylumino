"""Write rows.arrows, the Arrow stream the Tabulator frontend test decodes.

Run from the repository root:
uv run --no-sync python tests/frontend/fixtures/tabulator/write_rows.py
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

import anylumino as al


frame = pd.DataFrame(
    {
        "symbol": ["ESZ6", "NQZ6"],
        "last": [5012.25, float("nan")],
        "qty": [3, -1],
        "live": [True, False],
        "ts": [datetime(2026, 11, 11, 9, 30), None],
        "note": [None, "halt"],
    }
)
table = al.Tabulator(frame, transport="arrow")
messages = []
table.send = lambda content, buffers=None: messages.append(buffers)
table._send_snapshot()
Path(__file__).with_name("rows.arrows").write_bytes(bytes(messages[0][0]))
