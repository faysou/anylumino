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

from IPython.display import HTML, display

import anylumino as al


display(HTML(
    """
    <style>
      .cookbook-accent-box {
        display: inline-block;
        padding: 10px 12px;
        border: 1px solid #1473e6;
        border-radius: 6px;
        background: #eef5ff;
        color: #123b6d;
        font-weight: 600;
      }
    </style>
    """
))

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
text = al.TextInput(value='Iris', description='Name')
status = al.TextWidget(f'initial value: {text.value!r}')
text.observe(lambda change: setattr(status, 'text', f"changed to: {change['new']!r}"), names='value')
button = al.Button(description='Set Rose', icon='Edit')
button.on_click(lambda _button: setattr(text, 'value', 'Rose'))
layout = al.VBox({'field': text, 'button': button, 'status': status}, height=180, spacing=8)
display(layout)

# %% [markdown]
# # Layout widgets

# %% [markdown]
# ## LayoutWidget
#
# LayoutWidget is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.TabPanel({'input': al.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.TabPanel({'input': al.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
panel

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.TabPanel({'input': al.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
panel.select_key('extra')
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.TabPanel({'input': al.TextInput(value='Iris', description='Input'), 'status': al.TextWidget('Status child')}, titles={'input': 'Input', 'status': 'Status'}, height=180)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## TabPanel
#
# TabPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.TabPanel({'first': al.TextWidget('First tab'), 'second': al.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.TabPanel({'first': al.TextWidget('First tab'), 'second': al.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.TabPanel({'first': al.TextWidget('First tab'), 'second': al.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
panel.select_key('extra')
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.TabPanel({'first': al.TextWidget('First tab'), 'second': al.TextInput(value='Second', description='Value')}, titles={'first': 'First', 'second': 'Second'}, selected_index=0, height=180)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## BoxPanel
#
# BoxPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.BoxPanel({'left': al.TextInput(value='Left', description='Left'), 'right': al.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.BoxPanel({'left': al.TextInput(value='Left', description='Left'), 'right': al.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.BoxPanel({'left': al.TextInput(value='Left', description='Left'), 'right': al.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.BoxPanel({'left': al.TextInput(value='Left', description='Left'), 'right': al.Button(description='Right')}, direction='left-to-right', spacing=12, stretches=[2, 1], height=150)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## HBox
#
# HBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.HBox({'name': al.TextInput(value='Iris', description='Name'), 'apply': al.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.HBox({'name': al.TextInput(value='Iris', description='Name'), 'apply': al.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.HBox({'name': al.TextInput(value='Iris', description='Name'), 'apply': al.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.HBox({'name': al.TextInput(value='Iris', description='Name'), 'apply': al.Button(description='Apply')}, spacing=12, child_min_width=180, height=130)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## VBox
#
# VBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.VBox({'name': al.TextInput(value='Iris', description='Name'), 'notes': al.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.VBox({'name': al.TextInput(value='Iris', description='Name'), 'notes': al.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.VBox({'name': al.TextInput(value='Iris', description='Name'), 'notes': al.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.VBox({'name': al.TextInput(value='Iris', description='Name'), 'notes': al.TextArea(value='Notes', description='Notes')}, spacing=10, height=190)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## ScrollBox
#
# ScrollBox is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.ScrollBox({'one': al.TextInput(value='One', description='One'), 'two': al.TextInput(value='Two', description='Two'), 'three': al.TextInput(value='Three', description='Three'), 'four': al.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.ScrollBox({'one': al.TextInput(value='One', description='One'), 'two': al.TextInput(value='Two', description='Two'), 'three': al.TextInput(value='Three', description='Three'), 'four': al.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.ScrollBox({'one': al.TextInput(value='One', description='One'), 'two': al.TextInput(value='Two', description='Two'), 'three': al.TextInput(value='Three', description='Three'), 'four': al.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.ScrollBox({'one': al.TextInput(value='One', description='One'), 'two': al.TextInput(value='Two', description='Two'), 'three': al.TextInput(value='Three', description='Three'), 'four': al.TextInput(value='Four', description='Four')}, height=150, child_min_height=54)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## SplitPanel
#
# SplitPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.SplitPanel({'left': al.TextWidget('Left pane'), 'right': al.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.SplitPanel({'left': al.TextWidget('Left pane'), 'right': al.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.SplitPanel({'left': al.TextWidget('Left pane'), 'right': al.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.SplitPanel({'left': al.TextWidget('Left pane'), 'right': al.TextInput(value='Right pane', description='Right')}, orientation='horizontal', sizes=[0.35, 0.65], height=180)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## DockPanel
#
# DockPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': al.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': al.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': al.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.DockPanel({'table': al.TextWidget('Table dock'), 'details': al.TextArea(value='Details', description='Details')}, titles={'table': 'Table', 'details': 'Details'}, mode='split-right', height=220)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## AccordionPanel
#
# AccordionPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.AccordionPanel({'settings': al.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.AccordionPanel({'settings': al.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.AccordionPanel({'settings': al.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.AccordionPanel({'settings': al.TextInput(value='Iris', description='Name'), 'details': al.TextWidget('Details panel')}, titles={'settings': 'Settings', 'details': 'Details'}, height=220)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## StackedPanel
#
# StackedPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.StackedPanel({'summary': al.TextWidget('Summary view'), 'details': al.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.StackedPanel({'summary': al.TextWidget('Summary view'), 'details': al.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.StackedPanel({'summary': al.TextWidget('Summary view'), 'details': al.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
panel.select_key('extra')
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.StackedPanel({'summary': al.TextWidget('Summary view'), 'details': al.TextInput(value='Details', description='Details')}, selected_index=0, height=160)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## GridPanel
#
# GridPanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.GridPanel({'a': al.TextWidget('A'), 'b': al.TextWidget('B'), 'c': al.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.GridPanel({'a': al.TextWidget('A'), 'b': al.TextWidget('B'), 'c': al.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.GridPanel({'a': al.TextWidget('A'), 'b': al.TextWidget('B'), 'c': al.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.GridPanel({'a': al.TextWidget('A'), 'b': al.TextWidget('B'), 'c': al.Button(description='Action')}, columns='1fr 1fr', rows='80px 80px', gap=8, height=180)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

# %% [markdown]
# ## ResponsivePanel
#
# ResponsivePanel is shown as a Lumino layout example. Mapping keys become stable child ids.

# %% [markdown]
# ### Basic example

# %%
panel = al.ResponsivePanel({'filters': al.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
display(panel)

# %% [markdown]
# ### Access child widgets by key

# %%
panel = al.ResponsivePanel({'filters': al.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
first_key = panel.child_keys[0]
first_owner = panel.get_owner(first_key)
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through get_owner()'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through get_owner()'
display(panel)

# %% [markdown]
# ### Add, remove, or select a child

# %%
panel = al.ResponsivePanel({'filters': al.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
panel.add('extra', al.TextWidget('Added after construction'), title='Extra')
removed = panel.remove_widget(panel.child_keys[0])
# This layout has no active selection API; add/remove still works.
display(panel)

# %% [markdown]
# ### Customize size and layout behavior

# %%
panel = al.ResponsivePanel({'filters': al.TextInput(value='Filter', description='Filter'), 'content': al.TextWidget('Responsive content')}, breakpoint=640, wide_direction='left-to-right', narrow_direction='top-to-bottom', spacing=10, height=170)
panel.width = '420px'
panel.height = '180px'
panel.resizable = False
panel.child_min_width = '160px'
panel.child_min_height = '44px'
display(panel)

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
display(widget)

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('Toolbar: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'text', f'Toolbar: {action_id}'),
    'add': lambda action_id: setattr(status, 'text', f'Toolbar: {action_id}'),
    'clear': lambda action_id: setattr(status, 'text', f'Toolbar: {action_id}'),
}
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}], callbacks=callbacks)
display(al.VBox({'actions': widget, 'status': status}, height=180, spacing=8))

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}])
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
display(container)

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.Toolbar([{'id': 'refresh', 'label': 'Refresh', 'icon': 'RotateRight'}, {'id': 'add', 'label': 'Add', 'icon': 'AddContent'}, {'id': 'clear', 'label': 'Clear', 'icon': 'Close'}])
widget.width = '420px'
widget.height = 'auto'
display(widget)

# %% [markdown]
# ## MenuBar
#
# MenuBar turns Lumino-style actions into Python callbacks keyed by action id.

# %% [markdown]
# ### Basic example

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
display(widget)

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('MenuBar: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'text', f'MenuBar: {action_id}'),
    'add': lambda action_id: setattr(status, 'text', f'MenuBar: {action_id}'),
    'clear': lambda action_id: setattr(status, 'text', f'MenuBar: {action_id}'),
}
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}], callbacks=callbacks)
display(al.VBox({'menus': widget, 'status': status}, height=180, spacing=8))

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
display(container)

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.MenuBar([{'id': 'file', 'label': 'File', 'items': [{'id': 'refresh', 'label': 'Refresh'}, {'id': 'clear', 'label': 'Clear'}]}, {'id': 'edit', 'label': 'Edit', 'items': [{'id': 'add', 'label': 'Add'}]}])
widget.width = '420px'
widget.height = 'auto'
display(widget)

