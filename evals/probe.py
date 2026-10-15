"""Run a product's unittest files and print each test's outcome as JSON.

  python3 probe.py [--only TEST_ID ...] tests/test_x.py ...

Run from the product directory. Outcomes are `pass`, `fail` (an assertion failed),
`error` (anything else raised, including import errors) or `skip`; a failing subtest
marks its test. The JSON follows a marker line so test output cannot corrupt it.
"""

import json
import os
import sys
import unittest

MARKER = "--- ow-probe ---"
RANK = {"skip": 0, "pass": 1, "error": 2, "fail": 3}


class Outcomes(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.outcomes, self.messages = {}, {}

    def record(self, test, outcome, err=None):
        key = test.id()
        if RANK[outcome] >= RANK[self.outcomes.get(key, "skip")]:
            self.outcomes[key] = outcome
            if err:
                self.messages[key] = f"{err[0].__name__}: {err[1]}"[:300]

    def addSuccess(self, test):
        self.record(test, "pass")

    def addFailure(self, test, err):
        self.record(test, "fail", err)

    def addError(self, test, err):
        self.record(test, "error", err)

    def addSkip(self, test, reason):
        self.record(test, "skip")

    def addExpectedFailure(self, test, err):
        self.record(test, "pass")

    def addUnexpectedSuccess(self, test):
        self.record(test, "fail", (AssertionError, "unexpected success"))

    def addSubTest(self, test, subtest, err):
        if err is None:
            self.record(test, "pass")
        else:
            self.record(test, "fail" if issubclass(err[0], test.failureException) else "error", err)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main(argv):
    only = set()
    if argv and argv[0] == "--only":
        separator = argv.index("--")
        only, argv = set(argv[1:separator]), argv[separator + 1:]
    sys.path.insert(0, os.getcwd())
    loader = unittest.defaultTestLoader
    names = [path[:-3].replace("/", ".") for path in argv]
    tests = [test for test in flatten(loader.loadTestsFromNames(names)) if not only or test.id() in only]
    result = Outcomes()
    unittest.TestSuite(tests).run(result)
    print(MARKER)
    print(json.dumps({"outcomes": result.outcomes, "messages": result.messages}))


if __name__ == "__main__":
    main(sys.argv[1:])
