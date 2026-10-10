"""Dependency-free terminal interaction for initialization."""

from contextlib import contextmanager
import os
import shutil
import sys

from .integrations import HARNESSES
from .storage import WishError

LABELS = {"opencode": "OpenCode", "claude": "Claude Code", "codex": "Codex",
          "generic": "Generic Agent Skills (shares Codex's .agents directory)"}


def interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


@contextmanager
def keyboard():
    if os.name == "nt":
        import msvcrt

        def read_key():
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "ignored")
            return key

        yield read_key
        return
    import select
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    original = termios.tcgetattr(descriptor)

    def read_key():
        key = os.read(descriptor, 1).decode("utf-8", errors="ignore")
        if key == "\x1b":
            sequence = ""
            for _ in range(2):
                if not select.select([descriptor], [], [], 0.1)[0]:
                    break
                sequence += os.read(descriptor, 1).decode("ascii", errors="ignore")
            return {"[A": "up", "[B": "down", "OA": "up", "OB": "down"}.get(sequence, "\x1b")
        return key

    try:
        tty.setcbreak(descriptor)
        yield read_key
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, original)


@contextmanager
def ansi_output():
    """Enable Windows VT output temporarily; fall back when unavailable."""
    if os.name != "nt":
        yield os.environ.get("TERM") != "dumb"
        return
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.windll.kernel32
    kernel.GetStdHandle.argtypes = [wintypes.DWORD]
    kernel.GetStdHandle.restype = wintypes.HANDLE
    kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    handle = kernel.GetStdHandle(-11)
    mode = wintypes.DWORD()
    enabled = bool(kernel.GetConsoleMode(handle, ctypes.byref(mode)) and
                   kernel.SetConsoleMode(handle, mode.value | 0x0004))
    try:
        yield enabled
    finally:
        if enabled:
            kernel.SetConsoleMode(handle, mode.value)


def numbered_selection(selected):
    print("Select harnesses (enter numbers separated by spaces, or Q to cancel):")
    for index, name in enumerate(HARNESSES, 1):
        print(f"  [{'x' if name in selected else ' '}] {index}. {LABELS[name]}")
    while True:
        answer = input("Harnesses: ").strip()
        if answer.lower() == "q":
            raise KeyboardInterrupt()
        if not answer and selected:
            return [name for name in HARNESSES if name in selected]
        values = answer.replace(",", " ").split()
        if values and all(value.isascii() and value.isdigit() and 1 <= int(value) <= len(HARNESSES) for value in values):
            return [name for index, name in enumerate(HARNESSES, 1) if index in {int(value) for value in values}]
        print("Choose at least one harness using the listed numbers.")


def select_harnesses(installed=()):
    if not interactive():
        raise WishError("No interactive terminal. Specify harnesses, e.g. 'ow init --harness opencode claude'.")
    selected = set(installed)
    with ansi_output() as ansi:
        size = shutil.get_terminal_size()
        if not ansi or size.columns < 80 or size.lines < len(HARNESSES) + 5:
            return numbered_selection(selected)
        index, drawn, message = 0, False, ""
        rows = len(HARNESSES) + 3
        with keyboard() as read_key:
            sys.stdout.write("\x1b[?25l")
            try:
                while True:
                    if drawn:
                        sys.stdout.write(f"\x1b[{rows}A\x1b[J")
                    lines = ["OpenWish - select harnesses",
                             "Arrows: move | Space: toggle | A: all | Enter: apply | Q/Esc: cancel"]
                    for position, name in enumerate(HARNESSES):
                        lines.append(f"{'>' if index == position else ' '} [{'x' if name in selected else ' '}] {LABELS[name]}")
                    lines.append(message or "Select one or more harnesses.")
                    sys.stdout.write("\n".join(lines) + "\n")
                    sys.stdout.flush()
                    drawn = True
                    key = read_key()
                    if key in ("up", "k"):
                        index = (index - 1) % len(HARNESSES)
                    elif key in ("down", "j", "\t"):
                        index = (index + 1) % len(HARNESSES)
                    elif key == " ":
                        selected.symmetric_difference_update([HARNESSES[index]])
                    elif key.lower() == "a":
                        selected = set() if len(selected) == len(HARNESSES) else set(HARNESSES)
                    elif key in ("\r", "\n"):
                        if selected:
                            return [name for name in HARNESSES if name in selected]
                        message = "Choose at least one harness before initializing."
                    elif key in ("q", "Q", "\x1b", "\x03", "\x04", ""):
                        raise KeyboardInterrupt()
            finally:
                sys.stdout.write("\x1b[?25h")
                sys.stdout.flush()


def confirm_downgrade(entries):
    if not interactive():
        raise WishError("Downgrade requires confirmation in an interactive terminal. Run 'ow init' there.")
    installed = ", ".join(sorted({entry["installed"] for entry in entries}))
    target = entries[0]["available"]
    print(f"\n1. {len(entries)} selected OW files have newer versions ({installed}) than {target}. Downgrade them?")
    print("A. (Recommended) Keep newer files. Other selected installs/upgrades will proceed.")
    print(f"B. Downgrade these files to {target}. Their contents will be overwritten.")
    while True:
        answer = input("Choice [A]: ").strip().lower()
        if answer in ("", "a"):
            return False
        if answer == "b":
            return True
        print("Enter A or B.")
