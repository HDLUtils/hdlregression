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
        print("Output cleared")


def setup_function():
    if os.path.isdir("./hdlregression"):
        print("WARNING! hdlregression folder already exist!")
        clear_output()


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


def test_compile_library(sim_env, tb_path):
    """
    Check that library is compiled to hdlregression/library/
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.set_result_check_string("passing testcase")
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename, "test_lib")

    hr.start()
    dirs = os.listdir("./hdlregression/library")
    assert "test_lib" in dirs, "checking compiled library"


def test_never_recompile_setting(sim_env, tb_path):
    """
    Check that library set to never recompile.
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.configure_library(library="test_lib_never_recompile", never_recompile=True)
    hr.set_result_check_string("passing testcase")
    filename = get_file_path(tb_path + "/tb_passing.vhd")

    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")

    library_never_recompile = hr._get_library_object("test_lib_never_recompile")
    library_recompile = hr._get_library_object("test_lib_compile")
    assert (
        library_never_recompile.get_never_recompile() is True
    ), "Check never recompile update."
    assert (
        library_recompile.get_never_recompile() is False
    ), "Check never recompile default."


def test_never_recompile_library_initial_compilation(sim_env, tb_path):
    """
    Check that library set to never recompile is compiled the first time
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    hr.set_result_check_string("passing testcase")
    filename = get_file_path(tb_path + "/tb_passing.vhd")

    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")

    hr.configure_library(library="test_lib_never_recompile", never_recompile=True)

    hr.start()

    dirs = os.listdir("./hdlregression/library")
    assert "test_lib_never_recompile" in dirs, "checking compiled library"
    assert "tesl_lib_recompile" in dirs, "checking compiled library"


def test_never_recompile_library_compilation(sim_env, tb_path):
    """
    Check that library set to never recompile is compiled the first time
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.set_result_check_string("passing testcase")
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename, "test_lib_never_recompile")
    hr.add_files(filename, "tesl_lib_recompile")
    hr.configure_library(library="test_lib_never_recompile", never_recompile=True)
    hr.start(verbose=True)

    # Touch file to create changes
    Path(filename).touch()
    hr.start()

    compiled_lib_list = hr.settings.get_library_compile()
    lib_name_list = [lib.get_name() for lib in compiled_lib_list]

    assert "test_lib_never_recompile" not in lib_name_list, "Check not recompiled"
    assert "tesl_lib_recompile" in lib_name_list, "Check recompiled"


@pytest.mark.modelsim
def test_precompiled_library_modelsim(sim_env, precompiled_path):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator=sim_env["simulator"])

        lib_name = "pytest_lib"

        hr.add_precompiled_library(compile_path=precompiled_path, library_name=lib_name)
        hr.start()

        modelsim_ini = get_file_path("../hdlregression/library/modelsim.ini")

        assert os.path.isfile(modelsim_ini), "Check modelsim.ini exists"

        precompiled_exists = False
        with open(modelsim_ini, "r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith(lib_name) is True:
                if os.path.realpath(precompiled_path) in line:
                    precompiled_exists = True

        assert (
            precompiled_exists is True
        ), "check precompiled library and path in modelsim.ini"


def test_empty_library_and_library_with_files_no_threads(sim_env, tb_path):
    """
    Check that an empty library is ignored
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.set_result_check_string("passing testcase")

    filename = get_file_path(tb_path + "/no_such_file.foo")
    hr.add_files(filename, "empty_lib")

    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename, "test_lib")

    hr.start(threading=False)
    dirs = os.listdir("./hdlregression/library")
    assert "empty_lib" not in dirs, "checking empty library not in compiled libraries"
    assert "test_lib" in dirs, "checking compiled library in compiled libraries"


def test_library_without_file_and_library_with_file_one_thread(sim_env, tb_path):
    """
    Check that an empty library is ignored
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.set_result_check_string("passing testcase")

    filename = get_file_path(tb_path + "/no_such_file.foo")
    hr.add_files(filename, "empty_lib")

    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename, "test_lib")

    hr.start(threading=True)
    dirs = os.listdir("./hdlregression/library")
    assert "empty_lib" not in dirs, "checking empty library not in compiled libraries"
    assert "test_lib" in dirs, "checking compiled library in compiled libraries"


def test_empty_library(sim_env, tb_path):
    """
    Check that an empty library is ignored
    """
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    hr.set_result_check_string("passing testcase")

    filename = get_file_path(tb_path + "/no_such_file.foo")
    hr.add_files(filename, "empty_lib")

    hr.start()
    dirs = os.listdir("./hdlregression/library")
    assert "empty_lib" not in dirs, "checking empty library not in compiled libraries"


# def test_recursing_library_dependency_detection():
#    '''
#    Check that libraries that depend on each other are detected and reported.
#    '''
#    clear_output()
#    hr = HDLRegression()
#
#    hr.set_result_check_string('testcase done')
#
#    filename = get_file_path('../tb/rec_a.vhd')
#    hr.add_files(filename, "req_lib")
#    filename = get_file_path('../tb/rec_b.vhd')
#    hr.add_files(filename, "req_lib")
#    filename = get_file_path('../tb/rec_c.vhd')
#    hr.add_files(filename, "req_lib")
#
#    res = hr.start()
#
#    assert res == 1, "check recursive dependency detection and report"
