"""
Week 1 — CLI Security Utils Toolkit (starter)
 
Two subcommands:
    cipher   - ROT-N shift cipher, encode or decode
    checkpw  - password strength rule check
 
Fill in the TODO sections. The function boundaries are already laid out
for you this week — later weeks will ask you to design more of this
structure yourself, so pay attention to *why* the program is split up
this way, not just *what* goes in each blank.
 
Run examples (once implemented):
    python week01_starter.py cipher "Hello, World!" --shift 3
    python week01_starter.py cipher "Khoor, Zruog!" --shift 3 --decode
    python week01_starter.py checkpw "pass1"
"""
 
import argparse
import re
import json
import csv
 
 
# ---------------------------------------------------------------------------
# Cipher logic
# ---------------------------------------------------------------------------
 
def shift_char(char: str, shift: int) -> str:
    """
    Shift a single character by `shift` positions in the alphabet.
 
    Letters wrap around (A -> B -> ... -> Z -> A) and preserve case.
    Non-letter characters (spaces, punctuation, digits, etc.) are
    returned unchanged.
 
    Work out the math for one uppercase letter and one lowercase
    letter by hand before writing this (see the challenge's worked
    trace example).
    """
    # we can just return non alphanumeric characters with no actions performed
    if not char.isalpha():
        return char

    # otherwise we do the shifting 
    start = 97 if char.islower() else 65
    return chr((ord(char) - start + shift) % 26 + start)

 
 
def rot_n_transform(text: str, shift: int) -> str:
    """
    Apply shift_char() to every character in `text` and return the
    resulting string.
 
    This function does NOT need to know anything about encode vs.
    decode — that distinction is handled by the sign of `shift`
    before this function is ever called.
    """
    # TODO: implement (hint: build a list of shifted characters,
    # then "".join() them)
    ciphered_text = []
    for char in text:
        ciphered_text.append(shift_char(char, shift))  

    return "".join(ciphered_text)

    
 
 
# ---------------------------------------------------------------------------
# Password rule checking
# ---------------------------------------------------------------------------
 
MIN_PASSWORD_LENGTH = 8
# A symbol, for our purposes, is any non-alphanumeric, non-whitespace
# character. Feel free to adjust this pattern if you want to be stricter.
SYMBOL_PATTERN = re.compile(r"[^\w\s]")
DIGIT_PATTERN =  re.compile(r"\d")
UPPERCASE_PATTERN = re.compile(r"[A-Z]")
LOWERCASE_PATTERN = re.compile(r"[a-z]")

RULE_MAP = {
    "Contains a symbol": SYMBOL_PATTERN,
    "Contains a digit": DIGIT_PATTERN,
    "Contains an uppercase letter": UPPERCASE_PATTERN,
    "Contains a lowercase letter": LOWERCASE_PATTERN,
}
 
 
def check_password_rules(password: str) -> dict:
    """
    Evaluate `password` against the strength rules and return a dict
    mapping a human-readable rule description to True (passed) or
    False (failed).
 
    Expected keys (exact strings, so the report formatter and any
    tests can rely on them):
        "Length >= 8 characters"
        "Contains a digit"
        "Contains an uppercase letter"
        "Contains a lowercase letter"
        "Contains a symbol"
 
    Use re.search() for the pattern-based rules (digit, uppercase,
    lowercase, symbol) — this is the point of this week's re practice,
    not a plain character-by-character loop.
    """
    results = {}
    # first do the length check (not a regex)
    results["Length >= 8 characters"] = len(password) >= MIN_PASSWORD_LENGTH
    # then loop through the regex checks
    for check, rule in RULE_MAP.items():
        if rule.search(password) is not None:
            results[check] = True
        else:
            results[check] = False
    return results 
 
 