# %% [markdown]
# ## CommandPalette
#
# CommandPalette turns Lumino-style actions into Python callbacks keyed by action id.

# %% [markdown]
# ### Basic example

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
display(widget)

# %% [markdown]
# ### Pass callbacks by action id

# %%
status = al.TextWidget('CommandPalette: no action yet')
callbacks = {
    'refresh': lambda action_id: setattr(status, 'text', f'CommandPalette: {action_id}'),
    'add': lambda action_id: setattr(status, 'text', f'CommandPalette: {action_id}'),
    'clear': lambda action_id: setattr(status, 'text', f'CommandPalette: {action_id}'),
}
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], callbacks=callbacks, height=220)
display(al.VBox({'commands': widget, 'status': status}, height=180, spacing=8))

# %% [markdown]
# ### Use as a child in a layout

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
container = al.VBox({'commands': widget, 'content': al.TextWidget('Action output area')}, height=180, spacing=8)
display(container)

# %% [markdown]
# ### Customize labels, icons, and size

# %%
widget = al.CommandPalette([{'id': 'refresh', 'label': 'Refresh', 'category': 'Data'}, {'id': 'add', 'label': 'Add item', 'category': 'Data'}, {'id': 'clear', 'label': 'Clear', 'category': 'View'}], height=220)
widget.width = '420px'
widget.height = 'auto'
display(widget)

