#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/LinearQuant/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s

    # 1) Add parameter to function signature if missing
    m = re.search(r'(void\s+pulp_nn_linear_[\w_]*\s*\()(.*?)(\)\s*\{)', s, re.S)
    if m:
        params = m.group(2)
        if 'nb_dedicated_cores' not in params:
            insert = ',\n                        int nb_dedicated_cores'
            s = s[:m.start(2)] + params + insert + s[m.end(2):]

    # 2) Replace NUM_CORES with nb_dedicated_cores
    if 'NUM_CORES' in s:
        s = s.replace('NUM_CORES', 'nb_dedicated_cores')

    # 3) Insert modulo after core_id = pi_core_id(); (handles int and uint8_t)
    if 'core_id = pi_core_id();' in s:
        lines = s.splitlines(True)
        out = []
        i = 0
        changed = False
        while i < len(lines):
            line = lines[i]
            out.append(line)
            m2 = re.match(r'^(?P<indent>\s*)(?:uint8_t|int)\s+core_id\s*=\s*pi_core_id\s*\(\s*\)\s*;\s*$', line)
            if m2:
                # check next few lines for existing modulo
                next_has_mod = False
                for j in range(1,4):
                    if i + j < len(lines):
                        nxt = lines[i+j]
                        if 'core_id = core_id %' in nxt or '% nb_dedicated_cores' in nxt:
                            next_has_mod = True
                            break
                if not next_has_mod:
                    indent = m2.group('indent')
                    out.append(indent + 'core_id = core_id % nb_dedicated_cores;\n')
                    changed = True
            i += 1
        if changed:
            s = ''.join(out)

    if s != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
        modified.append(f)

print(f"Scanned {len(files)} files, modified {len(modified)} files")
for m in modified:
    print(m)

sys.exit(0)
