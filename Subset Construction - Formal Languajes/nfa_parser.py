"""
nfa_parser.py - Parser and validator for NFA input specifications.

Input format (assignment, section 3):
    c                      number of cases (c > 0)
    for each case:
        n                  number of states (states are 1..n)
        S                  initial states, separated by blanks ("0" = empty set)
        Sigma              alphabet: letters a-z separated by blanks
        F                  final states, separated by blanks ("0" = empty set)
        n rows             "state cell_1 ... cell_k"   (one cell per symbol)
                           each cell is "0" (empty set) or a set like "{1 5}"

Any problem in the input raises InputFormatError with the line number.
"""
import re
import sys
from typing import Dict, List, Set, Tuple

from models import NFA


class InputFormatError(Exception):
    """Raised when the input text does not follow the specification."""


_NATURAL = re.compile(r"[0-9]+")
_CELL_TOKENS = re.compile(r"\{[^{}]*\}|\S+")   # "{...}" is ONE token, even with blanks inside
_SET_BODY = re.compile(r"[0-9\s,]*")            # allowed content between the braces


class _LineReader:
    """Reads non-blank lines one at a time, remembering the line numbers."""

    def __init__(self, text: str):
        # utf-8 BOM (added by some Windows editors) would break the first int()
        self.lines = text.lstrip("\ufeff").splitlines()
        self.pos = 0

    def next_line(self, what: str) -> Tuple[int, str]:
        while self.pos < len(self.lines) and not self.lines[self.pos].strip():
            self.pos += 1
        if self.pos >= len(self.lines):
            raise InputFormatError(f"Unexpected end of input: expected {what}.")
        line_no = self.pos + 1
        text = self.lines[self.pos].strip()
        self.pos += 1
        return line_no, text

    def first_extra_line(self):
        """Line number of the first non-blank line not consumed yet (or None)."""
        for i in range(self.pos, len(self.lines)):
            if self.lines[i].strip():
                return i + 1
        return None


def _to_natural(token: str, line_no: int, what: str) -> int:
    if not _NATURAL.fullmatch(token):
        raise InputFormatError(
            f"Line {line_no}: {what} must be a natural number, got '{token}'."
        )
    return int(token)


def _check_states(values: List[int], n: int, line_no: int, what: str) -> Set[int]:
    """Turns a list of numbers into a set of states, validating the range 1..n.
    The list [0] (or an empty list) means the empty set."""
    if not values or values == [0]:
        return set()
    if 0 in values:
        raise InputFormatError(
            f"Line {line_no}: 0 (empty set) cannot be combined with other states in {what}."
        )
    for v in values:
        if v > n:
            raise InputFormatError(
                f"Line {line_no}: state {v} in {what} is out of range (valid states: 1..{n})."
            )
    return set(values)


def _parse_state_list(line: str, line_no: int, n: int, what: str) -> Set[int]:
    tokens = line.replace(",", " ").split()
    values = [_to_natural(t, line_no, what) for t in tokens]
    return _check_states(values, n, line_no, what)


def _parse_alphabet(line: str, line_no: int) -> List[str]:
    symbols = line.split()
    for s in symbols:
        if len(s) != 1 or not ("a" <= s <= "z"):
            raise InputFormatError(
                f"Line {line_no}: invalid symbol '{s}'. Symbols must be single "
                f"lowercase letters (a-z)."
            )
    if len(set(symbols)) != len(symbols):
        raise InputFormatError(f"Line {line_no}: the alphabet has repeated symbols.")
    return symbols


def _parse_cell(token: str, line_no: int, n: int, state: int, symbol: str) -> Set[int]:
    what = f"the transition of state {state} on '{symbol}'"
    if token == "0":
        return set()
    if token.startswith("{") and token.endswith("}") and _SET_BODY.fullmatch(token[1:-1]):
        values = [int(x) for x in re.findall(r"[0-9]+", token)]
        return _check_states(values, n, line_no, what)
    raise InputFormatError(
        f"Line {line_no}: {what} must be 0 or a set like {{1 2}}, got '{token}'."
    )


def _parse_row(line: str, line_no: int, n: int, alphabet: List[str]) -> Tuple[int, Dict[str, Set[int]]]:
    tokens = _CELL_TOKENS.findall(line)
    expected = 1 + len(alphabet)
    if len(tokens) != expected:
        raise InputFormatError(
            f"Line {line_no}: expected {expected} values (the state + one set per symbol "
            f"of the alphabet), found {len(tokens)}."
        )
    state = _to_natural(tokens[0], line_no, "the state at the start of the row")
    if not 1 <= state <= n:
        raise InputFormatError(
            f"Line {line_no}: state {state} is out of range (valid states: 1..{n})."
        )
    row = {sym: _parse_cell(tok, line_no, n, state, sym) for sym, tok in zip(alphabet, tokens[1:])}
    return state, row


def _read_case(reader: _LineReader) -> NFA:
    line_no, text = reader.next_line("the number of states")
    n = _to_natural(text, line_no, "the number of states")
    if n < 1:
        raise InputFormatError(f"Line {line_no}: the number of states must be greater than 0.")

    line_no, text = reader.next_line("the initial states")
    initial_states = _parse_state_list(text, line_no, n, "the initial states")

    line_no, text = reader.next_line("the alphabet")
    alphabet = _parse_alphabet(text, line_no)
    if not alphabet:
        raise InputFormatError(f"Line {line_no}: the alphabet cannot be empty.")

    line_no, text = reader.next_line("the final states")
    final_states = _parse_state_list(text, line_no, n, "the final states")

    delta: Dict[int, Dict[str, Set[int]]] = {}
    for k in range(1, n + 1):
        line_no, text = reader.next_line(f"transition row {k} of {n}")
        state, row = _parse_row(text, line_no, n, alphabet)
        if state in delta:
            raise InputFormatError(f"Line {line_no}: the row for state {state} appears twice.")
        delta[state] = row

    return NFA(n, initial_states, alphabet, final_states, delta)


def read_all_nfas_from_string(input_text: str) -> List[NFA]:
    """Parses and validates every case. Raises InputFormatError on malformed input."""
    reader = _LineReader(input_text)

    line_no, text = reader.next_line("the number of cases")
    c_cases = _to_natural(text, line_no, "the number of cases")
    if c_cases < 1:
        raise InputFormatError(f"Line {line_no}: the number of cases must be greater than 0.")

    nfas = []
    for case_num in range(1, c_cases + 1):
        try:
            nfas.append(_read_case(reader))
        except InputFormatError as err:
            raise InputFormatError(f"Case {case_num}: {err}") from None

    extra = reader.first_extra_line()
    if extra is not None:
        print(
            f"Warning: line {extra} and the following lines are ignored "
            f"(only {c_cases} case(s) were announced).",
            file=sys.stderr,
        )
    return nfas
