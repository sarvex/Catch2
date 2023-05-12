#!/usr/bin/env python3

#              Copyright Catch2 Authors
# Distributed under the Boost Software License, Version 1.0.
#   (See accompanying file LICENSE.txt or copy at
#        https://www.boost.org/LICENSE_1_0.txt)

# SPDX-License-Identifier: BSL-1.0

from typing import List, Tuple

import os
import subprocess

def configure_and_build(source_path: str, project_path: str, options: List[Tuple[str, str]]):
    base_configure_cmd = [
        'cmake',
        f'-B{project_path}',
        f'-H{source_path}',
        '-DCMAKE_BUILD_TYPE=Debug',
        '-DCATCH_DEVELOPMENT_BUILD=ON',
    ]
    base_configure_cmd.extend(f'-D{option}={value}' for option, value in options)
    try:
        subprocess.run(base_configure_cmd,
                       stdout = subprocess.PIPE,
                       stderr = subprocess.STDOUT,
                       check = True)
    except subprocess.SubprocessError as ex:
        print(f"Could not configure build to '{project_path}' from '{source_path}'")
        print(f"Return code: {ex.returncode}")
        print(f"output: {ex.output}")
        raise
    print(f'Configuring {project_path} finished')

    build_cmd = ['cmake', '--build', f'{project_path}', '--config', 'Debug']
    try:
        subprocess.run(build_cmd,
                       stdout = subprocess.PIPE,
                       stderr = subprocess.STDOUT,
                       check = True)
    except subprocess.SubprocessError as ex:
        print(f"Could not build project in '{project_path}'")
        print(f"Return code: {ex.returncode}")
        print(f"output: {ex.output}")
        raise
    print(f'Building {project_path} finished')

def run_and_return_output(base_path: str, binary_name: str, other_options: List[str]) -> Tuple[str, str]:
    # For now we assume that Windows builds are done using MSBuild under
    # Debug configuration. This means that we need to add "Debug" folder
    # to the path when constructing it. On Linux, we don't add anything.
    config_path = "Debug" if os.name == 'nt' else ""
    full_path = os.path.join(base_path, config_path, binary_name)

    base_cmd = [full_path, *other_options]
    try:
        ret = subprocess.run(base_cmd,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             check = True,
                             universal_newlines = True)
    except subprocess.SubprocessError as ex:
        print(f'Could not run "{base_cmd}"')
        print(f'Args: "{other_options}"')
        print(f'Return code: {ex.returncode}')
        print(f'stdout: {ex.stdout}')
        print(f'stderr: {ex.stdout}')
        raise

    return (ret.stdout, ret.stderr)
