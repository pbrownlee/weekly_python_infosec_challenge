"""
Week 3 Challenge: Fix the Bugs (and Prove It with pytest)
Tier 0 - Level-Up Phase

A small login-attempt tracking tool. It has FIVE planted bugs. Do not
rewrite it from scratch - find each bug, fix it in place, and use
week03_test.py to prove you fixed it.

See week03_challenge.md for the full brief.
"""

MAX_ATTEMPTS = 3


def start_session(log=[]):
    """Return a fresh, empty attempt log for a new tracking session."""
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
    """Return True once the user has reached MAX_ATTEMPTS failed attempts."""
    attempts = count_attempts(log, username)
    if attempts > MAX_ATTEMPTS:
        return True
    return False


def parse_attempt_limit(raw_value):
    """Parse a config value like '3' into an int. Returns None if the
    value isn't a valid number."""
    try:
        return int(raw_value)
    except TypeError:
        return None


def get_last_n_attempts(log, n):
    """Return the last n entries from the attempt log, most-recent last."""
    result = []
    for i in range(len(log) - n, len(log) - 1):
        result.append(log[i])
    return result


def check_limit_reached(attempts_str, limit):
    """Compare a count of attempts (as a string, e.g. read from a config
    file) against the numeric limit."""
    if attempts_str == limit:
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
