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


def has_display() -> bool:
    """CI runs pytest in headless Linux Docker containers with no display,
    where `vsim -gui` would fail outright even though vsim itself is
    installed. Skip there; assume a display on Windows dev machines."""
    if platform.system() == "Windows":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


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


@pytest.mark.modelsim
def test_set_simulator_modelsim(sim_env):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression()
        simulator = hr.settings.get_simulator_name()
        assert simulator == "MODELSIM", "Checking default simulator"


@pytest.mark.ghdl
def test_set_simulator_ghdl(sim_env):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="GHDL")
        simulator = hr.settings.get_simulator_name()
        assert simulator == "GHDL", "Checking updated simulator"


@pytest.mark.nvc
def test_set_simulator_nvc(sim_env):
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="NVC")
        simulator = hr.settings.get_simulator_name()
        assert simulator == "NVC", "Checking updated simulator"


@pytest.mark.modelsim
def test_set_sim_options_list_modelsim(sim_env, tb_path):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="MODELSIM")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(sim_options=["-t ps", "-l hr.log"])

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "hr.log"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 1, "checking sim_options for hr.log exists."
        assert result == 0, "check return code"


@pytest.mark.modelsim
def test_set_sim_options_string_modelsim(sim_env, tb_path):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="MODELSIM")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(sim_options="-t ps -l hr.log")

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "hr.log"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 1, "checking sim_options for hr.log exists."
        assert result == 0, "check return code"


@pytest.mark.ghdl
def test_set_sim_options_list_ghdl(sim_env, tb_path):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="GHDL")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(
            sim_options=["--wave=wave_file.tst", "--vcd=vcd_file.tst"], gui=True
        )

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "*_file.tst"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
        assert result == 0, "check return code"


@pytest.mark.ghdl
def test_set_sim_options_string_ghdl(sim_env, tb_path):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="GHDL")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(
            sim_options="--wave=wave_file.tst --vcd=vcd_file.tst", gui=True
        )

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "*_file.tst"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
        assert result == 0, "check return code"


@pytest.mark.modelsim
def test_gui_mode_launches_vsim_with_sim_path_as_cwd(sim_env, tb_path, tmp_path, monkeypatch):
    """
    Regression test for the tcl_runner.py GUI-mode cwd fix: vsim's -gui
    process must be launched with sim_path (the parent of the hdlregression
    output folder) as its OS working directory, not whatever the live
    Python process's cwd happens to be at that moment.
    """
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    if not has_display():
        pytest.skip("No display available for vsim -gui")

    clear_output()
    hr = HDLRegression(simulator="MODELSIM")

    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename, "test_lib")
    hr.set_result_check_string("passing testcase")

    import hdlregression.run.tcl_runner as tcl_runner_mod

    pwd_marker = tmp_path / "vsim_pwd.txt"
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    original_init = tcl_runner_mod.TclRunnerModelsim._init
    original_load_simulator = tcl_runner_mod.TclRunnerModelsim._load_simulator

    def auto_quit_init(self, test=None):
        # Have vsim report its own cwd via Tcl's `pwd`, then quit itself
        # immediately instead of blocking on the interactive console.
        txt = original_init(self, test)
        txt += """
set fh [open {%s} w]
puts $fh [pwd]
close $fh
quit -code 0
""" % str(pwd_marker).replace("\\", "/")
        return txt

    def load_simulator_from_elsewhere(self, test):
        # Simulate the live process cwd having drifted away from sim_path by
        # the time the GUI is launched -- exactly the scenario the fix
        # addresses. Compilation already happened (using absolute paths), so
        # this only affects the gui_run() call inside _load_simulator. Restore
        # the cwd again right after, since later steps in start() (e.g.
        # saving project state) also resolve relative to the live cwd.
        real_cwd = os.getcwd()
        monkeypatch.chdir(str(elsewhere))
        try:
            return original_load_simulator(self, test)
        finally:
            monkeypatch.chdir(real_cwd)

    monkeypatch.setattr(tcl_runner_mod.TclRunnerModelsim, "_init", auto_quit_init)
    monkeypatch.setattr(
        tcl_runner_mod.TclRunnerModelsim, "_load_simulator", load_simulator_from_elsewhere
    )

    # GUI mode never runs a test itself, so start() always returns 1 here
    # regardless of whether the GUI launched correctly -- not asserted on.
    hr.start(gui_mode=True)

    assert pwd_marker.exists(), "vsim did not report back its working directory"
    vsim_cwd = pwd_marker.read_text().strip()

    expected_lab_dir = os.path.dirname(
        os.path.join(hr.settings.get_sim_path(), hr.settings.get_output_path())
    )
    assert os.path.normpath(vsim_cwd) == os.path.normpath(expected_lab_dir)
    assert os.path.normpath(vsim_cwd) != os.path.normpath(str(elsewhere))


@pytest.mark.nvc
def test_set_sim_options_list_nvc(sim_env, tb_path):
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="NVC")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(
            sim_options=["--wave=wave_file.vcd", "--gtk=gtk_file.vcd"], gui=True
        )

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "*_file.vcd"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
        assert result == 0, "check return code"


@pytest.mark.nvc
def test_set_sim_options_string_nvc(sim_env, tb_path):
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="NVC")

        filename = tb_path + "/tb_passing.vhd"
        filename = get_file_path(filename)
        hr.add_files(filename, "test_lib")
        hr.set_result_check_string("passing testcase")

        result = hr.start(
            sim_options=["--wave=wave_file.vcd", "--gtk=gtk_file.vcd"], gui=True
        )

        matches = []
        for root, dirnames, filenames in os.walk("./hdlregression/test/"):
            for filename in fnmatch.filter(filenames, "*_file.vcd"):
                matches.append(os.path.join(root, filename))

        assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."
        assert result == 0, "check return code"
