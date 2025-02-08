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
        else "NVC" if nvc_installed else "GHDL" if ghdl_installed else ""
    )

    return {
        "platform": platform_info,
        "modelsim": modelsim_installed,
        "ghdl": ghdl_installed,
        "nvc": nvc_installed,
        "simulator": simulator,
    }


def test_add_files_directory(sim_env, uvvm_path):
    """
    Check that directory will add no files, i.e. no filename or wildcard.
    """
    if not is_folder_present(uvvm_path):
        pytest.skip(f"UVVM path '{uvvm_path}' not found, skipping test.")
    else:
        clear_output()
        hr = HDLRegression(simulator=sim_env["simulator"])

        test_path = get_file_path(uvvm_path + "/bitvis_uart/src/")
        hr.add_files(test_path, "bitvis_uart")
        library = hr._get_library_object("bitvis_uart")
        file_list = library.get_hdlfile_list()
        assert len(file_list) == 0, "No files added"


def test_add_files_wildcase(sim_env, tb_path):
    """
    Test adding files using wildcard name.
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    test_files = get_file_path(tb_path + "/my_tb_ent.vhd")
    hr.add_files(test_files, "test_lib")
    test_files = get_file_path(tb_path + "/my_tb_arch_*.vhd")
    hr.add_files(test_files, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    library = hr._get_library_object("test_lib")
    file_list = library.get_hdlfile_list()
    assert len(file_list) == 4, "Check number of files added"


def test_add_files_name(sim_env, tb_path):
    """
    Test adding files using full name.
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    test_files = get_file_path(tb_path + "/my_tb_ent.vhd")
    hr.add_files(test_files, "test_lib")

    test_files = [
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/my_tb_arch_2.vhd",
        tb_path + "/my_tb_arch_3_4.vhd",
    ]

    for test_file in test_files:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    library = hr._get_library_object("test_lib")
    file_list = library.get_hdlfile_list()

    assert len(file_list) == 4, "Check number of files added"

def test_add_file_invalid_file_name(sim_env, tb_path):
    """
    Test adding files using full name.
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    test_files = get_file_path(tb_path + "/my_tb_ent.vhd")
    hr.add_files(test_files, "test_lib")

    test_files = [
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/invalid.vhd",
    ]

    for test_file in test_files:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    library = hr._get_library_object("test_lib")
    file_list = library.get_hdlfile_list()

    assert len(file_list) == 2, "Check number of files added"

def test_add_file_invalid_file_path(sim_env, tb_path):
    """
    Test adding files using full name.
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    test_files = get_file_path(tb_path + "/my_tb_ent.vhd")
    hr.add_files(test_files, "test_lib")

    test_files = [
        tb_path + "/my_tb_arch_1.vhd",
        "../foo/" + "/invalid.vhd",
    ]

    for test_file in test_files:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    library = hr._get_library_object("test_lib")
    file_list = library.get_hdlfile_list()

    assert len(file_list) == 2, "Check number of files added"




def test_readback_file_list_one_library(sim_env, tb_path):
    """
    Test readback of added files
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    test_files = [
        tb_path + "/my_tb_ent.vhd",
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/my_tb_arch_2.vhd",
        tb_path + "/my_tb_arch_3_4.vhd",
    ]

    for test_file in test_files:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    file_list = hr.get_file_list()

    assert len(file_list) == len(test_files), "Check number of files added"

    def get_path_tail(path):
        # Get the real path
        path = os.path.realpath(path)
        # Split the drive or mount point
        drive, tail = os.path.splitdrive(path)
        # Normalize the tail for consistent formatting
        tail = os.path.normcase(os.path.normpath(tail))
        return tail

    for test_file in test_files:
        file_tail = get_path_tail(test_file)
        file_list_tails = [get_path_tail(f) for f in file_list]
        assert file_tail in file_list_tails, "check file present"


def test_readback_file_list_multiple_libraries(sim_env, tb_path):
    """
    Test readback of added files
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    test_files_1 = [
        tb_path + "/my_tb_ent.vhd",
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/my_tb_arch_2.vhd",
        tb_path + "/my_tb_arch_3_4.vhd",
    ]

    for test_file in test_files_1:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib_1")

    test_files_2 = [tb_path + "/tb_passing.vhd", tb_path + "/tb_passing_2.vhd"]

    for test_file in test_files_2:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib_2")

    test_files_3 = [tb_path + "/tb_failing.vhd"]
    test_file = get_file_path(test_files_3[0])
    hr.add_files(test_file, "test_lib_3")

    hr.set_result_check_string(" : sim done")
    hr.start()

    file_list = hr.get_file_list()

    test_files = test_files_1 + test_files_2 + test_files_3

    assert len(file_list) == len(test_files), "Check number of files added"

    def get_normalized_path_tail(path):
        # Resolve the absolute path
        path = Path(path).resolve()
        # Remove the drive or mount point
        tail = path.relative_to(path.anchor)
        # Normalize the path for consistent formatting
        return tail.as_posix().lower()

    for test_file in test_files:
        file_tail = get_normalized_path_tail(test_file)
        file_list_tails = [get_normalized_path_tail(f) for f in file_list]
        assert file_tail in file_list_tails, f"File '{file_tail}' not found in file list"


def test_remove_file(sim_env, tb_path):
    """
    Test readback of added files
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    test_files_1 = [
        tb_path + "/my_tb_ent.vhd",
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/my_tb_arch_2.vhd",
        tb_path + "/my_tb_arch_3_4.vhd",
    ]

    for test_file in test_files_1:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    #remove_file = get_file_path(tb_path + "/my_tb_arch_2.vhd")
    remove_file = "my_tb_arch_2.vhd"
    hr.remove_file(remove_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    file_list = hr.get_file_list()

    assert "my_tb_arch_2.vhd" not in file_list, "Found in list: {}".format(file_list)

def test_remove_file_with_path(sim_env, tb_path):
    """
    Test readback of added files
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    test_files_1 = [
        tb_path + "/my_tb_ent.vhd",
        tb_path + "/my_tb_arch_1.vhd",
        tb_path + "/my_tb_arch_2.vhd",
        tb_path + "/my_tb_arch_3_4.vhd",
    ]

    for test_file in test_files_1:
        test_file = get_file_path(test_file)
        hr.add_files(test_file, "test_lib")

    remove_file = get_file_path(tb_path + "/my_tb_arch_2.vhd")
    hr.remove_file(remove_file, "test_lib")

    hr.set_result_check_string(" : sim done")
    hr.start()

    file_list = hr.get_file_list()

    assert "my_tb_arch_2.vhd" not in file_list, "Found in list: {}".format(file_list)
    
