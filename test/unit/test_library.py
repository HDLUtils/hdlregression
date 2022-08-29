# ================================================================================================================================
#  Copyright 2021 Bitvis
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 and in the provided LICENSE.TXT.
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and limitations under the License.
# ================================================================================================================================
#  Note : Any functionality not explicitly described in the documentation is subject to change at any time
# --------------------------------------------------------------------------------------------------------------------------------

import pytest
import sys
import os
import shutil
from pathlib import Path

from hdlregression import HDLRegression
from pickle import FALSE


if len(sys.argv) >= 2:
    '''
    Remove pytest from argument list
    '''
    sys.argv.pop(1)


def get_file_path(path) -> str:
    '''
    Adjust file paths to match running directory.
    '''
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(TEST_DIR, path)


def clear_output():
    if os.path.isdir('./hdlregression'):
        shutil.rmtree('./hdlregression')
        print('Output cleared')


def setup_function():
    if os.path.isdir('./hdlregression'):
        print('WARNING! hdlregression folder already exist!')
        clear_output()


def tear_down_function():
    clear_output()


def test_compile_library():
    '''
    Check that library is compiled to hdlregression/library/
    '''
    clear_output()
    hr = HDLRegression()

    hr.set_result_check_string('passing testcase')
    filename = get_file_path('../tb/tb_passing.vhd')
    hr.add_files(filename, "test_lib")

    hr.start()
    dirs = os.listdir("./hdlregression/library")
    assert "test_lib" in dirs, "checking compiled library"


def test_never_recompile_setting():
    '''
    Check that library set to never recompile.
    '''
    clear_output()
    hr = HDLRegression()

    hr.configure_library(
        library="test_lib_never_recompile", never_recompile=True)
    hr.set_result_check_string('passing testcase')
    filename = get_file_path('../tb/tb_passing.vhd')

    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")

    library_never_recompile = hr._get_library_object(
        'test_lib_never_recompile')
    library_recompile = hr._get_library_object('test_lib_compile')
    assert library_never_recompile.get_never_recompile(
    ) is True, "Check never recompile update."
    assert library_recompile.get_never_recompile(
    ) is False, "Check never recompile default."


def test_never_recompile_library_initial_compilation():
    '''
    Check that library set to never recompile is compiled the first time
    '''
    clear_output()
    hr = HDLRegression()
    hr.set_result_check_string('passing testcase')
    filename = get_file_path('../tb/tb_passing.vhd')

    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")

    hr.configure_library(
        library="test_lib_never_recompile", never_recompile=True)

    hr.start()

    dirs = os.listdir("./hdlregression/library")
    assert "test_lib_never_recompile" in dirs, "checking compiled library"
    assert "tesl_lib_recompile" in dirs, "checking compiled library"


def test_never_recompile_library_compilation():
    '''
    Check that library set to never recompile is compiled the first time
    '''
    clear_output()
    hr = HDLRegression()
    hr.set_result_check_string('passing testcase')
    #filename = get_file_path(os.path.join(TEST_DIR, '../tb/tb_passing.vhd'))
    filename = get_file_path('../tb/tb_passing.vhd')

    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")

    hr.configure_library(
        library="test_lib_never_recompile", never_recompile=True)

    hr.start(verbose=True)

    # Touch file to create changes
    Path(filename).touch()

    hr.start()
    compiled_lib_list = hr.settings.get_library_compile()

    lib_name_list = [lib.get_name() for lib in compiled_lib_list]

    assert "test_lib_never_recompile" not in lib_name_list, "Check not recompiled"
    assert "tesl_lib_recompile" in lib_name_list, "Check recompiled"


def test_precompiled_library():
    clear_output()
    hr = HDLRegression()

    lib_name = "pytest_lib"
    compile_path = "../precompiled_path"

    hr.add_precompiled_library(compile_path=compile_path, library_name=lib_name)
    hr.start()

    lib = hr._get_library_object(library_name=lib_name)

    modelsim_ini = './hdlregression/library/modelsim.ini'

    assert os.path.isfile(modelsim_ini), "Check modelsim.ini exists"

    precompiled_exists = False
    with open(modelsim_ini, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith(lib_name) is True:
            if compile_path in line:
                precompiled_exists = True

    assert precompiled_exists is True, "check precompiled library and path in modelsim.ini"
