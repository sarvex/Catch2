#!/usr/bin/env python3

import sys
import glob

correct_licence = """\

//              Copyright Catch2 Authors
// Distributed under the Boost Software License, Version 1.0.
//   (See accompanying file LICENSE.txt or copy at
//        https://www.boost.org/LICENSE_1_0.txt)

// SPDX-License-Identifier: BSL-1.0
"""

def check_licence_in_file(filename: str) -> bool:
    with open(filename, 'r') as f:
        file_preamble = ''.join(f.readlines()[:7])

    if correct_licence != file_preamble:
        print(f'File {filename} does not have proper licence')
        return False
    return True

def check_licences_in_path(path: str) -> int:
    files_to_check = glob.glob(f'{path}/**/*.cpp', recursive=True) + glob.glob(
        f'{path}/**/*.hpp', recursive=True
    )
    return sum(1 for file in files_to_check if not check_licence_in_file(file))

def check_licences():
    roots = ['src/catch2', 'tests']
    if failed := sum(check_licences_in_path(root) for root in roots):
        print(f'{failed} files are missing licence')
        sys.exit(1)

if __name__ == "__main__":
    check_licences()
