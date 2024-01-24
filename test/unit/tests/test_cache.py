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
import glob

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
    clear_output()


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


def test_clean(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(sim_env["simulator"])
    input_file = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(input_file)
    hr.set_result_check_string("passing testcase")
    hr.start()

    hr = HDLRegression(sim_env["simulator"])
    hr.settings.set_clean(True)
    hr._rebuild_databases_if_required_or_requested(True)

    test_folder = get_file_path("../hdlregression/test/*")
    test_folder = glob.glob(test_folder)
    assert len(test_folder) == 0, "Check cleaning tests"

    lib_folder = get_file_path("../hdlregression/library/*")
    lib_folder = glob.glob(lib_folder)
    assert len(lib_folder) == 0, "Check cleaning library compile"

    hr_folder = get_file_path("../hdlregression/*")
    hr_folder = glob.glob(hr_folder)
    assert len(hr_folder) == 2, "Check cleaning hdlregression folder"

    test_folder = any(folder for folder in hr_folder)
    lib_folder = any(folder for folder in hr_folder)
    assert test_folder is True, "Checking empty test folder present"
    assert lib_folder is True, "Checking empty library folder present"


def test_initial_simulator_setting(sim_env, tb_path):
    simulator = sim_env["simulator"]
    clear_output()
    hr = HDLRegression()
    input_file = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(input_file)
    hr.set_result_check_string("passing testcase")
    hr.start()

    discovered_files = glob.glob("./**/hdlregression/library/*", recursive=True)
    filenames = [os.path.basename(filename).lower() for filename in discovered_files]

    assert (
        hr.settings.get_simulator_name() == simulator
    ), "checking initial simulator setting"
    if simulator == "MODELSIM":
        assert "modelsim.ini" in filenames, "check modelsim.ini exsist"


@pytest.mark.modelsim
def test_set_simulator_modelsim(sim_env, tb_path):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression()
        hr.set_simulator("modelsim")
        input_file = get_file_path(tb_path + "/tb_passing.vhd")
        hr.add_files(input_file, "library_2")
        hr.set_result_check_string("passing testcase")

        hr.start()
        num_tests = hr.get_num_pass_tests() + hr.get_num_fail_tests()

        discovered_files = glob.glob("./**/hdlregression/library/*", recursive=True)
        filenames = [
            os.path.basename(filename).lower() for filename in discovered_files
        ]

        sim_name = hr.settings.get_simulator_name()
        assert sim_name == "MODELSIM", "checking initial simulator setting"
        assert num_tests == 1, "check number of tests"
        assert (
            "modelsim.ini" in filenames
        ), "check Modelsim simulator used in test suite"


@pytest.mark.ghdl
def test_set_simulator_ghdl(sim_env, tb_path):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression()
        hr.set_simulator("ghdl")
        input_file = get_file_path(tb_path + "/tb_passing.vhd")
        hr.add_files(input_file, "library_2")
        hr.set_result_check_string("passing testcase")

        hr.start()
        num_tests = hr.get_num_pass_tests() + hr.get_num_fail_tests()

        discovered_files = glob.glob("./**/hdlregression/library/*", recursive=True)
        filenames = [
            os.path.basename(filename).lower() for filename in discovered_files
        ]

        sim_name = hr.settings.get_simulator_name()
        assert sim_name == "GHDL", "checking initial simulator setting"
        assert num_tests == 1, "check number of tests"
        assert (
            "modelsim.ini" not in filenames
        ), "check GHDL simulator used in test suite"


@pytest.mark.nvc
def test_set_simulator_nvc(sim_env, tb_path):
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression()
        hr.set_simulator("nvc")
        input_file = get_file_path(tb_path + "/tb_passing.vhd")
        hr.add_files(input_file, "library_2")
        hr.set_result_check_string("passing testcase")

        hr.start()
        num_tests = hr.get_num_pass_tests() + hr.get_num_fail_tests()

        discovered_files = glob.glob("./**/hdlregression/library/*", recursive=True)
        filenames = [
            os.path.basename(filename).lower() for filename in discovered_files
        ]

        sim_name = hr.settings.get_simulator_name()
        assert sim_name == "NVC", "checking initial simulator setting"
        assert num_tests == 1, "check number of tests"
        assert "modelsim.ini" not in filenames, "check NVC simulator used in test suite"
