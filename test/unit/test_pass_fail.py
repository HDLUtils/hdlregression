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


def test_pass():
    clear_output()
    hr = HDLRegression()

    filename = '../tb/tb_passing.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'passing_lib')
    hr.set_result_check_string('passing testcase')

    result = hr.start()

    (pass_list, fail_list) = hr.get_results()

    assert result == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 1, "check number of passing tests"


def test_fail():
    clear_output()
    hr = HDLRegression()

    filename = '../tb/tb_failing.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'failing_lib')
    hr.set_result_check_string('passing testcase')
    result = hr.start()

    (pass_list, fail_list) = hr.get_results()

    assert result == 1, "check number of failing tests"
    assert len(fail_list) == 1, "check number of failing tests"
    assert len(pass_list) == 0, "check number of passing tests"
    assert 'failing_lib.tb_failing.test' in '\t'.join(fail_list), "checking failing test"


def test_multiple_pass_one_fail():
    clear_output()
    hr = HDLRegression()

    filename = '../tb/tb_failing.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'regression_lib')

    filename = '../tb/tb_testcase.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'regression_lib')

    hr.set_result_check_string('testcase_arch: testcase')

    result = hr.start()

    (pass_list, fail_list) = hr.get_results()

    assert result == 1, "check number of failing tests"
    assert len(fail_list) == 1, "check number of failing tests"
    assert len(pass_list) == 3, "check number of passing tests"
    assert 'regression_lib.tb_failing.test' in '\t'.join(fail_list), "checking failing test in regression"


def test_multiple_pass_mupltiple_fail():
    clear_output()
    hr = HDLRegression()

    filename = '../tb/tb_failing*.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'regression_lib')

    filename = '../tb/tb_testcase.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'regression_lib')

    hr.set_result_check_string('testcase_arch: testcase')

    result = hr.start()

    (pass_list, fail_list) = hr.get_results()

    assert result == 1, "check number of failing tests"
    assert len(fail_list) == 2, "check number of failing tests"
    assert len(pass_list) == 3, "check number of passing tests"
    assert 'regression_lib.tb_failing.test' in '\t'.join(fail_list), "checking failing test in regression"
    assert 'regression_lib.tb_failing_2.test' in '\t'.join(fail_list), "checking failing test in regression"