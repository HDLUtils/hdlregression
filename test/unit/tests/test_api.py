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


def test_init_only():
    """
    Check that no tests are created in an empty project
    """
    # clear_output()
    hdlregression = HDLRegression()

    hdlregression.start()
    num_pass = hdlregression.get_num_pass_tests()
    num_fail = hdlregression.get_num_fail_tests()

    assert (num_pass == 0) and (
        num_fail == 0
    ), "Checking initialization without test run"


def test_init_default_simulator(sim_env):
    """
    Test init without arguments
    """
    clear_output()
    hr = HDLRegression()
    simulator = sim_env["simulator"]

    assert (
        simulator == hr.settings.get_simulator_name()
    ), "checking init default simulator"


@pytest.mark.modelsim
def test_init_set_simulator_modelsim(sim_env):
    """
    Test init without arguments
    """
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="modelsim")

        assert (
            "MODELSIM" == hr.settings.get_simulator_name()
        ), "checking init set simulator"


@pytest.mark.ghdl
def test_init_set_simulator_ghdl(sim_env):
    """
    Test init without arguments
    """
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="GHDL")

        assert "GHDL" == hr.settings.get_simulator_name(), "checking init set simulator"


@pytest.mark.nvc
def test_init_set_simulator_nvc(sim_env):
    """
    Test init without arguments
    """
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="NVC")

        assert "NVC" == hr.settings.get_simulator_name(), "checking init set simulator"


def test_init_default_init_from_gui():
    """
    Test init without arguments
    """
    clear_output()
    hr = HDLRegression()

    assert hr.init_from_gui is False, "checking init default init_from_gui"


def test_set_library():
    clear_output()
    hr = HDLRegression()

    hr.set_library(library_name="new_default_lib_name")
    lib_name = hr.settings.get_library_name()
    assert lib_name == "new_default_lib_name", "checking setting default library name"


def test_add_precompiled_library():
    clear_output()
    hr = HDLRegression()

    lib_name = "pytest_lib"
    compile_path = "../precompiled_path"

    hr.add_precompiled_library(compile_path=compile_path, library_name=lib_name)

    lib = hr._get_library_object(library_name=lib_name)

    assert (
        lib.get_is_precompiled() is True
    ), "checking library is precompiled class (%s)" % (lib.get_name())
    assert lib.get_name() == lib_name, "checking precompiled library name"
    assert (
        lib.get_compile_path() == compile_path
    ), "checking precompiled library path setting"


def test_start_dry_run_parameter():
    clear_output()
    hr = HDLRegression()
    return_code = hr.start(dry_run=True)
    assert return_code == 1, "checking dry_run return code - exp 1 for no testcases run"


def test_default_library_with_add_files(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()
    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename)
    hr.start(dry_run=True)
    lib = hr._get_library_object(library_name="my_work_lib")
    assert lib.get_name() == "my_work_lib", "checking default library name"


def test_set_library_with_add_files(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()
    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename, library_name="new_library_name")
    hr.start(dry_run=True)
    lib = hr._get_library_object(library_name="new_library_name")
    assert lib.get_name() == "new_library_name", "checking default library name"


def test_add_file_with_default_settings(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()

    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename, library_name="new_library_name")
    library = hr._get_library_object(library_name="new_library_name")
    hr._prepare_libraries()

    module_list = [module.get_name() for module in library._get_list_of_lib_modules()]
    assert "simple_tb" in module_list, "check modules"

    for file_obj in library.get_hdlfile_list():
        assert (
            file_obj.get_hdl_version() == "2008"
        ), "check default file version for %s" % (file_obj.get_name())
        assert (
            file_obj.get_library().get_name() == "new_library_name"
        ), "check library for file obj"
        assert file_obj.get_com_options() == hr.settings.get_com_options(
            "vhdl"
        ), "check default VHDL compile options"
        assert (
            file_obj.get_code_coverage() is False
        ), "check default code coverage setting"


