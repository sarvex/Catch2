#!/usr/bin/env python3

#              Copyright Catch2 Authors
# Distributed under the Boost Software License, Version 1.0.
#   (See accompanying file LICENSE.txt or copy at
#        https://www.boost.org/LICENSE_1_0.txt)

# SPDX-License-Identifier: BSL-1.0

import os
import re
import sys
import subprocess

"""
Test that Catch2 recognizes the three sharding-related environment variables
and responds accordingly (running only the selected shard, creating the
response file, etc).

Requires 2 arguments, path to Catch2 binary to run and the output directory
for the output file.
"""
if len(sys.argv) != 3:
    print(f"Wrong number of arguments: {len(sys.argv)}")
    print(f"Usage: {sys.argv[0]} test-bin-path output-dir")
    exit(1)


bin_path = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
info_file_path = os.path.join(
    output_dir, f'{os.path.basename(bin_path)}.shard-support'
)

# Ensure no file exists from previous test runs
if os.path.isfile(info_file_path):
    os.remove(info_file_path)

print('bin path:', bin_path)
print('shard confirmation path:', info_file_path)

env = os.environ.copy()
# We will run only one shard, and it should have the passing test.
# This simplifies our work a bit, and if we have any regression in this
# functionality we can make more complex tests later.
env["BAZEL_TEST"] = "1"
env["TEST_SHARD_INDEX"] = "0"
env["TEST_TOTAL_SHARDS"] = "2"
env["TEST_SHARD_STATUS_FILE"] = info_file_path


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
    print(f'Could not run "{bin_path}"')
    print(f"Return code: {ex.returncode}")
    print(f"stdout: {ex.stdout}")
    print(f"stderr: {ex.stderr}")
    raise


if "All tests passed (1 assertion in 1 test case)" not in stdout:
    print("Did not find expected output in stdout.")
    print(f"stdout:\n{stdout}")
    exit(1)

if not os.path.isfile(info_file_path):
    print(f"Catch2 did not create expected file at path '{info_file_path}'")
    exit(2)
