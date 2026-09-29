"""Tests for the hide-condition summary in layout_to_summary.py. Runs under pytest."""

import xml.etree.ElementTree as ET

import pytest

from layout_to_summary import parse_conditions


def obj(calc):
    return ET.fromstring(
        '<LayoutObject type="Text"><Conditions>'
        f'<Hide findMode="False"><Calculation><Text><![CDATA[{calc}]]></Text></Calculation></Hide>'
        "</Conditions></LayoutObject>"
    )


@pytest.mark.parametrize("calc", ["1", "1=1", " 1 = 1 ", "1 =1"])
def test_always_true_hide_is_flagged(calc):
    result = parse_conditions(obj(calc))
    assert result["hideAlways"] is True
    assert result["hideWhen"] == calc.strip()


@pytest.mark.parametrize(
    "calc",
    ["IsEmpty ( Orders::CustomerCode )", "0", "1=2", "Case ( $$Branch = \"A\"; 1; 0 )", "11"],
)
def test_conditional_hide_is_not_flagged(calc):
    assert "hideAlways" not in parse_conditions(obj(calc))
