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
import subprocess
import shutil

from pathlib import Path
from hdlregression import HDLRegression


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
        subprocess.run([simulator, version], check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def sim_env():
    # Detect platform and simulators
    platform_info = platform.system()
    modelsim_installed = is_simulator_installed("vsim")
    ghdl_installed = is_simulator_installed("ghdl")
    nvc_installed = is_simulator_installed("nvc")
    rp_installed = is_simulator_installed("vsimsa")
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
        "riviera-pro": rp_installed,
        "not-a-simulator": False,
        "simulator": simulator,
    }

DUMMY_SIM_TEMPLATE = r"""
import sys
from hdlregression import HDLRegression
from hdlregression.settings import UnavailableSimulatorError

def main():
    try:
        hr = HDLRegression()
        hr.add_files("{}", "test_lib_1")
        hr.add_files("{}", "test_lib_1")
        hr.add_files("{}", "test_lib_2")
        hr.add_files("{}", "test_lib_2")

        hr.set_result_check_string(" : sim done")
        result = hr.start()
        sys.exit(result)

    except UnavailableSimulatorError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

def create_dummy_sim(tmp_path: Path, tb_path: str) -> Path:
    """
    Lager en midlertidig sim_dummy.py som konfigurerer HDLRegression
    med de testbench-filene vi trenger.
    """
    ent1  = get_file_path(tb_path + "/my_tb_ent.vhd")
    arch1 = get_file_path(tb_path + "/my_tb_arch_1.vhd")
    ent2  = get_file_path(tb_path + "/my_tb_ent.vhd")
    arch2 = get_file_path(tb_path + "/my_tb_arch_2.vhd")

    code = DUMMY_SIM_TEMPLATE.format(ent1, arch1, ent2, arch2)

    sim_path = tmp_path / "sim_dummy.py"
    sim_path.write_text(code)
    return sim_path


def run_cli(tmp_path : str, tb_path: str, cmd : list) -> subprocess.CompletedProcess:
    sim_path = create_dummy_sim(tmp_path, tb_path)   
    full_cmd = [sys.executable, str(sim_path)] + cmd
    result = subprocess.run(
        full_cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    return result


@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_list_testcase(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["--listTestcase", "-s", sim_name])

    assert result.stderr == ""

    out = result.stdout
    assert "TC:1 - my_tb_arch.arch_1" in out, "check: testcase 1 listed"
    assert "TC:2 - my_tb_arch.arch_2" in out, "check: testcase 2 listed"
    assert result.returncode == 1, "check: return code is 1 for no tests run"


@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro', 'not-a-simulator'])
def test_select_sim(tmp_path, tb_path, sim_env, sim_name):
    if sim_name != 'not-a-simulator' and not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-s", sim_name])

    out = result.stdout
    err = result.stderr

    if sim_name == "not-a-simulator":
        assert result.returncode == 1, "check: return code is 1 for error"
        assert "unsupported" in err.lower() or "missing" in err.lower() or "error" in err.lower()
        assert "TC:1" not in out
        assert "TC:2" not in out

    else:
        assert err == ""
        assert "my_tb_arch.arch_1" in out
        assert "my_tb_arch.arch_2" in out
        assert result.returncode == 0, "check: return code is 0 for success"



@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_full(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "my_tb_arch.arch_1", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout


@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_partial_wildcard_arch(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "my_tb_arch.arch_*", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" in result.stdout
    assert "Running: test_lib_2.my_tb_arch.arch_2" in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout

@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_full_wildcard_arch(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "my_tb_arch.*", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" in result.stdout
    assert "Running: test_lib_2.my_tb_arch.arch_2" in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout

@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_partial_wildcard_entity(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "my_tb_*.arch_1", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" in result.stdout
    assert "Running: test_lib_2.my_tb_arch.arch_2" not in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout

@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_full_wildcard_entity(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "*.arch_2", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" not in result.stdout
    assert "Running: test_lib_2.my_tb_arch.arch_2" in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout

@pytest.mark.parametrize('sim_name', ['modelsim', 'nvc', 'ghdl', 'riviera-pro'])
def test_select_testcase_full_wildcard(tmp_path, tb_path, sim_env, sim_name):
    if not sim_env[sim_name]:
        pytest.skip("{} not installed".format(sim_name))

    clear_output()

    result = run_cli(tmp_path, tb_path, ["-tc", "*.arch_1", "-s", sim_name, "--noColor"])

    assert result.returncode == 0, (
        f"CLI failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    assert "Running: test_lib_1.my_tb_arch.arch_1" in result.stdout
    assert "Running: test_lib_2.my_tb_arch.arch_2" not in result.stdout
    assert "Result: PASS" in result.stdout
    assert "Result: FAIL" not in result.stdout