def format_password_report(results: dict, as_json: bool = False, as_csv: bool = False) -> str:
    """
    Turn the dict returned by check_password_rules() into the
    printable report shown in the challenge's example usage, e.g.:
 
        Password strength report:
          [FAIL] Length >= 8 characters
          [PASS] Contains a digit
          ...
        Overall: WEAK (2/5 rules passed)
 
    Overall label suggestion: "STRONG" if all rules pass, "WEAK"
    otherwise — but feel free to add a "MODERATE" tier if you want to
    go a bit further than the minimum.
 
    Notice this function only *formats* — it does not compute
    anything about the password itself. Keeping "compute" and
    "print/format" separate is deliberate; it's a structuring habit
    worth keeping as programs get bigger.
    """
    # TODO: implement
    total = len(results)
    pass_counter = 0
    report = ""
    report += "Password strength report: \n"
    for check, status in results.items():
        if status:
            report += f"[PASS] {check} \n"
            pass_counter += 1
        else: 
            report += f"[FAIL] {check} \n"

    if pass_counter == total:
        report += f"Overall: STRONG ({pass_counter}/{total} test passed)"
    elif 3 <= pass_counter < total:
        report += f"Overall: MODERATE ({pass_counter}/{total} test passed)"
    else:
        report += f"Overall: WEAK ({pass_counter}/{total} test passed)"

    if as_json:
        output_json_report(results)
    if as_csv:
        output_csv_report(results)
    return report


def output_json_report(results: dict) -> None:
    print("Outputting JSON")
    with open("pwreport.json", "w") as f:
        json.dump(results, f)


def output_csv_report(results: dict) -> None:
    print("Outputting CSV")
    with open("pwreport.csv", "w") as f:
        writer = csv.writer(f)

        writer.writerow(["Test Name", "Status"])

        for check, status in results.items():
            writer.writerow([check, status])

 
# ---------------------------------------------------------------------------
# Subcommand handlers (each one takes the parsed argparse Namespace)
# ---------------------------------------------------------------------------
 
def run_cipher(args: argparse.Namespace) -> None:
    """
    Handle the `cipher` subcommand: figure out the effective shift
    (negate it if --decode was passed), run the transform, and print
    the result.
    """
    # TODO: implement
    # Find out if there is a shift negate --decode true
    if args.decode:
        negated_shift = -args.shift 
        # send this to the rot_n_transform function
        result_string = rot_n_transform(args.text, negated_shift)
    # If no decode than send regular shift amount  
    else:
        result_string = rot_n_transform(args.text, args.shift)

    print(f"Your ciphered string is: {result_string}")
    
 
def run_checkpw(args: argparse.Namespace) -> None:
    """
    Handle the `checkpw` subcommand: run the rule checks and print
    the formatted report.
    """
    # Get the results
    results = check_password_rules(args.password)

    # Send them with to be printed with the optional json, csv arguments
    format_string = format_password_report(results, as_json=args.json, as_csv=args.csv)

    # print the resulting string
    print(format_string)
 
 
# ---------------------------------------------------------------------------
# Argument parsing and entry point
# ---------------------------------------------------------------------------
 
def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the top-level ArgumentParser, with two
    subparsers: "cipher" and "checkpw".
 
    cipher subcommand needs:
        text            (positional, the text to transform)
        --shift         (required int, the shift amount)
        --decode        (flag, store_true — if present, decode instead
                          of encode)
 
    checkpw subcommand needs:
        password        (positional, the password to check)
    """
    parser = argparse.ArgumentParser(
        description="CLI security utils: ROT-N cipher and password strength check."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
 
    # TODO: build the "cipher" subparser and add its arguments
    cipher_parser = subparsers.add_parser("cipher", help="run the chiper operation")
    cipher_parser.add_argument("text", type=str, help="The text to encode or decode")
    cipher_parser.add_argument("--shift", type=int, required=True, help="The number of times to shift the letters")
    cipher_parser.add_argument("--decode", action="store_true", help="If present decode the text")

 
    # TODO: build the "checkpw" subparser and add its arguments
    checkpw_parser = subparsers.add_parser("checkpw", help="run the checkpw operation")
    checkpw_parser.add_argument("password", type=str, help="The password string to check")
    checkpw_parser.add_argument("--json", action="store_true", help="Output a json file")
    checkpw_parser.add_argument("--csv", action="store_true", help="Output a csv file")

    return parser
 
 
def main() -> None:
    """
    Parse arguments and dispatch to the right subcommand handler.
    """
    parser = build_parser()
    args = parser.parse_args()
 
    # TODO: dispatch on args.command to run_cipher() or run_checkpw()
    print(f"Executing: {args.command}")
    if args.command == "cipher":
        run_cipher(args)
    elif args.command == "checkpw":
        run_checkpw(args)
    
 
 
if __name__ == "__main__":
    main()