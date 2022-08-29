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

from hdlregression import HDLRegression


if os.path.isdir('./hdlregression'):
    print('WARNING! hdlregression folder already exist!')

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


def setup_function():
    if os.path.isdir('./hdlregression'):
        print('WARNING! hdlregression folder already exist!')


def tear_down_function():
    if os.path.isdir('./hdlregression'):
        shutil.rmtree('./hdlregression')


def test_return_code_0_from_passing_library_compile():
    '''
    Check return code from passing library compile
    '''
    clear_output()
    hdlregression = HDLRegression()

    test_files = get_file_path('../tb/tb_passing.vhd')
    hdlregression.add_files(test_files, 'passing_library')
    hdlregression.set_result_check_string('passing testcase')

    return_code = hdlregression.start()

    assert return_code == 0, "Checking return code 0 from failing library compilation"
    assert hdlregression.get_num_pass_tests() == 1, "Checking test has been run and passed"


def test_return_code_1_from_failing_library_compile():
    '''
    Check return code from failing library compile
    '''
    clear_output()
    hdlregression = HDLRegression()

    test_files = get_file_path('../tb/tb_compile_error.vhd')
    hdlregression.add_files(test_files, 'failing_library')
    hdlregression.set_result_check_string('failing compilation')

    return_code = hdlregression.start()

    assert return_code == 1, "Checking return code 1 from failing library compilation"
    assert hdlregression.get_num_tests_run() == 0, "Checking no test has been run"
