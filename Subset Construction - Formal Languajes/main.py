"""
main.py - Entry point for the Subset Construction project.

Usage:
    python main.py [input_file]

The input is taken, in this order, from:
    1. the input_file argument, if given;
    2. data piped/redirected through stdin;
    3. an input.txt file in the current directory.

The DFA tables are printed to stdout; errors and warnings go to stderr.
An interactive HTML report is also generated (resultado_automata.html) and, when
the program is run from a terminal, opened automatically in the default browser.
"""
import os
import sys
import webbrowser
from pathlib import Path
from typing import NoReturn

from nfa_parser import InputFormatError, read_all_nfas_from_string
from subset_builder import SubsetConstructionBuilder
from html_generator import HTMLReportGenerator

DEFAULT_INPUT = "input.txt"
HTML_OUTPUT = "resultado_automata.html"


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def read_input_file(path: str) -> str:
    if not os.path.exists(path):
        fail(f"the input file '{path}' does not exist.")
    if not os.path.isfile(path):
        fail(f"'{path}' is not a file.")
    try:
        # utf-8-sig also accepts files that start with a BOM
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except PermissionError:
        fail(f"you do not have permission to read '{path}'.")
    except UnicodeDecodeError:
        fail(f"'{path}' is not a valid UTF-8 text file.")
    except OSError as exc:
        fail(f"could not read '{path}': {exc.strerror or exc}.")


def get_input_text() -> str:
    if len(sys.argv) > 2:
        fail("too many arguments. Usage: python main.py [input_file]", 2)
    if len(sys.argv) == 2:
        return read_input_file(sys.argv[1])

    # Data coming through a pipe or redirection (python main.py < input.txt)
    if sys.stdin is not None and not sys.stdin.isatty():
        try:
            piped = sys.stdin.read()
        except (UnicodeDecodeError, OSError) as exc:
            fail(f"could not read the standard input: {exc}.")
        if piped.strip():
            return piped

    if not os.path.exists(DEFAULT_INPUT):
        fail(
            "no input provided. Use 'python main.py <input_file>', pipe the data "
            f"through stdin, or create an {DEFAULT_INPUT} file."
        )
    return read_input_file(DEFAULT_INPUT)


def print_case(case_num: int, dfa) -> None:
    print(f"Case {case_num}:")
    print(f"Initial state: {dfa.start_state_id}")
    # 0 is the assignment's notation for the empty set
    finals = " ".join(map(str, dfa.final_state_ids)) if dfa.final_state_ids else "0"
    print(f"Final states: {finals}")
    print("DFA Transition Table:")
    print("State\t" + "\t".join(dfa.alphabet))
    for st_id in range(1, len(dfa.states) + 1):
        cells = [str(dfa.delta[st_id].get(sym, "-")) for sym in dfa.alphabet]
        print("\t".join([str(st_id)] + cells))


def open_in_browser(path: str) -> None:
    uri = Path(path).resolve().as_uri()
    try:
        opened = webbrowser.open(uri)
    except Exception:
        opened = False
    if not opened:
        print(f"Warning: could not open the browser automatically. Open '{path}' manually.",
              file=sys.stderr)


def main() -> None:
    input_text = get_input_text()

    try:
        nfas = read_all_nfas_from_string(input_text)
    except InputFormatError as exc:
        fail(f"invalid input. {exc}")

    processed_cases = []
    for case_num, nfa in enumerate(nfas, 1):
        dfa = SubsetConstructionBuilder.build_dfa(nfa)
        processed_cases.append((nfa, dfa))
        if case_num > 1:
            print()  # blank line only BETWEEN cases
        print_case(case_num, dfa)

    try:
        HTMLReportGenerator.generate_html(processed_cases, HTML_OUTPUT)
    except Exception as exc:
        print(f"Warning: failed to create the HTML report: {exc}", file=sys.stderr)
        return

    # Only when a person is at the terminal: never when the output is piped/redirected
    if sys.stdout.isatty():
        open_in_browser(HTML_OUTPUT)


if __name__ == "__main__":
    main()