# %% [markdown]
# # Controls and display widgets

# %% [markdown]
# ## TextInput
#
# TextInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TextInput(value='Iris', description='Name', placeholder='Enter a name')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TextInput(value='Iris', description='Name', placeholder='Enter a name')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TextInput(value='Iris', description='Name', placeholder='Enter a name')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TextInput(value='Iris', description='Name', placeholder='Enter a name')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Text
#
# Text is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Text(value='Iris', description='Name', placeholder='Enter a name')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Text(value='Iris', description='Name', placeholder='Enter a name')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Text(value='Iris', description='Name', placeholder='Enter a name')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Text(value='Iris', description='Name', placeholder='Enter a name')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## TextArea
#
# TextArea is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TextArea(value='Line one\nLine two', description='Notes', rows=4)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TextArea(value='Line one\nLine two', description='Notes', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TextArea(value='Line one\nLine two', description='Notes', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TextArea(value='Line one\nLine two', description='Notes', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Textarea
#
# Textarea is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Textarea(value='Line one\nLine two', description='Notes', rows=4)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Textarea(value='Line one\nLine two', description='Notes', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Textarea(value='Line one\nLine two', description='Notes', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Textarea(value='Line one\nLine two', description='Notes', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## PasswordInput
#
# PasswordInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.PasswordInput(value='secret', description='Password', placeholder='Password')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.PasswordInput(value='secret', description='Password', placeholder='Password')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.PasswordInput(value='secret', description='Password', placeholder='Password')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.PasswordInput(value='secret', description='Password', placeholder='Password')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Password
#
# Password is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Password(value='secret', description='Password', placeholder='Password')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Password(value='secret', description='Password', placeholder='Password')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Password(value='secret', description='Password', placeholder='Password')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Password(value='secret', description='Password', placeholder='Password')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Combobox
#
# Combobox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Combobox(options=['Iris', 'Orchid', 'Rose'], value='Iris', description='Flower')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## SearchInput
#
# SearchInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.SearchInput(value='orchid', description='Search', placeholder='Search')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.SearchInput(value='orchid', description='Search', placeholder='Search')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.SearchInput(value='orchid', description='Search', placeholder='Search')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.SearchInput(value='orchid', description='Search', placeholder='Search')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## TagsInput
#
# TagsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TagsInput(value=['alpha', 'beta'], allowed_tags=['alpha', 'beta', 'gamma'], description='Tags')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ColorsInput
#
# ColorsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ColorsInput(value=['#1473e6', '#d31510'], description='Colors')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatsInput
#
# FloatsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatsInput(value=[1.5, 2.25], description='Floats')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatsInput(value=[1.5, 2.25], description='Floats')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatsInput(value=[1.5, 2.25], description='Floats')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatsInput(value=[1.5, 2.25], description='Floats')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntsInput
#
# IntsInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntsInput(value=[1, 2, 3], description='Integers')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntsInput(value=[1, 2, 3], description='Integers')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntsInput(value=[1, 2, 3], description='Integers')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntsInput(value=[1, 2, 3], description='Integers')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Dropdown
#
# Dropdown is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Dropdown(options=['Small', 'Medium', 'Large'], value='Medium', description='Size')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## RadioButtons
#
# RadioButtons is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.RadioButtons(options=['Daily', 'Weekly', 'Monthly'], value='Weekly', description='Cadence')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ToggleButtons
#
# ToggleButtons is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ToggleButtons(options=['Table', 'Chart', 'Text'], value='Chart', description='View', icons={'Table': 'Table', 'Chart': 'GraphBarVertical', 'Text': 'Text'})
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ListBox
#
# ListBox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ListBox(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Select
#
# Select is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Select(options=['North', 'South', 'East', 'West'], value='North', description='Region', rows=4)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## MultiSelect
#
# MultiSelect is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.MultiSelect(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## SelectMultiple
#
# SelectMultiple is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.SelectMultiple(options=['A', 'B', 'C'], value=['A', 'C'], description='Letters', rows=3)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## SelectionSlider
#
# SelectionSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.SelectionSlider(options=['Low', 'Medium', 'High'], value='Medium', description='Level')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## SelectionRangeSlider
#
# SelectionRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.SelectionRangeSlider(options=['A', 'B', 'C', 'D'], value=['B', 'D'], description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Button
#
# Button is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Pass a callback

