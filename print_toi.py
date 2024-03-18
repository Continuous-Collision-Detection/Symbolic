#!/usr/bin/env python3
import sys
from wolframclient.deserializers import binary_deserialize
import sympy
from sympy.parsing.mathematica import parse_mathematica

with open(sys.argv[1], 'rb') as fp:
    expr = binary_deserialize(fp)
for i in expr:
    toi = str(i[0][1]).replace("Slot[1]", "t")
    print("toi =", toi)
    # print(sympy.latex(parse_mathematica(toi)))
