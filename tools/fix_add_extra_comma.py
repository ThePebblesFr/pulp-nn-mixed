#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Add/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s
    # Replace patterns with double commas or comma+newline+comma before int nb_dedicated_cores
    s, n1 = re.subn(r',\s*,\s*\n\s*int\s+nb_dedicated_cores', '\n    int nb_dedicated_cores', s)
    s, n2 = re.subn(r',\s*,\s*int\s+nb_dedicated_cores', ',\n    int nb_dedicated_cores', s)
    s, n3 = re.subn(r',\s*\n\s*,\s*int\s+nb_dedicated_cores', '\n    int nb_dedicated_cores', s)
    # Fix possible ',, int nb_dedicated_cores' -> ',\n    int nb_dedicated_cores'
    s, n4 = re.subn(r',,\s*int\s+nb_dedicated_cores', ',\n    int nb_dedicated_cores', s)

    if s != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
        modified.append((f, n1+n2+n3+n4))

print(f"Scanned {len(files)} files, fixed {len(modified)} files")
for m,c in modified:
    print(m, c)

sys.exit(0)
