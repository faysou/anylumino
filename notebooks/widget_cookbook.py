# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # anylumino widget cookbook
#
# This notebook is organized like an API cookbook. Each public anylumino widget gets its own section, and each subsection is a separate runnable example cell.
#
# The repeated patterns are intentional: a subsection should show one concrete operation, such as constructing a widget, reading state, wiring a callback, composing children, or changing appearance.

# %%
from __future__ import annotations

from datetime import date, datetime, time
from urllib.parse import quote

import anylumino as al
import anylumino.spectrum as sx


ACCENT_STYLE = (
    "display: inline-block; padding: 10px 12px; border: 1px solid #1473e6; "
    "border-radius: 6px; background: #eef5ff; color: #123b6d; font-weight: 600;"
)

SVG_DATA_URI = "data:image/svg+xml;utf8," + quote(
    """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 80'>
    <rect width='180' height='80' fill='#eef5ff'/>
    <circle cx='42' cy='40' r='24' fill='#1473e6'/>
    <rect x='78' y='24' width='84' height='12' rx='6' fill='#123b6d'/>
    <rect x='78' y='46' width='58' height='10' rx='5' fill='#5aa0f2'/>
    </svg>"""
)

# %% [markdown]
# ## Shared patterns
#
# The following small cell demonstrates the callback shapes used later in the notebook. Value widgets use traitlets observers; button-like widgets use `on_click`; layout widgets expose children by key.

# %%
text = sx.TextInput(value='Iris', description='Name')
status = al.TextWidget(f'initial value: {text.value!r}')
text.observe(lambda change: setattr(status, 'value', f"changed to: {change['new']!r}"), names='value')
button = sx.Button(description='Set Rose', icon='Edit')
button.on_click(lambda _button: setattr(text, 'value', 'Rose'))
layout = al.VBox({'field': text, 'button': button, 'status': status}, height=180, spacing=8)
layout

# %% [markdown]
# # Layout widgets

# %% [markdown]
# ## LayoutWidget
#
# LayoutWidget is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.TabPanel({'input': sx.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.TabPanel({'input': sx.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, width='520px', height=220)
status = al.TextWidget('Click Edit input to update the keyed child.')
edit = sx.Button(description='Edit input', icon='Edit')

def edit_input(_button, panel=panel, status=status):
    input_widget = panel.get_owner('input')
    input_widget.value = 'Edited through get_owner()'
    status.value = f"input value: {input_widget.value!r}"

edit.on_click(edit_input)
input_widget = panel.get_owner('input')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, width='540px', height=320, spacing=8, resizable=False)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.TabPanel({'input': sx.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove input', icon='Delete')
select = sx.Button(description='Select extra', icon='ChevronRight')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}; selected: {panel.selected_key!r}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra', select=True)
    update_status()

def remove_input(_button, panel=panel, update_status=update_status):
    if 'input' in panel:
        panel.remove_widget('input')
    update_status()

def select_extra(_button, panel=panel, update_status=update_status):
    if 'extra' in panel:
        panel.select_key('extra')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_input)
