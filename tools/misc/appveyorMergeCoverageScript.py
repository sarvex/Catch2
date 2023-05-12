#!/usr/bin/env python3

import glob
import subprocess

if __name__ == '__main__':
    cov_files = list(glob.glob('tests/cov-report*.bin'))
    base_cmd = [
        'OpenCppCoverage',
        '--quiet',
        '--export_type=cobertura:cobertura.xml',
    ] + [f'--input_coverage={f}' for f in cov_files]
    subprocess.check_call(base_cmd)
