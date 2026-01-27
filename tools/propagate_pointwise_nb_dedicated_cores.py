#!/usr/bin/env python3
import glob, re, io, sys

pattern_files = glob.glob('XpulpV2/*/src/Pointwise/*.c')
modified = []
for f in pattern_files:
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            s = fh.read()
    except Exception as e:
        print(f"ERROR reading {f}: {e}")
        continue

    orig = s
    if 'nb_dedicated_cores' in s:
        # already modified, skip
        continue

    changed = False

    # 1) Add parameter after flag_batch_norm)
    # Replace occurrences of 'flag_batch_norm)' with 'flag_batch_norm,\n                        int nb_dedicated_cores)'
    new_s, nsub = re.subn(r'flag_batch_norm\s*\)', "flag_batch_norm,\n                        int nb_dedicated_cores)", s)
    if nsub:
        s = new_s
        changed = True

    # 2) Replace NUM_CORES with nb_dedicated_cores
    if 'NUM_CORES' in s:
        s = s.replace('NUM_CORES', 'nb_dedicated_cores')
        changed = True

    # 3) Insert modulo line after core_id = pi_core_id(); for both int and uint8_t variants
    # We'll process line by line to preserve indentation
    if 'core_id = pi_core_id();' in s:
        lines = s.splitlines(True)
        out_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            out_lines.append(line)
            m = re.match(r'^(?P<indent>\s*)(?:uint8_t|int)\s+core_id\s*=\s*pi_core_id\s*\(\s*\)\s*;\s*$', line)
            if m:
                # check next non-empty line whether modulo already present
                next_idx = i + 1
                next_has_mod = False
                if next_idx < len(lines):
                    next_line = lines[next_idx]
                    if 'core_id = core_id %' in next_line or 'nb_dedicated_cores' in next_line:
                        next_has_mod = True
                if not next_has_mod:
                    indent = m.group('indent')
                    out_lines.append(indent + 'core_id = core_id % nb_dedicated_cores;\n')
                    changed = True
            i += 1
        s = ''.join(out_lines)

    if changed and s != orig:
        try:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(s)
            modified.append(f)
        except Exception as e:
            print(f"ERROR writing {f}: {e}")

print(f"Scanned {len(pattern_files)} files under Pointwise.")
print(f"Modified {len(modified)} files:")
for m in modified:
    print(m)

# exit code indicates number modified
sys.exit(0)
