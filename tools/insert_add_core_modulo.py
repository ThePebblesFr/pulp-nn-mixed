#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Add/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    orig = ''.join(lines)
    out = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = re.match(r'^(?P<indent>\s*)(?:uint8_t|int)\s+core_id\s*=\s*pi_core_id\s*\(\s*\)\s*;\s*$', line)
        if m:
            # check next few lines for existing modulo
            next_has_mod = False
            for j in range(1,4):
                if i + j < len(lines):
                    nxt = lines[i+j]
                    if 'core_id = core_id %' in nxt or '% nb_dedicated_cores' in nxt:
                        next_has_mod = True
                        break
            if not next_has_mod:
                indent = m.group('indent')
                out.append(indent + 'core_id = core_id % nb_dedicated_cores;\n')
                changed = True
        i += 1
    new = ''.join(out)
    if changed and new != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new)
        modified.append(f)

print(f"Scanned {len(files)} files, inserted modulo in {len(modified)} files")
for m in modified:
    print(m)

sys.exit(0)
