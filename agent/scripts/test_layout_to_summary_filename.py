"""Tests for summary file naming in layout_to_summary.py. Runs under pytest."""

import pytest

from layout_to_summary import summary_filename


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Invoices", "Invoices - ID 7.json"),
        ("Description/Notes", "Description_Notes - ID 7.json"),
        ("Desktop | Orders", "Desktop _ Orders - ID 7.json"),
        ('a\\b:c*d?e"f<g>h', "a_b_c_d_e_f_g_h - ID 7.json"),
    ],
)
def test_summary_filename(name, expected):
    assert summary_filename(name, 7) == expected


def test_a_slash_never_creates_a_subdirectory():
    assert "/" not in summary_filename("Description/Notes", 7)
