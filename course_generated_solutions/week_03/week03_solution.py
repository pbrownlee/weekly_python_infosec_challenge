"""
Week 3 Solution: Fix the Bugs (and Prove It with pytest)
Tier 0 - Level-Up Phase

This is week03_starter.py with all five planted bugs fixed. Each fix is
commented with what was wrong and why the replacement is correct.
"""

MAX_ATTEMPTS = 3


def start_session(log=None):
    """Return a fresh, empty attempt log for a new tracking session.

    BUG FIXED: the original signature was `log=[]`. Default argument
    values are created exactly ONCE, when the function is defined - not
    once per call. Every caller that didn't pass their own `log` was
    sharing and mutating that same list, so a "fresh" session from a
    second call would already contain entries from the first. The fix
    is the standard idiom: default to None, and build a new list inside
    the function body when nothing was passed.
    """
    if log is None:
        log = []
    return log


def record_attempt(username, log):
    """Record a failed login attempt for a user."""
    log.append(username)
    return log


def count_attempts(log, username):
    """Count how many failed attempts a username has in the log."""
    count = 0
    for entry in log:
        if entry == username:
            count += 1
    return count


def is_locked_out(log, username):
    """Return True once the user has reached MAX_ATTEMPTS failed attempts.

    BUG FIXED: the condition was `attempts > MAX_ATTEMPTS`, which only
    locks a user out on their 4th attempt, letting exactly MAX_ATTEMPTS
    (3) failed attempts through first. The requirement is "locked out
    once they REACH the max," so the comparison needs to include the
    boundary: `>=`.
    """
    attempts = count_attempts(log, username)
    if attempts >= MAX_ATTEMPTS:
        return True
    return False


def parse_attempt_limit(raw_value):
    """Parse a config value like '3' into an int. Returns None if the
    value isn't a valid number.

    BUG FIXED: the original caught `TypeError`, but `int("not_a_number")`
    raises `ValueError`, not `TypeError`. `TypeError` fires when you pass
    an object of the wrong *type* entirely (e.g. `int(None)` or
    `int([1, 2])`); `ValueError` fires when the type is right (a string)
    but the *content* can't be parsed as a number. Because the code
    caught the wrong one, a bad config string crashed the whole script
    instead of being handled - this is exactly the "matching exception
    types precisely" gap this challenge targets.
    """
    try:
        return int(raw_value)
    except ValueError:
        return None


def get_last_n_attempts(log, n):
    """Return the last n entries from the attempt log, most-recent last.

    BUG FIXED: the loop was `range(len(log) - n, len(log) - 1)`, which
    stops one index short of the end - a classic off-by-one that drops
    the very last (most recent) entry and returns only n-1 items. The
    range needs to run all the way through `len(log)` (exclusive upper
    bound, which is `len(log)` itself, not `len(log) - 1`).
    """
    result = []
    for i in range(len(log) - n, len(log)):
        result.append(log[i])
    return result


def check_limit_reached(attempts_str, limit):
    """Compare a count of attempts (as a string, e.g. read from a config
    file) against the numeric limit.

    BUG FIXED: the original compared `attempts_str == limit` directly -
    a `str` and an `int` are never equal in Python, regardless of their
    "value," so this was silently always False. The fix converts the
    string to an int before comparing, so "3" and 3 correctly match.
    """
    if int(attempts_str) == limit:
        return True
    return False


def main():
    log = []
    for user in ["alice", "alice", "bob", "alice"]:
        record_attempt(user, log)

    for user in ["alice", "bob", "carol"]:
        locked = is_locked_out(log, user)
        print(f"{user}: locked={locked}")

    limit = parse_attempt_limit("not_a_number")
    print(f"Configured limit: {limit}")

    print("Last 2 attempts:", get_last_n_attempts(log, 2))
    print("Limit reached ('3' vs 3):", check_limit_reached("3", 3))


if __name__ == "__main__":
    main()
