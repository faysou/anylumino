import inspect
import re
from enum import StrEnum

import pytest

import anylumino as al
import anylumino.astryx as ax
from anylumino import enums as layout_enums
from anylumino.astryx import enums as astryx_enums
from anylumino.enums import choice, optional_choice
from anylumino.workbench.catalog import CATALOG


OPTION_ENUMS = {
    name: value
    for module in (layout_enums, astryx_enums)
    for name, value in vars(module).items()
    if isinstance(value, type) and issubclass(value, StrEnum) and value is not StrEnum
}


def test_choice_accepts_a_member_or_its_value_and_names_the_keyword_when_rejecting():
    assert (choice(ax.Size.SM, ax.Size, "size"), choice("lg", ax.Size, "size")) == (ax.Size.SM, ax.Size.LG)
    assert optional_choice(None, ax.Size, "size") is None
    with pytest.raises(ValueError, match="^size='small' is not a valid Size; use one of 'sm', 'md', 'lg'$"):
        choice("small", ax.Size, "size")


def test_members_compare_equal_to_their_values_so_strings_keep_working():
    button = ax.Button("Go", size="lg", variant=ax.ButtonVariant.PRIMARY)

    assert (button.variant, button.props["size"]) == ("primary", "lg")
    assert (button.variant, button.props["size"]) == (ax.ButtonVariant.PRIMARY, ax.Size.LG)


@pytest.mark.parametrize(
    ("build", "message"),
    [
        (lambda: ax.Button("Go", variant="danger"), "variant='danger' is not a valid ButtonVariant"),
        (lambda: ax.Text("a", size="huge"), "size='huge' is not a valid TextSize"),
        (lambda: ax.Table([], ["a"], density="tight"), "density='tight' is not a valid Density"),
        (lambda: ax.Badge("a", variant="gray"), "variant='gray' is not a valid BadgeVariant"),
        (lambda: al.SplitPanel([], orientation="diagonal"), "orientation='diagonal' is not a valid Orientation"),
        (lambda: al.TabPanel([], tab_placement="middle"), "tab_placement='middle' is not a valid TabPlacement"),
        (lambda: al.BoxPanel([], direction="up"), "direction='up' is not a valid Direction"),
    ],
    ids=["button-variant", "text-size", "table-density", "badge-variant", "split-orientation", "tab-placement", "box-direction"],
)
def test_widgets_reject_values_outside_their_enum(build, message):
    with pytest.raises(ValueError, match=f"^{re.escape(message)}; use one of "):
        build()


def test_every_enum_annotated_keyword_validates_its_value():
    # A keyword typed with an option enum must also convert its value, or a typo would pass silently
    unchecked = []
    for module in (al, ax):
        for name in module.__all__:
            cls = getattr(module, name)
            if not inspect.isclass(cls) or issubclass(cls, StrEnum):
                continue

            source = inspect.getsource(cls.__init__) if "__init__" in vars(cls) else ""
            for parameter in inspect.signature(cls.__init__).parameters.values():
                parts = [part.strip() for part in str(parameter.annotation).split("|")]
                enums = [part for part in parts if part in OPTION_ENUMS]
                if enums and f"choice({parameter.name}, {enums[0]}" not in source and parameter.name not in ("color_mode", "mode"):
                    unchecked.append(f"{name}.{parameter.name}")

    assert unchecked == []


def test_catalog_options_list_the_enum_values():
    assert CATALOG["Table"].options["density"]["enum"] == [member.value for member in ax.Density]
    assert CATALOG["SplitPanel"].props[1].schema["enum"] == ["horizontal", "vertical"]
