"""
Week 6 tests -- Password Strength Auditor
Run with: pytest -v week06_test.py

CI-safe: pure in-memory logic, no network, no filesystem, no external
services.
"""

import pytest
from week06_starter import (
    DEFAULT_BLOCKLIST,
    calculate_strength_score,
    check_blocklist,
    check_character_variety,
    check_length,
    format_report,
)


@pytest.mark.parametrize(
    "password,min_length,expected_pass",
    [
        ("Sh0rt!", 12, False),
        ("ThisIsLongEnough1!", 12, True),
    ],
)
def test_check_length(password, min_length, expected_pass):
    passed, message = check_length(password, min_length=min_length)
    assert passed is expected_pass
    assert isinstance(message, str) and message


def test_check_character_variety_flags_missing_classes():
    passed, message = check_character_variety("alllowercase")
    assert passed is False
    assert message  # should explain what's missing, not be empty


def test_check_character_variety_passes_full_variety():
    passed, _ = check_character_variety("Str0ng!Pass")
    assert passed is True


def test_check_blocklist_is_case_insensitive():
    passed, _ = check_blocklist("PaSSwOrd", blocklist=DEFAULT_BLOCKLIST)
    assert passed is False


def test_check_blocklist_default_argument_not_mutated_between_calls():
    # Guards against the mutable-default-argument pitfall from Week 3:
    # two calls with no explicit blocklist argument must behave
    # identically -- if DEFAULT_BLOCKLIST were used directly as a mutable
    # default and something accidentally mutated it, these could diverge.
    first_passed, _ = check_blocklist("qwerty")
    second_passed, _ = check_blocklist("qwerty")
    assert first_passed is False
    assert second_passed is False


def test_calculate_strength_score_aggregates_all_three_checks():
    weak = calculate_strength_score("password")
    strong = calculate_strength_score("Tr0ub4dor&3xtra!")
    assert weak["overall_pass"] is False
    assert strong["overall_pass"] is True
    assert len(weak["checks"]) == 3
    assert len(strong["checks"]) == 3


def test_format_report_is_human_readable():
    result = calculate_strength_score("password")
    report = format_report("password", result)
    assert isinstance(report, str)
    assert "FAIL" in report.upper() or "PASS" in report.upper()
