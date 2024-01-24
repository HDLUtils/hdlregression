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

import sys
import os
import platform
import shutil
import pytest
import subprocess

from hdlregression.construct.hdlfile import HDLFile
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


def test_test_run_ok(sim_env, design_path, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    filename = get_file_path(design_path + "../design/dut_adder.vhd")
    hr.add_files(filename, "adder_lib")

    filename = get_file_path(tb_path + "/dut_adder_tb.vhd")
    hr.add_files(filename, "adder_lib")

    hr.set_result_check_string("passing testcase")
    rc = hr.start()

    assert rc == 0, "check return code: test run OK"


def test_no_test_run(sim_env, design_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    filename = get_file_path(design_path + "/dut_adder.vhd")
    hr.add_files(filename, "adder_lib")

    hr.set_result_check_string("passing testcase")
    rc = hr.start()

    assert rc == 1, "check return code: no tests run"


def test_compile_error(sim_env, design_path, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    filename = get_file_path(design_path + "/dut_adder_compile_error.vhd")
    hr.add_files(filename, "adder_lib")

    filename = get_file_path(tb_path + "/dut_adder_tb.vhd")
    hr.add_files(filename, "adder_lib")

    hr.set_result_check_string("passing testcase")
    rc = hr.start()

    assert rc == 1, "check return code: compile error"
