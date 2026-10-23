#!/usr/bin/env python3
"""Verify the `Check:` field of every `Type: problem` entry in a questions file.

Check form:  <arithmetic expression> == <value>

For each problem entry:
  1. The expression is evaluated. Only numbers, + - * / **, parentheses, the
     constants pi and e, and the functions in FUNCS are allowed; anything else is
     rejected without being executed.
  2. The result must equal <value> within REL_TOL (printed answers are rounded).
  3. <value> must appear among the numbers of the `Answer key:`.
  4. IF the entry's `Origin:` begins with `curated` THEN <value> must also appear
     among the numbers of its `Source quote:` — the book's printed answer (R13q3).
  5. The entry must carry `Answer key:`, `Elaboration:`, and `Check:`.
  6. `Check: none` marks a non-numeric result (expression, set, classification;
     problems.md R13r5b). It passes the arithmetic checks and is counted separately;
     only the R18c re-solve audits such an entry.

A Check proves the arithmetic. It cannot prove the setup; rule 4 ties a curated
problem to the book's own answer, and the R18c audit covers generated problems.

Usage: verify_problems.py <questions_file>
Exit status: 0 = every problem passed (or the file has none), 1 = a check failed,
2 = usage or file error.
"""

import ast
from collections.abc import Callable, Mapping
import math
import re
import sys
from pathlib import Path

from verify_quotes import extract_quotes, parse_entries

REL_TOL = 5e-3

FUNCS: Mapping[str, Callable[..., float]] = {
    "exp": math.exp, "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "degrees": math.degrees, "radians": math.radians,
    "round": lambda v, n=0: round(v, int(n)),  # for a printed answer rounded further than REL_TOL allows ("about 6%")
}
CONSTS: Mapping[str, float] = {"pi": math.pi, "e": math.e}


def safe_eval(node: ast.AST) -> float:
    """Evaluate an arithmetic AST; raise ValueError on anything that is not plain math."""
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in CONSTS:
        return CONSTS[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        operand = safe_eval(node.operand)
        return -operand if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in FUNCS and not node.keywords):
        return FUNCS[node.func.id](*(safe_eval(arg) for arg in node.args))
    raise ValueError(f"disallowed syntax: {ast.dump(node)[:60]}")


def field(body: str, name: str) -> str | None:
    """Return a field's value with its two-space continuation lines, or None when absent."""
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*(?:\n(?:  .*|[ \t]*(?=\n  )))*)", body, re.M)
    return match.group(1).strip() if match is not None else None


def numbers_in(text: str) -> list[float]:
    """Every number a reader sees, with Unicode minus signs and thousands commas handled."""
    cleaned = text.replace("−", "-").replace("–", "-")
    cleaned = re.sub(r"(?<=\d),(?=\d{3}\b)", "", cleaned)
    values = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", cleaned)]
    # A printed exact answer such as 9/5 or -7/3 also stands for its decimal value.
    for num, den in re.findall(r"(-?\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)(?!\d|\.\d)", cleaned):
        if float(den) != 0:
            values.append(float(num) / float(den))
    return values


def contains_value(numbers: list[float], value: float) -> bool:
    return any(math.isclose(n, value, rel_tol=REL_TOL, abs_tol=1e-12) for n in numbers)


def check_entry(body: str) -> tuple[bool, str]:
    """Return (passed, detail) for one problem entry."""
    check = field(body, "Check")
    answer = field(body, "Answer key")
    missing = [name for name, value in (("Check", check), ("Answer key", answer),
                                        ("Elaboration", field(body, "Elaboration")))
               if value is None or value == ""]
    if check is None or answer is None or missing:
        return False, f"missing or empty field(s): {', '.join(missing)}"

    if check.strip().lower() == "none":
        return True, "non-numeric result (Check: none) — R18c re-solve only"

    expr_text, sep, value_text = check.rpartition("==")
    if not sep:
        return False, "Check must read `<expression> == <value>`"
    try:
        computed = safe_eval(ast.parse(expr_text.strip(), mode="eval"))
        claimed = float(value_text.strip())
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
        return False, f"cannot evaluate Check: {error}"

    if not math.isclose(computed, claimed, rel_tol=REL_TOL, abs_tol=1e-12):
        return False, f"expression gives {computed:.6g}, Check claims {claimed:g}"
    if not contains_value(numbers_in(answer), claimed):
        return False, f"Check value {claimed:g} does not appear in the Answer key"

    origin = field(body, "Origin") or ""
    if origin.lower().startswith("curated"):
        state, quotes = extract_quotes(body)
        if state != "ok":
            return False, "curated problem has no usable Source quote to hold the printed answer"
        if not contains_value(numbers_in(" ".join(quotes)), claimed):
            return False, f"Check value {claimed:g} is not the printed answer in the Source quote"
        return True, f"{computed:.6g} ≈ {claimed:g}; matches Answer key and printed answer"
    return True, f"{computed:.6g} ≈ {claimed:g}; matches Answer key"


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    qpath = Path(sys.argv[1])
    try:
        text = qpath.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)

    checked = 0
    failures = 0
    nonnumeric = 0
    for unit, qid, body in parse_entries(text):
        if field(body, "Type") != "problem":
            continue
        checked += 1
        passed, detail = check_entry(body)
        if passed and detail.startswith("non-numeric"):
            nonnumeric += 1
        if not passed:
            failures += 1
        print(f"{'PASS' if passed else 'FAIL'}  [{unit}] {qid}: {detail}")

    print(f"\nproblems checked : {checked}")
    print(f"Check: none      : {nonnumeric}")
    print(f"FAILED           : {failures}")
    if checked == 0:
        print("No problem entries: nothing to check.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
