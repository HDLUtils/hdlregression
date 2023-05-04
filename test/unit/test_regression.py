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


if len(sys.argv) >= 2:
    """
    Remove pytest from argument list
    """
    sys.argv.pop(1)


def get_file_path(path) -> str:
    """
    Adjust file paths to match running directory.
    """
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(TEST_DIR, path)


def clear_output():
    if os.path.isdir("./hdlregression"):
        shutil.rmtree("./hdlregression")


def setup_function():
    if os.path.isdir("./hdlregression"):
        print("WARNING! hdlregression folder already exist!")


def tear_down_function():
    if os.path.isdir("./hdlregression"):
        shutil.rmtree("./hdlregression")


def test_full_regression():
    """
    Check that all tests are run the first time.
    """
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    result = hr.start(full_regression=True)
    assert result == 0, "Checking return code 0 - OK"

    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 3, "check 3 tests are run"


def test_full_regression_run_two_no_file_changes():
    """
    Check that all tests are run the first time,
    and no tests are run the second time (no file changes)
    """
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Run 1
    result = hr.start(full_regression=True)
    assert result == 0, "Checking return code 0 - OK"
    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 3, "check 3 tests are run"

    # Run 2
    result = hr.start(full_regression=True)
    assert result == 1, "Checking return code 1 - OK"
    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 0, "check 0 tests are run"


def test_full_regression_run_three_with_file_changes():
    """
    Check that all tests are run the first time,
    and no tests are run the second time (no file changes)
    """
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Run 1
    result = hr.start(full_regression=True)
    assert result == 0, "Checking return code 0 - OK"
    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 3, "check 3 tests are run"

    # Run 2
    hr.start(full_regression=True)
    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 0, "check 0 tests are run"

    # Touch file to create changes
    Path(filename).touch()

    # Run 3
    hr.start(full_regression=True)
    num_test_runs = hr.get_num_tests_run()
    assert num_test_runs == 3, "check 3 tests are run"
