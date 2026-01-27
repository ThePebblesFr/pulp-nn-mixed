#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET_DIR = ROOT / 'XpulpV2' / '32bit' / 'src' / 'Convolution'

def process_file(p: Path):
    s = p.read_text()
    if 'nb_dedicated_cores' in s:
        return False

    # 1) Replace NUM_CORES -> nb_dedicated_cores
    s2 = s.replace('NUM_CORES', 'nb_dedicated_cores')

    # 2) Insert nb_dedicated_cores parameter into function declaration
    # Find the first occurrence of function starting line: void pulp_nn_conv_
    m = re.search(r'(void\s+pulp_nn_conv_[^\(]*\()([\s\S]*?)(\)\s*\{)', s2)
    if m:
        params = m.group(2)
        if 'nb_dedicated_cores' not in params:
            # insert at end before closing )
            params_new = params.rstrip()
            # add with same indentation as many files use 24 spaces for params start
            insert = ',\n                        int nb_dedicated_cores'
            params_new = params_new + insert
            s2 = s2[:m.start(2)] + params_new + s2[m.end(2):]
    else:
        # no match, skip
        return False

    # 3) Add core_id modulo line after pi_core_id() assignment
    s3 = s2
    s3 = s3.replace('int core_id = pi_core_id();\n  uint8_t * pIm2ColBase', 'int core_id = pi_core_id();\n  core_id = core_id % nb_dedicated_cores;\n  uint8_t * pIm2ColBase')
    s3 = s3.replace('int core_id = pi_core_id();\n  core_id = core_id % nb_dedicated_cores;\n  uint8_t * pIm2ColBase', 'int core_id = pi_core_id();\n  core_id = core_id % nb_dedicated_cores;\n  uint8_t * pIm2ColBase')

    # 4) If core_id assigned on its own line without following pIm2ColBase immediate, try to insert after the pi_core_id line
    if 'int core_id = pi_core_id();' in s3 and 'core_id = core_id % nb_dedicated_cores;' not in s3:
        s3 = s3.replace('int core_id = pi_core_id();\n', 'int core_id = pi_core_id();\n  core_id = core_id % nb_dedicated_cores;\n')

    if s3 != s:
        p.write_text(s3)
        return True
    return False

changed = []
for f in sorted(TARGET_DIR.glob('*.c')):
    try:
        if process_file(f):
            changed.append(str(f.relative_to(ROOT)))
    except Exception as e:
        print('Error processing', f, e)

if changed:
    print('Modified files:')
    for c in changed:
        print(c)
else:
    print('No files modified.')
