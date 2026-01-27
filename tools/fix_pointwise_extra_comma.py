#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Pointwise/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s
    # patterns: double comma then newline then spaces then int nb_dedicated_cores
    s = re.sub(r',\s*,\s*\n\s*int\s+nb_dedicated_cores', '\n                        int nb_dedicated_cores', s)
    # patterns: comma newline then comma+spaces then int nb_dedicated_cores
    s = re.sub(r',\s*\n\s*,\s*int\s+nb_dedicated_cores', '\n                        int nb_dedicated_cores', s)
    # patterns: comma then spaces then comma then spaces then int nb_dedicated_cores on same line
    s = re.sub(r',\s*,\s*int\s+nb_dedicated_cores', '\n                        int nb_dedicated_cores', s)
    # If a leading comma remains before newline+int, remove it
    s = re.sub(r',\s*\n\s*int\s+nb_dedicated_cores', '\n                        int nb_dedicated_cores', s)

    # If this accidentally removed required comma (rare), ensure there's a comma at end of previous param line
    # We'll try to ensure the previous non-empty line in signature ends with a comma.
    if s != orig:
        # fix cases where the previous line might not end with comma by adding it if appropriate
        lines = s.splitlines()
        for i, line in enumerate(lines):
            if 'int nb_dedicated_cores' in line:
                # find previous non-empty line
                j = i-1
                while j >= 0 and lines[j].strip() == '':
                    j -= 1
                if j >= 0 and not lines[j].rstrip().endswith(',') and ')' not in lines[j]:
                    lines[j] = lines[j] + ','
                break
        s = '\n'.join(lines)

    if s != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
        modified.append(f)

print(f"Scanned {len(files)} files, fixed {len(modified)} files")
for m in modified:
    print(m)

sys.exit(0)
