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


def test_set_code_coverage(sim_env):
    """
    Check that code coverage settings are set
    """
    clear_output()
    hr = HDLRegression()

    hr.set_code_coverage(
        code_coverage_settings="bcestx",
        code_coverage_file="no_file.ucdb",
        merge_options="some_option",
    )

    assert (
        hr.hdlcodecoverage.get_code_coverage_settings() == "bcestx"
    ), "check code coverage settings"
    assert hr.hdlcodecoverage.get_options() == "some_option", "check merge options"


def test_remove_leading_hyphen(sim_env):
    """
    Check that code coverage settings are set
    """
    clear_output()
    hr = HDLRegression()

    hr.set_code_coverage(
        code_coverage_settings="-bcestx", code_coverage_file="no_file.ucdb"
    )

    assert (
        hr.hdlcodecoverage.get_code_coverage_settings() == "bcestx"
    ), "check code coverage settings removed hyphen"


def test_illegal_character(sim_env, capsys):
    """
    Check that code coverage settings are set
    """
    clear_output()
    hr = HDLRegression()

    coverage_settings = "bcuestx"
    hr.set_code_coverage(
        code_coverage_settings=coverage_settings, code_coverage_file="no_file.ucdb"
    )
    hr.start()
    
    # Capture the output from stdout and stderr
    captured = capsys.readouterr()

    # Assuming the error message is printed to stderr
    assert "Invalid coverage settings in: bcuestx" in captured.out    
    
    assert (
        hr.hdlcodecoverage.get_code_coverage_settings() is coverage_settings
    ), "check code coverage settings not set"


def test_minimal_code_coverage_settings(sim_env):
    """
    Check that code coverage settings are set
    """
    clear_output()
    hr = HDLRegression()

    hr.set_code_coverage(
        code_coverage_settings="teb", code_coverage_file="no_file.ucdb"
    )

    assert (
        hr.hdlcodecoverage.get_code_coverage_settings() == "teb"
    ), "check code coverage setting"
