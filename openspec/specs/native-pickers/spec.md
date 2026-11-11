# native-pickers Specification

## Purpose
The `DatePicker`, `TimePicker`, and `DatetimePicker` widgets: browser-native date and time
controls whose value is an ISO 8601 string or `None`.

## Requirements

### Requirement: Picker value is an ISO string or None

A picker's `value`, `min`, and `max` SHALL hold an ISO 8601 string or `None`. Assigning a `date`,
`time`, or `datetime` object, at construction or later, SHALL store its ISO string.

#### Scenario: Date object assigned after construction

- **WHEN** `picker.value = date(2026, 10, 22)` is assigned on a `DatePicker`
- **THEN** `picker.value` is `"2026-10-22"` and the widget state serializes to JSON

### Requirement: Datetime value is complete or None

A `DatetimePicker` SHALL sync a value only when it has both a date and a time. Clearing either
part SHALL set the value to `None`. Editing the date SHALL keep the seconds of the current time.

#### Scenario: Time picked before a date

- **WHEN** the user sets a time while the date is empty
- **THEN** `value` stays `None`

#### Scenario: Date cleared

- **WHEN** the user clears the date of a picker whose value is `"2026-10-21T14:30"`
- **THEN** `value` is `None`

#### Scenario: Seconds kept on a date edit

- **WHEN** the value is `"2026-10-21T14:30:15"` and the user changes the date to the 22nd
- **THEN** `value` is `"2026-10-22T14:30:15"`

### Requirement: Time popup reflects the current value

The hour and minute choices in a `TimePicker` popup SHALL start from the picker's current value,
whether that value was typed, picked, or assigned from Python.

#### Scenario: Value assigned from Python, then hour changed

- **WHEN** a picker created with `"14:30"` is assigned `"09:45"` and the user then picks hour 10
- **THEN** `value` is `"10:45"`

### Requirement: Pickers release their listeners

A picker SHALL remove every listener it registered when its view is disposed or rebuilt, and a
change to `continuous_update` after display SHALL take effect.

#### Scenario: Repeated attribute changes

- **WHEN** a displayed `TimePicker` has `disabled` toggled twenty times
- **THEN** one document-level listener belongs to the picker, as after the first render

#### Scenario: View disposed

- **WHEN** the output holding a picker is cleared
- **THEN** no listener registered by that picker remains on the document or the model
