#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Add/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s

    # 1) Add signature parameter if missing
    # Match function declaration: allow optional attributes between void and name
    m = re.search(r'(void(?:\s+__attribute__\s*\(\(.*?\)\))?\s+pulp_nn_add_[\w_]*\s*\()(.*?)(\)\s*\{)', s, re.S)
    if m:
        params = m.group(2)
        if 'nb_dedicated_cores' not in params:
            # determine indentation from first param line if possible
            # default to 4 spaces
            indent = '    '
            # insert before closing )
            insert = ',\n' + indent + 'int nb_dedicated_cores'
            s = s[:m.start(2)] + params + insert + s[m.end(2):]

    # 2) Replace NUM_CORES with nb_dedicated_cores
    if 'NUM_CORES' in s:
        s = s.replace('NUM_CORES', 'nb_dedicated_cores')

    # 3) Insert modulo after core_id = pi_core_id(); for int and uint8_t
    if 'core_id = pi_core_id();' in s:
        lines = s.splitlines(True)
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            out.append(line)
            m2 = re.match(r'^(?P<indent>\s*)(?:uint8_t|int)\s+core_id\s*=\s*pi_core_id\s*\(\s*\)\s*;\s*$', line)
            if m2:
                # check next non-empty line for existing modulo
                next_i = i + 1
                next_has = False
                if next_i < len(lines):
                    if 'core_id = core_id %' in lines[next_i] or 'nb_dedicated_cores' in lines[next_i]:
                        next_has = True
                if not next_has:
                    indent = m2.group('indent')
                    out.append(indent + 'core_id = core_id % nb_dedicated_cores;\n')
            i += 1
        s = ''.join(out)

    if s != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
        modified.append(f)

print(f"Scanned {len(files)} files, modified {len(modified)} files")
for m in modified:
    print(m)

sys.exit(0)
