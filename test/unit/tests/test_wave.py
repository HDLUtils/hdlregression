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
import fnmatch
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

# 
# @pytest.mark.ghdl
# def test_set_wave_file_vcd_ghdl(sim_env, tb_path):
#     if not sim_env["ghdl"]:
#         pytest.skip("GHDL not installed")
#     else:
#         clear_output()
#         hr = HDLRegression(simulator="GHDL")
# 
#         filename = tb_path + "/tb_passing.vhd"
#         filename = get_file_path(filename)
#         hr.add_files(filename, "test_lib")
#         hr.set_result_check_string("passing testcase")
# 
#         hr.set_simulator_wave_file_format("VCD")
# 
#         result = hr.start(
#             sim_options="--wave=wave_file.tst --vcd=vcd_file.tst", gui=True
#         )
# 
#         matches = []
#         for root, dirnames, filenames in os.walk("./hdlregression/test/"):
#             for filename in fnmatch.filter(filenames, "*_file.tst"):
#                 matches.append(os.path.join(root, filename))
# 
#         assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
#         assert result == 0, "check return code"

@pytest.mark.ghdl
def test_set_wave_file_ghw_ghdl(sim_env, tb_path):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="GHDL")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        hr.set_simulator_wave_file_format("GHW")

        result = hr.start(sim_options="--wave=wave_file.tst", gui=True)

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "wave_file.tst"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 1, "checking sim_options for wave/vcd_file.tst exists."
        assert result == 0, "check return code"

# 
# 
# @pytest.mark.nvc
# def test_set_sim_options_nvc(sim_env, tb_path):
#     if not sim_env["nvc"]:
#         pytest.skip("NVC not installed")
#     else:
#         clear_output()
#         hr = HDLRegression(simulator="NVC")
# 
#         filename = tb_path + "/tb_passing.vhd"
#         filename = get_file_path(filename)
#         hr.add_files(filename, "test_lib")
#         hr.set_result_check_string("passing testcase")
# 
#         result = hr.start(
#             sim_options=["--wave=wave_file.vcd", "--gtk=gtk_file.vcd"], gui=True
#         )
# 
#         matches = []
#         for root, dirnames, filenames in os.walk("./hdlregression/test/"):
#             for filename in fnmatch.filter(filenames, "*_file.vcd"):
#                 matches.append(os.path.join(root, filename))
# 
#         assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
#         assert result == 0, "check return code"