select.on_click(select_extra)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove, 'select': select}, height=64, spacing=8), 'status': status}, height=300, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.TabPanel({'input': sx.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## TabPanel
#
# TabPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.TabPanel({'first': sx.TextInput(value='First tab', description='First'), 'second': sx.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.TabPanel({'first': sx.TextInput(value='First tab', description='First'), 'second': sx.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, width='520px', height=220)
status = al.TextWidget('Click Edit first to update the keyed child.')
edit = sx.Button(description='Edit first', icon='Edit')

def edit_first(_button, panel=panel, status=status):
    first_widget = panel.get_owner('first')
    first_widget.value = 'Edited through get_owner()'
    status.value = f"first value: {first_widget.value!r}"

edit.on_click(edit_first)
first_widget = panel.get_owner('first')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, width='540px', height=320, spacing=8, resizable=False)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.TabPanel({'first': sx.TextInput(value='First tab', description='First'), 'second': sx.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove first', icon='Delete')
select = sx.Button(description='Select extra', icon='ChevronRight')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}; selected: {panel.selected_key!r}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra', select=True)
    update_status()

def remove_first(_button, panel=panel, update_status=update_status):
    if 'first' in panel:
        panel.remove_widget('first')
    update_status()

def select_extra(_button, panel=panel, update_status=update_status):
    if 'extra' in panel:
        panel.select_key('extra')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_first)
select.on_click(select_extra)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove, 'select': select}, height=64, spacing=8), 'status': status}, height=300, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.TabPanel({'first': sx.TextInput(value='First tab', description='First'), 'second': sx.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## BoxPanel
#
# BoxPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.BoxPanel({'left': sx.TextInput(value='Left', description='Left'), 'right': sx.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.BoxPanel({'left': sx.TextInput(value='Left', description='Left'), 'right': sx.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
status = al.TextWidget('Click Edit left to update the keyed child.')
edit = sx.Button(description='Edit left', icon='Edit')

def edit_left(_button, panel=panel, status=status):
    left_widget = panel.get_owner('left')
    left_widget.value = 'Edited through get_owner()'
    status.value = f"left value: {left_widget.value!r}"

edit.on_click(edit_left)
left_widget = panel.get_owner('left')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=240, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.BoxPanel({'left': sx.TextInput(value='Left', description='Left'), 'right': sx.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove left', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_left(_button, panel=panel, update_status=update_status):
    if 'left' in panel:
        panel.remove_widget('left')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_left)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=280, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.BoxPanel({'left': sx.TextInput(value='Left', description='Left'), 'right': sx.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], width='420px', height=180, resizable=False, child_min_width='160px', child_min_height='44px')
panel

# %% [markdown]
# ## HBox
#
# HBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.HBox({'name': sx.TextInput(value='Iris', description='Name'), 'apply': sx.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.HBox({'name': sx.TextInput(value='Iris', description='Name'), 'apply': sx.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
status = al.TextWidget('Click Edit name to update the keyed child.')
edit = sx.Button(description='Edit name', icon='Edit')

def edit_name(_button, panel=panel, status=status):
    name_widget = panel.get_owner('name')
    name_widget.value = 'Edited through get_owner()'
    status.value = f"name value: {name_widget.value!r}"

edit.on_click(edit_name)
name_widget = panel.get_owner('name')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=230, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.HBox({'name': sx.TextInput(value='Iris', description='Name'), 'apply': sx.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove name', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_name(_button, panel=panel, update_status=update_status):
    if 'name' in panel:
        panel.remove_widget('name')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_name)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.HBox({'name': sx.TextInput(value='Iris', description='Name'), 'apply': sx.Button(description='Apply')}, spacing=12, width='420px', height=180, resizable=False, child_min_width='160px', child_min_height='44px')
panel

# %% [markdown]
# ## VBox
#
# VBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.VBox({'name': sx.TextInput(value='Iris', description='Name'), 'notes': sx.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.VBox({'name': sx.TextInput(value='Iris', description='Name'), 'notes': sx.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
status = al.TextWidget('Click Edit name to update the keyed child.')
edit = sx.Button(description='Edit name', icon='Edit')

def edit_name(_button, panel=panel, status=status):
    name_widget = panel.get_owner('name')
    name_widget.value = 'Edited through get_owner()'
    status.value = f"name value: {name_widget.value!r}"

edit.on_click(edit_name)
name_widget = panel.get_owner('name')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=290, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.VBox({'name': sx.TextInput(value='Iris', description='Name'), 'notes': sx.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove name', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_name(_button, panel=panel, update_status=update_status):
    if 'name' in panel:
        panel.remove_widget('name')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_name)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=330, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.VBox({'name': sx.TextInput(value='Iris', description='Name'), 'notes': sx.TextArea(value='Notes', description='Notes')}, spacing=10, width='420px', height=180, resizable=False, child_min_width='160px', child_min_height='44px')
panel

# %% [markdown]
# ## ScrollBox
#
# ScrollBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.ScrollBox({'one': sx.TextInput(value='One', description='One'), 'two': sx.TextInput(value='Two', description='Two'), 'three': sx.TextInput(value='Three', description='Three'), 'four': sx.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.ScrollBox({'one': sx.TextInput(value='One', description='One'), 'two': sx.TextInput(value='Two', description='Two'), 'three': sx.TextInput(value='Three', description='Three'), 'four': sx.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
status = al.TextWidget('Click Edit one to update the keyed child.')
edit = sx.Button(description='Edit one', icon='Edit')

def edit_one(_button, panel=panel, status=status):
    one_widget = panel.get_owner('one')
    one_widget.value = 'Edited through get_owner()'
    status.value = f"one value: {one_widget.value!r}"

edit.on_click(edit_one)
one_widget = panel.get_owner('one')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=250, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.ScrollBox({'one': sx.TextInput(value='One', description='One'), 'two': sx.TextInput(value='Two', description='Two'), 'three': sx.TextInput(value='Three', description='Three'), 'four': sx.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove one', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_one(_button, panel=panel, update_status=update_status):
    if 'one' in panel:
        panel.remove_widget('one')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_one)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=290, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.ScrollBox({'one': sx.TextInput(value='One', description='One'), 'two': sx.TextInput(value='Two', description='Two'), 'three': sx.TextInput(value='Three', description='Three'), 'four': sx.TextInput(value='Four', description='Four')}, width='420px', height=180, resizable=False, child_min_width='160px', child_min_height='44px')
panel

# %% [markdown]
# ## SplitPanel
#
# SplitPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.SplitPanel({'left': sx.TextInput(value='Left pane', description='Left'), 'right': sx.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.SplitPanel({'left': sx.TextInput(value='Left pane', description='Left'), 'right': sx.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
status = al.TextWidget('Click Edit left to update the keyed child.')
edit = sx.Button(description='Edit left', icon='Edit')

def edit_left(_button, panel=panel, status=status):
    left_widget = panel.get_owner('left')
    left_widget.value = 'Edited through get_owner()'
    status.value = f"left value: {left_widget.value!r}"

edit.on_click(edit_left)
left_widget = panel.get_owner('left')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=280, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.SplitPanel({'left': sx.TextInput(value='Left pane', description='Left'), 'right': sx.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove left', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_left(_button, panel=panel, update_status=update_status):
    if 'left' in panel:
        panel.remove_widget('left')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_left)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=320, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.SplitPanel({'left': sx.TextInput(value='Left pane', description='Left'), 'right': sx.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## DockPanel
#
# DockPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': sx.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': sx.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
status = al.TextWidget('Click Edit details to update the keyed child.')
edit = sx.Button(description='Edit details', icon='Edit')

def edit_details(_button, panel=panel, status=status):
    details_widget = panel.get_owner('details')
    details_widget.value = 'Edited through get_owner()'
    status.value = f"details value: {details_widget.value!r}"

edit.on_click(edit_details)
details_widget = panel.get_owner('details')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=340, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': sx.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove table', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_table(_button, panel=panel, update_status=update_status):
    if 'table' in panel:
        panel.remove_widget('table')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_table)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=360, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': sx.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## AccordionPanel
#
# AccordionPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.AccordionPanel({'settings': sx.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.AccordionPanel({'settings': sx.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
status = al.TextWidget('Click Edit settings to update the keyed child.')
edit = sx.Button(description='Edit settings', icon='Edit')

def edit_settings(_button, panel=panel, status=status):
    settings_widget = panel.get_owner('settings')
    settings_widget.value = 'Edited through get_owner()'
    status.value = f"settings value: {settings_widget.value!r}"

edit.on_click(edit_settings)
settings_widget = panel.get_owner('settings')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=340, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.AccordionPanel({'settings': sx.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove settings', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_settings(_button, panel=panel, update_status=update_status):
    if 'settings' in panel:
        panel.remove_widget('settings')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_settings)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=360, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.AccordionPanel({'settings': sx.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## StackedPanel
#
# StackedPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.StackedPanel({'summary': sx.TextInput(value='Summary view', description='Summary'), 'details': sx.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.StackedPanel({'summary': sx.TextInput(value='Summary view', description='Summary'), 'details': sx.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
status = al.TextWidget('Click Edit summary to update the keyed child.')
edit = sx.Button(description='Edit summary', icon='Edit')

def edit_summary(_button, panel=panel, status=status):
    summary_widget = panel.get_owner('summary')
    summary_widget.value = 'Edited through get_owner()'
    status.value = f"summary value: {summary_widget.value!r}"

edit.on_click(edit_summary)
summary_widget = panel.get_owner('summary')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.StackedPanel({'summary': sx.TextInput(value='Summary view', description='Summary'), 'details': sx.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove summary', icon='Delete')
select = sx.Button(description='Select extra', icon='ChevronRight')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}; selected: {panel.selected_key!r}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra', select=True)
    update_status()

def remove_summary(_button, panel=panel, update_status=update_status):
    if 'summary' in panel:
        panel.remove_widget('summary')
    update_status()

def select_extra(_button, panel=panel, update_status=update_status):
    if 'extra' in panel:
        panel.select_key('extra')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_summary)
select.on_click(select_extra)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove, 'select': select}, height=64, spacing=8), 'status': status}, height=300, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.StackedPanel({'summary': sx.TextInput(value='Summary view', description='Summary'), 'details': sx.TextInput(value='Details', description='Details')}, selected_index=0, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## GridPanel
#
# GridPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.GridPanel({'a': sx.TextInput(value='A', description='A'), 'b': al.TextWidget('B'), 'c': sx.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.GridPanel({'a': sx.TextInput(value='A', description='A'), 'b': al.TextWidget('B'), 'c': sx.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
status = al.TextWidget('Click Edit A to update the keyed child.')
edit = sx.Button(description='Edit A', icon='Edit')

def edit_a(_button, panel=panel, status=status):
    a_widget = panel.get_owner('a')
    a_widget.value = 'Edited through get_owner()'
    status.value = f"a value: {a_widget.value!r}"

edit.on_click(edit_a)
a_widget = panel.get_owner('a')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=280, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.GridPanel({'a': sx.TextInput(value='A', description='A'), 'b': al.TextWidget('B'), 'c': sx.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove A', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_a(_button, panel=panel, update_status=update_status):
    if 'a' in panel:
        panel.remove_widget('a')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_a)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=320, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.GridPanel({'a': sx.TextInput(value='A', description='A'), 'b': al.TextWidget('B'), 'c': sx.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# ## ResponsivePanel
#
# ResponsivePanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.ResponsivePanel({'filters': sx.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
panel

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.ResponsivePanel({'filters': sx.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
status = al.TextWidget('Click Edit filters to update the keyed child.')
edit = sx.Button(description='Edit filters', icon='Edit')

def edit_filters(_button, panel=panel, status=status):
    filters_widget = panel.get_owner('filters')
    filters_widget.value = 'Edited through get_owner()'
    status.value = f"filters value: {filters_widget.value!r}"

edit.on_click(edit_filters)
filters_widget = panel.get_owner('filters')
al.VBox({'panel': panel, 'edit': edit, 'status': status}, height=270, spacing=8)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.ResponsivePanel({'filters': sx.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
status = al.TextWidget(f'children: {panel.child_keys}')
add = sx.Button(description='Add extra', icon='Add')
remove = sx.Button(description='Remove filters', icon='Delete')

def update_status(panel=panel, status=status):
    status.value = f'children: {panel.child_keys}'

def add_extra(_button, panel=panel, update_status=update_status):
    if 'extra' not in panel:
        panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
    update_status()

def remove_filters(_button, panel=panel, update_status=update_status):
    if 'filters' in panel:
        panel.remove_widget('filters')
    update_status()

add.on_click(add_extra)
remove.on_click(remove_filters)
al.VBox({'panel': panel, 'controls': al.HBox({'add': add, 'remove': remove}, height=64, spacing=8), 'status': status}, height=310, spacing=8)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.ResponsivePanel({'filters': sx.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, width='420px', height=180, resizable=False)
panel

# %% [markdown]
# # Action widgets

# %% [markdown]
# ## Toolbar
#
# Toolbar turns Lumino-style actions into Python callbacks keyed by action id.

# %% [markdown]
# ### Basic example

# %%
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}])
widget

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('Toolbar: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'value', f'Toolbar: {action_id}'),
    'add': lambda action_id: setattr(status, 'value', f'Toolbar: {action_id}'),
    'clear': lambda action_id: setattr(status, 'value', f'Toolbar: {action_id}'),
}
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}], callbacks=callbacks)
al.VBox({'actions': widget, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}])
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
container

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}])
widget.width = '420px'
widget.height = 'auto'
widget

# %% [markdown]
# ## MenuBar
#
# MenuBar turns Lumino-style actions into Python callbacks keyed by action id.

# %% [markdown]
# ### Basic example

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
widget

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('MenuBar: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'value', f'MenuBar: {action_id}'),
    'add': lambda action_id: setattr(status, 'value', f'MenuBar: {action_id}'),
    'clear': lambda action_id: setattr(status, 'value', f'MenuBar: {action_id}'),
}
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}], callbacks=callbacks)
al.VBox({'menus': widget, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
container

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
widget.width = '420px'
widget.height = 'auto'
widget

# %% [markdown]
# ## CommandPalette
#
# CommandPalette turns Lumino-style actions into Python callbacks keyed by action id.

# %% [markdown]
# ### Basic example

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
widget

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('CommandPalette: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'value', f'CommandPalette: {action_id}'),
    'add': lambda action_id: setattr(status, 'value', f'CommandPalette: {action_id}'),
    'clear': lambda action_id: setattr(status, 'value', f'CommandPalette: {action_id}'),
}
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], callbacks=callbacks, height=220)
al.VBox({'commands': widget, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
container

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
widget.width = '420px'
widget.height = 'auto'
widget

# %% [markdown]
# # Controls and display widgets

# %% [markdown]
# ## TextInput
#
# TextInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.TextInput(value='Iris', description='Name', placeholder='Enter a name')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.TextInput(value='Iris', description='Name', placeholder='Enter a name')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.TextInput(value='Iris', description='Name', placeholder='Enter a name')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.TextInput(value='Iris', description='Name', placeholder='Enter a name')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Text
#
# Text is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Text(value='Iris', description='Name', placeholder='Enter a name')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Text(value='Iris', description='Name', placeholder='Enter a name')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Text(value='Iris', description='Name', placeholder='Enter a name')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Text(value='Iris', description='Name', placeholder='Enter a name')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## TextArea
#
# TextArea is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.TextArea(value='Line one\nLine two', description='Notes', rows=4)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.TextArea(value='Line one\nLine two', description='Notes', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.TextArea(value='Line one\nLine two', description='Notes', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.TextArea(value='Line one\nLine two', description='Notes', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Textarea
#
# Textarea is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Textarea(value='Line one\nLine two', description='Notes', rows=4)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Textarea(value='Line one\nLine two', description='Notes', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Textarea(value='Line one\nLine two', description='Notes', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Textarea(value='Line one\nLine two', description='Notes', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## PasswordInput
#
# PasswordInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.PasswordInput(value='secret', description='Password', placeholder='Password')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.PasswordInput(value='secret', description='Password', placeholder='Password')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.PasswordInput(value='secret', description='Password', placeholder='Password')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.PasswordInput(value='secret', description='Password', placeholder='Password')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Password
#
# Password is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Password(value='secret', description='Password', placeholder='Password')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Password(value='secret', description='Password', placeholder='Password')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Password(value='secret', description='Password', placeholder='Password')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Password(value='secret', description='Password', placeholder='Password')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Combobox
#
# Combobox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## SearchInput
#
# SearchInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.SearchInput(value='orchid', description='Search', placeholder='Search')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.SearchInput(value='orchid', description='Search', placeholder='Search')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.SearchInput(value='orchid', description='Search', placeholder='Search')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.SearchInput(value='orchid', description='Search', placeholder='Search')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## TagsInput
#
# TagsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ColorsInput
#
# ColorsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatsInput
#
# FloatsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatsInput(value=[1.5, 2.25], description='Floats')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatsInput(value=[1.5, 2.25], description='Floats')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatsInput(value=[1.5, 2.25], description='Floats')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatsInput(value=[1.5, 2.25], description='Floats')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntsInput
#
# IntsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntsInput(value=[1, 2, 3], description='Integers')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntsInput(value=[1, 2, 3], description='Integers')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntsInput(value=[1, 2, 3], description='Integers')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntsInput(value=[1, 2, 3], description='Integers')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Dropdown
#
# Dropdown is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## RadioButtons
#
# RadioButtons is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ToggleButtons
#
# ToggleButtons is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ListBox
#
# ListBox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Select
#
# Select is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## MultiSelect
#
# MultiSelect is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## SelectMultiple
#
# SelectMultiple is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## SelectionSlider
#
# SelectionSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## SelectionRangeSlider
#
# SelectionRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Button
#
# Button is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
status = al.TextWidget('Button: waiting')

def on_click(clicked_widget):
    status.value = f'Button: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Checkbox
#
# Checkbox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Checkbox(value=True, description='Enabled')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Checkbox(value=True, description='Enabled')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Checkbox(value=True, description='Enabled')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Checkbox(value=True, description='Enabled')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ToggleButton
#
# ToggleButton is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
status = al.TextWidget('ToggleButton: waiting')

def on_click(clicked_widget):
    status.value = f'ToggleButton: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Switch
#
# Switch is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Switch(value=True, description='Active')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Switch(value=True, description='Active')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Switch(value=True, description='Active')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Switch(value=True, description='Active')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Valid
#
# Valid is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Valid(value=True, description='Status', readout='Valid')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Valid(value=True, description='Status', readout='Valid')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Valid(value=True, description='Status', readout='Valid')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Valid(value=True, description='Status', readout='Valid')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## StatusLight
#
# StatusLight is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.StatusLight(value=True, description='Online', variant='positive')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.StatusLight(value=True, description='Online', variant='positive')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.StatusLight(value=True, description='Online', variant='positive')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.StatusLight(value=True, description='Online', variant='positive')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntSlider
#
# IntSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntSlider(value=25, min=0, max=100, step=5, description='Count')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntSlider(value=25, min=0, max=100, step=5, description='Count')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntSlider(value=25, min=0, max=100, step=5, description='Count')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntSlider(value=25, min=0, max=100, step=5, description='Count')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntegerSlider
#
# IntegerSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntRangeSlider
#
# IntRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntegerRangeSlider
#
# IntegerRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntText
#
# IntText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntText(value=10, min=0, max=100, description='Count')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntText(value=10, min=0, max=100, description='Count')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntText(value=10, min=0, max=100, description='Count')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntText(value=10, min=0, max=100, description='Count')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntegerInput
#
# IntegerInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntegerInput(value=10, min=0, max=100, description='Integer')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntegerInput(value=10, min=0, max=100, description='Integer')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntegerInput(value=10, min=0, max=100, description='Integer')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntegerInput(value=10, min=0, max=100, description='Integer')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## BoundedIntText
#
# BoundedIntText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.BoundedIntText(value=10, min=0, max=100, description='Bounded')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.BoundedIntText(value=10, min=0, max=100, description='Bounded')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.BoundedIntText(value=10, min=0, max=100, description='Bounded')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.BoundedIntText(value=10, min=0, max=100, description='Bounded')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatSlider
#
# FloatSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatRangeSlider
#
# FloatRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatLogSlider
#
# FloatLogSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatText
#
# FloatText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## BoundedFloatText
#
# BoundedFloatText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## IntProgress
#
# IntProgress is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.IntProgress(value=65, min=0, max=100, description='Progress')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.IntProgress(value=65, min=0, max=100, description='Progress')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.IntProgress(value=65, min=0, max=100, description='Progress')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.IntProgress(value=65, min=0, max=100, description='Progress')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## FloatProgress
#
# FloatProgress is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Meter
#
# Meter is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Meter(value=72, description='Quality', variant='positive', readout=True)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Meter(value=72, description='Quality', variant='positive', readout=True)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Meter(value=72, description='Quality', variant='positive', readout=True)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Meter(value=72, description='Quality', variant='positive', readout=True)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ProgressCircle
#
# ProgressCircle is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ProgressCircle(value=45, label='Loading', spectrum_size='l')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ProgressCircle(value=45, label='Loading', spectrum_size='l')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ProgressCircle(value=45, label='Loading', spectrum_size='l')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ProgressCircle(value=45, label='Loading', spectrum_size='l')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Play
#
# Play is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Play(value=0, min=0, max=10, step=1, interval=250)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Play(value=0, min=0, max=10, step=1, interval=250)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Play(value=0, min=0, max=10, step=1, interval=250)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Play(value=0, min=0, max=10, step=1, interval=250)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## DatePicker
#
# DatePicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## TimePicker
#
# TimePicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## DatetimePicker
#
# DatetimePicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ColorPicker
#
# ColorPicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ColorPicker(value='#1473e6', description='Accent')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ColorPicker(value='#1473e6', description='Accent')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ColorPicker(value='#1473e6', description='Accent')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ColorPicker(value='#1473e6', description='Accent')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## ColorHandle
#
# ColorHandle is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ColorHandle(value='#1473e6')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ColorHandle(value='#1473e6')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ColorHandle(value='#1473e6')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ColorHandle(value='#1473e6')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## ColorLoupe
#
# ColorLoupe is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ColorLoupe(value='#1473e6', open=True)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.ColorLoupe(value='#1473e6', open=True)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ColorLoupe(value='#1473e6', open=True)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ColorLoupe(value='#1473e6', open=True)
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## OpacityCheckerboard
#
# OpacityCheckerboard is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.OpacityCheckerboard(width=160, height=48)
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.OpacityCheckerboard(width=160, height=48)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.OpacityCheckerboard(width=160, height=48)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.OpacityCheckerboard(width=160, height=48)
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## FileUpload
#
# FileUpload is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
status = al.TextWidget('FileUpload: waiting')

def on_click(clicked_widget):
    status.value = f'FileUpload: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Image
#
# Image is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Audio
#
# Audio is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Audio(value='', format='mp3')
al.VBox({'audio': widget, 'label': al.TextWidget('Audio control placeholder')}, height=110, spacing=8)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Audio(value='', format='mp3')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Audio(value='', format='mp3')
container = al.VBox({'control': widget, 'label': al.TextWidget('Audio control placeholder')}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Audio(value='', format='mp3')
wrapper = al.VBox({'control': widget, 'label': al.TextWidget('Audio control placeholder')}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Video
#
# Video is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Video(value='', format='mp4', width='260px', height='120px')
al.VBox({'video': widget, 'label': al.TextWidget('Video control placeholder')}, height=180, spacing=8)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Video(value='', format='mp4', width='260px', height='120px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Video(value='', format='mp4', width='260px', height='120px')
container = al.VBox({'control': widget, 'label': al.TextWidget('Video control placeholder')}, height=180, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Video(value='', format='mp4', width='260px', height='120px')
wrapper = al.VBox({'control': widget, 'label': al.TextWidget('Video control placeholder')}, width='380px', height=180, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Output
#
# Output is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Output(value='Output text')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Output(value='Output text')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Output(value='Output text')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Output(value='Output text')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## HTML
#
# HTML is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.HTML(value='<strong>Rich HTML</strong>', description='HTML')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.HTML(value='<strong>Rich HTML</strong>', description='HTML')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.HTML(value='<strong>Rich HTML</strong>', description='HTML')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.HTML(value='<strong>Rich HTML</strong>', description='HTML')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## HTMLMath
#
# HTMLMath is an HTML compatibility alias. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.HTMLMath(value='<strong>Rich HTML</strong>', description='HTML')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.HTMLMath(value='<strong>Rich HTML</strong>', description='HTML')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.HTMLMath(value='<strong>Rich HTML</strong>', description='HTML')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.HTMLMath(value='<strong>Rich HTML</strong>', description='HTML')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Label
#
# Label is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Label(value='Plain label', description='Label')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Label(value='Plain label', description='Label')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Label(value='Plain label', description='Label')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Label(value='Plain label', description='Label')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## TextWidget
#
# TextWidget is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TextWidget('Plain anylumino text')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TextWidget('Plain anylumino text')
status = al.TextWidget(f"initial value: {widget.value!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TextWidget('Plain anylumino text')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TextWidget('Plain anylumino text')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Badge
#
# Badge is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Link
#
# Link is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Link('https://example.com', description='Example link', variant='primary')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Link('https://example.com', description='Example link', variant='primary')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Link('https://example.com', description='Example link', variant='primary')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Link('https://example.com', description='Example link', variant='primary')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Divider
#
# Divider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Divider(orientation='horizontal', spectrum_size='l')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Divider(orientation='horizontal', spectrum_size='l')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Divider(orientation='horizontal', spectrum_size='l')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Divider(orientation='horizontal', spectrum_size='l')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
wrapper

# %% [markdown]
# ## Icon
#
# Icon is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Icon('AddContent', icon_size='l', label='Add')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Icon('AddContent', icon_size='l', label='Add')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Icon('AddContent', icon_size='l', label='Add')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Icon('AddContent', icon_size='l', label='Add')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## UIIcon
#
# UIIcon is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.UIIcon('checkmark100', label='Check')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.UIIcon('checkmark100', label='Check')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.UIIcon('checkmark100', label='Check')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.UIIcon('checkmark100', label='Check')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## HelpText
#
# HelpText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.HelpText('Use this field for a short label.', variant='neutral')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.HelpText('Use this field for a short label.', variant='neutral')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.HelpText('Use this field for a short label.', variant='neutral')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.HelpText('Use this field for a short label.', variant='neutral')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Underlay
#
# Underlay is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.Underlay(open=False)
al.VBox({'underlay': widget, 'label': al.TextWidget('Underlay widget placeholder')}, height=100, spacing=8)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.Underlay(open=False)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.Underlay(open=False)
container = al.VBox({'control': widget, 'label': al.TextWidget('Underlay widget placeholder')}, height=120, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.Underlay(open=False)
wrapper = al.VBox({'component': widget, 'label': al.TextWidget('Underlay widget placeholder')}, width='320px', height=120, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## SpectrumElement
#
# SpectrumElement is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = sx.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'style': ACCENT_STYLE})
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = sx.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'style': ACCENT_STYLE})
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.value = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
al.VBox({'widget': widget, 'status': status}, height=150, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'style': ACCENT_STYLE})
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.SpectrumElement(
    'div',
    text='Styled with a CSS class passed through attributes',
    attributes={'style': ACCENT_STYLE},
)
widget

# %% [markdown]
# # Spectrum action components

# %% [markdown]
# ## ClearButton
#
# ClearButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = sx.ClearButton(label='Clear')
widget

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.ClearButton(label='Clear')
status = al.TextWidget('ClearButton: waiting')

def on_click(clicked_widget):
    status.value = f'ClearButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
al.VBox({'button': widget, 'status': status}, height=140, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.ClearButton(label='Clear')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.ClearButton(label='Clear')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
wrapper

# %% [markdown]
# ## CloseButton
#
# CloseButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = sx.CloseButton(label='Close')
widget

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.CloseButton(label='Close')
status = al.TextWidget('CloseButton: waiting')

def on_click(clicked_widget):
    status.value = f'CloseButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
al.VBox({'button': widget, 'status': status}, height=140, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.CloseButton(label='Close')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.CloseButton(label='Close')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
wrapper

# %% [markdown]
# ## InfieldButton
#
# InfieldButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = sx.InfieldButton(label='Search', icon='Search')
widget

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.InfieldButton(label='Search', icon='Search')
status = al.TextWidget('InfieldButton: waiting')

def on_click(clicked_widget):
    status.value = f'InfieldButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
al.VBox({'button': widget, 'status': status}, height=140, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.InfieldButton(label='Search', icon='Search')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.InfieldButton(label='Search', icon='Search')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
wrapper

# %% [markdown]
# ## PickerButton
#
# PickerButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = sx.PickerButton(label='Pick', icon='ChevronDown')
widget

# %% [markdown]
# ### Pass a callback

# %%
widget = sx.PickerButton(label='Pick', icon='ChevronDown')
status = al.TextWidget('PickerButton: waiting')

def on_click(clicked_widget):
    status.value = f'PickerButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
al.VBox({'button': widget, 'status': status}, height=140, spacing=8)

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = sx.PickerButton(label='Pick', icon='ChevronDown')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
container

# %% [markdown]
# ### Customize appearance

# %%
widget = sx.PickerButton(label='Pick', icon='ChevronDown')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
wrapper

# %% [markdown]
# # Composable Spectrum surfaces

# %% [markdown]
# ## FieldGroup
#
# FieldGroup can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.FieldGroup({'name': sx.TextInput(value='Iris', description='Name'), 'enabled': sx.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
component

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.FieldGroup({'name': sx.TextInput(value='Iris', description='Name'), 'enabled': sx.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
status = al.TextWidget('Click Edit name to update the keyed child.')
edit = sx.Button(description='Edit name', icon='Edit')

def edit_name(_button, component=component, status=status):
    name_widget = component['name']
    name_widget.value = 'Edited through component[key]'
    status.value = f"name value: {name_widget.value!r}"

edit.on_click(edit_name)
name_widget = component['name']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.FieldGroup({'name': sx.TextInput(value='Iris', description='Name'), 'enabled': sx.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.FieldGroup({'name': sx.TextInput(value='Iris', description='Name'), 'enabled': sx.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Popover
#
# Popover can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
component

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.Popover({'content': sx.TextInput(value='Popover child content', description='Content')}, open=True, placement='bottom')
status = al.TextWidget('Click Edit content to update the keyed child.')
edit = sx.Button(description='Edit content', icon='Edit')

def edit_content(_button, component=component, status=status):
    content_widget = component['content']
    content_widget.value = 'Edited through component[key]'
    status.value = f"content value: {content_widget.value!r}"

edit.on_click(edit_content)
content_widget = component['content']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Tooltip
#
# Tooltip can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.Tooltip('Tooltip content', {'trigger': sx.Button(description='Tooltip trigger')}, open=True, placement='top')
component

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.Tooltip('Tooltip content', {'trigger': sx.TextInput(value='Tooltip trigger', description='Trigger')}, open=True, placement='top')
status = al.TextWidget('Click Edit trigger to update the keyed child.')
edit = sx.Button(description='Edit trigger', icon='Edit')

def edit_trigger(_button, component=component, status=status):
    trigger_widget = component['trigger']
    trigger_widget.value = 'Edited through component[key]'
    status.value = f"trigger value: {trigger_widget.value!r}"

edit.on_click(edit_trigger)
trigger_widget = component['trigger']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.Tooltip('Tooltip content', {'trigger': sx.Button(description='Tooltip trigger')}, open=True, placement='top')
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.Tooltip('Tooltip content', {'trigger': sx.Button(description='Tooltip trigger')}, open=True, placement='top')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Tray
#
# Tray can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.Tray({'content': al.TextWidget('Tray content')}, open=False)
al.VBox({'surface': component, 'label': al.TextWidget('Tray surface; click Toggle in the callback example to open it')}, height=150, spacing=8)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.Tray({'content': sx.TextInput(value='Tray content', description='Content')}, open=True)
status = al.TextWidget('Click Edit content to update the keyed child.')
edit = sx.Button(description='Edit content', icon='Edit')

def edit_content(_button, component=component, status=status):
    content_widget = component['content']
    content_widget.value = 'Edited through component[key]'
    status.value = f"content value: {content_widget.value!r}"

edit.on_click(edit_content)
content_widget = component['content']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.Tray({'content': al.TextWidget('Tray content')}, open=False)
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.Tray({'content': al.TextWidget('Tray content')}, open=False)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Overlay
#
# Overlay can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
component

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.Overlay({'content': sx.TextInput(value='Overlay content', description='Content')}, open=True, placement='bottom')
status = al.TextWidget('Click Edit content to update the keyed child.')
edit = sx.Button(description='Edit content', icon='Edit')

def edit_content(_button, component=component, status=status):
    content_widget = component['content']
    content_widget.value = 'Edited through component[key]'
    status.value = f"content value: {content_widget.value!r}"

edit.on_click(edit_content)
content_widget = component['content']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=180, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## DialogBox
#
# DialogBox can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.DialogBox({'body': al.VBox({'field': sx.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
al.VBox({'surface': component, 'label': al.TextWidget('DialogBox surface; click Toggle in the callback example to open it')}, height=150, spacing=8)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.DialogBox({'body': al.VBox({'field': sx.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=True, width=420)
status = al.TextWidget('Click Edit field to update the nested keyed child.')
edit = sx.Button(description='Edit field', icon='Edit')
body = component['body']

def edit_field(_button, body=body, status=status):
    field_widget = body.get_owner('field')
    field_widget.value = 'Edited through component[key]'
    status.value = f"field value: {field_widget.value!r}"

edit.on_click(edit_field)
field_widget = body.get_owner('field')
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.DialogBox({'body': al.VBox({'field': sx.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.DialogBox({'body': al.VBox({'field': sx.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# ## Modal
#
# Modal can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = sx.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
al.VBox({'surface': component, 'label': al.TextWidget('Modal surface; click Toggle in the callback example to open it')}, height=150, spacing=8)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = sx.Modal({'body': sx.TextInput(value='Modal body child', description='Body')}, title='Modal', open=True, width=360)
status = al.TextWidget('Click Edit body to update the keyed child.')
edit = sx.Button(description='Edit body', icon='Edit')

def edit_body(_button, component=component, status=status):
    body_widget = component['body']
    body_widget.value = 'Edited through component[key]'
    status.value = f"body value: {body_widget.value!r}"

edit.on_click(edit_body)
body_widget = component['body']
al.VBox({'surface': component, 'edit': edit, 'status': status}, height=220, spacing=8)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = sx.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
status = al.TextWidget(f'open={component.is_open!r}')
button = sx.Button(description='Toggle')

def toggle(_button, component=component, status=status):
    component.toggle()
    status.value = f'open={component.is_open!r}'

button.on_click(toggle)
al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8)

# %% [markdown]
# ### Customize appearance

# %%
component = sx.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
wrapper

# %% [markdown]
# # Notebook notes
#
# - Read value-bearing widgets with `widget.value`; `TextWidget` uses `widget.value`.
# - React to value changes with `widget.observe(callback, names="value")`.
# - Button-like widgets use `widget.on_click(callback)`.
# - Layout widgets expose keyed children with `child_keys`, `get_widget()`, `get_owner()`, and `widget[key]`.
# - Component surfaces such as dialogs, trays, overlays, and popovers expose keyed children plus `show()`, `hide()`, and `toggle()` when open state is meaningful.
# - Appearance customization is usually done through constructor arguments, wrapper layout sizing, Spectrum options such as `variant`/`icon`/`spectrum_size`, and `SpectrumElement(..., attributes={...})` for direct CSS class hooks.
