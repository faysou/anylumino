import assert from "node:assert/strict";
import test from "node:test";

import { composeDatetime } from "../../src/anylumino/static/controls/native_control_widget.js";

for (const [name, date, time, previous, expected] of [
  ["time picked before a date", "", "14:30", null, null],
  ["date cleared", "", "14:30", "2026-10-21T14:30", null],
  ["time cleared", "2026-10-21", "", "2026-10-21T14:30", null],
  ["both set from empty", "2026-10-21", "14:30", null, "2026-10-21T14:30"],
  ["date edit keeps seconds", "2026-10-22", "14:30", "2026-10-21T14:30:15", "2026-10-22T14:30:15"],
  ["time edit drops old seconds", "2026-10-21", "15:00", "2026-10-21T14:30:15", "2026-10-21T15:00"],
]) {
  test(`composeDatetime: ${name}`, () => {
    assert.equal(composeDatetime(date, time, previous), expected);
  });
}
