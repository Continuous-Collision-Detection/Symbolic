import os
import sys
import time

import numpy

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr, Global

def open_session(WolframKernel_path, mma_file, max_retry=5):
    for _ in range(max_retry):
        try:
            session = WolframLanguageSession(
                WolframKernel_path, stdout=sys.stdout)
            with open(mma_file, 'r') as f:
                script = f.read()
            session.evaluate(wlexpr(script))
            print("- mma file loaded", flush=True)
            return session
        except:
            print("- failed to check license, retrying", flush=True)
            time.sleep(1)
    return None

def rules_to_dict(rules):
    return dict(rule.args for rule in rules)

if len(sys.argv) >= 2:
    WolframKernel_path = sys.argv[1]
else:
    WolframKernel_path = os.getenv('WOLFRAM_KERNEL')

print(f"attempting to use {WolframKernel_path}")

session = open_session(WolframKernel_path, "roots_vf.mma")

if not session:
    print("failed to open mathematica!")
    exit(1)

query = [
    [0, 1, -1, 1, 0, 1],
    [1, 1, 0, 1, -1, 1],
    [0, 1, 0, 1, 1, 1],
    [-1, 1, 0, 1, -1, 1],
    [0, 1, 1, 1, 0, 1],
    [1, 1, 0, 1, -1, 1],
    [0, 1, 0, 1, 1, 1],
    [-1, 1, 0, 1, -1, 1]
]

# query = [
#     ['6004799504361621', '36028797018963968', '8406719305025405', '18014398509481984', '6004799504361621', '36028797018963968'],
#     ['5991880653447211', '18014398509481984', '1569622679492231', '1125899906842624', '3000580773410431', '9007199254740992'],
#     ['5552384021537779', '36028797018963968', '895195853007905', '2251799813685248', '2884273913025777', '18014398509481984'],
#     ['5994415962440743', '18014398509481984', '3143497780723795', '2251799813685248', '-4959467315358399', '18446744073709551616'],
#     ['6004799504361621', '36028797018963968', '8406719305025405', '18014398509481984', '6004799504361621', '36028797018963968'],
#     ['1446726186979235', '4503599627370496', '5675102972698969', '4503599627370496', '1505494021547267', '4503599627370496'],
#     ['4687563062029645', '36028797018963968', '601912797734833', '2251799813685248', '1471332316398453', '9007199254740992'],
#     ['2913215074912037', '9007199254740992', '5679403831262947', '4503599627370496', '6389336975038983', '18446744073709551616'],
# ]

result = session.evaluate(Global.roots(query, "roots.bin"))
print(result)
session.terminate()

session = open_session(WolframKernel_path, "compare_vf_toi.wl")
results = rules_to_dict(session.evaluate(Global.compareToI("roots.bin", 0.49)))
# results = rules_to_dict(session.evaluate(Global.compareToI("roots.bin", 0.243923)))
print(results)
session.terminate()

