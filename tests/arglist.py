#!/usr/bin/env python3

# this script is used to test how bash will parse and expand
# raw input with {} and []. This allows us to test by seeing:
#
#./arglist.py {a:1,b:2}
#['a:1', 'b:2']

import sys
print(sys.argv[1:])