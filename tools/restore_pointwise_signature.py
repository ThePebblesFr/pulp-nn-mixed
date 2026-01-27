#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Pointwise/*.c')
modified = []
scanned = 0
for f in files:
    scanned += 1
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s

    # Find the function signature for pulp_nn_pointwise_* that begins with 'void ' and ends with ')' before '{'
    m = re.search(r'(void\s+pulp_nn_pointwise_[a-zA-Z0-9_]*\s*\()(.*?)(\)\s*\{)', s, re.S)
    if not m:
        # no match, skip
        continue
    params = m.group(2)
    if 'nb_dedicated_cores' in params:
        # already present
        continue

    # Insert the parameter before the closing ')'
    # Keep indentation consistent: use 24 spaces as in other files
    insert = ',\n                        int nb_dedicated_cores'
    new_params = params + insert
    new_s = s[:m.start(2)] + new_params + s[m.end(2):]

    # Safety check: ensure we didn't mess up calls elsewhere by confirming function declaration area contains 'void pulp_nn_pointwise'
    if 'void pulp_nn_pointwise' not in new_s:
        continue

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(new_s)
    modified.append(f)

print(f"Scanned {scanned} files, modified {len(modified)} files")
for m in modified:
    print(m)

sys.exit(0)
