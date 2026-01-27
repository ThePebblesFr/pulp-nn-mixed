#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/LinearNoQuant/*.c')
modified = []
pattern = re.compile(r"(?P<line>^(?P<indent>\s*)(?:uint8_t|int)\s+core_id\s*=\s*pi_core_id\s*\(\s*\)\s*;)(\r?\n)(?!\s*core_id\s*=)", re.M)
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    new_s, n = pattern.subn(lambda m: m.group('line') + m.group(3) + m.group('indent') + 'core_id = core_id % nb_dedicated_cores;' + '\n', s)
    if n > 0 and new_s != s:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_s)
        modified.append((f,n))

print(f"Scanned {len(files)} files, modified {len(modified)} files")
for f,n in modified:
    print(f, n)

sys.exit(0)
