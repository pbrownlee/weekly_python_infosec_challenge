"""
Week 3 Starter Tests
Tier 0 - Level-Up Phase

Run with:
    pip install pytest
    pytest -v week03_test.py

These three tests are already written and currently FAIL because of bugs
in week03_starter.py. Run them, read the failure output (it tells you
exactly what was expected vs. what you got and on which line), fix one
bug at a time in week03_starter.py, and re-run until all three are green.

There are FIVE bugs total in week03_starter.py - these tests only catch
three of them. Also try running `python week03_starter.py` directly and
read the traceback it produces; that will point you at a fourth. The
fifth you'll need to notice by reading the code (or by writing a test
for it yourself - see the TODOs at the bottom of this file).
"""

import pytest

from week03_finished import (
    check_limit_reached,
    get_last_n_attempts,
    is_locked_out,
    parse_attempt_limit,
    start_session,
)


def test_start_session_is_fresh_each_time():
    """Each new session should start with an empty log - it should not
    carry over attempts recorded in a previous session."""
    session_one = start_session()
    session_one.append("alice")

    session_two = start_session()

    assert session_two == []


def test_lockout_triggers_at_max_attempts():
    """A user should be locked out once they REACH MAX_ATTEMPTS (3)
    failed attempts - not only after exceeding it."""
    log = ["bob", "bob", "bob"]

    assert is_locked_out(log, "bob") is True


def test_get_last_n_attempts_returns_n_items():
    """get_last_n_attempts(log, 2) should return exactly the last 2
    entries, in order."""
    log = ["alice", "bob", "carol", "dave"]

    assert get_last_n_attempts(log, 2) == ["carol", "dave"]



# --- Add your own tests below ---
# TODO 1: write a test for parse_attempt_limit("not_a_number"). What
#         should it return? Run `python week03_starter.py` first and
#         read the traceback closely - it tells you which exception
#         type is actually being raised vs. which one the code catches.
#
# TODO 2: write a test (or two, using @pytest.mark.parametrize) for
#         check_limit_reached(). Try it with a string count and an int
#         limit that represent the same number, e.g. ("3", 3), and
#         think about what type each argument actually is before you
#         write down the expected result.

def test_parse_attempt_limit_returns_int_or_none():
    """parse_attempt_limit('not_a_number') should return None"""
    assert parse_attempt_limit('not_a_number') == None

@pytest.mark.parametrize("i, r", [
    ('3', True),
    ('whatever', False)
])
def test_check_limit_reached_returns_right_boolean(i, r):
    """check_limit_reached('3') returns True is limit = 3 
 check_limit_reached('whatever') returns False"""
    limit = 3
    assert check_limit_reached(i, limit) == r