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


if os.path.isdir("./hdlregression"):
    print("WARNING! hdlregression folder already exist!")

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


def get_folders(base_folder):
    matches = Path().glob(base_folder)

    # Convert from WindowsPath() with str()
    return [str(item) for item in matches]


def test_test_folder():
    clear_output()
    hr = HDLRegression()
    test_files = get_file_path("../tb/tb_passing.vhd")
    hr.add_files(test_files, "test_lib")
    hr.set_result_check_string("passing testcase")

    hr.start()

    test_dirs = get_folders("./hdlregression/test/*")
    found = any("tb_passing" in dir for dir in test_dirs)

    assert found is True, "checking test folder %s" % (test_dirs)


def test_new_test_file_added_in_2nd_run():
    clear_output()
    hr = HDLRegression()

    # 1st run, one file
    hr.add_files(get_file_path("../tb/tb_passing.vhd"), "test_lib")
    hr.set_result_check_string("passing testcase")
    hr.start()

    # 2nd run, new file - old file no longer part of run
    hr = HDLRegression()
    hr.add_files(get_file_path("../tb/tb_new_passing.vhd"), "test_lib_2")
    hr.set_result_check_string("passing testcase")
    hr.start()

    test_dirs = get_folders("./hdlregression/test/*")
    found_old = any("tb_passing" in dir for dir in test_dirs)
    found_new = any("tb_new_passing" in dir for dir in test_dirs)

    assert found_old is True, "checking test folder with old test %s" % (test_dirs)
    assert found_new is True, "checking test folder with new test %s" % (test_dirs)


def test_old_test_run_in_test_backup():
    clear_output()
    hr = HDLRegression()
    test_files = get_file_path("../tb/tb_passing.vhd")
    hr.add_files(test_files, "test_lib")
    hr.set_result_check_string("passing testcase")

    # 1st run
    hr.start()

    # 2nd run
    hr.add_files(get_file_path("../tb/tb_passing_2.vhd"), "test_lib")
    hr.start()

    backup_dirs = get_folders("hdlregression/test_*/*")
    found = any("tb_passing" in dir for dir in backup_dirs)

    assert found is True, "checking old test run in backup folder %s" % (backup_dirs)


def test_new_test_run_not_in_test_backup():
    clear_output()
    hr = HDLRegression()
    test_files = get_file_path("../tb/tb_passing.vhd")
    hr.add_files(test_files, "test_lib")
    hr.set_result_check_string("passing testcase")

    # 1st run
    hr.start()
    # 2nd run
    hr.add_files(get_file_path("../tb/tb_passing_2.vhd"), "test_lib")
    hr.start()

    backup_dirs = get_folders("hdlregression/test_*/*")
    found = any("tb_simple_passing" in dir for dir in backup_dirs)

    assert found is False, "checking new test run not in backup folder %s" % (
        backup_dirs
    )


def test_keep_code_coverage_preserves_test_results():
    clear_output()
    hr = HDLRegression()
    test_files = get_file_path("../tb/tb_passing.vhd")
    hr.add_files(test_files, "test_lib")
    hr.set_result_check_string("passing testcase")

    # 1st run
    hr.start()

    # 2nd run
    hr = HDLRegression()
    hr.add_files(get_file_path("../tb/tb_passing_2.vhd"), "test_lib_2")
    hr.set_result_check_string("passing testcase")
    hr.start(keep_code_coverage=True)

    test_dirs = get_folders("./hdlregression/test/*")
    found = any("tb_passing" in dir for dir in test_dirs)

    assert (
        found is True
    ), "checking keep_code_coverage for test folder with old test %s" % (test_dirs)
