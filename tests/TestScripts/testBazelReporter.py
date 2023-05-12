#!/usr/bin/env python3

#              Copyright Catch2 Authors
# Distributed under the Boost Software License, Version 1.0.
#   (See accompanying file LICENSE.txt or copy at
#        https://www.boost.org/LICENSE_1_0.txt)

# SPDX-License-Identifier: BSL-1.0

import os
import re
import sys
import xml.etree.ElementTree as ET
import subprocess

"""
Test that Catch2 recognizes `XML_OUTPUT_FILE` env variable and creates
a junit reporter that writes to the provided path.

Requires 2 arguments, path to Catch2 binary configured with
`CATCH_CONFIG_BAZEL_SUPPORT`, and the output directory for the output file.
"""
if len(sys.argv) != 3:
    print(f"Wrong number of arguments: {len(sys.argv)}")
    print(f"Usage: {sys.argv[0]} test-bin-path output-dir")
    exit(1)


bin_path = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
xml_out_path = os.path.join(output_dir, f'{os.path.basename(bin_path)}.xml')

# Ensure no file exists from previous test runs
if os.path.isfile(xml_out_path):
    os.remove(xml_out_path)

print('bin path:', bin_path)
print('xml out path:', xml_out_path)

env = os.environ.copy()
env["XML_OUTPUT_FILE"] = xml_out_path
test_passing = True

try:
    ret = subprocess.run(
        bin_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        universal_newlines=True,
        env=env
    )
    stdout = ret.stdout
except subprocess.SubprocessError as ex:
    if ex.returncode == 1:
        # The test cases are allowed to fail.
        test_passing = False
        stdout = ex.stdout
    else:
        print(f'Could not run "{bin_path}"')
        print(f"Return code: {ex.returncode}")
        print(f"stdout: {ex.stdout}")
        print(f"stderr: {ex.stderr}")
        raise

# Check for valid XML output
try:
    tree = ET.parse(xml_out_path)
except ET.ParseError as ex:
    print(f"Invalid XML: '{ex}'")
    raise
except FileNotFoundError as ex:
    print(f"Could not find '{xml_out_path}'")
    raise

bin_name = os.path.basename(bin_path)
# Check for matching testsuite
if not tree.find(f'.//testsuite[@name="{bin_name}"]'):
    print(f"Could not find '{bin_name}' testsuite")
    exit(2)

# Check that we haven't disabled the default reporter
summary_test_cases = re.findall(r'test cases: \d* \| \d* passed \| \d* failed', stdout)
if len(summary_test_cases) == 0:
    print(f"Could not find test summary in {stdout}")
    exit(2)

total, passed, failed = [int(s) for s in summary_test_cases[0].split() if s.isdigit()]

if failed == 0 and not test_passing:
    print("Expected at least 1 test failure!")
    exit(2)

if len(tree.findall('.//testcase')) != total:
    print("Unexpected number of test cases!")
    exit(2)

if len(tree.findall('.//failure')) != failed:
    print("Unexpected number of test failures!")
    exit(2)

if (passed + failed) != total:
    print(f"Something has gone very wrong, ({passed} + {failed}) != {total}")
    exit(2)
