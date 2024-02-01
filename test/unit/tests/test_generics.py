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
import platform
import shutil
import subprocess

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


def is_simulator_installed(simulator):
    version = "-version" if simulator == "vsim" else "--version"
    try:
        subprocess.run([simulator, version], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_folder_present(folder_path):
    return os.path.isdir(folder_path)


@pytest.fixture(scope="session")
def sim_env():
    # Detect platform and simulators
    platform_info = platform.system()
    modelsim_installed = is_simulator_installed("vsim")
    ghdl_installed = is_simulator_installed("ghdl")
    nvc_installed = is_simulator_installed("nvc")
    simulator = (
        "MODELSIM"
        if modelsim_installed
        else "NVC"
        if nvc_installed
        else "GHDL"
        if ghdl_installed
        else ""
    )

    return {
        "platform": platform_info,
        "modelsim": modelsim_installed,
        "ghdl": ghdl_installed,
        "nvc": nvc_installed,
        "simulator": simulator,
    }


def test_default_generic_values(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = tb_path + "/tb_generics.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("PASS")

    result = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert result == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests, expecting 0 testcases"
    assert (
        len(pass_list) == 2
    ), "check number of passing tests, expecting 2 sequencer testcases"
    assert len(not_run_list) == 0, "check number of not run tests, exp 0"


def test_configuring_one_set_of_generics(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = tb_path + "/tb_generics.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("PASS")

    hr.add_generics(
        entity="tb_generics",
        generics=["GC_GENERIC_1", 10, "GC_GENERIC_2", 20, "GC_TESTCASE", "testcase_1"],
    )

    result = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert result == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 1, "check number of passing tests: %s" % (pass_list)
    assert len(not_run_list) == 0, "check number of not run tests"


def test_configuring_two_set_of_generics(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = tb_path + "/tb_generics.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("PASS")

    hr.add_generics(
        entity="tb_generics",
        generics=["GC_GENERIC_1", 11, "GC_GENERIC_2", 22, "GC_TESTCASE", "testcase_1"],
    )

    hr.add_generics(
        entity="tb_generics",
        generics=["GC_GENERIC_1", 33, "GC_GENERIC_2", 44, "GC_TESTCASE", "testcase_2"],
    )

    result = hr.start()

    (pass_list, fail_list, not_run_list) = hr.get_results()

    assert result == 0, "check number of failing tests"
    assert len(fail_list) == 0, "check number of failing tests"
    assert len(pass_list) == 2, "check number of passing tests"
    assert len(not_run_list) == 0, "check number of not run tests"


def test_path_generics(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = tb_path + "/tb_generics.vhd"
    filename = get_file_path(filename)
    hr.add_files(filename, "testcase_lib")
    hr.set_result_check_string("PASS")

    hr.add_generics(
        entity="tb_generics", generics=["GC_PATH", ("../script/test_path", "PATH")]
    )
    hr.start()

    simulated_tests = hr.runner.get_test_list()
    assert len(simulated_tests) == 2, "check number of tests"

    run_test_path = simulated_tests[0].get_gc_str().replace("//", "/")
    assert "../script/test_path" in run_test_path, "checking generic path"
