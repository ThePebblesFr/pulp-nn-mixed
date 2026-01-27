#!/usr/bin/env python3
import glob, re, sys

files = glob.glob('XpulpV2/*/src/Pointwise/*.c')
modified = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        s = fh.read()
    orig = s
    # Only target occurrences that end with ');' (function calls), not function signatures which end with ')' (no semicolon)
    # Patterns to remove:
    # 1) comma then optional whitespace/newline then int nb_dedicated_cores then ) then ;
    s = re.sub(r',\s*\n\s*int\s+nb_dedicated_cores\s*\)\s*;', '\n);', s)
    s = re.sub(r',\s*int\s+nb_dedicated_cores\s*\)\s*;', ');', s)
    # 2) newline then int nb_dedicated_cores then ) then ;
    s = re.sub(r'\n\s*int\s+nb_dedicated_cores\s*\)\s*;', '\n);', s)
    # 3) newline then int nb_dedicated_cores then ; (in case ) was elsewhere)
    s = re.sub(r'\n\s*int\s+nb_dedicated_cores\s*\)\s*', '\n)', s)
    # 4) any leftover 'int nb_dedicated_cores);' on same line
    s = re.sub(r'\bint\s+nb_dedicated_cores\s*\)\s*;', ') ;', s)
    # Clean possible ',);' -> ');'
    s = re.sub(r',\s*\)\s*;', ') ;', s)
    # Finally collapse ' ) ;' to ');'
    s = s.replace(') ;', ');')

    if s != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
        modified.append(f)

print(f"Scanned {len(files)} files.")
print(f"Fixed {len(modified)} files:")
for m in modified:
    print(m)

sys.exit(0)
