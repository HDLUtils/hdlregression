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


@pytest.fixture(scope="session")
def sim_env():
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


def _add_passing_tb(hr: HDLRegression, tb_path: str, library_name: str):
    """
    Use existing tb_passing.vhd from test/tb.
    """
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename=filename, library_name=library_name)
    hr.set_result_check_string("passing testcase")


def _discover_first_base_test_triplet(hr: HDLRegression):
    """
    Discover (entity, architecture, testcase, generics) from HDLRegression internals,
    so we don't guess names.

    This relies on runner/testbuilder being available after hr.start().
    """
    # After start(), runner + testbuilder exist
    testbuilder = hr.runner.testbuilder
    base_tests = testbuilder.base_tests_container.get()
    assert len(base_tests) >= 1, "Expected at least one base test to exist after start()"

    t = base_tests[0]
    entity = t.get_name()
    architecture = t.get_arch().get_name()
    testcase = t.get_tc()  # can be None
    generics = []          # keep empty for these unit tests
    return entity, architecture, testcase, generics


def _set_testgroup(hr: HDLRegression, name: str):
    """
    Use the public API if it exists, otherwise go via settings.
    """
    if hasattr(hr, "set_testgroup"):
        hr.set_testgroup(name)
    else:
        hr.settings.set_testgroup(name)


def test_add_to_testgroup_creates_container_and_stores_tuple(tb_path, sim_env):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    _add_passing_tb(hr, tb_path, library_name="lib_1")

    hr.add_to_testgroup(
        testgroup_name="tg_store",
        entity="tb_passing",
        architecture=None,
        testcase=None,
        generic=[],
    )

    tg = hr._get_testgroup_container(testgroup_name="tg_store", create_if_not_found=False)
    assert tg is not None, "Expected testgroup container to exist"
    assert ("tb_passing", None, None, []) in tg.get(), "Expected stored tuple not found"


def test_start_with_testgroup_runs_selected(tb_path, sim_env):
    """
    NO dry_run.
    Testgroup selection does NOT include library, so selecting by (entity, arch, tc)
    will match all libraries that contain the same TB/arch/tc.

    Therefore, when we add the same TB to two libraries, we EXPECT both tests to run.
    """
    if sim_env["simulator"] == "":
        pytest.skip("No supported simulator installed")

    clear_output()

    # 1) First run: run normally to discover exact (entity, arch, tc)
    hr1 = HDLRegression(simulator=sim_env["simulator"])
    _add_passing_tb(hr1, tb_path, library_name="lib_1")
    _add_passing_tb(hr1, tb_path, library_name="lib_2")

    rc1 = hr1.start()
    assert rc1 == 0, f"Expected initial run to succeed (rc={rc1})"

    entity, architecture, testcase, generics = _discover_first_base_test_triplet(hr1)

    # 2) Second run: run via testgroup using the discovered exact strings
    clear_output()
    hr2 = HDLRegression(simulator=sim_env["simulator"])
    _add_passing_tb(hr2, tb_path, library_name="lib_1")
    _add_passing_tb(hr2, tb_path, library_name="lib_2")

    hr2.add_to_testgroup(
        testgroup_name="tg_run_one",
        entity=entity,
        architecture=architecture,
        testcase=testcase,
        generic=generics,
    )
    _set_testgroup(hr2, "tg_run_one")

    rc2 = hr2.start()
    assert rc2 == 0, f"Expected testgroup run to succeed (rc={rc2})"

    pass_tests, fail_tests, not_run_tests = hr2.get_results()

    assert len(fail_tests) == 0, "Expected no failing tests"

    # IMPORTANT: Because library is not part of testgroup matching, both libs match.
    assert len(pass_tests) == 2, (
        "Expected both tests to run because testgroup does not filter on library. "
        f"Got pass_tests={len(pass_tests)}, not_run_tests={len(not_run_tests)}"
    )
    assert len(not_run_tests) == 0, "Expected no NOT_RUN when both tests match the testgroup selector"


def test_start_with_unknown_testgroup_returns_1(tb_path, sim_env):
    """
    If testgroup doesn't exist, _build_testgroup() ends up with 0 tests_to_run,
    sets return_code=1.
    """
    if sim_env["simulator"] == "":
        pytest.skip("No supported simulator installed")

    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    _add_passing_tb(hr, tb_path, library_name="lib_1")

    _set_testgroup(hr, "this_testgroup_does_not_exist")

    rc = hr.start()
    assert rc == 1, f"Expected rc=1 for unknown/empty testgroup (rc={rc})"