# %%
widget = al.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
status = al.TextWidget('Button: waiting')

def on_click(clicked_widget):
    status.text = f'Button: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Button(description='Apply', icon='CheckmarkCircle', variant='accent', tooltip='Run')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Checkbox
#
# Checkbox is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Checkbox(value=True, description='Enabled')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Checkbox(value=True, description='Enabled')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Checkbox(value=True, description='Enabled')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Checkbox(value=True, description='Enabled')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ToggleButton
#
# ToggleButton is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Pass a callback

# %%
widget = al.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
status = al.TextWidget('ToggleButton: waiting')

def on_click(clicked_widget):
    status.text = f'ToggleButton: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ToggleButton(value=False, description='Pin', icon='Star', variant='secondary')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Switch
#
# Switch is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Switch(value=True, description='Active')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Switch(value=True, description='Active')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Switch(value=True, description='Active')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Switch(value=True, description='Active')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Valid
#
# Valid is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Valid(value=True, description='Status', readout='Valid')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Valid(value=True, description='Status', readout='Valid')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Valid(value=True, description='Status', readout='Valid')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Valid(value=True, description='Status', readout='Valid')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## StatusLight
#
# StatusLight is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.StatusLight(value=True, description='Online', variant='positive')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.StatusLight(value=True, description='Online', variant='positive')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.StatusLight(value=True, description='Online', variant='positive')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.StatusLight(value=True, description='Online', variant='positive')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntSlider
#
# IntSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntSlider(value=25, min=0, max=100, step=5, description='Count')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntSlider(value=25, min=0, max=100, step=5, description='Count')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntSlider(value=25, min=0, max=100, step=5, description='Count')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntSlider(value=25, min=0, max=100, step=5, description='Count')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntegerSlider
#
# IntegerSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntegerSlider(value=30, min=0, max=100, step=10, description='Integer')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntRangeSlider
#
# IntRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntRangeSlider(value=[20, 80], min=0, max=100, step=5, description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntegerRangeSlider
#
# IntegerRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntegerRangeSlider(value=[10, 90], min=0, max=100, step=5, description='Integer range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntText
#
# IntText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntText(value=10, min=0, max=100, description='Count')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntText(value=10, min=0, max=100, description='Count')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntText(value=10, min=0, max=100, description='Count')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntText(value=10, min=0, max=100, description='Count')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntegerInput
#
# IntegerInput is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntegerInput(value=10, min=0, max=100, description='Integer')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntegerInput(value=10, min=0, max=100, description='Integer')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntegerInput(value=10, min=0, max=100, description='Integer')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntegerInput(value=10, min=0, max=100, description='Integer')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## BoundedIntText
#
# BoundedIntText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.BoundedIntText(value=10, min=0, max=100, description='Bounded')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.BoundedIntText(value=10, min=0, max=100, description='Bounded')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.BoundedIntText(value=10, min=0, max=100, description='Bounded')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.BoundedIntText(value=10, min=0, max=100, description='Bounded')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatSlider
#
# FloatSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Ratio')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatRangeSlider
#
# FloatRangeSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description='Range')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatLogSlider
#
# FloatLogSlider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatLogSlider(value=10.0, min=0.0, max=3.0, step=0.1, description='Log')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatText
#
# FloatText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatText(value=3.14, min=0.0, max=10.0, description='Float')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## BoundedFloatText
#
# BoundedFloatText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.BoundedFloatText(value=3.14, min=0.0, max=10.0, description='Bounded')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## IntProgress
#
# IntProgress is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.IntProgress(value=65, min=0, max=100, description='Progress')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.IntProgress(value=65, min=0, max=100, description='Progress')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.IntProgress(value=65, min=0, max=100, description='Progress')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.IntProgress(value=65, min=0, max=100, description='Progress')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## FloatProgress
#
# FloatProgress is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FloatProgress(value=0.65, min=0.0, max=1.0, description='Progress')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Meter
#
# Meter is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Meter(value=72, description='Quality', variant='positive', readout=True)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Meter(value=72, description='Quality', variant='positive', readout=True)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Meter(value=72, description='Quality', variant='positive', readout=True)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Meter(value=72, description='Quality', variant='positive', readout=True)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ProgressCircle
#
# ProgressCircle is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ProgressCircle(value=45, label='Loading', spectrum_size='l')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ProgressCircle(value=45, label='Loading', spectrum_size='l')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ProgressCircle(value=45, label='Loading', spectrum_size='l')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ProgressCircle(value=45, label='Loading', spectrum_size='l')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Play
#
# Play is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Play(value=0, min=0, max=10, step=1, interval=250)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Play(value=0, min=0, max=10, step=1, interval=250)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Play(value=0, min=0, max=10, step=1, interval=250)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Play(value=0, min=0, max=10, step=1, interval=250)
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## DatePicker
#
# DatePicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.DatePicker(value=date(2026, 6, 2), description='Date', width='260px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## TimePicker
#
# TimePicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TimePicker(value=time(9, 30), description='Time', step=60, width='260px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

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
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.DatetimePicker(value=datetime(2026, 6, 2, 9, 30), description='Date and time', step=60, width='320px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ColorPicker
#
# ColorPicker is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ColorPicker(value='#1473e6', description='Accent')
widget

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ColorPicker(value='#1473e6', description='Accent')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ColorPicker(value='#1473e6', description='Accent')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ColorPicker(value='#1473e6', description='Accent')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## ColorHandle
#
# ColorHandle is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ColorHandle(value='#1473e6')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ColorHandle(value='#1473e6')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ColorHandle(value='#1473e6')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ColorHandle(value='#1473e6')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## ColorLoupe
#
# ColorLoupe is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.ColorLoupe(value='#1473e6', open=True)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.ColorLoupe(value='#1473e6', open=True)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ColorLoupe(value='#1473e6', open=True)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ColorLoupe(value='#1473e6', open=True)
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## OpacityCheckerboard
#
# OpacityCheckerboard is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.OpacityCheckerboard(width=160, height=48)
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.OpacityCheckerboard(width=160, height=48)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.OpacityCheckerboard(width=160, height=48)
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.OpacityCheckerboard(width=160, height=48)
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## FileUpload
#
# FileUpload is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Pass a callback

# %%
widget = al.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
status = al.TextWidget('FileUpload: waiting')

def on_click(clicked_widget):
    status.text = f'FileUpload: clicked; current value={getattr(clicked_widget, "value", None)!r}'

widget.on_click(on_click)
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
widget = al.FileUpload(description='Upload file', accept='.csv,.txt', multiple=True, icon='Upload')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Image
#
# Image is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Image(value=SVG_DATA_URI, format='svg+xml', width='180px', height='80px')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Audio
#
# Audio is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Audio(value='', format='mp3')
display(al.VBox({'audio': widget, 'label': al.TextWidget('Audio control placeholder')}, height=110, spacing=8))

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Audio(value='', format='mp3')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Audio(value='', format='mp3')
container = al.VBox({'control': widget, 'label': al.TextWidget('Audio control placeholder')}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Audio(value='', format='mp3')
wrapper = al.VBox({'control': widget, 'label': al.TextWidget('Audio control placeholder')}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Video
#
# Video is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Video(value='', format='mp4', width='260px', height='120px')
display(al.VBox({'video': widget, 'label': al.TextWidget('Video control placeholder')}, height=180, spacing=8))

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Video(value='', format='mp4', width='260px', height='120px')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Video(value='', format='mp4', width='260px', height='120px')
container = al.VBox({'control': widget, 'label': al.TextWidget('Video control placeholder')}, height=180, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Video(value='', format='mp4', width='260px', height='120px')
wrapper = al.VBox({'control': widget, 'label': al.TextWidget('Video control placeholder')}, width='380px', height=180, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Output
#
# Output is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Output(value='Output text')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Output(value='Output text')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Output(value='Output text')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Output(value='Output text')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## HTML
#
# HTML is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.HTML(value='<strong>Rich HTML</strong>', description='HTML')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.HTML(value='<strong>Rich HTML</strong>', description='HTML')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.HTML(value='<strong>Rich HTML</strong>', description='HTML')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.HTML(value='<strong>Rich HTML</strong>', description='HTML')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## HTMLMath
#
# HTMLMath is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.HTMLMath(value=r'\(x^2 + y^2 = z^2\)', description='Math')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.HTMLMath(value=r'\(x^2 + y^2 = z^2\)', description='Math')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.HTMLMath(value=r'\(x^2 + y^2 = z^2\)', description='Math')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.HTMLMath(value=r'\(x^2 + y^2 = z^2\)', description='Math')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Label
#
# Label is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Label(value='Plain label', description='Label')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Label(value='Plain label', description='Label')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Label(value='Plain label', description='Label')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Label(value='Plain label', description='Label')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

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
status = al.TextWidget(f"initial text: {getattr(widget, 'text', None)!r}")

def update(change):
    status.text = f"changed text: {change['new']!r}"

widget.observe(update, names='text')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.TextWidget('Plain anylumino text')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'text'):
    accessed.text = widget.text
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.TextWidget('Plain anylumino text')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Badge
#
# Badge is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Badge(value='Ready', variant='positive', icon='CheckmarkCircle')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Link
#
# Link is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Link('https://example.com', description='Example link', variant='primary')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Link('https://example.com', description='Example link', variant='primary')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Link('https://example.com', description='Example link', variant='primary')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Link('https://example.com', description='Example link', variant='primary')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Divider
#
# Divider is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Divider(orientation='horizontal', spectrum_size='l')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Divider(orientation='horizontal', spectrum_size='l')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Divider(orientation='horizontal', spectrum_size='l')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Divider(orientation='horizontal', spectrum_size='l')
wrapper = al.VBox({'control': widget}, width='380px', height=140, spacing=10, resizable=False)
display(wrapper)

# %% [markdown]
# ## Icon
#
# Icon is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Icon('AddContent', icon_size='l', label='Add')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Icon('AddContent', icon_size='l', label='Add')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Icon('AddContent', icon_size='l', label='Add')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Icon('AddContent', icon_size='l', label='Add')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## UIIcon
#
# UIIcon is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.UIIcon('checkmark100', label='Check')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.UIIcon('checkmark100', label='Check')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.UIIcon('checkmark100', label='Check')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.UIIcon('checkmark100', label='Check')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## HelpText
#
# HelpText is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.HelpText('Use this field for a short label.', variant='neutral')
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.HelpText('Use this field for a short label.', variant='neutral')
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.HelpText('Use this field for a short label.', variant='neutral')
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.HelpText('Use this field for a short label.', variant='neutral')
wrapper = al.VBox({'component': widget}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Underlay
#
# Underlay is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.Underlay(open=False)
display(al.VBox({'underlay': widget, 'label': al.TextWidget('Underlay widget placeholder')}, height=100, spacing=8))

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.Underlay(open=False)
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.Underlay(open=False)
container = al.VBox({'control': widget, 'label': al.TextWidget('Underlay widget placeholder')}, height=120, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.Underlay(open=False)
wrapper = al.VBox({'component': widget, 'label': al.TextWidget('Underlay widget placeholder')}, width='320px', height=120, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## SpectrumElement
#
# SpectrumElement is a public anylumino widget. The examples below separate construction, state access, composition, and appearance.

# %% [markdown]
# ### Basic example

# %%
widget = al.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'class': 'cookbook-accent-box'})
display(widget)

# %% [markdown]
# ### Access state and react to changes

# %%
widget = al.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'class': 'cookbook-accent-box'})
status = al.TextWidget(f"initial value: {getattr(widget, 'value', None)!r}")

def update(change):
    status.text = f"changed value: {change['new']!r}"

widget.observe(update, names='value')
display(al.VBox({'widget': widget, 'status': status}, height=150, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.SpectrumElement('div', text='Custom SpectrumElement content', attributes={'class': 'cookbook-accent-box'})
container = al.VBox({'control': widget}, height=150, spacing=8)
accessed = container['control']
if hasattr(accessed, 'value'):
    accessed.value = widget.value
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.SpectrumElement(
    'div',
    text='Styled with a CSS class passed through attributes',
    attributes={'class': 'cookbook-accent-box'},
)
display(widget)

# %% [markdown]
# # Spectrum action components

# %% [markdown]
# ## ClearButton
#
# ClearButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = al.ClearButton(label='Clear')
display(widget)

# %% [markdown]
# ### Pass a callback

# %%
widget = al.ClearButton(label='Clear')
status = al.TextWidget('ClearButton: waiting')

def on_click(clicked_widget):
    status.text = f'ClearButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
display(al.VBox({'button': widget, 'status': status}, height=140, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.ClearButton(label='Clear')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.ClearButton(label='Clear')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
display(wrapper)

# %% [markdown]
# ## CloseButton
#
# CloseButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = al.CloseButton(label='Close')
display(widget)

# %% [markdown]
# ### Pass a callback

# %%
widget = al.CloseButton(label='Close')
status = al.TextWidget('CloseButton: waiting')

def on_click(clicked_widget):
    status.text = f'CloseButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
display(al.VBox({'button': widget, 'status': status}, height=140, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.CloseButton(label='Close')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.CloseButton(label='Close')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
display(wrapper)

# %% [markdown]
# ## InfieldButton
#
# InfieldButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = al.InfieldButton(label='Search', icon='Search')
display(widget)

# %% [markdown]
# ### Pass a callback

# %%
widget = al.InfieldButton(label='Search', icon='Search')
status = al.TextWidget('InfieldButton: waiting')

def on_click(clicked_widget):
    status.text = f'InfieldButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
display(al.VBox({'button': widget, 'status': status}, height=140, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.InfieldButton(label='Search', icon='Search')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.InfieldButton(label='Search', icon='Search')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
display(wrapper)

# %% [markdown]
# ## PickerButton
#
# PickerButton is a Spectrum-backed action component. Use `on_click` for Python-side callbacks.

# %% [markdown]
# ### Basic example

# %%
widget = al.PickerButton(label='Pick', icon='ChevronDown')
display(widget)

# %% [markdown]
# ### Pass a callback

# %%
widget = al.PickerButton(label='Pick', icon='ChevronDown')
status = al.TextWidget('PickerButton: waiting')

def on_click(clicked_widget):
    status.text = f'PickerButton: clicked; disabled={clicked_widget.disabled!r}'

widget.on_click(on_click)
display(al.VBox({'button': widget, 'status': status}, height=140, spacing=8))

# %% [markdown]
# ### Use as a keyed child in a layout

# %%
widget = al.PickerButton(label='Pick', icon='ChevronDown')
container = al.HBox({'button': widget, 'status': al.TextWidget('Ready')}, height=100, spacing=8)
display(container)

# %% [markdown]
# ### Customize appearance

# %%
widget = al.PickerButton(label='Pick', icon='ChevronDown')
widget.disabled = False
wrapper = al.VBox({'button': widget}, width='260px', height=100, resizable=False)
display(wrapper)

# %% [markdown]
# # Composable Spectrum surfaces

# %% [markdown]
# ## FieldGroup
#
# FieldGroup can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.FieldGroup({'name': al.TextInput(value='Iris', description='Name'), 'enabled': al.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
display(component)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.FieldGroup({'name': al.TextInput(value='Iris', description='Name'), 'enabled': al.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('Tray surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.FieldGroup({'name': al.TextInput(value='Iris', description='Name'), 'enabled': al.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.FieldGroup({'name': al.TextInput(value='Iris', description='Name'), 'enabled': al.Switch(value=True, description='Enabled')}, label='Field group', orientation='horizontal')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Popover
#
# Popover can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
display(component)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('DialogBox surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.Popover({'content': al.TextWidget('Popover child content')}, open=True, placement='bottom')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Tooltip
#
# Tooltip can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.Tooltip('Tooltip content', {'trigger': al.Button(description='Tooltip trigger')}, open=True, placement='top')
display(component)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.Tooltip('Tooltip content', {'trigger': al.Button(description='Tooltip trigger')}, open=True, placement='top')
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('Modal surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.Tooltip('Tooltip content', {'trigger': al.Button(description='Tooltip trigger')}, open=True, placement='top')
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.Tooltip('Tooltip content', {'trigger': al.Button(description='Tooltip trigger')}, open=True, placement='top')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Tray
#
# Tray can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.Tray({'content': al.TextWidget('Tray content')}, open=False)
display(al.VBox({'surface': component, 'label': al.TextWidget('Tray surface; click Toggle in the callback example to open it')}, height=150, spacing=8))

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.Tray({'content': al.TextWidget('Tray content')}, open=False)
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('Tray surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.Tray({'content': al.TextWidget('Tray content')}, open=False)
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.Tray({'content': al.TextWidget('Tray content')}, open=False)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Overlay
#
# Overlay can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
display(component)

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(component)

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.Overlay({'content': al.TextWidget('Overlay content')}, open=True, placement='bottom')
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## DialogBox
#
# DialogBox can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.DialogBox({'body': al.VBox({'field': al.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
display(al.VBox({'surface': component, 'label': al.TextWidget('DialogBox surface; click Toggle in the callback example to open it')}, height=150, spacing=8))

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.DialogBox({'body': al.VBox({'field': al.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('DialogBox surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.DialogBox({'body': al.VBox({'field': al.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.DialogBox({'body': al.VBox({'field': al.TextInput(value='Dialog value', description='Field'), 'message': al.TextWidget('Dialog body')}, height=140)}, title='DialogBox', open=False, width=420)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# ## Modal
#
# Modal can hold child anywidgets. Keyed children make the component composable from Python.

# %% [markdown]
# ### Basic example

# %%
component = al.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
display(al.VBox({'surface': component, 'label': al.TextWidget('Modal surface; click Toggle in the callback example to open it')}, height=150, spacing=8))

# %% [markdown]
# ### Access subcomponents by key

# %%
component = al.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
key = component.child_keys[0] if component.child_keys else None
first_owner = component[key] if key else None
if hasattr(first_owner, 'value'):
    first_owner.value = 'Edited through component[key]'
elif hasattr(first_owner, 'text'):
    first_owner.text = 'Edited through component[key]'
display(al.VBox({'surface': component, 'label': al.TextWidget('Modal surface; the child was edited through component[key]')}, height=150, spacing=8))

# %% [markdown]
# ### Control open state or callbacks

# %%
component = al.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
status = al.TextWidget(f'open={component.is_open!r}')
button = al.Button(description='Toggle')

def toggle(_button):
    component.toggle()
    status.text = f'open={component.is_open!r}'

button.on_click(toggle)
display(al.VBox({'button': button, 'component': component, 'status': status}, height=260, spacing=8))

# %% [markdown]
# ### Customize appearance

# %%
component = al.Modal({'body': al.TextWidget('Modal body child')}, title='Modal', open=False, width=360)
component.width = '360px'
component.height = 'auto'
wrapper = al.VBox({'surface': component, 'label': al.TextWidget('Surface wrapper')}, width='420px', height=260, spacing=8, resizable=False)
display(wrapper)

# %% [markdown]
# # Notebook notes
#
# - Read value-bearing widgets with `widget.value`; `TextWidget` uses `widget.text`.
# - React to value changes with `widget.observe(callback, names="value")` or `names="text"`.
# - Button-like widgets use `widget.on_click(callback)`.
# - Layout widgets expose keyed children with `child_keys`, `get_widget()`, `get_owner()`, and `widget[key]`.
# - Component surfaces such as dialogs, trays, overlays, and popovers expose keyed children plus `show()`, `hide()`, and `toggle()` when open state is meaningful.
# - Appearance customization is usually done through constructor arguments, wrapper layout sizing, Spectrum options such as `variant`/`icon`/`spectrum_size`, and `SpectrumElement(..., attributes={...})` for direct CSS class hooks.
