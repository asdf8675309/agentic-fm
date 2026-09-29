"""Tests for the object flags decoding in layout_to_summary.py. Runs under pytest."""

import xml.etree.ElementTree as ET

import pytest

from layout_to_summary import parse_layout_object, parse_object_flags


def obj(options=None, body=""):
    opts = "" if options is None else f"<Options>{options}</Options>"
    return ET.fromstring(
        f'<LayoutObject type="Text" key="1"><Bounds top="0" left="0" bottom="10" right="10"/>'
        f"{opts}{body}</LayoutObject>"
    )


def test_default_anchor_adds_nothing():
    # 0x30000000 is left+top, FileMaker's default and 98% of a real solution's objects
    assert parse_object_flags(obj(0x30000000)) == {}


@pytest.mark.parametrize(
    "value, anchor",
    [
        (0x70000000, ["left", "top", "right"]),
        (0xB0000000, ["left", "top", "bottom"]),
        (0xF0000000, ["left", "top", "right", "bottom"]),
        (0x90000000, ["left", "bottom"]),
        (0x10000000, ["left"]),
        (0x00000000, []),
    ],
)
def test_anchor_bits(value, anchor):
    assert parse_object_flags(obj(value)) == {"anchor": anchor}


def test_slide_and_flags_are_reported_next_to_the_default_anchor():
    result = parse_object_flags(obj(0x30000000 | 0x10 | 0x20 | 0x2 | 0x200 | 0x10000))
    assert result == {
        "slide": ["up", "left"],
        "flags": ["locked", "noPrintImage", "handCursor"],
    }


def test_bits_with_an_xml_counterpart_are_not_repeated():
    # hide (0x4), conditional formatting (0x1), tooltip (0x4000) come from their own elements
    assert parse_object_flags(obj(0x30000000 | 0x4 | 0x1 | 0x4000)) == {}


@pytest.mark.parametrize("element", [obj(None), obj("not-a-number"), obj("")])
def test_missing_or_unreadable_options_is_ignored(element):
    assert parse_object_flags(element) == {}


def test_portal_inner_options_is_not_read_as_object_flags():
    # A Portal's own <Options show="5"> sits one layer down and means something else
    element = obj(0x30000000, body='<Portal><Options show="5"/></Portal>')
    assert parse_object_flags(element) == {}


def test_flags_reach_the_object_summary():
    summary = parse_layout_object(obj(0x70000000))
    assert summary["anchor"] == ["left", "top", "right"]


# ── field entry (the <Options> inside <Field>) ────────────────────────────────

from layout_to_summary import parse_field, parse_field_entry


def field(options=None):
    opts = "" if options is None else f"<Options>{options}</Options>"
    return ET.fromstring(
        '<Field><FieldReference id="1" name="F"><TableOccurrenceReference name="T"/>'
        f"</FieldReference>{opts}</Field>"
    )


def test_default_field_entry_adds_nothing():
    # 0x80E0: tab, return, enter, placeholder in Find mode; entry allowed in both modes
    assert parse_field_entry(field(0x80E0)) == {}


@pytest.mark.parametrize(
    "value, expected",
    [
        (0x80E2, {"selectOnEntry": True}),
        (0x80F0, {"findEntry": False}),
        (0x80E4, {"browseEntry": False}),
        (0x80F4, {"browseEntry": False, "findEntry": False}),
        (0x80F2, {"findEntry": False, "selectOnEntry": True}),
    ],
)
def test_field_entry_bits(value, expected):
    assert parse_field_entry(field(value)) == expected


@pytest.mark.parametrize("element", [field(None), field("x"), field("")])
def test_field_without_readable_options_is_ignored(element):
    assert parse_field_entry(element) == {}


def test_field_entry_reaches_the_field_summary():
    element = ET.fromstring(
        '<LayoutObject type="Edit Box"><Bounds top="0" left="0" bottom="1" right="1"/>'
        '<Field><FieldReference id="1" name="F"><TableOccurrenceReference name="T"/>'
        "</FieldReference><Options>32948</Options></Field></LayoutObject>"
    )
    assert parse_field(element)["findEntry"] is False