def test_add_file_with_new_settings(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(
        filename=filename,
        library_name="new_library_name",
        hdl_version="1993",
        com_options=["some_option"],
        code_coverage=True,
    )
    library = hr._get_library_object(library_name="new_library_name")
    hr._prepare_libraries()

    module_list = [module.get_name() for module in library._get_list_of_lib_modules()]
    assert "simple_tb" in module_list, "check modules"

    for file_obj in library.get_hdlfile_list():
        assert file_obj.get_hdl_version() == "1993", "check file version for %s" % (
            file_obj.get_name()
        )
        assert (
            file_obj.get_library().get_name() == "new_library_name"
        ), "check library for file obj"
        assert file_obj.get_com_options() == [
            "some_option"
        ], "check VHDL compile options"
        assert file_obj.get_code_coverage() is True, "check code coverage setting"


def test_add_library_dependency(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename, library_name="lib_1")
    hr.add_files(filename=filename, library_name="dep_lib_1")
    hr.add_files(filename=filename, library_name="dep_lib_2")

    library = hr._get_library_object(library_name="lib_1")

    hr.set_dependency(library_name="lib_1", dependent_libs=["dep_lib_1", "dep_lib_2"])
    hr._prepare_libraries()

    dep_libs = [lib.get_name() for lib in library.get_lib_obj_dep()]
    assert "dep_lib_1" in dep_libs, "check dependency library"
    assert "dep_lib_2" in dep_libs, "check dependency library"


def test_default_library():
    clear_output()
    hr = HDLRegression()

    assert hr.settings.get_library_name() == "my_work_lib", "check default library name"


def test_new_default_library():
    clear_output()
    hr = HDLRegression()

    hr.set_library(library_name="new_default_lib")

    assert (
        hr.settings.get_library_name() == "new_default_lib"
    ), "check new default library name"


def test_add_generics(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename, library_name="lib_1")

    hr.add_generics(entity="simple_tb", architecture="test_arch", generics=["GC_1", 2])

    containers = hr.generic_container.get()
    assert len(containers) == 1, "check number of generics"
    assert containers[0].get_name() == "simple_tb", "check correct generic container"

    for generic in containers[0].get():
        assert generic[0] == "test_arch", "check architecture set for generic"
        assert generic[1] == ["GC_1", 2], "check set generic"


def test_generate_report_defaults():
    clear_output()
    hr = HDLRegression()
    hr.gen_report()

    assert (
        hr.reporter.get_report_compile_order() is False
    ), "check default reporting of compile order"
    assert (
        hr.reporter.get_report_spec_cov() is False
    ), "check default reporting of specification coverage"
    assert (
        hr.reporter.get_report_library() is False
    ), "check default no library reporting"


def test_generate_report_updated():
    clear_output()
    hr = HDLRegression()
    hr.gen_report(
        report_file="test_report.csv", compile_order=True, spec_cov=True, library=True
    )

    assert (
        hr.reporter.get_report_compile_order() is True
    ), "check reporting of compile order"
    assert (
        hr.reporter.get_report_spec_cov() is True
    ), "check reporting of specification coverage"
    assert hr.reporter.get_report_library() is True, "check library set"
    assert hr.reporter.get_filename() == "test_report.csv", "check report file name"


@pytest.mark.modelsim
def test_set_simulator_modelsim(sim_env):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression()

        simulator = sim_env["simulator"]
        com_options = ["some_options_1"]
        simulator_dummy_path = "../../test"
        hr.set_simulator(
            simulator=simulator, path=simulator_dummy_path, com_options=com_options
        )

        assert (
            hr.settings.get_simulator_name() == simulator
        ), "check simulator selection"
        assert (
            hr.settings.get_com_options() == com_options
        ), "checking simulator options"
        assert (
            hr.settings.get_simulator_path() == simulator_dummy_path
        ), "checking simulator path"


@pytest.mark.ghdl
def test_set_simulator_ghdl(sim_env):
    if not sim_env["ghdl"]:
        pytest.skip("GHDL not installed")
    else:
        clear_output()
        hr = HDLRegression()

        simulator = sim_env["simulator"]
        com_options = ["some_options_1"]
        simulator_dummy_path = "../../test"
        hr.set_simulator(
            simulator=simulator, path=simulator_dummy_path, com_options=com_options
        )

        assert (
            hr.settings.get_simulator_name() == simulator
        ), "check simulator selection"
        assert (
            hr.settings.get_com_options() == com_options
        ), "checking simulator options"
        assert (
            hr.settings.get_simulator_path() == simulator_dummy_path
        ), "checking simulator path"


@pytest.mark.nvc
def test_set_simulator_nvc(sim_env):
    if not sim_env["nvc"]:
        pytest.skip("NVC not installed")
    else:
        clear_output()
        hr = HDLRegression()

        simulator = sim_env["simulator"]
        com_options = ["some_options_1"]
        simulator_dummy_path = "../../test"
        hr.set_simulator(
            simulator=simulator, path=simulator_dummy_path, com_options=com_options
        )

        assert (
            hr.settings.get_simulator_name() == simulator
        ), "check simulator selection"
        assert (
            hr.settings.get_com_options() == com_options
        ), "checking simulator options"
        assert (
            hr.settings.get_simulator_path() == simulator_dummy_path
        ), "checking simulator path"


def test_set_result_check_string():
    clear_output()
    hr = HDLRegression()
    new_string = "new_string"
    hr.set_result_check_string(check_string=new_string)

    assert (
        hr.settings.get_result_check_str() == new_string
    ), "check setting of new test string"


def test_add_testcase(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()
    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename)
    hr.add_testcase("simple_tb.simple_arch.test_1")
    assert hr.settings.get_testcase() == [
        "simple_tb",
        "simple_arch",
        "test_1",
    ], "check testcase selection"


def test_add_to_testgroup(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()
    filename = get_file_path(tb_path + "/tb_simple.vhd")
    hr.add_files(filename=filename)
    hr.add_testcase("simple_tb.simple_arch.test_1")

    hr.add_to_testgroup(
        testgroup_name="test_1",
        entity="simple_tb",
        architecture="simple_arch",
        testcase="test_1",
        generic=[],
    )
    testgroup = hr._get_testgroup_container(
        testgroup_name="test_1", create_if_not_found=False
    )
    for testcase in testgroup.get():
        assert testcase == ("simple_tb", "simple_arch", "test_1", []), "check testgroup"


def test_default_testcase_identifier():
    clear_output()
    hr = HDLRegression()
    assert (
        hr.settings.get_testcase_identifier_name().upper() == "GC_TESTCASE"
    ), "check default tc identifier"


def test_set_testcase_identifier():
    clear_output()
    hr = HDLRegression()
    tc_identifier = "NEW_TC_IDENTIFIER"
    hr.set_testcase_identifier_name(tc_id=tc_identifier)
    assert (
        hr.settings.get_testcase_identifier_name().upper() == tc_identifier
    ), "check setting new tc identifier"


def test_set_code_coverage_default():
    clear_output()
    hr = HDLRegression()
    assert (
        hr.hdlcodecoverage.get_code_coverage_settings() == None
    ), "check default code coverage settings"
    assert (
        hr.hdlcodecoverage.get_code_coverage_file() == None
    ), "check default code coverage file"
    assert (
        hr.hdlcodecoverage.get_exclude_file() == None
    ), "check default code coverage exclude file"
    assert hr.hdlcodecoverage.get_options() == None, "check default merge options"


@pytest.mark.modelsim
def test_set_code_coverage_updated_modelsim(sim_env, tb_path):
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        hr = HDLRegression(simulator="MODELSIM")
        filename = get_file_path(tb_path + "/tb_simple.vhd")
        hr.add_files(filename=filename, library_name="lib_1", code_coverage=True)
        hr.set_code_coverage(
            code_coverage_settings="btc",
            code_coverage_file="test_cov.ucdb",
            exclude_file="exclude.tcl",
            merge_options="some_option",
        )

        assert (
            hr.hdlcodecoverage.get_code_coverage_settings() == "btc"
        ), "check code coverage settings"
        assert (
            "test_cov.ucdb" in hr.hdlcodecoverage.get_code_coverage_file()
        ), "check code coverage file without complete path"
        assert (
            "exclude.tcl" in hr.hdlcodecoverage.get_exclude_file()
        ), "check code coverage exclude file without complete path"
        assert hr.hdlcodecoverage.get_options() == "some_option", "check merge options"


def test_no_default_com_options(sim_env, tb_path):
    clear_output()
    hr = HDLRegression()
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename=filename, library_name="lib_1")
    hr.set_result_check_string("passing testcase")
    hr.start(no_default_com_options=True)

    assert hr.settings.get_com_options() == [], "check no default com options set"


def test_get_results_with_failing_design_compile(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    # TB 1
    filename = get_file_path(tb_path + "/failing_compile.vhd")
    hr.add_files(filename=filename, library_name="lib_1")
    # TB 2
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename=filename, library_name="lib_1")

    hr.set_result_check_string("passing testcase")
    hr.start()

    result = hr.get_results()
    pass_test, fail_test, not_run_test = result[0], result[1], result[2]

    assert len(pass_test) == 0, "check get_results() pass_test"
    assert len(fail_test) == 0, "check get_results() fail_test"
    assert len(not_run_test) == 2, "check get_results() not_run_test"


def test_get_results_with_failing_tb_compile(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    # TB 1
    filename = get_file_path(tb_path + "/passing_compile.vhd")
    hr.add_files(filename=filename, library_name="lib_1")
    # TB 2
    filename = get_file_path(tb_path + "/tb_compile_error.vhd")
    hr.add_files(filename=filename, library_name="lib_1")

    hr.set_result_check_string("passing testcase")
    hr.start()

    result = hr.get_results()
    pass_test, fail_test, not_run_test = result[0], result[1], result[2]

    assert len(pass_test) == 0, "check get_results() pass_test"
    assert len(fail_test) == 0, "check get_results() fail_test"
    assert len(not_run_test) == 2, "check get_results() not_run_test"


def test_get_results(sim_env, tb_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    filename = get_file_path(tb_path + "/tb_passing.vhd")
    hr.add_files(filename=filename, library_name="lib_1")

    hr.set_result_check_string("passing testcase")
    hr.start()

    result = hr.get_results()
    pass_test, fail_test, not_run_test = result[0], result[1], result[2]

    assert len(pass_test) == 1, "check get_results() pass_test"
    assert len(fail_test) == 0, "check get_results() fail_test"
    assert len(not_run_test) == 0, "check get_results() not_run_test"


def test_compile_uvvm(sim_env, uvvm_path):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])

    if not is_folder_present(uvvm_path):
        pytest.skip(f"UVVM path '{uvvm_path}' not found, skipping test.")
    else:
        success = hr.compile_uvvm(path_to_uvvm=uvvm_path)
        hr.start()

        assert success is True, "Compile UVVM success"

        compiled_lib_list = hr.settings.get_library_compile()
        lib_name_list = [lib.get_name() for lib in compiled_lib_list]
        assert "bitvis_vip_sbi" in lib_name_list, "Check recompiled"


def test_compile_uvvm_wrong_path(sim_env):
    clear_output()
    hr = HDLRegression(simulator=sim_env["simulator"])
    uvvm_path = "../wrong/path/to/uvvm"
    success = hr.compile_uvvm(uvvm_path)

    assert success is False, "check failing UVVM compilation"
