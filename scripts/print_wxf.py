#!/usr/bin/env python3
"""Print the time of impact (toi) from a .wxf file."""

import sys
from wolframclient.deserializers import binary_deserialize

with open(sys.argv[1], 'rb') as fp:
    expr = binary_deserialize(fp)
for i in expr:
    toi = str(i[0][1]).replace("Slot[1]", "t")
    print("toi =", toi)
