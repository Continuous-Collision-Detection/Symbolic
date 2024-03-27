"""Wolfram Language utilities."""

import os
import sys
import pathlib
import time

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wlexpr


def default_wolfram_kernel_path():
    paths = []
    WOLFRAM_KERNEL = os.getenv("WOLFRAM_KERNEL")
    if WOLFRAM_KERNEL:
        paths.append(pathlib.Path(WOLFRAM_KERNEL))
    paths.append(pathlib.Path("/share/apps/mathematica/12.1.1/bin/wolfram"))
    paths.append(pathlib.Path(
        "/Applications/Mathematica.app/Contents/MacOS/wolfram"))

    for p in paths:
        if p.exists():
            return str(p)

    raise Exception("no mathematica kernel found!")


def open_wolfram_language_session(WolframKernel_path, max_retry=5):
    for _ in range(max_retry):
        try:
            session = WolframLanguageSession(
                WolframKernel_path, stdout=sys.stdout)
            return session
        except Exception as e:
            print(f"- failed to check license ({e}), retrying", flush=True)
            time.sleep(1)
    return None


def load_wolfram_script(session, script_path):
    with open(script_path, 'r') as f:
        script = f.read()
    session.evaluate(wlexpr(script))


def rules_to_dict(rules):
    return dict(rule.args for rule in rules)
