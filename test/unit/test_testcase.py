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


def test_testcase():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 3, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_testcase_select():
    clear_output()
    hr = HDLRegression()

    hr.add_testcase("testbench_test.architecture_test.testcase_test")

    testcase = hr.settings.get_testcase()

    # Testcase is stored as list [testbench, architecture, test]
    testcase = ".".join(testcase)

    assert (
        testcase == "testbench_test.architecture_test.testcase_test"
    ), "checking add_testcase()"


def test_testcase_with_whitespace():
    clear_output()
    hr = HDLRegression()

    hr.add_testcase("testbench_test.architecture_test.testcase_test ")

    testcase = hr.settings.get_testcase()

    # Testcase is stored as list [testbench, architecture, test]
    testcase = ".".join(testcase)

    assert (
        testcase == "testbench_test.architecture_test.testcase_test"
    ), "checking add_testcase()"


def test_testcase_with_tabulator():
    clear_output()
    hr = HDLRegression()

    hr.add_testcase("testbench_test.architecture_test.testcase_test ")

    testcase = hr.settings.get_testcase()

    # Testcase is stored as list [testbench, architecture, test]
    testcase = ".".join(testcase)

    assert (
        testcase == "testbench_test.architecture_test.testcase_test"
    ), "checking add_testcase()"


def test_one_testcase_selected():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    hr.add_testcase("tb_testcase.testcase_arch.testcase_1")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 1, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_two_testcases_selected():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 2 expected to be run
    hr.add_testcase("tb_testcase.testcase_arch.testcase_1")
    hr.add_testcase("tb_testcase.testcase_arch.testcase_2")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 2, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_list_of_testcases():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 2 expected to be run
    testcase_list = [
        "tb_testcase.testcase_arch.testcase_1",
        "tb_testcase.testcase_arch.testcase_2",
    ]
    hr.add_testcase(testcase_list)

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 2, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_unsupported_type():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Add invalid testcase type
    hr.add_testcase(True)

    assert hr.settings.get_testcase() == None, "check unsupported testcase type"


def test_correct_number_of_testcases():
    clear_output()

    hr = HDLRegression()

    filename = "../tb/tb_passing.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "test_lib")
    hr.set_result_check_string("passing testcase")
    hr.start()

    tests = hr.runner.testbuilder.get_list_of_tests_to_run()

    assert len(tests) == 1, "checking number of testcases"


def test_list_testcases():
    from hdlregression.hdlregression_pkg import list_testcases

    clear_output()

    hr = HDLRegression()

    filename = "../tb/tb_passing.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "test_lib")
    hr.set_result_check_string("passing testcase")
    hr.start()

    tc_list = list_testcases(hr.runner)

    assert tc_list.strip() == "TC:1 - tb_passing.test", "checking list testcases"


def test_wildcard_asterix_testcases():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 3 expected to be run
    hr.add_testcase("tb_testcase.testcase_arch.testcase_*")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 3, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"

    exp_test = "testcase_lib.tb_testcase.testcase_arch.testcase_"
    for idx in range(1, 3):
        testcase = exp_test + str(idx)
        assert testcase in "".join(pass_list)


def test_wildcard_question_mark_testcases():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 1 expected to be run
    hr.add_testcase("tb_testcase.testcase_arch.test????_2")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 1, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"
    assert (
        pass_list[0] == "testcase_lib.tb_testcase.testcase_arch.testcase_2 (test_id: 2)"
    )


def test_wildcard_not_found_testcases():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 1 expected to be run
    hr.add_testcase("tb_testcase.testcase_arch.testcase_*_")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 1, "check return code for not found testcase"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 0, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_wildcard_asterix_architecture_and_testcase():
    clear_output()
    hr = HDLRegression()

    filename = "../tb/tb_testcase.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("testcase_arch: testcase")

    # Testcase 3 expected to be run
    hr.add_testcase("tb_testcase.testcase_*.testcase_*")

    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 3, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"

    exp_test = "testcase_lib.tb_testcase.testcase_arch.testcase_"
    for idx in range(1, 3):
        testcase = exp_test + str(idx)
        assert testcase in "".join(pass_list)


def test_passing_testcase_failing_in_second_run():
    clear_output()

    # First run
    hr = HDLRegression()
    filename = "../tb/tb_passing.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("passing testcase")
    return_code = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 1, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"

    # Second 
    hr = HDLRegression()
    hr.set_result_check_string("failing_testcase")
    return_code = hr.start(regression_mode=True)

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert return_code == 1, "check number of failing tests"
    assert len(fail_list) == 1, "check number of failing tests"
    assert len(pass_list) == 0, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"    